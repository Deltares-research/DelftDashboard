# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
import os
# import math
# import numpy as np
import geopandas as gpd
# import shapely
# import json
# import os
from delftdashboard.app import app
from delftdashboard.operations import map

from cht_cyclones import track_selector

# Callbacks

def select(*args):
    # De-activate() existing layers
    map.update()
    # Tab selected
    # Show track
    app.toolbox["tropical_cyclone"].set_layer_mode("active")

def select_dataset(*args):
    pass

def select_track(*args):

    # For now, only read in dataset "IBTrACS_NA_v04r00"
    dataset_name = app.gui.getvar("tropical_cyclone", "selected_track_dataset")
    dataset = app.toolbox["tropical_cyclone"].cyclone_track_database.get_dataset(dataset_name)

    # Get the center of the map
    center = app.map.map_center

    # Open track selector
    tc, okay = track_selector(dataset,
        app, lon=center[0], lat=center[1], distance=300.0, year_min=2000, year_max=2025
    )

    if okay:
        app.toolbox["tropical_cyclone"].tc = tc
        app.toolbox["tropical_cyclone"].tc.name = app.toolbox["tropical_cyclone"].tc.name.lower()
        app.toolbox["tropical_cyclone"].track_added()

def load_track(*args):
    app.toolbox["tropical_cyclone"].load_track()

def save_track(*args):
    app.toolbox["tropical_cyclone"].save_track()

def delete_track(*args):
    app.toolbox["tropical_cyclone"].delete_track()
