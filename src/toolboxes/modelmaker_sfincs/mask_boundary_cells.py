# -*- coding: utf-8 -*-
"""
GUI methods for modelmaker_sfincs -> mask_boundary_cells

Created on Mon May 10 12:18:09 2021

@author: Maarten van Ormondt
"""

from ddb import ddb

def select():
    # De-activate existing layers
    ddb.update_map()
    # Show the mask boundary layer
    ddb.gui.map_widget["map"].layer["modelmaker_sfincs"].layer["mask_boundary"].set_mode("active")

def draw_boundary_polygon():
    ddb.toolbox["modelmaker_sfincs"].draw_boundary_polygon()
