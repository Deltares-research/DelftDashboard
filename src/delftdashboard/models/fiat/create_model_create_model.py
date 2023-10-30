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

def create_model(*args):
    app.model["fiat"].domain.save_data_catalog()
    app.model["fiat"].domain.build_config_ini()
    app.model["fiat"].domain.run_hydromt_fiat()

def edit(*args):
    app.model["fiat"].set_model_variables()

def display_asset_locations(*args):
    """Show/hide buildings layer"""
    app.gui.setvar("fiat", "show_asset_locations", args[0])
    if args[0]:
        app.map.layer["fiat"].layer["exposure_points"].show()
    else:
        app.map.layer["fiat"].layer["exposure_points"].hide()