# -*- coding: utf-8 -*-
"""
GUI methods for modelmaker_sfincs -> domain

Created on Mon May 10 12:18:09 2021

@author: Maarten van Ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations import map

def select(*args):
    # De-activate existing layers
    map.update()
    # Show the grid outline layer
    app.map.layer["modelmaker_sfincs"].layer["grid_outline"].set_mode("active")

def edit(*args):
    pass

def draw_grid_outline(*args):
    app.toolbox["modelmaker_sfincs"].draw_grid_outline()

def generate_grid():
    app.toolbox["modelmaker_sfincs"].generate_grid()
