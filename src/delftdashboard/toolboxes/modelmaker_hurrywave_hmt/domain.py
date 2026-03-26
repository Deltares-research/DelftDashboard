import numpy as np
import math

from delftdashboard.app import app
from delftdashboard.operations import map

_TB = "modelmaker_hurrywave_hmt"
_MODEL = "hurrywave_hmt"


def select(*args):
    map.update()
    app.map.layer[_MODEL].layer["grid"].show()
    app.map.layer[_TB].layer["grid_outline"].activate()


def draw_grid_outline(*args):
    app.map.layer[_TB].layer["grid_outline"].crs = app.crs
    app.map.layer[_TB].layer["grid_outline"].draw()


def grid_outline_created(gdf, index, id):
    if len(gdf) > 1:
        id0 = gdf["id"][0]
        app.map.layer[_TB].layer["grid_outline"].delete_feature(id0)
        gdf = gdf.drop([0]).reset_index()
    app.toolbox[_TB].grid_outline = gdf
    update_geometry()
    app.gui.window.update()


def grid_outline_modified(gdf, index, id):
    app.toolbox[_TB].grid_outline = gdf
    update_geometry()
    app.gui.window.update()


def generate_grid(*args):
    app.toolbox[_TB].generate_grid()


def update_geometry():
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
    app.gui.setvar(group, "rotation", float(round(gdf["rotation"][0] * 180 / math.pi, 1)))
    app.gui.setvar(group, "nmax", int(np.floor(leny / app.gui.getvar(group, "dy"))))
    app.gui.setvar(group, "mmax", int(np.floor(lenx / app.gui.getvar(group, "dx"))))


def edit_origin(*args):
    redraw_rectangle()


def edit_nmmax(*args):
    redraw_rectangle()


def edit_rotation(*args):
    redraw_rectangle()


def edit_dxdy(*args):
    group = _TB
    lenx = app.toolbox[_TB].lenx
    leny = app.toolbox[_TB].leny
    app.gui.setvar(group, "nmax", int(np.floor(leny / app.gui.getvar(group, "dy"))))
    app.gui.setvar(group, "mmax", int(np.floor(lenx / app.gui.getvar(group, "dx"))))


def redraw_rectangle():
    group = _TB
    app.toolbox[_TB].lenx = app.gui.getvar(group, "dx") * app.gui.getvar(group, "mmax")
    app.toolbox[_TB].leny = app.gui.getvar(group, "dy") * app.gui.getvar(group, "nmax")
    app.map.layer[_TB].layer["grid_outline"].clear()
    app.map.layer[_TB].layer["grid_outline"].add_rectangle(
        app.gui.getvar(group, "x0"),
        app.gui.getvar(group, "y0"),
        app.toolbox[_TB].lenx,
        app.toolbox[_TB].leny,
        app.gui.getvar(group, "rotation"))


def read_setup_yaml(*args):
    fname = app.gui.window.dialog_open_file("Select yml file", filter="*.yml")
    if fname[0]:
        app.toolbox[_TB].read_setup_yaml(fname[0])


def write_setup_yaml(*args):
    app.toolbox[_TB].write_setup_yaml()
    app.toolbox[_TB].write_include_polygon()
    app.toolbox[_TB].write_exclude_polygon()
    app.toolbox[_TB].write_boundary_polygon()


def build_model(*args):
    app.toolbox[_TB].build_model()


def info(*args):
    pass
