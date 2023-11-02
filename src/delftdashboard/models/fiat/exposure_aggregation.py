# -*- coding: utf-8 -*-
"""
Created on Mon October 30 12:18:09 2023

@author: Santonia27
"""

from delftdashboard.app import app
from delftdashboard.operations import map
import geopandas as gpd 
from pathlib import Path
import pandas as pd


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
    current_list_string = app.gui.getvar("fiat", "selected_aggregation_files_string")
    deselected_aggregation = app.gui.getvar("fiat", "selected_aggregation_files")
    if deselected_aggregation > len(current_list_string) or deselected_aggregation == len(current_list_string):
        deselected_aggregation = 0
    else:
        pass
    name = current_list_string[deselected_aggregation]
    deselection(name)

def deselection(name): 
    current_list_string = app.gui.getvar("fiat", "selected_aggregation_files_string")
    current_list_string.remove(name)
    app.gui.setvar("fiat", "selected_aggregation_files_string", current_list_string)

def load_aggregation_file(*args):
    fn = app.gui.window.dialog_open_file("Select geometry",
                                          filter="Geometry (*.shp *.gpkg *.geojson)")
    fn = fn[0]
    fn_value = app.gui.getvar("fiat", "loaded_aggregation_files_value")
    if fn in fn_value:
        pass
    else:
        fn_value.append(Path(fn))
    app.gui.setvar("fiat", "loaded_aggregation_files_value", fn_value)
    name = Path(fn).name
    load_aggregation(name)

def load_aggregation(name):
    current_list_string = app.gui.getvar("fiat", "loaded_aggregation_files_string")
    if name in current_list_string:
        pass
    else:
        current_list_string.append(name)
    app.gui.setvar("fiat", "loaded_aggregation_files_string", current_list_string)

def open_gdf(*args):
    index = app.gui.getvar("fiat", "loaded_aggregation_files")
    path = app.gui.getvar("fiat", "loaded_aggregation_files_value")[index]
    gdf = gpd.read_file(path)
    list_columns = list(gdf.columns)
    app.gui.setvar("fiat", "aggregation_file_field_name_value", list_columns)
    app.gui.setvar("fiat", "aggregation_file_field_name_string", list_columns)
   
    
def write_input_to_table(*args):
    aggregation_attribute = [app.gui.getvar("fiat", "aggregation_file_field_name")]
    aggregation_label = [app.gui.getvar("fiat", "aggregation_label_string")]
    file = app.gui.getvar("fiat", "loaded_aggregation_files_string")
    fn = app.gui.getvar("fiat", "loaded_aggregation_files_value")
    df_aggregation = pd.DataFrame({"File": file, "Aggregation Label": aggregation_label, "Aggregation Attribute": aggregation_attribute })
    app.gui.setvar("fiat", "aggregation_table", df_aggregation)

def add_aggregations(*args):
    aggregation_files_values = app.gui.getvar("fiat", "loaded_aggregation_files_value")
    aggregation_files_string = app.gui.getvar("fiat", "selected_aggregation_files_string")
    aggregation_fn = []
    for i in aggregation_files_values:
        if i.name in aggregation_files_string:
            aggregation_fn.append(i)
    app.gui.setvar("fiat", "loaded_aggregation_files_value", aggregation_fn)
    a = app.gui.getvar("fiat", "loaded_aggregation_files_value")
    print(a)
