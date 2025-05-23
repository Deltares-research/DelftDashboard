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
    app.map.layer["hurrywave"].layer["boundary_points"].activate()
    update_conditions()
    update_list()


def write():
    app.model["hurrywave"].domain.boundary_conditions.write()


def add_boundary_point_on_map(*args):
    app.map.click_point(point_clicked)


def point_clicked(x, y):
    # Point clicked on map. Add boundary point.
    hs = app.gui.getvar("hurrywave", "boundary_hm0")
    tp = app.gui.getvar("hurrywave", "boundary_tp")
    wd = app.gui.getvar("hurrywave", "boundary_wd")
    ds = app.gui.getvar("hurrywave", "boundary_ds")
    app.model["hurrywave"].domain.boundary_conditions.add_point(
        x, y, hs=hs, tp=tp, wd=wd, ds=ds
    )
    index = len(app.model["hurrywave"].domain.boundary_conditions.gdf) - 1

    # Remove timeseries column (MapBox cannot deal with this)
    gdf = app.model["hurrywave"].domain.boundary_conditions.gdf.drop(
        ["timeseries"], axis=1
    )

    app.map.layer["hurrywave"].layer["boundary_points"].set_data(gdf, index)
    app.gui.setvar("hurrywave", "nr_boundary_points", len(app.model["hurrywave"].domain.boundary_conditions.gdf))
    app.gui.setvar("hurrywave", "active_boundary_point", index)
    update_list()
    update_conditions()
    write()


def select_boundary_point_from_list(*args):
    index = app.gui.getvar("hurrywave", "active_boundary_point")
    app.map.layer["hurrywave"].layer["boundary_points"].select_by_index(index)
    update_conditions()


def select_boundary_point_from_map(*args):
    index = args[0]["id"]
    app.gui.setvar("hurrywave", "active_boundary_point", index)
    update_conditions()
    app.gui.window.update()


def delete_point_from_list(*args):
    index = app.gui.getvar("hurrywave", "active_boundary_point")
    app.model["hurrywave"].domain.boundary_conditions.delete_point(index)
    gdf = app.model["hurrywave"].domain.boundary_conditions.gdf
    index = max(min(index, len(gdf) - 1), 0)
    app.map.layer["hurrywave"].layer["boundary_points"].set_data(gdf, index)
    app.gui.setvar("hurrywave", "active_boundary_point", index)
    app.gui.setvar("hurrywave", "nr_boundary_points", len(gdf))
    update_conditions()
    update_list()
    write()


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

    update_conditions()
    update_list()


def update_list():
    # Update boundary point names
    nr_boundary_points = len(app.model["hurrywave"].domain.boundary_conditions.gdf)
    boundary_point_names = []
    # Loop through boundary points
    for index, row in app.model["hurrywave"].domain.boundary_conditions.gdf.iterrows():
        boundary_point_names.append(row["name"])
    app.gui.setvar("hurrywave", "boundary_point_names", boundary_point_names)
    app.gui.setvar("hurrywave", "nr_boundary_points", nr_boundary_points)
    app.gui.window.update()


def update_conditions():
    if (
        app.model["hurrywave"].domain.boundary_conditions.forcing == "timeseries"
        and app.gui.getvar("hurrywave", "nr_boundary_points") > 0
    ):
        index = app.gui.getvar("hurrywave", "active_boundary_point")
        # # Check if there are any points
        # if len(app.model["hurrywave"].domain.boundary_conditions.gdf) == 0:
        #     return  
        df = (
            app.model["hurrywave"]
            .domain.boundary_conditions.gdf["timeseries"]
            .loc[index]
        )
        hm0 = df["hs"].iloc[0]
        tp = df["tp"].iloc[0]
        wd = df["wd"].iloc[0]
        ds = df["ds"].iloc[0]
        app.gui.setvar("hurrywave", "boundary_hm0", hm0)
        app.gui.setvar("hurrywave", "boundary_tp", tp)
        app.gui.setvar("hurrywave", "boundary_wd", wd)
        app.gui.setvar("hurrywave", "boundary_ds", ds)


def select_boundary_forcing(*args):
    app.model["hurrywave"].domain.boundary_conditions.forcing = args[0]


def edit_hm0(*args):
    index = app.gui.getvar("hurrywave", "active_boundary_point")
    app.model["hurrywave"].domain.boundary_conditions.set_conditions_at_point(
        index, "hs", args[0]
    )
    write()


def edit_tp(*args):
    index = app.gui.getvar("hurrywave", "active_boundary_point")
    app.model["hurrywave"].domain.boundary_conditions.set_conditions_at_point(
        index, "tp", args[0]
    )
    write()


def edit_wd(*args):
    index = app.gui.getvar("hurrywave", "active_boundary_point")
    app.model["hurrywave"].domain.boundary_conditions.set_conditions_at_point(
        index, "wd", args[0]
    )
    write()


def edit_ds(*args):
    index = app.gui.getvar("hurrywave", "active_boundary_point")
    app.model["hurrywave"].domain.boundary_conditions.set_conditions_at_point(
        index, "ds", args[0]
    )
    write()


def apply_to_all(*args):
    hs = app.gui.getvar("hurrywave", "boundary_hm0")
    tp = app.gui.getvar("hurrywave", "boundary_tp")
    wd = app.gui.getvar("hurrywave", "boundary_wd")
    ds = app.gui.getvar("hurrywave", "boundary_ds")
    app.model["hurrywave"].domain.boundary_conditions.set_timeseries_uniform(
        hs, tp, wd, ds
    )
    write()
