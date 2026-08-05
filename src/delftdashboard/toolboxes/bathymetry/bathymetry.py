"""Bathymetry import toolbox for DelftDashboard.

Allows importing GeoTIFF, NetCDF, and XYZ files as Cloud Optimized
GeoTIFF datasets into the topography database.
"""

import os
import traceback

import numpy as np
import rasterio
import yaml
from cht_utils.cog import geotiff_to_cog, netcdf_to_cog, xyz_to_cog
from pyproj import CRS

from delftdashboard.app import app
from delftdashboard.misc.select_other_geographic.select_geographic_crs import (
    select_geographic_crs,
)
from delftdashboard.misc.select_other_projected.select_projected_crs import (
    select_projected_crs,
)
from delftdashboard.operations.toolbox import GenericToolbox


class Toolbox(GenericToolbox):
    """Toolbox for importing bathymetry/topography datasets."""

    def __init__(self, name):
        super().__init__()
        self.name = name
        self.long_name = "Bathymetry"

    def initialize(self):
        """Set up default GUI variables."""
        group = "bathymetry"
        app.gui.setvar(group, "import_file_format_names", ["GeoTIFF", "NetCDF", "XYZ"])
        app.gui.setvar(group, "import_file_format_values", ["geotiff", "netcdf", "xyz"])
        app.gui.setvar(group, "import_file_format", "geotiff")
        app.gui.setvar(group, "import_file_filter", "GeoTIFF (*.tif;*.tiff)")
        app.gui.setvar(group, "import_file_selected", False)
        app.gui.setvar(group, "import_file_name", "")
        app.gui.setvar(group, "import_as", "cog")

        app.gui.setvar(group, "dataset_name", "")
        app.gui.setvar(group, "dataset_long_name", "")
        app.gui.setvar(group, "dataset_source", "")

        app.gui.setvar(group, "variable_names", [])
        app.gui.setvar(group, "variable_name", "")

        app.gui.setvar(group, "vertical_datum", "unknown")
        app.gui.setvar(group, "vertical_units", "m")
        app.gui.setvar(group, "vertical_difference_with_msl", 0.0)

    def set_layer_mode(self, mode):
        """Handle layer mode changes (no layers for this toolbox)."""

    def add_layers(self):
        """Register map layers (none for this toolbox)."""

    def import_dataset(self):
        """Import a bathymetry file and add it to the topography data catalog."""
        fmt = app.gui.getvar("bathymetry", "import_file_format")
        import_as = app.gui.getvar("bathymetry", "import_as")
        filename = app.gui.getvar("bathymetry", "import_file_name")
        name = app.gui.getvar("bathymetry", "dataset_name")
        long_name = app.gui.getvar("bathymetry", "dataset_long_name")
        src = app.gui.getvar("bathymetry", "dataset_source")

        # Check if name already exists
        short_names, _, _ = app.topography_data_catalog.dataset_names()
        if name in short_names:
            yes = app.gui.window.dialog_yes_no(
                "Dataset name already exists! Do you want to overwrite it?", ""
            )
            if not yes:
                return

        if import_as == "tiles":
            self.import_dataset_tiles(fmt, filename, name, long_name, src)
            return
        elif import_as != "cog":
            app.gui.window.dialog_warning(f"Unknown import option: {import_as}")
            return

        dbpath = app.topography_data_catalog.path
        output_dir = os.path.join(dbpath, name)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        filename_cog = os.path.join(output_dir, f"{name}.tif")

        # Convert to COG
        wb = app.gui.window.dialog_wait("Generating Cloud Optimized GeoTIFF ...")
        try:
            if fmt == "geotiff":
                ok = geotiff_to_cog(filename, filename_cog)
            elif fmt == "netcdf":
                variable_name = app.gui.getvar("bathymetry", "variable_name")
                ok = netcdf_to_cog(filename, variable_name, filename_cog)
            elif fmt == "xyz":
                xyz = np.loadtxt(filename)
                xx, yy = xyz[:, 0], xyz[:, 1]
                d = np.sqrt((xx[1] - xx[0]) ** 2 + (yy[1] - yy[0]) ** 2)
                if d > 0.1:
                    crs = select_projected_crs(app)
                else:
                    crs = select_geographic_crs(app)
                if crs is None:
                    wb.close()
                    return
                ok = xyz_to_cog(filename, filename_cog, crs)
            else:
                ok = False
        except Exception as e:
            traceback.print_exc()
            wb.close()
            app.gui.window.dialog_warning(f"Error converting to COG:\n{e}")
            return
        wb.close()

        if not os.path.exists(filename_cog) or not ok:
            app.gui.window.dialog_warning("An error occurred while importing dataset!")
            return

        # Read CRS from the output file
        with rasterio.open(filename_cog) as fff:
            crs = CRS(fff.crs)

        vertical_datum = app.gui.getvar("bathymetry", "vertical_datum")
        vertical_units = app.gui.getvar("bathymetry", "vertical_units")
        difference_with_msl = app.gui.getvar(
            "bathymetry", "vertical_difference_with_msl"
        )

        # Catalog entry for data_catalog_local.yml (the single registration
        # point for imported datasets; uri relative to the database root).
        # Include ``crs`` in the metadata when the COG isn't already in
        # EPSG:4326 — some hydromt read paths silently default the catalog CRS
        # to 4326 when it's omitted, which yields empty-data bbox queries for
        # projected sources (see the AHN RD New case).
        local_metadata = {
            "category": "bathymetry",
            "unit": vertical_units,
            "long_name": long_name,
            "source": src,
            "difference_with_msl": difference_with_msl,
        }
        epsg = crs.to_epsg()
        if epsg is not None and epsg != 4326:
            local_metadata["crs"] = epsg
        local_entry = {
            "data_type": "RasterDataset",
            "driver": "rasterio",
            "uri": f"{name}/{name}.tif",
            "metadata": local_metadata,
        }

        self._register_imported_dataset(name, long_name, src, local_entry)

    def import_dataset_tiles(self, fmt, filename, name, long_name, src):
        """Import a bathymetry file as a tiled web map (slippy tiles).

        The input is first converted to a temporary COG (so the tiler can read
        arbitrary zoom windows efficiently through its overviews), after which
        cht_tiling's TiledWebMap generates the terrarium16-encoded tile pyramid
        directly into the topography database. The maximum zoom level is
        derived from the source resolution. The dataset is registered with the
        hydromt ``slippy_tile`` driver, the same driver used for e.g.
        ``gebco_2024``.
        """
        import math
        import shutil
        import tempfile

        from cht_tiling import TiledWebMap
        from hydromt import DataCatalog

        vertical_units = app.gui.getvar("bathymetry", "vertical_units")
        difference_with_msl = app.gui.getvar(
            "bathymetry", "vertical_difference_with_msl"
        )

        dbpath = app.topography_data_catalog.path
        output_dir = os.path.join(dbpath, name)
        tmp_dir = tempfile.mkdtemp(prefix="ddb_tile_import_")
        filename_cog = os.path.join(tmp_dir, f"{name}.tif")

        # --- Convert input to a temporary COG (tiling intermediate) ----------
        wb = app.gui.window.dialog_wait("Preparing input data ...")
        try:
            if fmt == "geotiff":
                ok = geotiff_to_cog(filename, filename_cog)
            elif fmt == "netcdf":
                variable_name = app.gui.getvar("bathymetry", "variable_name")
                ok = netcdf_to_cog(filename, variable_name, filename_cog)
            elif fmt == "xyz":
                xyz = np.loadtxt(filename)
                xx, yy = xyz[:, 0], xyz[:, 1]
                d = np.sqrt((xx[1] - xx[0]) ** 2 + (yy[1] - yy[0]) ** 2)
                if d > 0.1:
                    crs = select_projected_crs(app)
                else:
                    crs = select_geographic_crs(app)
                if crs is None:
                    wb.close()
                    shutil.rmtree(tmp_dir, ignore_errors=True)
                    return
                ok = xyz_to_cog(filename, filename_cog, crs)
            else:
                ok = False
        except Exception as e:
            traceback.print_exc()
            wb.close()
            shutil.rmtree(tmp_dir, ignore_errors=True)
            app.gui.window.dialog_warning(f"Error preparing input data:\n{e}")
            return
        wb.close()

        if not os.path.exists(filename_cog) or not ok:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            app.gui.window.dialog_warning("An error occurred while importing dataset!")
            return

        # --- Dataset extent and resolution -----------------------------------
        with rasterio.open(filename_cog) as ds:
            src_crs = CRS(ds.crs)
            res_x = abs(ds.transform.a)
            bounds = ds.bounds

        if src_crs.is_geographic:
            lon_range = [bounds.left, bounds.right]
            lat_range = [bounds.bottom, bounds.top]
            lat_mid = 0.5 * (lat_range[0] + lat_range[1])
            dx_max_zoom = res_x * 111320.0 * max(0.1, math.cos(math.radians(lat_mid)))
        else:
            from pyproj import Transformer

            tr = Transformer.from_crs(src_crs, CRS.from_epsg(4326), always_xy=True)
            lons, lats = tr.transform(
                [bounds.left, bounds.left, bounds.right, bounds.right],
                [bounds.bottom, bounds.top, bounds.bottom, bounds.top],
            )
            lon_range = [min(lons), max(lons)]
            lat_range = [min(lats), max(lats)]
            dx_max_zoom = res_x  # assume projected units are metres

        # Web-mercator tiling is undefined beyond ~85 degrees
        lat_range = [max(lat_range[0], -85.0), min(lat_range[1], 85.0)]

        # --- Temporary hydromt catalog for the tiler --------------------------
        tmp_yml = os.path.join(tmp_dir, "catalog.yml")
        with open(tmp_yml, "w") as f:
            yaml.dump(
                {
                    # NOTE: absolute uri - a relative meta.root in a yml passed
                    # to DataCatalog(data_libs=...) resolves against the process
                    # working directory, not the yml location.
                    name: {
                        "data_type": "RasterDataset",
                        "driver": "rasterio",
                        "uri": filename_cog.replace(os.sep, "/"),
                    },
                },
                f,
                sort_keys=False,
            )
        tmp_catalog = DataCatalog(data_libs=[tmp_yml])

        # --- Generate the tile pyramid ----------------------------------------
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        twm = TiledWebMap(
            output_dir,
            data=[{"name": name}],
            type="data",
            parameter="elevation",
            encoder="terrarium16",
            name=name,
            long_name=long_name,
            source=src,
            vertical_units=vertical_units,
            difference_with_msl=difference_with_msl,
            data_catalog=tmp_catalog,
            lon_range=lon_range,
            lat_range=lat_range,
            dx_max_zoom=dx_max_zoom,
            write_metadata=True,
            make_webviewer=True,
            parallel=True,
        )
        dlg = app.gui.window.dialog_wait(
            "Generating tiles ... (progress is printed to the console)"
        )
        try:
            twm.make()
        except Exception as e:
            traceback.print_exc()
            dlg.close()
            # Keep the temporary COG so a retry / diagnosis does not need to
            # redo the (potentially long) conversion.
            print(f"Temporary COG kept for diagnosis in: {tmp_dir}")
            app.gui.window.dialog_warning(f"Error generating tiles:\n{e}")
            return
        dlg.close()
        max_zoom = int(twm.zoom_range[1])
        shutil.rmtree(tmp_dir, ignore_errors=True)

        # --- Register in the topography database ------------------------------
        entry_metadata = {
            "crs": 3857,
            "category": "bathymetry",
            "unit": vertical_units,
            "long_name": long_name,
            "source": src,
            "difference_with_msl": difference_with_msl,
        }
        driver = {
            "name": "slippy_tile",
            "options": {
                "encoder": "terrarium16",
                "variable_name": "elevation",
                "max_zoom": max_zoom,
            },
        }
        local_entry = {
            "data_type": "RasterDataset",
            "driver": driver,
            "uri": name,
            "metadata": entry_metadata,
        }

        self._register_imported_dataset(name, long_name, src, local_entry)

    def _register_imported_dataset(self, name, long_name, src, local_entry):
        """Register a freshly imported dataset: local catalog + topography menu.

        Parameters
        ----------
        name, long_name, src : str
            Dataset identifiers.
        local_entry : dict
            Catalog entry for data_catalog_local.yml (uri relative to the
            bathymetry database root).
        """
        # Single registration point: data_catalog_local.yml + in-memory catalog.
        # Entries here take precedence over the remote catalog (data_catalog_remote.yml).
        app.topography_data_catalog.register_local_entry(name, local_entry)

        # Add to topography menu
        source_menu = app.gui.window.find_menu_item_by_id(f"topography.{src}")
        if source_menu is None:
            source_menu = {
                "text": src,
                "id": f"topography.{src}",
                "menu": [],
            }
            app.gui.window.add_menu_from_dict(
                source_menu, "topography", has_children=True
            )
        dependency = [
            {
                "action": "check",
                "checkfor": "all",
                "check": [
                    {
                        "variable": "topography_dataset",
                        "operator": "eq",
                        "value": name,
                    }
                ],
            }
        ]
        dataset_menu = {
            "id": f"topography.{name}",
            "variable_group": "view_settings",
            "text": long_name,
            "separator": False,
            "checkable": True,
            "option": name,
            "method": "select_dataset",
            "dependency": dependency,
        }
        app.gui.window.add_menu_from_dict(
            dataset_menu, f"topography.{src}", has_children=False
        )

        app.gui.window.dialog_info(
            "Dataset imported successfully! It has been added to the Topography menu.",
            "Success",
        )

    def export_dataset(self):
        """Export a dataset (not yet implemented)."""
        if not self.check_dataset_name():
            return

    def check_dataset_name(self):
        """Validate the dataset name contains only safe characters."""
        name = app.gui.getvar("bathymetry", "dataset_name")
        if not all(c.isalnum() or c in "_-" for c in name):
            app.gui.window.dialog_warning(
                "Dataset name can only contain letters, numbers, _ and -"
            )
            return False
        return True
