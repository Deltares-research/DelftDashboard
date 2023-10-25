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

def create_model(*args):
    hydro_vm = HydroMtViewModel(
    app.config["working_directory"], app.config["data_libs"]
    )
    hydro_vm.save_data_catalog()
    hydro_vm.build_config_ini()
    hydro_vm.run_hydromt_fiat()

def edit(*args):
    app.model["fiat"].set_model_variables()

def display_asset_locations(*args):
    """Show/hide buildings layer"""
    app.gui.setvar("fiat", "show_asset_locations", args[0])
    if args[0]:
        app.map.layer["fiat"].layer["exposure_points"].show()
    else:
        app.map.layer["fiat"].layer["exposure_points"].hide()