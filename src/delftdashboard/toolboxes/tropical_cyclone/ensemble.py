# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

from datetime import datetime

from delftdashboard.app import app
from delftdashboard.operations import map


# Callbacks

def select(*args):
    # De-activate() existing layers
    map.update()
    # Tab selected
    # Show track and enseble layers
    # app.map.layer["tropical_cyclone"].layer["cyclone_track"].show()
    app.toolbox["tropical_cyclone"].set_layer_mode("active")
    app.map.layer["tropical_cyclone"].layer["cyclone_track_ensemble"].show()
    app.map.layer["tropical_cyclone"].layer["cyclone_track_ensemble_cone"].show()
    update_track_time_strings()

def make_ensemble(*args):
    tc = app.toolbox["tropical_cyclone"].tc
    tstart = app.gui.getvar("tropical_cyclone", "ensemble_start_time")
    duration = app.gui.getvar("tropical_cyclone", "ensemble_duration")
    nr_realizations = app.gui.getvar("tropical_cyclone", "ensemble_number_of_realizations")
    # Add wait box
    p = app.gui.window.dialog_wait("               Generating ensemble ...                ")
    ensemble = tc.make_ensemble(duration=duration,
                                tstart=tstart, 
                                compute_wind_fields=False,
                                number_of_realizations=nr_realizations)
    p.close()
    app.toolbox["tropical_cyclone"].ensemble = ensemble
    # Plot ensemble tracks
    plot_ensemble_tracks()
    # Plot ensemble cone
    plot_ensemble_cone()

def edit_cone_buffer(*args):
    plot_ensemble_cone()

def edit_duration(*args):
    pass

def edit_number_of_realizations(*args):
    pass

def select_tstart(*args):
    index = app.gui.getvar("tropical_cyclone", "ensemble_start_time_index")
    track_time_strings = app.gui.getvar("tropical_cyclone", "track_time_strings")
    if len(track_time_strings) > 0:
        tstart = datetime.strptime(track_time_strings[index], "%Y%m%d %H%M%S")
        app.gui.setvar("tropical_cyclone", "ensemble_start_time", tstart)        
    else:
        app.gui.setvar("tropical_cyclone", "ensemble_start_time", None)

def plot_ensemble_tracks():    
    gdf = app.toolbox["tropical_cyclone"].ensemble.to_gdf(option="tracks",
                          filename=None).set_crs(epsg=4326)
    app.map.layer["tropical_cyclone"].layer["cyclone_track_ensemble"].set_data(gdf)

def plot_ensemble_cone():
    cone_buffer = app.gui.getvar("tropical_cyclone", "ensemble_cone_buffer")
    only_forecast = app.gui.getvar("tropical_cyclone", "ensemble_cone_only_forecast")
    gdf_cone = app.toolbox["tropical_cyclone"].ensemble.to_gdf(option="cone",
                               filename=None,
                               buffer=cone_buffer,
                               only_forecast=only_forecast).set_crs(epsg=4326)
    app.map.layer["tropical_cyclone"].layer["cyclone_track_ensemble_cone"].set_data(gdf_cone)

def update_track_time_strings():
    track_time_strings = []
    if app.toolbox["tropical_cyclone"].tc is None:
        return
    for i in range(len(app.toolbox["tropical_cyclone"].tc.track.gdf)):
        track_time_strings.append(app.toolbox["tropical_cyclone"].tc.track.gdf.loc[i, "datetime"])
    app.gui.setvar("tropical_cyclone", "track_time_strings", track_time_strings)    
