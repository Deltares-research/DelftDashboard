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

# def create_boundary_points(*args):
#     app.toolbox["modelmaker_hurrywave"].create_boundary_points()

def create_boundary_points(*args):

    dlg = app.gui.window.dialog_wait("Making boundary points ...")

    # First check if there are already boundary points
    if len(app.model["hurrywave"].domain.boundary_conditions.gdf.index)>0:
        ok = app.gui.window.dialog_ok_cancel("Existing boundary points will be overwritten! Continue?",                                
                                    title="Warning")
        if not ok:
            return

    # Create points from mask
    bnd_dist = app.gui.getvar("hurrywave", "boundary_dx")
    app.model["hurrywave"].domain.boundary_conditions.get_boundary_points_from_mask(bnd_dist=bnd_dist)
    # Drop time series (MapBox doesn't like it)
    gdf = app.model["hurrywave"].domain.boundary_conditions.gdf.drop(["timeseries"], axis=1)
    app.map.layer["hurrywave"].layer["boundary_points"].set_data(gdf, 0)
    # Save points to bnd file
    app.model["hurrywave"].domain.boundary_conditions.write_boundary_points()
    # Set all boundary conditions to constant values
    app.model["hurrywave"].domain.boundary_conditions.set_timeseries_uniform(1.0, 8.0, 45.0, 20.0)
    # Save points to bhs, etc. files
    app.model["hurrywave"].domain.boundary_conditions.write_boundary_conditions_timeseries()

    dlg.close()
