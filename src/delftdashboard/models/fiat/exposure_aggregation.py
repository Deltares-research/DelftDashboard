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




def select_aggregation(*args):
    selected_aggregation = app.gui.getvar("fiat", "loaded_aggregation_files")
    current_list_string = app.gui.getvar("fiat", "loaded_aggregation_files_string")
    name = current_list_string[selected_aggregation]
    selection(name)


def selection(name):
    current_list_string = app.gui.getvar("fiat", "selected_aggregation_files_string")
    if name in current_list_string:
        pass
    else:
        current_list_string.append(name)
    app.gui.setvar("fiat", "selected_aggregation_files_string", current_list_string)
    

def deselect_aggregation(*args):
    deselected_aggregation = app.gui.getvar("fiat", "selected_aggregation_files")
    current_list_string = app.gui.getvar("fiat", "selected_aggregation_files_string")
    name = current_list_string[deselected_aggregation]
    deselection(name)

def deselection(name): 
    current_list_string = app.gui.getvar("fiat", "selected_aggregation_files_string")
    current_list_string.remove(name)
    app.gui.setvar("fiat", "selected_aggregation_files_string", current_list_string)
    
def add_aggregations(*args):
    print("Add aggregations to model")


def load_aggregation_file(*args):
    fn = app.gui.window.dialog_open_file("Select geometry",
                                          filter="Geometry (*.shp *.gpkg *.geojson)")
    fn = fn[0]
    name = Path(fn).name
    load_aggregation(name)

def load_aggregation(name):
    current_list_string = app.gui.getvar("fiat", "loaded_aggregation_files_string")
    if name in current_list_string:
        pass
    else:
        current_list_string.append(name)
    app.gui.setvar("fiat", "loaded_aggregation_files_string", current_list_string)
    