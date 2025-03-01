# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations import map

def select(*args):
    # De-activate existing layers
    map.update()

def set_model_variables(*args):
    # All variables will be set
    app.model["sfincs_hmt"].set_model_variables()

    # Now check that the boundary and other forcing fully covers the simulation time
    app.model["sfincs_hmt"].check_times()
