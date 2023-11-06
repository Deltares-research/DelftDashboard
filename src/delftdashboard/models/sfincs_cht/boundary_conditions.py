# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
import shapely
import pandas as pd
import geopandas as gpd

from delftdashboard.app import app
from delftdashboard.operations import map

def select(*args):
    # Set all layer inactive, except boundary_points
    map.update()
    app.map.layer["sfincs_cht"].layer["boundary_points"].activate()
    update_list()

def write():
    app.model["sfincs_cht"].domain.boundary_conditions.write()

def add_boundary_point_on_map(*args):
    app.map.click_point(point_clicked)

def point_clicked(x, y):
    # Point clicked on map. Add boundary point.
    app.model["sfincs_cht"].domain.boundary_conditions.add_point(x, y, wl=0.0)
    index = len(app.model["sfincs_cht"].domain.boundary_conditions.gdf) - 1
    gdf = app.model["sfincs_cht"].domain.boundary_conditions.gdf
    app.map.layer["sfincs_cht"].layer["boundary_points"].set_data(gdf, index)
    app.gui.setvar("sfincs_cht", "active_boundary_point", index)
    update_list()
    write()


def select_boundary_point_from_list(*args):
    index = app.gui.getvar("sfincs_cht", "active_boundary_point")
    app.map.layer["sfincs_cht"].layer["boundary_points"].select_by_index(index)

def select_boundary_point_from_map(*args):
    index = args[0]["id"]
    app.gui.setvar("sfincs_cht", "active_boundary_point", index)
    app.gui.window.update()

def delete_point_from_list(*args):
    index = app.gui.getvar("sfincs_cht", "active_boundary_point")
    app.model["sfincs_cht"].domain.boundary_conditions.delete_point(index)
    gdf = app.model["sfincs_cht"].domain.boundary_conditions.gdf
    index = max(min(index, len(gdf) - 1), 0)
    app.map.layer["sfincs_cht"].layer["boundary_points"].set_data(gdf, index)
    app.gui.setvar("sfincs_cht", "active_boundary_point", index)
    update_list()
    write()

def update_list():
    # Update boundary point names
    nr_boundary_points = len(app.model["sfincs_cht"].domain.boundary_conditions.gdf)
    boundary_point_names = []
    # Loop through boundary points
    for index, row in app.model["sfincs_cht"].domain.boundary_conditions.gdf.iterrows():
        boundary_point_names.append(row["name"])
    app.gui.setvar("sfincs_cht", "boundary_point_names", boundary_point_names)
    app.gui.setvar("sfincs_cht", "nr_boundary_points", nr_boundary_points)
    app.gui.window.update()

def create_boundary_points(*args):
    # First check if there are already boundary points
    if len(app.model["sfincs_cht"].domain.boundary_conditions.gdf.index)>0:
        ok = app.gui.window.dialog_ok_cancel("Existing boundary points will be overwritten! Continue?",                                
                                    title="Warning")
        if not ok:
            return
    # Check for open boundary points in mask
    mask = app.model["sfincs_cht"].domain.grid.data["mask"]
    if mask is None:
        ok = app.gui.window.dialog_info("Please first create a mask for this domain.",                                
                                    title=" ")
        return
    if not app.model["sfincs_cht"].domain.mask.has_open_boundaries():
        ok = app.gui.window.dialog_info("The mask for this domain does not have any open boundary points !",                                
                                    title=" ")
        return
    # Create points from mask
    bnd_dist = app.gui.getvar("sfincs_cht", "boundary_dx")
    app.model["sfincs_cht"].domain.boundary_conditions.get_boundary_points_from_mask(bnd_dist=bnd_dist)
    gdf = app.model["sfincs_cht"].domain.boundary_conditions.gdf
    app.map.layer["sfincs_cht"].layer["boundary_points"].set_data(gdf, 0)
    # Set uniform conditions (wl = 0.0 for all points)
    app.model["sfincs_cht"].domain.boundary_conditions.set_timeseries_uniform(0.0)
    # Save points to bnd and bzs files
    app.model["sfincs_cht"].domain.boundary_conditions.write_boundary_points()
    app.model["sfincs_cht"].domain.boundary_conditions.write_boundary_conditions_timeseries()
    app.gui.setvar("sfincs_cht", "active_boundary_point", 0)
    update_list()
