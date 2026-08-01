"""Topography/bathymetry data catalog for DelftDashboard.

Wraps the HydroMT ``DataCatalog`` and provides the source/dataset browsing
interface that the DDB GUI expects.
"""

import glob
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import geopandas as gpd
from hydromt import DataCatalog
from shapely.geometry import box

logger = logging.getLogger(__name__)


class TopographyDataCatalog:
    """Browse and query topography/bathymetry datasets.

    Loads all ``data_catalog.yml`` files found under *path* (one per
    dataset sub-folder) and optionally a master catalog at the root.

    Parameters
    ----------
    path : str
        Root directory of the topography/bathymetry database.
    """

    def __init__(self, path: str) -> None:
        self.path = path
        self.catalog = DataCatalog()
        # Maps source name → YAML file that provided it. Populated by
        # :py:meth:`_load` and consumed by :py:meth:`data_libs_for` to
        # emit an accurate ``global.data_libs`` in the model setup yaml.
        self._source_yaml: Dict[str, str] = {}
        self._load(path)

    def _load(self, path: str) -> None:
        """Load and merge all data catalog YAML files from the database directory.

        Two catalogs have a defined role:

        * ``data_catalog_local.yml`` - optional, maintained by the user (and
          appended to by the bathymetry import toolbox) for local datasets.
        * ``data_catalog_s3.yml``    - a copy of the catalog on the DDB S3
          bucket, refreshed by :py:meth:`update_from_s3` at every online start.
          Do not edit; it is overwritten.

        All files are merged with a first-definition-wins rule, in this order:
        local catalog, legacy root ``data_catalog.yml``, legacy per-dataset
        ``<name>/data_catalog.yml`` files, and finally the S3 catalog. A local
        definition therefore always overrides a same-named S3 dataset.
        """
        candidates: List[Tuple[str, str]] = [
            (os.path.join(path, "data_catalog_local.yml"), path),
            (os.path.join(path, "data_catalog.yml"), path),  # legacy master
        ]
        candidates += [
            (yml, os.path.dirname(yml))
            for yml in sorted(glob.glob(os.path.join(path, "*", "data_catalog.yml")))
        ]
        candidates.append((os.path.join(path, "data_catalog_s3.yml"), path))

        for yml, root in candidates:
            if not os.path.exists(yml):
                continue
            try:
                self._merge_catalog_file(yml, root=root)
            except Exception as e:
                logger.warning("Could not load %s: %s", yml, e)

    def update_from_s3(self, s3_bucket: str, s3_key: str = "data/bathymetry") -> None:
        """Refresh the S3-provided bathymetry catalog and merge it in.

        Downloads ``<s3_key>/data_catalog.yml`` from the (public, unsigned) S3
        bucket - the hydromt data catalog maintained on the bucket itself - and
        stores it locally as ``data_catalog_s3.yml``. Its sources are then
        merged into the running catalog; datasets already defined locally
        (imported or customised by the user) take precedence. The actual
        tiles/COGs are downloaded on demand by their drivers.

        Failures are logged and never fatal (e.g. offline: a previously
        downloaded ``data_catalog_s3.yml`` was already loaded by ``_load``).

        Parameters
        ----------
        s3_bucket : str
            Bucket name, e.g. ``"deltares-ddb"``.
        s3_key : str, optional
            Key prefix of the bathymetry database on the bucket.
        """
        import boto3
        from botocore import UNSIGNED
        from botocore.client import Config

        os.makedirs(self.path, exist_ok=True)
        catalog_file = os.path.join(self.path, "data_catalog_s3.yml")
        print("Updating bathymetry database ...")
        try:
            s3 = boto3.client("s3", config=Config(signature_version=UNSIGNED))
            s3.download_file(
                Bucket=s3_bucket,
                Key=f"{s3_key}/data_catalog.yml",
                Filename=catalog_file,
            )
        except Exception:
            print(
                f"Failed to download {s3_key}/data_catalog.yml from {s3_bucket}. "
                "Bathymetry database will not be updated."
            )
            return

        added = self._merge_catalog_file(catalog_file)
        for name in added:
            print(f"Adding bathymetry dataset {name} to local database ...")

    def _merge_catalog_file(self, yml: str, root: Optional[str] = None) -> List[str]:
        """Merge sources from a catalog YAML, keeping existing sources.

        Sources whose name is already present in the catalog are left
        untouched (first definition wins), so user/local definitions always
        override the S3-provided catalog.

        Returns the names of the sources that were added.
        """
        tmp = DataCatalog()
        tmp.from_yml(yml, root=root or self.path)
        added: List[str] = []
        for name, source in tmp._sources.items():
            if name not in self.catalog.sources:
                self.catalog._sources[name] = source
                self._source_yaml[name] = yml
                added.append(name)
        return added

    def data_libs_for(self, names: List[str]) -> List[str]:
        """Return the minimal set of catalog YAML paths covering *names*.

        Used when writing a hydromt build YAML so ``global.data_libs``
        lists exactly the catalog files needed to resolve the selected
        elevation datasets. Duplicates and unknown names are dropped.
        Paths are normalised to forward-slash form so the emitted YAML
        is the same regardless of OS.
        """
        seen: List[str] = []
        for n in names:
            path = self._source_yaml.get(n)
            if not path:
                continue
            normalised = Path(path).as_posix()
            if normalised not in seen:
                seen.append(normalised)
        return seen

    def sources(self) -> Tuple[List[str], List[str]]:
        """Return a sorted list of unique source names.

        Returns
        -------
        tuple[list[str], list[str]]
            ``(source_names, source_names)`` — both lists are identical,
            matching the ``BathymetryDatabase.sources()`` interface.
        """
        source_set = set()
        for name in self.catalog.sources:
            src = self.catalog.get_source(name)
            source = getattr(src.metadata, "source", "unknown")
            source_set.add(source)
        source_names = sorted(source_set)
        return source_names, source_names

    def dataset_names(
        self, source: Optional[str] = None
    ) -> Tuple[List[str], List[str], List[str]]:
        """Return dataset names, optionally filtered by source.

        Parameters
        ----------
        source : str, optional
            If provided, only return datasets from this source.

        Returns
        -------
        tuple[list[str], list[str], list[str]]
            ``(names, long_names, source_names)``
        """
        names = []
        long_names = []
        source_names = []
        for name in sorted(self.catalog.sources):
            src = self.catalog.get_source(name)
            src_source = getattr(src.metadata, "source", "unknown")
            if source is not None and src_source != source:
                continue
            src_long_name = getattr(src.metadata, "long_name", name)
            names.append(name)
            long_names.append(src_long_name)
            source_names.append(src_source)
        return names, long_names, source_names

    def get_source(self, name: str):
        """Return the raw HydroMT source object for a dataset.

        Parameters
        ----------
        name : str
            Dataset name as it appears in the catalog.
        """
        return self.catalog.get_source(name)

    def add_to_model_catalog(self, model_data_catalog: DataCatalog) -> None:
        """Inject all topography sources into a model's data catalog.

        Parameters
        ----------
        model_data_catalog : DataCatalog
            The ``model.data_catalog`` to add sources to.
        """
        for name, src in self.catalog._sources.items():
            model_data_catalog._sources[name] = src

    def check_coverage(
        self,
        selected_datasets: List[Dict[str, Any]],
        bbox: Tuple[float, float, float, float],
        crs: int = 4326,
    ) -> Tuple[List[str], List[str]]:
        """Check which datasets have data within a bounding box.

        Parameters
        ----------
        selected_datasets : list of dict
            DDB-format list with ``"name"`` keys.
        bbox : tuple
            ``(xmin, ymin, xmax, ymax)`` in the given CRS.
        crs : int
            EPSG code of the bbox coordinates.

        Returns
        -------
        tuple[list[str], list[str]]
            ``(covered, not_covered)`` — dataset names that do/don't
            have data in the bbox.
        """
        from hydromt.error import NoDataException

        geom = gpd.GeoDataFrame(
            geometry=[box(bbox[0], bbox[1], bbox[2], bbox[3])], crs=crs
        )
        covered = []
        not_covered = []
        for ds in selected_datasets:
            name = ds["name"]
            try:
                self.catalog.get_rasterdataset(name, geom=geom)
                covered.append(name)
            except (NoDataException, IndexError, ValueError, IOError):
                not_covered.append(name)
        return covered, not_covered

    def _ensure_source_dir(self, name: str) -> None:
        """Create the local directory of a tile-based (S3) source if it is missing.

        The ``slippy_tile`` driver downloads missing tiles from S3 on demand,
        but HydroMT's URI resolver only reaches the driver when the source
        directory already exists (an *empty* directory is enough - the driver
        then downloads into it). On a fresh data folder that per-dataset
        directory may not exist yet, which makes the resolver raise
        ``NoDataException`` before any tile can be fetched. Creating the empty
        directory here lets the download bootstrap.

        On first creation, the dataset's ``index.html`` (a Leaflet viewer of the
        locally cached tiles) is also fetched from the same S3 bucket, if
        present, as a convenience. Failures are ignored.

        Restricted to ``slippy_tile`` sources so file-based datasets are never
        given a bogus directory in place of their data file.
        """
        try:
            src = self.catalog.get_source(name)
        except Exception:
            return
        driver = getattr(src, "driver", None)
        if getattr(driver, "name", "") != "slippy_tile":
            return
        folder = getattr(src, "full_uri", None) or getattr(src, "uri", None)
        if not folder:
            return
        if not os.path.isabs(folder):
            folder = os.path.join(self.path, folder)
        if os.path.isdir(folder):
            return  # already exists - resolver will find it, nothing to do
        try:
            os.makedirs(folder, exist_ok=True)
        except OSError as e:
            logger.warning("Could not create source directory %s: %s", folder, e)
            return
        # Folder was just created: fetch the local-tile viewer from S3.
        self._download_index_html(driver, folder)

    def _download_index_html(self, driver: Any, folder: str) -> None:
        """Download ``index.html`` for a slippy_tile source from its S3 bucket.

        Reads ``s3_bucket`` / ``s3_key`` from the driver options and fetches
        ``<s3_key>/index.html`` (a Leaflet viewer of the locally available
        tiles) into *folder*. Best-effort: any failure is logged and ignored so
        it never blocks the actual data fetch.
        """
        opts = getattr(driver, "options", None)
        s3_bucket = getattr(opts, "s3_bucket", None)
        s3_key = getattr(opts, "s3_key", None)
        if not (s3_bucket and s3_key):
            return
        try:
            import s3fs

            fs = s3fs.S3FileSystem(anon=True)
            remote = f"{s3_bucket}/{s3_key}/index.html"
            fs.get_file(remote, os.path.join(folder, "index.html"))
        except Exception as e:
            logger.info("Could not download index.html for tile source: %s", e)

    def get_rasterdataset(self, name: str, **kwargs):
        """Fetch raster data from the catalog.

        Passes all keyword arguments through to
        ``DataCatalog.get_rasterdataset()``.

        Parameters
        ----------
        name : str
            Dataset name.
        **kwargs
            Forwarded to ``DataCatalog.get_rasterdataset()`` (e.g.
            ``geom``, ``zoom``, ``bbox``).
        """
        # Tile sources download on demand but need their folder to exist first.
        self._ensure_source_dir(name)
        return self.catalog.get_rasterdataset(name, **kwargs)

    def resolve_elevation_list(
        self,
        selected_datasets: List[Dict[str, Any]],
        geom: gpd.GeoDataFrame,
        res: float,
    ) -> List[Dict[str, Any]]:
        """Resolve dataset names to DataArrays for hydromt elevation builders.

        Fetches raster data from the catalog for each selected dataset and
        returns an ``elevation_list`` compatible with hydromt's
        ``_parse_datasets_elevation`` (each entry has a ``"da"`` key with
        the fetched DataArray).

        Parameters
        ----------
        selected_datasets : list of dict
            DDB-format list, e.g.
            ``[{"name": "gebco_2024", "zmin": -99999, "zmax": 99999}]``.
        geom : gpd.GeoDataFrame
            Geometry (bounding box) to clip the data to.
        res : float
            Target resolution in metres.

        Returns
        -------
        list of dict
            Hydromt-format list with ``"da"`` (DataArray), ``"zmin"``,
            ``"zmax"`` keys.
        """
        result = []
        errors: List[str] = []
        for ds in selected_datasets:
            name = ds["name"]
            try:
                da = self.catalog.get_rasterdataset(
                    name, geom=geom, zoom=(res, "metre")
                )
            except Exception as e:
                logger.warning(f"Could not load dataset '{name}': {e}")
                errors.append(f"- {name}: {e}")
                continue
            entry = {"da": da}
            if "zmin" in ds:
                entry["zmin"] = ds["zmin"]
            if "zmax" in ds:
                entry["zmax"] = ds["zmax"]
            result.append(entry)
        # Re-raise when nothing resolved, so callers don't hit a
        # downstream IndexError on an empty list.
        if not result:
            raise RuntimeError(
                "No elevation datasets could be resolved for this bbox:\n"
                + "\n".join(errors)
            )
        return result


def to_hydromt_elevation_list(
    selected_datasets: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Convert DDB-format selections to a hydromt ``elevation_list``.

    DDB stores selections as ``{"name": ..., "zmin": ..., "zmax": ...}``,
    while hydromt's ``_parse_datasets_elevation`` expects the source name
    under the key ``"elevation"``. This helper rewrites each entry so
    hydromt-side code stays strict about the keys it accepts.
    """
    out: List[Dict[str, Any]] = []
    for ds in selected_datasets:
        entry: Dict[str, Any] = {"elevation": ds["name"]}
        if "zmin" in ds:
            entry["zmin"] = ds["zmin"]
        if "zmax" in ds:
            entry["zmax"] = ds["zmax"]
        out.append(entry)
    return out
