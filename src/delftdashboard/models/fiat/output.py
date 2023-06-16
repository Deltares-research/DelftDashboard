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


def edit(*args):
    app.model["fiat"].set_model_variables()


def select_selected_primary_classification(*args):
    print("Select primary classification type")


def select_selected_secondary_classification(*args):
    print("Select secondary classification type")


def display_primary_classification(*args):
    print("Display primary classification fields")


def display_secondary_classification(*args):
    print("Display secondary classification fields")


def create_model_setup(*args):
    hydro_vm = HydroMtViewModel(
        app.config["working_directory"], app.config["data_libs_fiat"][0]
    )
    hydro_vm.save_data_catalog()
    hydro_vm.build_config_ini()
    hydro_vm.run_hydromt_fiat()
