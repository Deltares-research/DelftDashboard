"""Bathymetry import toolbox for DelftDashboard.

Allows importing GeoTIFF, NetCDF, and XYZ files as Cloud Optimized
GeoTIFF datasets into the topography database.
"""

import os
import traceback

import numpy as np
import rasterio
import yaml
from cht_utils import geotiff_to_cog, netcdf_to_cog, xyz_to_cog
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

        if import_as != "cog":
            app.gui.window.dialog_warning(
                "Tiles option is not implemented yet. Please use COG option."
            )
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
                ok = geotiff_to_cog.geotiff_to_cog(filename, filename_cog)
            elif fmt == "netcdf":
                variable_name = app.gui.getvar("bathymetry", "variable_name")
                ok = netcdf_to_cog.netcdf_to_cog(filename, variable_name, filename_cog)
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
                ok = xyz_to_cog.xyz_to_cog(filename, filename_cog, crs)
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

        # Write data_catalog.yml for this dataset
        catalog_entry = {
            "meta": {"root": "."},
            name: {
                "data_type": "RasterDataset",
                "driver": "rasterio",
                "uri": f"{name}.tif",
                "metadata": {
                    "category": "bathymetry",
                    "unit": vertical_units,
                    "long_name": long_name,
                    "source": src,
                    "difference_with_msl": difference_with_msl,
                },
            },
        }
        catalog_file = os.path.join(output_dir, "data_catalog.yml")
        with open(catalog_file, "w") as f:
            yaml.dump(catalog_entry, f, default_flow_style=False, sort_keys=False)

        # Add to the master data_catalog.yml
        master_file = os.path.join(dbpath, "data_catalog.yml")
        if os.path.exists(master_file):
            with open(master_file, "r") as f:
                master = yaml.safe_load(f)
            master[name] = {
                "data_type": "RasterDataset",
                "driver": "rasterio",
                "uri": f"{name}/{name}.tif",
                "metadata": {
                    "unit": vertical_units,
                    "long_name": long_name,
                    "source": src,
                    "difference_with_msl": difference_with_msl,
                },
            }
            with open(master_file, "w") as f:
                yaml.dump(master, f, default_flow_style=False, sort_keys=False)

        # Add to in-memory catalog
        app.topography_data_catalog.catalog.from_yml(catalog_file, root=output_dir)

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
