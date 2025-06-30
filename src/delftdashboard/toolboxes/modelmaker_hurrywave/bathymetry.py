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
    app.map.layer["hurrywave"].layer["grid"].activate()

def generate_bathymetry(*args):
    app.toolbox["modelmaker_hurrywave"].generate_bathymetry()

def edit(*args):
    pass

def info(*args):
    pass
