# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations import map

def select(*args):
    # De-activate() existing layers
    map.update()
    # Show the grid and mask
    app.map.layer["hurrywave"].layer["grid"].activate()
    app.map.layer["hurrywave"].layer["mask_include"].activate()
    app.map.layer["hurrywave"].layer["mask_boundary"].activate()

def set_model_variables(*args):
    app.model["hurrywave"].set_input_variables()
