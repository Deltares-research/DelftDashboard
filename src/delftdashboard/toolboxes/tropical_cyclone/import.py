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

from cht_cyclones import CycloneTrackDatabase, track_selector

# Callbacks

def select(*args):
    # De-activate() existing layers
    map.update()
    # Tab selected
    # Show track
    app.toolbox["tropical_cyclone"].set_layer_mode("active")

def select_track(*args):

    # For now, only read in dataset "IBTrACS_NA_v04r00"
    dataset = app.toolbox["tropical_cyclone"].cyclone_track_database.get_dataset("IBTrACS_NA_v04r00")

    # Open track selector
    tc, okay = track_selector(dataset,
        app, lon=-80.0, lat=30.0, distance=300.0, year_min=2000, year_max=2023
    )

    if okay:
        app.toolbox["tropical_cyclone"].tc = tc
        app.toolbox["tropical_cyclone"].tc.name = app.toolbox["tropical_cyclone"].tc.name.lower()
        app.toolbox["tropical_cyclone"].track_added()
