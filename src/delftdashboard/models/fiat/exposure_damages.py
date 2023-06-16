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


def set_feedback_damage_values(*args):
    damage_source = app.gui.getvar("fiat", "damage_source")
    if damage_source == "hazus":
        app.gui.setvar(
            "fiat", "text_feedback_damage_values", "Hazus damage values selected"
        )
    elif damage_source == "nsi":
        app.gui.setvar(
            "fiat", "text_feedback_damage_values", "NSI damage values selected"
        )
    elif damage_source == "create":
        app.gui.setvar(
            "fiat", "text_feedback_damage_values", "Custom damage values selected"
        )
