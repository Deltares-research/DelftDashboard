# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
import os
from delftdashboard.app import app
from delftdashboard.operations import map

# Callbacks

def select(*args):
    # Tab selected
    # De-activate() existing layers
    map.update()

def export_dataset(*args):
    app.toolbox["bathymetry"].export_dataset()
