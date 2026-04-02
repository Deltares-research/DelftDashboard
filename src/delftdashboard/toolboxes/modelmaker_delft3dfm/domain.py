"""GUI callbacks for the domain tab of the Delft3D-FM model maker toolbox."""

from typing import Any

import numpy as np

from delftdashboard.app import app
from delftdashboard.operations import map

_TB = "modelmaker_delft3dfm"
_MODEL = "delft3dfm"


def select(*args: Any) -> None:
    """Activate the domain tab and show the grid outline layer."""
    map.update()
    app.map.layer[_MODEL].layer["grid"].show()
    app.map.layer[_TB].layer["grid_outline"].activate()


def draw_grid_outline(*args: Any) -> None:
    """Start interactive drawing of the grid outline rectangle."""
    app.map.layer[_TB].layer["grid_outline"].crs = app.crs
    app.map.layer[_TB].layer["grid_outline"].draw()


def grid_outline_created(gdf: Any, index: int, id: Any) -> None:
    """Store a newly created grid outline and update geometry.

    Parameters
    ----------
    gdf : GeoDataFrame
        The GeoDataFrame containing the drawn rectangle(s).
    index : int
        Index of the created feature.
    id : Any
        Feature identifier.
    """
    if len(gdf) > 1:
        # Remove the old grid outline
        id0 = gdf["id"][0]
        app.map.layer[_TB].layer["grid_outline"].delete_feature(id0)
        gdf = gdf.drop([0]).reset_index()
    app.toolbox[_TB].grid_outline = gdf
    update_geometry()
    app.gui.window.update()


def grid_outline_modified(gdf: Any, index: int, id: Any) -> None:
    """Update the stored grid outline after the user modifies it.

    Parameters
    ----------
    gdf : GeoDataFrame
        The modified GeoDataFrame.
    index : int
        Index of the modified feature.
    id : Any
        Feature identifier.
    """
    app.toolbox[_TB].grid_outline = gdf
    update_geometry()
    app.gui.window.update()


def generate_grid(*args: Any) -> None:
    """Trigger grid generation via the toolbox."""
    app.toolbox[_TB].generate_grid()


def update_geometry() -> None:
    """Recalculate grid dimensions from the drawn outline rectangle."""
    gdf = app.toolbox[_TB].grid_outline
    group = _TB
    x0 = float(round(gdf["x0"][0], 3))
    y0 = float(round(gdf["y0"][0], 3))
    app.gui.setvar(group, "x0", x0)
    app.gui.setvar(group, "y0", y0)
    lenx = float(gdf["dx"][0])
    leny = float(gdf["dy"][0])
    app.toolbox[_TB].lenx = lenx
    app.toolbox[_TB].leny = leny
    app.gui.setvar(group, "nmax", int(np.floor(leny / app.gui.getvar(group, "dy"))))
    app.gui.setvar(group, "mmax", int(np.floor(lenx / app.gui.getvar(group, "dx"))))


def edit_origin(*args: Any) -> None:
    """Redraw the grid rectangle after the origin is edited."""
    redraw_rectangle()


def edit_nmmax(*args: Any) -> None:
    """Redraw the grid rectangle after the grid dimensions are edited."""
    redraw_rectangle()


def edit_rotation(*args: Any) -> None:
    """Redraw the grid rectangle after the rotation is edited."""
    redraw_rectangle()


def edit_dxdy(*args: Any) -> None:
    """Recalculate grid cell counts after dx/dy values are edited."""
    group = _TB
    lenx = app.toolbox[_TB].lenx
    leny = app.toolbox[_TB].leny
    app.gui.setvar(
        group, "nmax", np.floor(leny / app.gui.getvar(group, "dy")).astype(int)
    )
    app.gui.setvar(
        group, "mmax", np.floor(lenx / app.gui.getvar(group, "dx")).astype(int)
    )


def redraw_rectangle() -> None:
    """Clear and redraw the grid outline rectangle from current GUI values."""
    group = _TB
    app.toolbox[_TB].lenx = app.gui.getvar(group, "dx") * app.gui.getvar(group, "mmax")
    app.toolbox[_TB].leny = app.gui.getvar(group, "dy") * app.gui.getvar(group, "nmax")
    app.map.layer[_TB].layer["grid_outline"].clear()
    app.map.layer[_TB].layer["grid_outline"].add_rectangle(
        app.gui.getvar(group, "x0"),
        app.gui.getvar(group, "y0"),
        app.toolbox[_TB].lenx,
        app.toolbox[_TB].leny,
        0,  # rotation in degrees
    )


def read_setup_yaml(*args: Any) -> None:
    """Open a file dialog and load a YAML setup file."""
    full_name, path, name, ext, fltr = app.gui.window.dialog_open_file(
        "Select yml file", filter="*.yml"
    )
    if not full_name:
        return
    # This will automatically also read and plot the polygons
    app.toolbox[_TB].read_setup_yaml(full_name)


def write_setup_yaml(*args: Any) -> None:
    """Write the current setup to a YAML file."""
    app.toolbox[_TB].write_setup_yaml()


def build_model(*args: Any) -> None:
    """Build the full Delft3D-FM model from current settings."""
    app.toolbox[_TB].build_model()


# def use_snapwave(*args):
#     # group = _TB
#     app.gui.setvar(_MODEL, "snapwave", app.gui.getvar(_TB, "use_snapwave"))
#     app.model[_MODEL].domain.input.variables.snapwave = app.gui.getvar(_TB, "use_snapwave")

# def use_subgrid(*args):
#     pass
