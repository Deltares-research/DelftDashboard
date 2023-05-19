# -*- coding: utf-8 -*-
"""
GUI methods for modelmaker_sfincs -> mask_active_cells

Created on Mon May 10 12:18:09 2021

@author: Maarten van Ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations import map

def select(*args):
    # De-activate existing layers
    map.update()
    # Show the mask include and exclude layer
    app.map.layer["modelmaker_sfincs"].layer["mask_include"].set_mode("active")
    app.map.layer["modelmaker_sfincs"].layer["mask_exclude"].set_mode("active")

def draw_include_polygon(*args):
    app.toolbox["modelmaker_sfincs"].draw_include_polygon()

def draw_exclude_polygon(*args):
    app.toolbox["modelmaker_sfincs"].draw_exclude_polygon()
