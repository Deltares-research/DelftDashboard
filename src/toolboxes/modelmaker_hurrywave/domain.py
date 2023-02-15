# -*- coding: utf-8 -*-
"""
GUI methods for modelmaker_hurrywave -> domain

Created on Mon May 10 12:18:09 2021

@author: Maarten van Ormondt
"""

from ddb import ddb

def select(*args):
    # De-activate existing layers
    ddb.update_map()
    # Show the grid outline layer
    ddb.map.layer["modelmaker_hurrywave"].layer["grid_outline"].set_mode("active")

def draw_grid_outline(*args):
    ddb.toolbox["modelmaker_hurrywave"].draw_grid_outline()

def generate_grid(*args):
    ddb.toolbox["modelmaker_hurrywave"].generate_grid()
