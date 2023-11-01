# -*- coding: utf-8 -*-
"""
Created on Mon October 30 12:18:09 2023

@author: Santonia27
"""

from delftdashboard.app import app
from delftdashboard.operations import map
import geopandas as gpd 
from pathlib import Path


def select(*args):
    # De-activate existing layers
    map.update()

def set_variables(*args):
    app.model["fiat"].set_input_variables()


def deselect_aggregation(*args):
    print("Deselect aggregation field")

def add_aggregations(*args):
    print("Add aggregations to model")


def load_aggregation_file(*args):
    fn = app.gui.window.dialog_open_file("Select geometry",
                                          filter="Geometry (*.shp *.gpkg *.geojson)")
    
    name = Path(fn).name
    load_aggregation(name)

def load_aggregation(name):
    current_list_string = app.gui.getvar("fiat", "loaded_aggregation_files_string")
    if name in current_list_string:
        return
    current_list_string.append(name)
    app.gui.setvar("fiat", "loaded_aggregation_files_string", current_list_string)
