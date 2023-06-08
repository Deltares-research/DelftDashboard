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
    app.map.layer["fiat"].layer["grid"].set_mode("active")

def create_boundary_points(*args):
    app.toolbox["modelmaker_fiat"].create_boundary_points()
