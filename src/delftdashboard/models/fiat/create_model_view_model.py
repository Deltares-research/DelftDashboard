# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
import geopandas as gpd
import os
import pandas as pd
from pathlib import Path

from delftdashboard.app import app
from delftdashboard.operations import map
from delftdashboard.models.fiat.exposure_aggregation import get_table_data


def select(*args):
    # De-activate existing layers
    map.update()
    if all(values.data is None for key, values in app.map.layer["buildings"].layer.items()):
        app.map.layer["modelmaker_fiat"].layer[app.gui.getvar("modelmaker_fiat", "active_area_of_interest")].show()
    app.gui.setvar("_main", "show_fiat_checkbox", False)
    app.gui.setvar("fiat", "show_asset_locations", True)


def edit(*args):
    app.active_model.set_model_variables()


def display_properties(*args):
    model = "fiat"
    properties_to_display = app.gui.getvar("fiat", "properties_to_display")
    app.gui.setvar("fiat", "show_primary_classification", False)
    app.gui.setvar("fiat", "show_secondary_classification", False)
    if properties_to_display == "Classification":
        app.gui.setvar(model, "classification_display_string", ["Primary", "Secondary"])
        app.gui.setvar(model, "classification_display_value", ["Primary", "Secondary"])
        app.gui.setvar(model, "classification_display_name", "Primary")
        display_classification()
    elif properties_to_display == "ground_flht":
        display_asset_height()
    elif properties_to_display == "Max potential damages":
        app.gui.setvar(model, "max_potential_damage_string", ["Structure", "Content"])
        app.gui.setvar(model, "max_potential_damage_value", ["Structure", "Content"])
        app.gui.setvar(model, "max_potential_damage_name", "Structure")
        display_damage()
    elif properties_to_display == "ground_elevtn":
        display_ground_elevation()
    elif properties_to_display == "Social Vulnerability Index (SVI)":
        display_svi()


def display_classification(*args):
    if app.gui.getvar("fiat", "show_asset_locations"):
        app.map.layer["buildings"].clear()
        if app.gui.getvar("fiat", "classification_display_name") == "Primary":
            app.map.layer["buildings"].layer[
                "exposure_points"
            ].hover_property = "Primary Object Type"
            app.active_model.show_classification(type="primary")
        else:
            app.map.layer["buildings"].layer[
                "exposure_points"
            ].hover_property = "Secondary Object Type"
            app.active_model.show_classification(type="secondary")


def display_damage(*args):
    if app.gui.getvar("fiat", "show_asset_locations"):
        app.map.layer["buildings"].clear()
        if app.gui.getvar("fiat", "max_potential_damage_name") == "Structure":
            app.active_model.show_max_potential_damage_struct()
        else:
            app.active_model.show_max_potential_damage_cont()

def display_asset_height(*args):
    if app.gui.getvar("fiat", "show_asset_locations"):
        app.map.layer["buildings"].clear()
        app.active_model.show_asset_height()

def display_ground_elevation(*args):
    if app.gui.getvar("fiat", "show_asset_locations"):
        app.map.layer["buildings"].clear()
        app.active_model.show_ground_elevation()

def display_svi(*args):    
    if app.gui.getvar("fiat", "show_asset_locations"):
        app.map.layer["buildings"].clear()
        app.active_model.show_svi()

def display_roads(*args):
    """Show/hide roads layer"""
    app.gui.setvar("fiat", "show_roads", args[0])
    if args[0]:
        app.active_model.show_exposure_roads()
    else:
        app.active_model.hide_exposure_roads()

def display_asset_location(*args):
    """Show/hide asset layer"""
    app.gui.setvar("fiat", "show_asset_locations", args[0])
    if args[0]:
        app.map.layer["buildings"].show()
    else:
        app.map.layer["buildings"].hide()

def display_attribute(*args):
    label_to_visualize = app.gui.getvar("fiat", "aggregation_label_display_name")
    table = app.gui.getvar("fiat", "aggregation_table")
    row_index = table.index[table["Attribute Label"] == label_to_visualize].tolist()[0]
    attribute_id = table["Attribute ID"].iloc[row_index]
    data_to_visualize = Path(table["File Path"].iloc[row_index])
    gdf = gpd.read_file(data_to_visualize)
    app.active_model.aggregation = gdf
    paint_properties = app.active_model.create_paint_properties(
        gdf, attribute_id, type="polygon", opacity=0.3
    )
    app.map.layer["aggregation"].layer["aggregation_layer"].clear()
    app.map.layer["aggregation"].layer["aggregation_layer"].set_data(
        gdf,
        paint_properties,
    )


def display_asset_locations(*args):
    """Show/hide buildings layer"""
    app.gui.setvar("fiat", "show_asset_locations", args[0])
    if args[0]:
        app.active_model.show_exposure_buildings()
    else:
        app.active_model.hide_exposure_buildings()


def toggle_attr_map(*args):
    """Show/hide aggregation areas layer if it is already there, or add it in
    mapbox if it is the first time it is called."""
    app.gui.setvar("fiat", "show_attributes", args[0])
    app.map.layer["aggregation"].layer["aggregation_layer"].clear()
    if args[0]:
        fn, attribute, label = get_table_data()
        if len(fn) == 0:
            app.gui.window.dialog_info(
                text="There are no additional attributes in your model.  Please add additional attribute data when you set up your model.",
                title="Additional attributes not found.",
            )
            app.gui.setvar("fiat", "show_attributes", False)
        else:
            label = ["Select"] + label
            app.gui.setvar("fiat", "aggregation_label_display_string", label)
            app.gui.setvar("fiat", "aggregation_label_display_value",  label)
            attributes = [app.gui.getvar("fiat", "aggregation_label_display_name")]
            if len(attributes) > 0:
                app.gui.setvar("fiat", "aggregation_label_display_name", 0)
            app.gui.setvar("fiat", "show_aggregation_zone", False)
    else:
        app.gui.setvar("fiat", "aggregation_label_display_string", [])
        app.gui.setvar("fiat", "aggregation_label_display_value", [])


def open_exposure_results(*args):
    # TODO: Take file from output folder. If is empty open error window, else continue with below.
    model_fn = app.gui.getvar("fiat", "scenario_folder")
    exposure_data_fn = (
        Path(os.path.abspath("")) / model_fn / "exposure" / "exposure.csv"
    )
    if exposure_data_fn.exists():
        exposure_data = gpd.read_file(exposure_data_fn)
        app.gui.setvar("fiat", "view_exposure_value", exposure_data)
        app.active_model.view_exposure()
    else:
        app.gui.window.dialog_info(
            text="Your model is empty. Please create model first.", title="Empty model"
        )


def open_svi_results(*args):
    model_fn = app.gui.getvar("fiat", "scenario_folder")
    svi_data_fn = (
        Path(os.path.abspath(""))
        / model_fn
        / "exposure"
        / "SVI"
        / "social_vulnerability_scores.csv"
    )
    if svi_data_fn.exists():
        svi_data = pd.read_csv(svi_data_fn)
        app.gui.setvar("fiat", "view_svi_value", svi_data)
        app.active_model.view_svi()
    else:
        app.gui.window.dialog_info(
            text="Your model is empty. Please create model first.", title="Empty model"
        )


def open_equity_results(*args):
    print("open equity csv in tableview in extra window")
