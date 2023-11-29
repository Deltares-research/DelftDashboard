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
    app.model["fiat"].domain.run_hydromt_fiat()
    app.gui.window.dialog_info(
            f"A FIAT model is created in:\n{app.model['fiat'].domain.fiat_model.root}",
            "FIAT model created",
        )

def edit(*args):
    app.model["fiat"].set_model_variables()

def display_properties(*args):
    model = "fiat"
    properties_to_display = app.gui.getvar("fiat", "properties_to_display")
    if properties_to_display == "Classification":
        app.model[model].show_classification()
    elif properties_to_display == "Asset heights":
        NotImplemented
    elif properties_to_display == "Max potential damages":
        NotImplemented
    elif properties_to_display == "Aggregation":
        NotImplemented
    elif properties_to_display == "Damage curves":
        NotImplemented
    elif properties_to_display == "Roads":
        app.model[model].show_exposure_roads()
