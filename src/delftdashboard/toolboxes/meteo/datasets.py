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
    app.toolbox["meteo"].set_layer_mode("active")

def select_dataset(*args):
    pass

def add_dataset(*args):
    pass

def select_source(*args):
    pass

def edit_bbox(*args):
    pass
