# -*- coding: utf-8 -*-
"""
GUI methods for modelmaker_hurrywave -> domain

Created on Mon May 10 12:18:09 2021

@author: Maarten van Ormondt
"""
import numpy as np

from ddb import ddb
import math


def select(*args):
    # De-activate existing layers
    ddb.update_map()
    # Show the grid outline layer
    ddb.map.layer["hurrywave"].layer["grid"].set_mode("active")
    ddb.map.layer["modelmaker_hurrywave"].layer["grid_outline"].set_mode("active")

def draw_grid_outline(*args):
    # Clear grid outline layer
    ddb.map.layer["modelmaker_hurrywave"].layer["grid_outline"].crs = ddb.crs
    ddb.map.layer["modelmaker_hurrywave"].layer["grid_outline"].draw()

def grid_outline_created(gdf, index, id):
    if len(gdf) > 1:
        # Remove the old grid outline
        id0 = gdf["id"][0]
        ddb.map.layer["modelmaker_hurrywave"].layer["grid_outline"].delete_feature(id0)
        gdf = gdf.drop([0]).reset_index()
    ddb.toolbox["modelmaker_hurrywave"].grid_outline = gdf
    update_geometry()
    ddb.gui.window.update()

def grid_outline_modified(gdf, index, id):
    ddb.toolbox["modelmaker_hurrywave"].grid_outline = gdf
    update_geometry()
    ddb.gui.window.update()

def generate_grid(*args):
    ddb.toolbox["modelmaker_hurrywave"].generate_grid()

def update_geometry():
    gdf = ddb.toolbox["modelmaker_hurrywave"].grid_outline
    group = "modelmaker_hurrywave"
    ddb.gui.setvar(group, "x0", round(gdf["x0"][0], 3))
    ddb.gui.setvar(group, "y0", round(gdf["y0"][0], 3))
    lenx = gdf["dx"][0]
    leny = gdf["dy"][0]
    ddb.toolbox["modelmaker_hurrywave"].lenx = lenx
    ddb.toolbox["modelmaker_hurrywave"].leny = leny
    ddb.gui.setvar(group, "rotation", round(gdf["rotation"][0] * 180 / math.pi, 1))
    ddb.gui.setvar(group, "nmax", np.floor(leny / ddb.gui.getvar(group, "dy")).astype(int))
    ddb.gui.setvar(group, "mmax", np.floor(lenx / ddb.gui.getvar(group, "dx")).astype(int))

def edit_origin(*args):
    redraw_rectangle()

def edit_nmmax(*args):
    redraw_rectangle()

def edit_rotation(*args):
    redraw_rectangle()

def edit_dxdy(*args):
    group = "modelmaker_hurrywave"
    lenx = ddb.toolbox["modelmaker_hurrywave"].lenx
    leny = ddb.toolbox["modelmaker_hurrywave"].leny
    ddb.gui.setvar(group, "nmax", np.floor(leny / ddb.gui.getvar(group, "dy")).astype(int))
    ddb.gui.setvar(group, "mmax", np.floor(lenx / ddb.gui.getvar(group, "dx")).astype(int))


def redraw_rectangle():
    group = "modelmaker_hurrywave"
    ddb.toolbox["modelmaker_hurrywave"].lenx = ddb.gui.getvar(group, "dx") * ddb.gui.getvar(group, "mmax")
    ddb.toolbox["modelmaker_hurrywave"].leny = ddb.gui.getvar(group, "dy") * ddb.gui.getvar(group, "nmax")
    ddb.map.layer["modelmaker_hurrywave"].layer["grid_outline"].clear()
    ddb.map.layer["modelmaker_hurrywave"].layer["grid_outline"].add_rectangle("rect",
                                                                              ddb.gui.getvar(group, "x0"),
                                                                              ddb.gui.getvar(group, "y0"),
                                                                              ddb.toolbox["modelmaker_hurrywave"].lenx,
                                                                              ddb.toolbox["modelmaker_hurrywave"].leny,
                                                                              0.0)
