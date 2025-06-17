# -*- coding: utf-8 -*-
"""
GUI methods for modelmaker_sfincs -> domain

Created on Mon May 10 12:18:09 2021

@author: Maarten van Ormondt
"""
import numpy as np
import math

from delftdashboard.app import app
from delftdashboard.operations import map

def select(*args):
    # De-activate() existing layers
    map.update()
    # Show the grid outline layer
    app.map.layer["sfincs_cht"].layer["grid"].activate()
    app.map.layer["modelmaker_sfincs_cht"].layer["grid_outline"].activate()
    # Show and deactivate the mask polygons
    app.toolbox["modelmaker_sfincs_cht"].show_mask_polygons()

def draw_grid_outline(*args):
    # Clear grid outline layer
    app.map.layer["modelmaker_sfincs_cht"].layer["grid_outline"].crs = app.crs
    app.map.layer["modelmaker_sfincs_cht"].layer["grid_outline"].draw()


def grid_outline_created(gdf, index, id):
    if len(gdf) > 1:
        # Remove the old grid outline
        id0 = gdf["id"][0]
        app.map.layer["modelmaker_sfincs_cht"].layer["grid_outline"].delete_feature(id0)
        gdf = gdf.drop([0]).reset_index()
    app.toolbox["modelmaker_sfincs_cht"].grid_outline = gdf
    update_geometry()
    app.gui.window.update()


def grid_outline_modified(gdf, index, id):
    app.toolbox["modelmaker_sfincs_cht"].grid_outline = gdf
    update_geometry()
    app.gui.window.update()


def generate_grid(*args):
    # First check that nmax, mmax, dx, and dy are > 0
    group = "modelmaker_sfincs_cht"
    nmax = app.gui.getvar(group, "nmax")
    mmax = app.gui.getvar(group, "mmax")
    dx = app.gui.getvar(group, "dx")
    dy = app.gui.getvar(group, "dy")
    if nmax <= 0 or mmax <= 0 or dx <= 0.0 or dy <= 0.0:
        app.gui.window.dialog_warning("Please first create bounding box for model domain!",
            "Warning"
        )
        return
    app.toolbox["modelmaker_sfincs_cht"].generate_grid()


def update_geometry():
    gdf = app.toolbox["modelmaker_sfincs_cht"].grid_outline
    group = "modelmaker_sfincs_cht"
    x0 = float(round(gdf["x0"][0], 3))
    y0 = float(round(gdf["y0"][0], 3))
    app.gui.setvar(group, "x0", x0)
    app.gui.setvar(group, "y0", y0)
    lenx = float(gdf["dx"][0])
    leny = float(gdf["dy"][0])
    app.toolbox["modelmaker_sfincs_cht"].lenx = lenx
    app.toolbox["modelmaker_sfincs_cht"].leny = leny
    app.gui.setvar(group, "rotation", float(round(gdf["rotation"][0] * 180 / math.pi, 1)))
    app.gui.setvar(
        group, "nmax", int(np.floor(leny / app.gui.getvar(group, "dy")))
    )
    app.gui.setvar(
        group, "mmax", int(np.floor(lenx / app.gui.getvar(group, "dx")))
    )


def edit_origin(*args):
    redraw_rectangle()


def edit_nmmax(*args):
    redraw_rectangle()


def edit_rotation(*args):
    redraw_rectangle()


def edit_dxdy(*args):
    group = "modelmaker_sfincs_cht"
    lenx = app.toolbox["modelmaker_sfincs_cht"].lenx
    leny = app.toolbox["modelmaker_sfincs_cht"].leny
    app.gui.setvar(
        group, "nmax", np.floor(leny / app.gui.getvar(group, "dy")).astype(int)
    )
    app.gui.setvar(
        group, "mmax", np.floor(lenx / app.gui.getvar(group, "dx")).astype(int)
    )


def redraw_rectangle():
    group = "modelmaker_sfincs_cht"
    app.toolbox["modelmaker_sfincs_cht"].lenx = app.gui.getvar(
        group, "dx"
    ) * app.gui.getvar(group, "mmax")
    app.toolbox["modelmaker_sfincs_cht"].leny = app.gui.getvar(
        group, "dy"
    ) * app.gui.getvar(group, "nmax")
    app.map.layer["modelmaker_sfincs_cht"].layer["grid_outline"].clear()
    app.map.layer["modelmaker_sfincs_cht"].layer["grid_outline"].add_rectangle(
        app.gui.getvar(group, "x0"),
        app.gui.getvar(group, "y0"),
        app.toolbox["modelmaker_sfincs_cht"].lenx,
        app.toolbox["modelmaker_sfincs_cht"].leny,
        app.gui.getvar(group, "rotation"),
    )

def read_setup_yaml(*args):
    full_name, path, name, ext, fltr = app.gui.window.dialog_open_file("Select yml file", filter="*.yml")
    if not full_name:
        return
    # This will automatically also read and plot the polygons    
    app.toolbox["modelmaker_sfincs_cht"].read_setup_yaml(full_name)

def write_setup_yaml(*args):
    # This will automatically also write the polygons    
    app.toolbox["modelmaker_sfincs_cht"].write_setup_yaml()

def build_model(*args):
    app.toolbox["modelmaker_sfincs_cht"].build_model()

def use_snapwave(*args):
    use = app.gui.getvar("modelmaker_sfincs_cht", "use_snapwave")
    # Update domain
    app.model["sfincs_cht"].domain.input.variables.snapwave = use
    # Update GUI variable
    app.gui.setvar("sfincs_cht", "snapwave", use)

def use_subgrid(*args):
    pass

def show_mask_polygons(*args):
    app.toolbox["modelmaker_sfincs_cht"].show_mask_polygons()
