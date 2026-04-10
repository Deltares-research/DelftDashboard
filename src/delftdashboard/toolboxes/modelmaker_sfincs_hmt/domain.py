"""GUI callbacks for the domain tab of the SFINCS HMT model-maker toolbox.

Handles grid outline drawing, geometry updates, and model setup YAML I/O.
"""

import math
from typing import Any

import geopandas as gpd
import numpy as np

from delftdashboard.app import app
from delftdashboard.operations import map

_TB = "modelmaker_sfincs_hmt"
_MODEL = "sfincs_hmt"


def select(*args: Any) -> None:
    """Activate the domain tab and display grid-related map layers.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    map.update()
    app.map.layer[_MODEL].layer["grid"].activate()
    app.map.layer[_TB].layer["grid_outline"].activate()
    app.toolbox[_TB].show_mask_polygons()


def draw_grid_outline(*args: Any) -> None:
    """Start interactive drawing of the grid outline rectangle.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    app.map.layer[_TB].layer["grid_outline"].crs = app.crs
    app.map.layer[_TB].layer["grid_outline"].draw()


def grid_outline_created(gdf: gpd.GeoDataFrame, index: int, id: Any) -> None:
    """Handle creation of a new grid outline rectangle on the map.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing the grid outline feature(s).
    index : int
        Index of the created feature.
    id : Any
        Identifier of the created feature.
    """
    if len(gdf) > 1:
        # Remove the old grid outline
        id0 = gdf["id"][0]
        app.map.layer[_TB].layer["grid_outline"].delete_feature(id0)
        gdf = gdf.drop([0]).reset_index()
    app.toolbox[_TB].grid_outline = gdf
    update_geometry()
    app.gui.window.update()


def grid_outline_modified(gdf: gpd.GeoDataFrame, index: int, id: Any) -> None:
    """Handle modification of the grid outline rectangle on the map.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing the modified grid outline feature(s).
    index : int
        Index of the modified feature.
    id : Any
        Identifier of the modified feature.
    """
    app.toolbox[_TB].grid_outline = gdf
    update_geometry()
    app.gui.window.update()


def generate_grid(*args: Any) -> None:
    """Generate the computational grid from the current outline and parameters.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    nmax = app.gui.getvar(_TB, "nmax")
    mmax = app.gui.getvar(_TB, "mmax")
    dx = app.gui.getvar(_TB, "dx")
    dy = app.gui.getvar(_TB, "dy")
    if nmax <= 0 or mmax <= 0 or dx <= 0.0 or dy <= 0.0:
        app.gui.window.dialog_warning(
            "Please first create bounding box for model domain!", "Warning"
        )
        return
    app.toolbox[_TB].generate_grid()


def update_geometry() -> None:
    """Recompute grid dimensions from the current outline rectangle geometry."""
    gdf = app.toolbox[_TB].grid_outline
    x0 = float(round(gdf["x0"][0], 3))
    y0 = float(round(gdf["y0"][0], 3))
    app.gui.setvar(_TB, "x0", x0)
    app.gui.setvar(_TB, "y0", y0)
    lenx = float(gdf["dx"][0])
    leny = float(gdf["dy"][0])
    app.toolbox[_TB].lenx = lenx
    app.toolbox[_TB].leny = leny
    app.gui.setvar(_TB, "rotation", float(round(gdf["rotation"][0] * 180 / math.pi, 1)))
    app.gui.setvar(_TB, "nmax", int(np.floor(leny / app.gui.getvar(_TB, "dy"))))
    app.gui.setvar(_TB, "mmax", int(np.floor(lenx / app.gui.getvar(_TB, "dx"))))


def edit_origin(*args: Any) -> None:
    """Redraw the grid outline after the origin is edited.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    redraw_rectangle()


def edit_nmmax(*args: Any) -> None:
    """Redraw the grid outline after nmax/mmax is edited.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    redraw_rectangle()


def edit_rotation(*args: Any) -> None:
    """Redraw the grid outline after the rotation angle is edited.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    redraw_rectangle()


def edit_dxdy(*args: Any) -> None:
    """Recompute nmax/mmax after the grid spacing is edited.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    lenx = app.toolbox[_TB].lenx
    leny = app.toolbox[_TB].leny
    app.gui.setvar(_TB, "nmax", np.floor(leny / app.gui.getvar(_TB, "dy")).astype(int))
    app.gui.setvar(_TB, "mmax", np.floor(lenx / app.gui.getvar(_TB, "dx")).astype(int))


def redraw_rectangle() -> None:
    """Clear and redraw the grid outline rectangle from current GUI parameters."""
    app.toolbox[_TB].lenx = app.gui.getvar(_TB, "dx") * app.gui.getvar(_TB, "mmax")
    app.toolbox[_TB].leny = app.gui.getvar(_TB, "dy") * app.gui.getvar(_TB, "nmax")
    app.map.layer[_TB].layer["grid_outline"].clear()
    app.map.layer[_TB].layer["grid_outline"].add_rectangle(
        app.gui.getvar(_TB, "x0"),
        app.gui.getvar(_TB, "y0"),
        app.toolbox[_TB].lenx,
        app.toolbox[_TB].leny,
        app.gui.getvar(_TB, "rotation"),
    )


def read_setup_yaml(*args: Any) -> None:
    """Open a file dialog and read a model setup YAML file.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    full_name, path, name, ext, fltr = app.gui.window.dialog_open_file(
        "Select yml file", filter="*.yml"
    )
    if not full_name:
        return
    # This will automatically also read and plot the polygons
    app.toolbox[_TB].read_setup_yaml(full_name)


def write_setup_yaml(*args: Any) -> None:
    """Write the current model setup to a YAML file.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    app.toolbox[_TB].write_setup_yaml()


def build_model(*args: Any) -> None:
    """Build the complete SFINCS model from the current setup.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    app.toolbox[_TB].build_model()


def use_snapwave(*args: Any) -> None:
    """Toggle SnapWave coupling in the domain configuration.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    use = app.gui.getvar(_TB, "use_snapwave")
    # Update domain
    app.model[_MODEL].domain.config.set("snapwave", use)
    # Update GUI variable
    app.gui.setvar(_MODEL, "snapwave", use)


def use_subgrid(*args: Any) -> None:
    """Toggle sub-grid tables in the domain configuration (placeholder).

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    pass


def show_mask_polygons(*args: Any) -> None:
    """Show or hide mask polygons on the map according to the GUI toggle.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    app.toolbox[_TB].show_mask_polygons()
