# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
from delftdashboard.app import app
from delftdashboard.operations import map

# Callbacks
def select(*args):
    # De-activate() existing layers
    map.update()
    # Tab selected
    app.toolbox["flood_map"].set_layer_mode("active")

def load_topobathy_geotiff(*args):
    # Load topobathy geotiff
    app.toolbox["flood_map"].load_topobathy_geotiff()

def generate_topobathy_geotiff(*args):
    # Generate topobathy geotiff
    app.toolbox["flood_map"].generate_topobathy_geotiff()

def load_index_geotiff(*args):
    # Load index geotiff
    app.toolbox["flood_map"].load_index_geotiff()

def generate_index_geotiff(*args):
    # Generate index geotiff
    app.toolbox["flood_map"].generate_index_geotiff()
