# -*- coding: utf-8 -*-
"""
GUI methods for modelmaker_sfincs -> quadtree

Created on Mon May 10 12:18:09 2021

@author: Maarten van Ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations import map

def select(*args):
    # De-activate existing layers
    map.update()
    # Show the refinement layer
    app.map.layer["modelmaker_sfincs"].layer["quadtree_refinement"].set_mode("active")

def draw_refinement_polygon(*args):
    app.toolbox["modelmaker_sfincs"].draw_refinement_polygon()
