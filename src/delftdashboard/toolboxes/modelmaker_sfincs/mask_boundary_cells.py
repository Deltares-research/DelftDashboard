# -*- coding: utf-8 -*-
"""
GUI methods for modelmaker_sfincs -> mask_boundary_cells

Created on Mon May 10 12:18:09 2021

@author: Maarten van Ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations import map

def select(*args):
    # De-activate existing layers
    map.update()
    # Show the mask boundary layer
    app.map.layer["modelmaker_sfincs"].layer["mask_boundary"].set_mode("active")

def draw_boundary_polygon(*args):
    app.toolbox["modelmaker_sfincs"].draw_boundary_polygon()
