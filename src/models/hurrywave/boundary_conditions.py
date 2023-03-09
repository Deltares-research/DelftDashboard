# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
import shapely
import pandas as pd
import geopandas as gpd

from ddb import ddb

def select(*args):
    # Set all layer inactive, except boundary_points
    ddb.update_map()
    ddb.map.layer["hurrywave"].layer["boundary_points"].set_mode("active")
    ddb.map.layer["hurrywave"].layer["mask_boundary"].set_mode("active")
    update()

def add_boundary_point_on_map(*args):
    ddb.map.click_point(point_clicked)

def point_clicked(coords):
    # Point clicked on map. Add boundary point.
    x = coords["lng"]
    y = coords["lat"]
    ddb.model["hurrywave"].domain.boundary_conditions.add_point(x, y)
    index = len(ddb.model["hurrywave"].domain.boundary_conditions.gdf) - 1

    # Remove timeseries column (MapBox cannot deal with this)
    gdf = ddb.model["hurrywave"].domain.boundary_conditions.gdf.drop(["timeseries"], axis=1)

    ddb.map.layer["hurrywave"].layer["boundary_points"].set_data(gdf, index)
    ddb.gui.setvar("hurrywave", "active_boundary_point", index)
    update()


def select_boundary_point_from_list(*args):
    index = ddb.gui.getvar("hurrywave", "active_boundary_point")
    ddb.map.layer["hurrywave"].layer["boundary_points"].set_selected_index(index)

def select_boundary_point_from_map(*args):
    index = args[0]["id"]
    ddb.gui.setvar("hurrywave", "active_boundary_point", index)
    update()

def delete_point_from_list(*args):
    index = ddb.gui.getvar("hurrywave", "active_boundary_point")
    ddb.model["hurrywave"].domain.boundary_conditions.delete_point(index)
    gdf = ddb.model["hurrywave"].domain.boundary_conditions.gdf.drop(["timeseries"], axis=1)
    index = max(min(index, len(gdf) - 1), 0)
    ddb.map.layer["hurrywave"].layer["boundary_points"].set_data(gdf, index)
    ddb.gui.setvar("hurrywave", "active_boundary_point", index)
    update()

def update():
    # Update boundary point names
    nr_boundary_points = len(ddb.model["hurrywave"].domain.boundary_conditions.gdf)
    boundary_point_names = []
    # Loop through boundary points
    for index, row in ddb.model["hurrywave"].domain.boundary_conditions.gdf.iterrows():
        boundary_point_names.append(row["name"])
    ddb.gui.setvar("hurrywave", "boundary_point_names", boundary_point_names)
    ddb.gui.setvar("hurrywave", "nr_boundary_points", nr_boundary_points)
    ddb.gui.window.update()
