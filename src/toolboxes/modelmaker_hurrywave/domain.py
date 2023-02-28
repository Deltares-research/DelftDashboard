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
    ddb.map.layer["modelmaker_hurrywave"].layer["grid_outline"].set_mode("active")

def draw_grid_outline(*args):
    ddb.map.layer["modelmaker_hurrywave"].layer["grid_outline"].draw()

def grid_outline_created(gdf, index, id):
    # Remove the old grid outline
    layer = ddb.map.layer["modelmaker_hurrywave"].layer["grid_outline"]
    if len(ddb.toolbox["modelmaker_hurrywave"].grid_outline) > 0:
        layer.delete_feature(ddb.toolbox["modelmaker_hurrywave"].grid_outline["id"][0])
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
    ddb.gui.setvar(group, "rotation", round(gdf["rotation"][0] * 180 / math.pi, 1))
    ddb.gui.setvar(group, "nmax", np.floor(leny / ddb.gui.getvar(group, "dy")).astype(int))
    ddb.gui.setvar(group, "mmax", np.floor(lenx / ddb.gui.getvar(group, "dx")).astype(int))

def edit(*args):
    pass
    # Should redraw outline here
