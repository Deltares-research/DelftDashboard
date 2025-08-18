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
    app.map.layer["flood_map"].layer["polygon"].show()
    app.map.layer["flood_map"].layer["polygon"].activate()

def generate_topobathy_geotiff(*args):
    # Generate topobathy geotiff
    app.toolbox["flood_map"].generate_topobathy_geotiff()

def draw_polygon(*args):
    # Delete existing polygon
    delete_polygon()
    app.map.layer["flood_map"].layer["polygon"].crs = app.crs
    app.map.layer["flood_map"].layer["polygon"].draw()

def delete_polygon(*args):
    # Delete polygon
    app.toolbox["flood_map"].polygon = gpd.GeoDataFrame()
    app.map.layer["flood_map"].layer["polygon"].clear()

def polygon_created(gdf, index, id):
    app.toolbox["flood_map"].polygon = gdf
