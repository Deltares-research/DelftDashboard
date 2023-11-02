# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations import map
from pathlib import Path


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


def load_asset_locations_nsi(*args):
    new_source_value = app.gui.getvar("fiat", "asset_locations")
    idx = app.gui.getvar("fiat", "asset_locations_value").index(new_source_value)
    new_source_string = app.gui.getvar("fiat", "asset_locations_string")[idx]
    load_asset_locations(new_source_string)


def load_asset_locations_file(*args):
    fn = app.gui.window.dialog_open_file("Select geometry",
                                          filter="Geometry (*.shp *.gpkg *.geojson)")
    name = Path(fn[0]).name
    load_asset_locations(name)


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
    else:
        app.gui.window.dialog_info(text="The option to have multiple asset location sources is not implemented yet.", title="Not yet implemented")
        return
    
    app.model["fiat"].domain.exposure_vm.set_asset_data_source(selected_asset_locations)
