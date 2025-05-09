# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
# import math
# import numpy as np
import geopandas as gpd
# import shapely
# import json
# import os
from delftdashboard.app import app
from delftdashboard.operations import map


# Callbacks

def select(*args):
    # De-activate existing layers
    map.update()
    # Tab selected
    app.toolbox["tropical_cyclone"].set_layer_mode("active")

def edit_variables(*args):
    pass

def build_spiderweb(*args):
    app.toolbox["tropical_cyclone"].build_spiderweb()

def load_config(*args):
    app.toolbox["tropical_cyclone"].load_config()

def save_config(*args):
    app.toolbox["tropical_cyclone"].save_config()
