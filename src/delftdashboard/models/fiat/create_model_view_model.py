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


def display_roads(*args):
    """Show/hide roads layer""" 
    app.gui.setvar("fiat", "show_roads", args[0])
    if args[0]:
        app.model["fiat"].show_exposure_roads()
    else:
        app.model["fiat"].hide_exposure_roads()
