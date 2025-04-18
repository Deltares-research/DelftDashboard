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
    # De-activate() existing layers
    map.update()
    # Tab selected
    # Show track
    app.toolbox["tropical_cyclone"].set_layer_mode("active")

def modify(*args):
    pass
