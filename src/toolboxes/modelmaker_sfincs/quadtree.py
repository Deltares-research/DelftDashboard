# -*- coding: utf-8 -*-
"""
GUI methods for modelmaker_sfincs -> quadtree

Created on Mon May 10 12:18:09 2021

@author: Maarten van Ormondt
"""

from ddb import ddb

def select():
    # De-activate existing layers
    ddb.update_map()
    # Show the refinement layer
    ddb.gui.map_widget["map"].layer["modelmaker_sfincs"].layer["quadtree_refinement"].set_mode("active")

def draw_refinement_polygon():
    ddb.toolbox["modelmaker_sfincs"].draw_refinement_polygon()
