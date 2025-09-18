# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
import geopandas as gpd
from delftdashboard.app import app
from delftdashboard.operations import map

# Callbacks
def select(*args):
    # De-activate() existing layers
    map.update()
    # Tab selected
    app.toolbox["flood_map"].set_layer_mode("active")
    update()

def select_instantaneous_or_maximum(*args):
    # Update the map with the selected option
    app.gui.setvar("flood_map", "time_index", 0)
    update()

def select_time(*args):
    # Update the map with the selected time
    update()

def export(*args):
    # Export flood map
    app.toolbox["flood_map"].export_flood_map()

def select_opacity(*args):
    # Update the opacity of the flood map layer
    opacity = app.gui.getvar("flood_map", "flood_map_opacity")
    app.map.layer["flood_map"].layer["flood_map"].set_opacity(opacity)

def select_continuous_or_discrete_colors(*args):
    # Update the flood map with continuous or discrete colors
    mode = app.gui.getvar("flood_map", "continuous_or_discrete_colors")
    if mode == "continuous":
        app.toolbox["flood_map"].flood_map.discrete_colors = False
    else:
        app.toolbox["flood_map"].flood_map.discrete_colors = True
    update()

def edit_cmin_cmax(*args):
    # Update the flood map with new cmin and cmax values
    try:
        cmin = float(app.gui.getvar("flood_map", "cmin"))
        cmax = float(app.gui.getvar("flood_map", "cmax"))
        cmap = app.gui.getvar("flood_map", "cmap")

        # if cmin >= cmax:
        #     raise ValueError("cmin must be less than cmax")
        app.toolbox["flood_map"].flood_map.cmin = cmin
        app.toolbox["flood_map"].flood_map.cmax = cmax
        app.toolbox["flood_map"].flood_map.cmap = cmap
        update()

    except ValueError:
        print("Invalid cmin or cmax value")    

def update():
    # Update the flood map layer
    if app.gui.getvar("flood_map", "instantaneous_or_maximum") == "instantaneous":
        app.gui.setvar("flood_map", "available_time_strings", app.toolbox["flood_map"].instantaneous_time_strings)
    else:
        app.gui.setvar("flood_map", "available_time_strings", app.toolbox["flood_map"].maximum_time_strings)
    app.toolbox["flood_map"].update_flood_map()
