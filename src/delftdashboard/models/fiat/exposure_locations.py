# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations import map
from pathlib import Path
import pandas as pd


def select(*args):
    # De-activate existing layers
    map.update()


def set_variables(*args):
    app.model["fiat"].set_input_variables()


def set_asset_locations(*args):
    print("Set asset locations")


def load_asset_locations(name):
    current_list_string = app.gui.getvar("fiat", "selected_asset_locations_string")
    if name in current_list_string:
        return
    current_list_string.append(name)
    app.gui.setvar("fiat", "selected_asset_locations_string", current_list_string)


def load_asset_locations_file(*args):
    fn = app.gui.window.dialog_open_file("Select geometry",
                                          filter="Geometry (*.shp *.gpkg *.geojson)")
    name = Path(fn[0]).name
    load_asset_locations(name)



def display_roads(*args):
    """Show/hide roads layer""" 
    app.gui.setvar("fiat", "show_roads", args[0])
    if args[0]:
        app.model["fiat"].show_exposure_roads()
    else:
        app.model["fiat"].hide_exposure_roads()


def display_asset_locations(*args):
    """Show/hide buildings layer"""
    app.gui.setvar("fiat", "show_asset_locations", args[0])
    if args[0]:
        app.model["fiat"].show_exposure_buildings()
    else:
        app.model["fiat"].hide_exposure_buildings()


def apply_extraction_method(*args):
    # TODO: only apply to the selected dataset?
    extraction_method = app.gui.getvar("fiat", "extraction_method")
    app.model["fiat"].domain.exposure_vm.setup_extraction_method(extraction_method)


def add_exposure_locations_to_model(*args):
    selected_asset_locations = app.gui.getvar("fiat", "selected_asset_locations_string")
    if len(selected_asset_locations) == 1 and selected_asset_locations[0] == 'National Structure Inventory (NSI)':
        selected_asset_locations = "NSI"
        build_nsi_exposure()
    else:
        app.gui.window.dialog_info(text="The option to have multiple asset location sources is not implemented yet.", title="Not yet implemented")
        return
    
    app.model["fiat"].domain.exposure_vm.set_asset_data_source(selected_asset_locations)


def build_nsi_exposure(*args):
    model = "fiat"
    checkbox_group = "_main"
    try:
        dlg = app.gui.window.dialog_wait("\nDownloading NSI data...")
        app.gui.setvar(model, "created_nsi_assets", "nsi")
        app.gui.setvar(
            model, "text_feedback_create_asset_locations", "NSI assets created"
        )

        crs = app.gui.getvar(model, "selected_crs")
        (
            gdf,
            unique_primary_types,
            unique_secondary_types,
        ) = app.model[
            model
        ].domain.exposure_vm.set_asset_locations_source(source="NSI", crs=crs)
        gdf.set_crs(crs, inplace=True)

        # Set the buildings attribute to gdf for easy visualization of the buildings
        app.model["fiat"].buildings = gdf

        app.map.layer["buildings"].layer["exposure_points"].crs = crs
        app.map.layer["buildings"].layer["exposure_points"].set_data(
            gdf
        )

        app.gui.setvar(
            model, "selected_primary_classification_string", unique_primary_types
        )
        app.gui.setvar(
            model, "selected_secondary_classification_string", unique_secondary_types
        )
        app.gui.setvar(
            model, "selected_primary_classification_value", unique_primary_types
        )
        app.gui.setvar(
            model, "selected_secondary_classification_value", unique_secondary_types
        )

        app.gui.setvar(model, "show_asset_locations", True)

        df = pd.DataFrame(columns=["Assigned"])
        df["Secondary Object Type"] = list(gdf["Secondary Object Type"].unique())
        ## TODO: add the nr of stories and the basement
        df.fillna("", inplace=True)
        
        app.gui.setvar(model, "exposure_categories_to_link", df)

        # Set the checkboxes checked
        app.gui.setvar(checkbox_group, "checkbox_asset_locations", True)
        app.gui.setvar(checkbox_group, "checkbox_classification", True)
        app.gui.setvar(checkbox_group, "checkbox_damage_values", True)
        app.gui.setvar(checkbox_group, "checkbox_elevation", True)

        dlg.close()

    except FileNotFoundError:
        app.gui.window.dialog_info(
            text="Please first select a model boundary.",
            title="No model boundary selected",
        )