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
    if deselected_aggregation > len(
        current_list_string
    ) or deselected_aggregation == len(current_list_string):
        deselected_aggregation = 0
    name = current_list_string[deselected_aggregation]
    deselection(name)


def deselection(name):
    current_list_string = app.gui.getvar("fiat", "selected_aggregation_files_string")
    current_list_string.remove(name)
    app.gui.setvar("fiat", "selected_aggregation_files_string", current_list_string)


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
        app.gui.setvar("fiat", "aggregation_file_field_name", 0)


def write_input_to_table(*args):
    aggregation_attribute = [app.gui.getvar("fiat", "aggregation_file_field_name")]
    aggregation_label = [app.gui.getvar("fiat", "aggregation_label_string")]
    file_index = app.gui.getvar("fiat", "loaded_aggregation_files")
    file = app.gui.getvar("fiat", "loaded_aggregation_files_string")[file_index]
    df_aggregation = pd.DataFrame(
        {
            "File": file,
            "Aggregation Attribute": aggregation_attribute,
            "Aggregation Label": aggregation_label,
        }
    )
    df_all_aggregation = copy.deepcopy(app.gui.getvar("fiat", "aggregation_table"))

    if len(df_all_aggregation) == 0:
        df_all_aggregation = pd.DataFrame(
            columns=["File", "Aggregation Attribute", "Aggregation Label"]
        )

    added_aggregation = df_aggregation["File"].tolist()
    added_aggregation_list = df_all_aggregation["File"].tolist()

    if added_aggregation[0] not in added_aggregation_list:
        df_all_aggregation = pd.concat([df_all_aggregation,df_aggregation])
    df_all_aggregation.reset_index(drop=True, inplace=True)
    app.gui.setvar("fiat", "aggregation_table", df_all_aggregation)
def add_aggregations(*args):
    aggregation_files_values = app.gui.getvar("fiat", "loaded_aggregation_files_value")
    aggregation_table = app.gui.getvar("fiat", "aggregation_table")
    file_name = aggregation_table["File"].tolist()
    aggregation_fn = []
    for i in aggregation_files_values:
        if i.name in file_name:
            aggregation_fn.append(i.__str__())
    for idx, row in aggregation_table.iterrows():
        for name in aggregation_fn:
            if row['File'] in name:
                aggregation_table.at[idx, 'File'] = name
    fn = aggregation_table["File"].tolist()
    attribute   = aggregation_table["Aggregation Attribute"].tolist()
    label = aggregation_table["Aggregation Label"].tolist()
    app.model["fiat"].domain.exposure_vm.set_aggregation_areas_config(fn, attribute, label)

    attribute_to_visualize = "TO FILL"
    data_to_visualize = "TO FILL"
    gdf = gpd.read_file(data_to_visualize)
    paint_properties = app.model["fiat"].create_paint_properties(
        gdf, attribute_to_visualize, type="polygon", opacity=0.5
    )
    legend = []  # Still needs to be made in the mapbox code

    # Clear previously made layers and add a new one with the right properties
    app.map.layer["aggregation"].layer["aggregation_layer"].clear()
    app.map.layer["aggregation"].add_layer(
            "aggregation_layer",
            type="choropleth",
            legend_position="top-right",
            legend_title="Aggregation",
            hoover_property=attribute_to_visualize
        )
    app.map.layer["aggregation"].layer["aggregation_layer"].set_data(
        gdf, paint_properties, legend
    )
