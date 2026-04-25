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
        """Load all data catalog YAML files from the database directory."""
        # First try the master catalog at the root
        master = os.path.join(path, "data_catalog.yml")
        if os.path.exists(master):
            before = set(self.catalog.sources)
            self.catalog.from_yml(master, root=path)
            for name in set(self.catalog.sources) - before:
                self._source_yaml[name] = master
        else:
            # Fall back to individual catalogs in sub-folders
            for yml in sorted(glob.glob(os.path.join(path, "*", "data_catalog.yml"))):
                before = set(self.catalog.sources)
                self.catalog.from_yml(yml, root=os.path.dirname(yml))
                for name in set(self.catalog.sources) - before:
                    self._source_yaml[name] = yml

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
