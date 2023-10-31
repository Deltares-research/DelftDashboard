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
    app.gui.window.dialog_info(
            f"A FIAT model is created in:\n{app.model['fiat'].domain.fiat_model.root}",
            "FIAT model created",
        )

def edit(*args):
    app.model["fiat"].set_model_variables()

def display_asset_locations(*args):
    """Show/hide buildings layer"""
    app.gui.setvar("fiat", "show_asset_locations", args[0])
    if args[0]:
        app.model["fiat"].show_exposure_layers()
    else:
        app.model["fiat"].hide_exposure_layers()
