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


def remove_datasource(*args):
    current_list_string = app.gui.getvar("fiat", "loaded_aggregation_files_string")
    deselected_aggregation = app.gui.getvar("fiat", "loaded_aggregation_files")
    if deselected_aggregation > len(
        current_list_string
    ) or deselected_aggregation == len(current_list_string):
        deselected_aggregation = 0
    name = current_list_string[deselected_aggregation]
    deselect_aggregation(name)

def deselect_aggregation(name):
    current_list_string = app.gui.getvar("fiat", "loaded_aggregation_files_string")
    current_list_value = app.gui.getvar("fiat", "loaded_aggregation_files_value")
    aggregation_table = app.gui.getvar("fiat", "aggregation_table")
    if name in aggregation_table["File"].values:
        app.gui.window.dialog_info(
            text="File source can't be removed when selected in the 'Selected Attributes' table.",
            title="Source can't be removed.",
        )
    else:
        current_list_string.remove(name)
        current_list_value = [i for i in current_list_value if name not in str(i)]
        app.gui.setvar("fiat", "loaded_aggregation_files_string", current_list_string)
        app.gui.setvar("fiat", "loaded_aggregation_files_value", current_list_value)

def load_aggregation_file(*args):
    fn = app.gui.window.dialog_open_file(
        "Select geometry", filter="Geometry (*.shp *.gpkg *.geojson)"
    )
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


def open_gdf(*args):
    index = app.gui.getvar("fiat", "loaded_aggregation_files")
    file_list = app.gui.getvar("fiat", "loaded_aggregation_files_value")
    if len(file_list) == 0:
        app.gui.window.dialog_info(
            text="Please load a datasource.",
            title="No datasource",
        )
    else:
        path = app.gui.getvar("fiat", "loaded_aggregation_files_value")[index]
        gdf = gpd.read_file(path)
        list_columns = list(gdf.columns)
        app.gui.setvar("fiat", "aggregation_file_field_name_value", list_columns)
        app.gui.setvar("fiat", "aggregation_file_field_name_string", list_columns)
        aggregation_attribute = [app.gui.getvar("fiat", "aggregation_file_field_name")]
        if len(aggregation_attribute) > 0:
            app.gui.setvar("fiat", "aggregation_file_field_name", 0)


def write_input_to_table(*args):
    aggregation_attribute = [app.gui.getvar("fiat", "aggregation_file_field_name")]
    aggregation_label = [app.gui.getvar("fiat", "aggregation_label_string")]
    if aggregation_label[0] == None or len(aggregation_label[0]) == 0:
        app.gui.window.dialog_info(
            text="Please first define the Label name.",
            title="No attribute label added",
        )
    else:
        file_index = app.gui.getvar("fiat", "loaded_aggregation_files")
        file = app.gui.getvar("fiat", "loaded_aggregation_files_string")[file_index]
        file_path = app.gui.getvar("fiat", "loaded_aggregation_files_value")[file_index]
        df_aggregation = pd.DataFrame(
            {
                "File": file,
                "Attribute ID": aggregation_attribute,
                "Attribute Label": aggregation_label,
                "File Path": file_path,
            }
         )
        df_all_aggregation = copy.deepcopy(app.gui.getvar("fiat", "aggregation_table"))

        if len(df_all_aggregation) == 0:
            df_all_aggregation = pd.DataFrame(
                columns=["File", "Attribute ID", "Attribute Label", "File Path"]
            )
        added_aggregation = df_aggregation["File"].tolist()
        added_aggregation_list = df_all_aggregation["File"].tolist()

        if added_aggregation[0] not in added_aggregation_list:
            df_all_aggregation = pd.concat([df_all_aggregation,df_aggregation])
        df_all_aggregation.reset_index(drop=True, inplace=True)
        app.gui.setvar("fiat", "aggregation_table", df_all_aggregation)

def get_table_data(*args): 
    aggregation_files_values = app.gui.getvar("fiat", "loaded_aggregation_files_value")
    aggregation_table = app.gui.getvar("fiat", "aggregation_table")
    file_name = aggregation_table["File"].tolist()
    aggregation_fn = []
    for i in aggregation_files_values:
        if i.name in file_name:
            aggregation_fn.append(i.__str__())
    fn   = aggregation_table["File Path"].tolist()
    attribute   = aggregation_table["Attribute ID"].tolist()
    label = aggregation_table["Attribute Label"].tolist()
    return fn, attribute, label


def add_aggregations(*args):
    if app.model["fiat"].domain:
        fn, attribute, label = get_table_data()
        app.active_model.domain.exposure_vm.set_aggregation_areas_config(fn, attribute, label)
        print("Attributes added to model")
        app.gui.window.dialog_info(
        text="Your additional attributes were added to the model",
        title="Added additional attributes",
        )
    else:
        print("no active model")
        app.gui.window.dialog_info(
        text="Please create a model first.",
        title="No active model",
        )
    
def display_aggregation_zone(*args):
    if app.gui.getvar("fiat","show_aggregation_zone"): 
        select_additional_attribute()
    else: 
        app.map.layer["aggregation"].layer["aggregation_layer"].hide()


def deselect_attribute(*args):
    current_aggregation = app.gui.getvar("fiat", "aggregation_table")
    index = app.gui.getvar("fiat", "aggregation_table_name")[0]
    if index > len(
        current_aggregation.values
    ) or index == len(current_aggregation.values):
        index = 0
    current_aggregation = current_aggregation.drop(index, axis=0)
    app.gui.setvar("fiat", "aggregation_table", current_aggregation)
        
def select_additional_attribute(*args):
    """When selecting aggregation area highlight it and if it is activated"""
    # Get info of area selection
    index = app.gui.getvar(
        "fiat", "aggregation_table_name"
    )[0]  # get index of aggregation area
    # Highlight area in map
    if app.gui.getvar("fiat","show_aggregation_zone"): 
        fn, attribute, label = get_table_data()
        attribute_to_visualize = str(attribute[index]) 
        data_to_visualize = Path(fn[index])
        gdf = gpd.read_file(data_to_visualize)
        legend = [] 
        paint_properties = app.model["fiat"].create_paint_properties(
            gdf, attribute_to_visualize, type="polygon", opacity=0.5
        )
        app.map.layer["aggregation"].layer["aggregation_layer"].clear()
            
        app.map.layer["aggregation"].add_layer(
            "aggregation_layer",
            type="choropleth",
            legend_position="top-right",
            legend_title="replace with label name",
            hoover_property=attribute_to_visualize
        )
        app.map.layer["aggregation"].layer["aggregation_layer"].set_data(
        gdf, paint_properties, legend
        )
    else:
        app.map.layer["aggregation"].layer["aggregation_layer"].hide()
    