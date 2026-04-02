"""GUI callbacks for the bathymetry import tab.

Handle file format selection, file browsing, variable inspection,
and dataset import into the topography catalog.
"""

import os
from typing import Any

import xarray as xr

from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args: Any) -> None:
    """Activate the import tab."""
    map.update()


def select_import_file_format(*args: Any) -> None:
    """Update the file filter based on the selected import format."""
    fmt = app.gui.getvar("bathymetry", "import_file_format")
    if fmt == "geotiff":
        app.gui.setvar("bathymetry", "import_file_filter", "GeoTIFF (*.tif;*.tiff)")
    elif fmt == "netcdf":
        app.gui.setvar("bathymetry", "import_file_filter", "NetCDF (*.nc)")
    elif fmt == "xyz":
        app.gui.setvar("bathymetry", "import_file_filter", "XYZ (*.xyz)")
    else:
        app.gui.setvar("bathymetry", "import_file_filter", "")


def select_import_file(*args: Any) -> None:
    """Process the selected import file and extract metadata."""
    app.gui.setvar("bathymetry", "import_file_selected", True)
    # Get the file name without path and extension
    filename = app.gui.getvar("bathymetry", "import_file_name")
    basename = os.path.basename(filename)
    name, ext = os.path.splitext(basename)
    # Set the dataset name to the file name without path and extension
    app.gui.setvar("bathymetry", "dataset_name", name)
    app.gui.setvar("bathymetry", "dataset_long_name", name)

    fmt = app.gui.getvar("bathymetry", "import_file_format")
    if fmt == "netcdf":
        # Need to get a list with the variable names
        wb = app.gui.window.dialog_wait("Loading dataset ...")
        ds = xr.open_dataset(filename)
        variable_names = list(ds.data_vars)
        # Remove variables that are not 2D
        variable_names = [name for name in variable_names if ds[name].ndim == 2]
        ds.close()
        app.gui.setvar("bathymetry", "variable_names", variable_names)
        app.gui.setvar("bathymetry", "variable_name", variable_names[0])
        wb.close()


def edit_dataset_name(*args: Any) -> None:
    """Handle dataset name edit events (placeholder)."""


def edit_dataset_long_name(*args: Any) -> None:
    """Handle dataset long name edit events (placeholder)."""


def edit_dataset_source(*args: Any) -> None:
    """Handle dataset source edit events (placeholder)."""


def select_variable_name(*args: Any) -> None:
    """Handle variable name selection events (placeholder)."""


def select_import_as(*args: Any) -> None:
    """Handle import-as option selection events (placeholder)."""


def import_dataset(*args: Any) -> None:
    """Import the selected dataset into the topography catalog."""
    app.toolbox["bathymetry"].import_dataset()
