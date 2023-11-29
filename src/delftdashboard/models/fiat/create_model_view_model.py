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
    elif properties_to_display == "Max potential damages: Structure":
        app.map.layer["buildings"].clear()
        app.model[model].show_max_potential_damage_struct()

    elif properties_to_display == "Max potential damages: Content":
        app.map.layer["buildings"].clear()
        app.model[model].show_max_potential_damage_cont()


def display_roads(*args):
    """Show/hide roads layer""" 
    app.gui.setvar("fiat", "show_roads", args[0])
    if args[0]:
        app.model["fiat"].show_exposure_roads()
    else:
        app.model["fiat"].hide_exposure_roads()

def display_attribute(*args):
    app.gui.setvar("fiat", "show_attributes", args[0])
    if args[0]:
        index = app.gui.getvar("fiat", "aggregation_table_name")[0]
        fn, attribute, label = get_table_data()
        if len(fn) == 0:
            app.gui.window.dialog_info(
            text="There are no additional attributes in your model.Please add attributes when you set up the exposure data.",
            title="Additional attributes not found."
        )
        else:
            attribute_to_visualize = str(attribute[index])
            data_to_visualize = Path(fn[index])
            gdf = gpd.read_file(data_to_visualize)
            app.model["fiat"].aggregation = gdf
            paint_properties = app.model["fiat"].create_paint_properties(
                gdf, attribute_to_visualize, type="polygon", opacity=0.3
            )   
            app.map.layer["aggregation"].layer["aggregation_layer"].clear()
            app.map.layer["aggregation"].layer["aggregation_layer"].set_data(
            gdf, paint_properties,
            )