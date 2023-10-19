# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations import map
from hydromt_fiat.api.hydromt_fiat_vm import HydroMtViewModel


def select(*args):
    # De-activate existing layers
    map.update()


def set_variables(*args):
    app.model["fiat"].set_input_variables()


def build_nsi_exposure(*args):
    print("Build NSI exposure")

def set_asset_locations(*args):
    print("Set asset locations")


def set_asset_locations_field(*args):
    app.model["fiat"].set_asset_locations_field()


def activate_create_nsi_assets(*args):
    app.gui.setvar("fiat", "created_nsi_assets", "nsi")
    app.gui.setvar("fiat", "text_feedback_create_asset_locations", "NSI assets created")

    hydro_vm = HydroMtViewModel(
        app.config["working_directory"], app.config["data_libs"]
    )
    crs = app.gui.getvar("fiat", "selected_crs")
    (
        gdf,
        unique_primary_types,
        unique_secondary_types,
    ) = hydro_vm.exposure_vm.set_asset_locations_source(input_source="NSI", crs=crs)
    gdf.set_crs(crs, inplace=True)

    app.map.layer["fiat"].layer["exposure_points"].crs = crs
    app.map.layer["fiat"].layer["exposure_points"].set_data(
        gdf, hover_property="Object ID"
    )

    app.gui.setvar(
        "fiat", "selected_primary_classification_string", unique_primary_types
    )
    app.gui.setvar(
        "fiat", "selected_secondary_classification_string", unique_secondary_types
    )
    app.gui.setvar(
        "fiat", "selected_primary_classification_value", unique_primary_types
    )
    app.gui.setvar(
        "fiat", "selected_secondary_classification_value", unique_secondary_types
    )

    app.gui.setvar("fiat", "show_asset_locations", True)


def display_asset_locations(*args):
    """Show/hide buildings layer"""
    app.gui.setvar("fiat", "show_asset_locations", args[0])
    if args[0]:
        app.map.layer["fiat"].layer["exposure_points"].show()
    else:
        app.map.layer["fiat"].layer["exposure_points"].hide()


def display_extraction_method(*args):
    print("Display extraction method")


def draw_extraction_method_exception(*args):
    print("Draw extraction method")


def apply_extraction_method(*args):
    print("Apply extraction method")


def apply_extraction_exception_method(*args):
    print("Apply extraction exception")
