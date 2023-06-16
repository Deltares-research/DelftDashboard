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


def set_asset_locations(*args):
    print("Set asset locations")


def set_asset_locations_field(*args):
    app.model["fiat"].set_asset_locations_field()


def activate_create_nsi_assets(*args):
    app.gui.setvar("fiat", "created_assets", "nsi")
    app.gui.setvar(
        "fiat", "text_feedback_create_asset_locations", "Assets created from NSI"
    )

    hydro_vm = HydroMtViewModel(
        app.config["working_directory"], app.config["data_libs_fiat"][0]
    )
    hydro_vm.exposure_vm.set_asset_locations_source(
        input_source="NSI", fiat_model=hydro_vm.fiat_model
    )


def display_asset_locations(*args):
    print("Display assets")


def display_extraction_method(*args):
    print("Display extraction method")


def draw_extraction_method_exception(*args):
    print("Draw extraction method")
