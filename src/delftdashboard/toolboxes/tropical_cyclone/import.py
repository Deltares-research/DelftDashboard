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

    # Open menu to either use the center point of the model or map to load tracks
    if app.gui.module.active_model is not None and app.gui.window.dialog_yes_no(
            "Would you like to use the center point of your active model to load tracks?"
        ):
        app.gui.module.active_model.domain.grid.get_exterior()
        center = app.gui.module.active_model.domain.grid.exterior.centroid
        if app.gui.module.active_model.domain.crs.is_projected:
            # If the CRS is not geographic, we need to transform the coordinates to geographic
            center = center.to_crs("EPSG:4326")
        lon, lat = center.x[0], center.y[0]
    else:
        # Use map center point
        lon = app.map.map_center[0]
        lat = app.map.map_center[1]
        if app.map.crs.is_projected:
            # If the CRS is not geographic, we need to transform the coordinates to geographic
            lon, lat = app.map.crs.to_geographic(lon, lat)

    # Open track selector
    tc, okay = track_selector(dataset,
        app, lon=lon, lat=lat, distance=300.0, year_min=2000, year_max=2023
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
