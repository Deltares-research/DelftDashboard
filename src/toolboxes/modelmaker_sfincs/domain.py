# -*- coding: utf-8 -*-
"""
GUI methods for modelmaker_sfincs -> domain

Created on Mon May 10 12:18:09 2021

@author: Maarten van Ormondt
"""

from ddb import ddb

def select():
    # De-activate existing layers
    ddb.update_map()
    # Show the grid outline layer
    ddb.gui.map_widget["map"].layer["modelmaker_sfincs"].layer["grid_outline"].set_mode("active")

def draw_grid_outline():
    ddb.toolbox["modelmaker_sfincs"].draw_grid_outline()

def generate_grid():
    ddb.toolbox["modelmaker_sfincs"].generate_grid()
