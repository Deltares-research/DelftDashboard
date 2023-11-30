# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
import geopandas as gpd
from pathlib import Path

from delftdashboard.app import app
from delftdashboard.operations import map
from delftdashboard.models.fiat.exposure_aggregation import get_table_data

def select(*args):
    # De-activate existing layers
    map.update()


def edit(*args):
    app.model["fiat"].set_model_variables()


def display_properties(*args):
    model = "fiat"
    properties_to_display = app.gui.getvar("fiat", "properties_to_display")
    if properties_to_display == "Classification":
        app.map.layer["buildings"].clear()
        app.model[model].show_classification()
    elif properties_to_display == "Asset heights":
        app.map.layer["buildings"].clear()
        app.model[model].show_asset_height()
    elif properties_to_display == "Max potential damages":
        app.map.layer["buildings"].clear()
        app.gui.setvar("fiat", "max_potential_damage_string", ["Structure", "Content"])
        app.gui.setvar("fiat", "max_potential_damage_value", ["Structure", "Content"])
    elif properties_to_display == "Ground Elevation":
        app.map.layer["buildings"].clear()
        app.model[model].show_ground_elevation()

def display_damage(*args):
    app.map.layer["buildings"].clear()
    if app.gui.getvar("fiat", "max_potential_damage_name") == "Structure":
        app.model["fiat"].show_max_potential_damage_struct()
    else:
        app.model["fiat"].show_max_potential_damage_cont()
    
def display_roads(*args):
    """Show/hide roads layer""" 
    app.gui.setvar("fiat", "show_roads", args[0])
    if args[0]:
        app.model["fiat"].show_exposure_roads()
    else:
        app.model["fiat"].hide_exposure_roads()

def display_attribute(*args):
        label_to_visualize = app.gui.getvar("fiat", "aggregation_label_display_name")
        table = app.gui.getvar("fiat", "aggregation_table")
        row_index = table.index[table["Attribute Label"] == label_to_visualize].tolist()[0]
        attribute_id = table["Attribute ID"].iloc[row_index]
        data_to_visualize = Path(table["File Path"].iloc[row_index])
        gdf = gpd.read_file(data_to_visualize)
        app.model["fiat"].aggregation = gdf
        paint_properties = app.model["fiat"].create_paint_properties(
            gdf, attribute_id, type="polygon", opacity=0.3
        )   
        app.map.layer["aggregation"].layer["aggregation_layer"].clear()
        app.map.layer["aggregation"].layer["aggregation_layer"].set_data(
        gdf, paint_properties,
        )

def toggle_attr_map(*args):
    """Show/hide aggregation areas layer if it is already there, or add it in
    mapbox if it is the first time it is called."""
    app.gui.setvar("fiat", "show_attributes", args[0])
    app.map.layer["aggregation"].layer["aggregation_layer"].clear()
    if args[0]:
            fn, attribute, label = get_table_data()
            if len(fn) == 0:
                app.gui.window.dialog_info(
                text="There are no additional attributes in your model. Please add attributes when you set up the exposure data.",
                title="Additional attributes not found."
                )
                app.gui.setvar("fiat", "show_attributes", False)
            else:
                app.gui.setvar("fiat", "aggregation_label_display_string", label)
                app.gui.setvar("fiat", "aggregation_label_display_value", label)
                attributes = [app.gui.getvar("fiat", "aggregation_label_display_name")]
                if len(attributes) > 0:
                    app.gui.setvar("fiat", "aggregation_label_display_name", 0)
                app.gui.setvar("fiat", "show_aggregation_zone", False)
    else:
        app.gui.setvar("fiat", "aggregation_label_display_string", [])
        app.gui.setvar("fiat", "aggregation_label_display_value", [])

def display_asset_locations(*args):
    """Show/hide buildings layer"""
    app.gui.setvar("fiat", "show_asset_locations", args[0])
    if args[0]:
        app.active_model.show_exposure_buildings()
    else:
        app.active_model.hide_exposure_buildings()