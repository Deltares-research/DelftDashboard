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
    app.map.layer["sfincs_cht"].layer["grid"].activate()

def generate_bathymetry(*args):
    app.toolbox["modelmaker_sfincs_cht"].generate_bathymetry()

def edit(*args):
    pass

def info(*args):
    pass
