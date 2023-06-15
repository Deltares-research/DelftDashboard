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


def set_asset_locations(*args):
    print("Set asset locations")


def set_asset_locations_field(*args):
    app.model["fiat"].set_asset_locations_field()


def activate_create_nsi_assets(*args):
    print("Create NSI assets")
    app.gui.setvar("fiat", "create_nsi_assets", True)


def display_asset_locations(*args):
    print("Display assets")


def display_extraction_method(*args):
    print("Display extraction method")


def draw_extraction_method_exception(*args):
    print("Draw extraction method")