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

def update():
    # Update the flood map layer
    if app.gui.getvar("flood_map", "instantaneous_or_maximum") == "instantaneous":
        app.gui.setvar("flood_map", "available_time_strings", app.toolbox["flood_map"].instantaneous_time_strings)
    else:
        app.gui.setvar("flood_map", "available_time_strings", app.toolbox["flood_map"].maximum_time_strings)
    app.toolbox["flood_map"].update_flood_map()
