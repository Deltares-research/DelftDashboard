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
import copy

def select(*args):
    # De-activate existing layers
    map.update()

def set_variables(*args):
    app.model["fiat"].set_input_variables()


    

def deselect_aggregation(*args):
    current_list_string = app.gui.getvar("fiat", "selected_aggregation_files_string")
    deselected_aggregation = app.gui.getvar("fiat", "selected_aggregation_files")
    if deselected_aggregation > len(current_list_string) or deselected_aggregation == len(current_list_string):
        deselected_aggregation = 0
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
    if fn not in fn_value:
        fn_value.append(Path(fn))
    app.gui.setvar("fiat", "loaded_aggregation_files_value", fn_value)
    name = Path(fn).name
    load_aggregation(name)

def load_aggregation(name):
    current_list_string = app.gui.getvar("fiat", "loaded_aggregation_files_string")
    if name not in current_list_string:
        current_list_string.append(name)
        
    app.gui.setvar("fiat", "loaded_aggregation_files_string", current_list_string)

def delete_loaded_file(*args):
    print("remove")

def open_gdf(*args):
    index = app.gui.getvar("fiat", "loaded_aggregation_files")
    path = app.gui.getvar("fiat", "loaded_aggregation_files_value")[index]
    gdf = gpd.read_file(path)
    list_columns = list(gdf.columns)
    app.gui.setvar("fiat", "aggregation_file_field_name_value", list_columns)
    app.gui.setvar("fiat", "aggregation_file_field_name_string", list_columns)
    aggregation_attribute = [app.gui.getvar("fiat", "aggregation_file_field_name")]
    if len(aggregation_attribute) > 0:
        app.gui.setvar("fiat", "aggregation_file_field_name",0)       
    
def write_input_to_table(*args):
    aggregation_attribute = [app.gui.getvar("fiat", "aggregation_file_field_name")]
    aggregation_label = [app.gui.getvar("fiat", "aggregation_label_string")]
    file_index = app.gui.getvar("fiat", "loaded_aggregation_files")
    file = app.gui.getvar("fiat", "loaded_aggregation_files_string")[file_index]
    df_aggregation = pd.DataFrame({"File": file, "Aggregation Attribute": aggregation_attribute, "Aggregation Label": aggregation_label })
    df_all_aggregation = copy.deepcopy(app.gui.getvar("fiat", "aggregation_table"))

    if len(df_all_aggregation) ==0:
       df_all_aggregation = pd.DataFrame(columns=["File", "Aggregation Attribute", "Aggregation Label"])
    
    added_aggregation = df_aggregation["File"].tolist()
    added_aggregation_list = df_all_aggregation["File"].tolist()
    
    if added_aggregation[0] not in added_aggregation_list:
        df_all_aggregation = pd.concat([df_all_aggregation,df_aggregation])
    app.gui.setvar("fiat", "aggregation_table", df_all_aggregation)

def add_aggregations(*args):
    #FN get the file path of the file from value
    aggregation_files_values = app.gui.getvar("fiat", "loaded_aggregation_files_value")
    aggregation_table = app.gui.getvar("fiat",  "aggregation_table")
    file_name = aggregation_table["File"].tolist()
    aggregation_fn = []
    for i in aggregation_files_values:
        if i.name in file_name:
            aggregation_fn.append(i)
    app.gui.setvar("fiat", "loaded_aggregation_files_value", aggregation_fn)
    a = app.gui.getvar("fiat", "loaded_aggregation_files_value")
    print(a)
    #fn = 
    #attribute =
    #label = 
    #app.model["fiat"].domain.exposure_vm.set_aggregation_areas_config(fn, attribute, label)


    
