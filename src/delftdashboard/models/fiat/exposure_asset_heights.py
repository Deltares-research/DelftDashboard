# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations import map

def select(*args):
    # De-activate existing layers
    map.update()


def set_variables(*args):
    app.model["fiat"].set_input_variables()


def select_loaded_dataset(*args):
    print("Select loaded dataset")


def deselect_selected_dataset(*args):
    print("Deselect selected dataset")


def load_asset_heights_file(*args):
    fn = app.gui.window.dialog_open_file(
        "Select geometry", filter="Geometry (*.shp *.gpkg *.geojson)"
    )
    fn = fn[0]
    fn_value = app.gui.getvar("fiat", "loaded_asset_heights_files_value")
    if fn not in fn_value:
        fn_value.append(Path(fn))
    app.gui.setvar("fiat", "loaded_asset_heights_files_value", fn_value)
    name = Path(fn).name
    load_asset_heights(name)

def load_asset_heights(name):
    current_list_string = app.gui.getvar("fiat", "loaded_asset_heights_files_string")
    if name not in current_list_string:
        current_list_string.append(name)

    app.gui.setvar("fiat", "loaded_asset_heights_files_string", current_list_string)


def move_up_selected_dataset(*args):
    print("Move up selected dataset")


def move_down_selected_dataset(*args):
    print("Move down selected dataset")


def merge_data(*args):
    print("Merge data")


def display_asset_heights(*args):
    print("Display asset heights")


def add_to_model(*args):
    print("Add to model")