# -*- coding: utf-8 -*-
"""
Created on Mon October 30 12:18:09 2023

@author: Santonia27
"""

from delftdashboard.app import app
from delftdashboard.operations import map
import geopandas as gpd 
from pathlib import Path


def select(*args):
    # De-activate existing layers
    map.update()

def set_variables(*args):
    app.model["fiat"].set_input_variables()


def deselect_aggregation(*args):
    print("Deselect aggregation field")

def add_aggregations():
    print("Add aggregations to model")


def load_aggregation_file(name):
    current_list = app.gui.getvar("fiat", "loaded_aggregation_files_string")
    current_list.append(name)
    app.gui.setvar("fiat", "loaded_aggregation_files_string", current_list)

    #app.gui.setvar("fiat", "loaded_aggregation_files", current_list)
    #app.gui.setvar("fiat", "loaded_aggregation_files_string", current_list)
    #app.gui.setvar("fiat", "loaded_aggregation_files_value", current_list)

#def select_aggregation(*args):
    #aggregation_zones = app.gui.getvar("fiat", "loaded_aggregation_files")
    #app.gui.setvar("fiat", "selected_aggregation_files_string",  [aggregation_zones])