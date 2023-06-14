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


def activate_create_curves_panel(*args):
    app.gui.setvar("fiat", "create_curves", True)


def set_curve_join_type(*args):
    curve_join_type = app.gui.getvar("fiat", "curve_join_type_value")
    app.gui.setvar("fiat", "curve_join_type", curve_join_type)