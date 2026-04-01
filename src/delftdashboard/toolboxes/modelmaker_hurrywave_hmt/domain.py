"""GUI callbacks for the HurryWave Model Maker Domain tab.

Handles drawing the grid outline on the map, editing grid parameters,
and triggering grid generation.
"""

import math
from typing import Any

import geopandas as gpd
import numpy as np

from delftdashboard.app import app
from delftdashboard.operations import map

_TB = "modelmaker_hurrywave_hmt"
_MODEL = "hurrywave_hmt"


def select(*args: Any) -> None:
    """Activate the Domain tab and show the grid outline."""
    map.update()
    app.map.layer[_MODEL].layer["grid"].show()
    app.map.layer[_TB].layer["grid_outline"].activate()


def draw_grid_outline(*args: Any) -> None:
    """Start interactive grid outline drawing on the map."""
    app.map.layer[_TB].layer["grid_outline"].crs = app.crs
    app.map.layer[_TB].layer["grid_outline"].draw()


def grid_outline_created(gdf: gpd.GeoDataFrame, index: int, id: Any) -> None:
    """Handle creation of a grid outline rectangle on the map.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame with grid outline features.
    index : int
        Index of the created feature.
    id : Any
        Feature identifier.
    """
    if len(gdf) > 1:
        id0 = gdf["id"][0]
        app.map.layer[_TB].layer["grid_outline"].delete_feature(id0)
        gdf = gdf.drop([0]).reset_index()
    app.toolbox[_TB].grid_outline = gdf
    update_geometry()
    app.gui.window.update()


def grid_outline_modified(gdf: gpd.GeoDataFrame, index: int, id: Any) -> None:
    """Handle modification of the grid outline rectangle.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        Updated GeoDataFrame with grid outline features.
    index : int
        Index of the modified feature.
    id : Any
        Feature identifier.
    """
    app.toolbox[_TB].grid_outline = gdf
    update_geometry()
    app.gui.window.update()


def generate_grid(*args: Any) -> None:
    """Trigger grid generation from the current domain settings."""
    app.toolbox[_TB].generate_grid()


def update_geometry() -> None:
    """Update GUI variables from the current grid outline geometry."""
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
    """Redraw the grid outline after editing the origin coordinates."""
    redraw_rectangle()


def edit_nmmax(*args: Any) -> None:
    """Redraw the grid outline after editing nmax or mmax."""
    redraw_rectangle()


def edit_rotation(*args: Any) -> None:
    """Redraw the grid outline after editing the rotation angle."""
    redraw_rectangle()


def edit_dxdy(*args: Any) -> None:
    """Recompute nmax/mmax after editing dx or dy."""
    lenx = app.toolbox[_TB].lenx
    leny = app.toolbox[_TB].leny
    app.gui.setvar(_TB, "nmax", int(np.floor(leny / app.gui.getvar(_TB, "dy"))))
    app.gui.setvar(_TB, "mmax", int(np.floor(lenx / app.gui.getvar(_TB, "dx"))))


def redraw_rectangle() -> None:
    """Recompute grid dimensions and redraw the outline on the map."""
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
    """Read a model set-up YAML file."""
    fname = app.gui.window.dialog_open_file("Select yml file", filter="*.yml")
    if fname[0]:
        app.toolbox[_TB].read_setup_yaml(fname[0])


def write_setup_yaml(*args: Any) -> None:
    """Write the current set-up and all polygons to files."""
    app.toolbox[_TB].write_setup_yaml()
    app.toolbox[_TB].write_include_polygon()
    app.toolbox[_TB].write_exclude_polygon()
    app.toolbox[_TB].write_boundary_polygon()


def build_model(*args: Any) -> None:
    """Build the complete model (grid, bathymetry, mask, wave blocking)."""
    app.toolbox[_TB].build_model()


def info(*args: Any) -> None:
    """Show dataset information (not yet implemented)."""
