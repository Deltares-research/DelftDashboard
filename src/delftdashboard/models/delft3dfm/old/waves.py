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
    app.model["delft3dfm"].set_model_variables()
