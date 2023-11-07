import shapely
import pandas as pd
import geopandas as gpd

from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args):
    # Set all layer inactive, except boundary_points
    map.update
    app.map.layer["sfincs_hmt"].layer["boundary_points"].activate()
    app.map.layer["sfincs_hmt"].layer["mask_bound_wlev"].activate()
    app.map.layer["sfincs_hmt"].layer["mask_bound_outflow"].activate()


def add_boundary_point_on_map(*args):
    app.map.click_point(point_clicked)


def point_clicked(coords):
    # Point clicked on map. Add boundary point.
    x = coords["lng"]
    y = coords["lat"]
    app.model["sfincs_hmt"].domain.boundary_conditions.add_point(x, y)
    index = len(app.model["sfincs_hmt"].domain.boundary_conditions.gdf) - 1

    # Remove timeseries column (MapBox cannot deal with this)
    gdf = app.model["sfincs_hmt"].domain.boundary_conditions.gdf.drop(
        ["timeseries"], axis=1
    )

    app.map.layer["sfincs_hmt"].layer["boundary_points"].set_data(gdf, index)
    app.gui.setvar("sfincs_hmt", "active_boundary_point", index)
    update()


def select_boundary_point_from_list(*args):
    index = app.gui.getvar("sfincs_hmt", "active_boundary_point")
    app.map.layer["sfincs_hmt"].layer["boundary_points"].set_selected_index(index)


def select_boundary_point_from_map(*args):
    index = args[0]["id"]
    app.gui.setvar("sfincs_hmt", "active_boundary_point", index)
    update()


def delete_point_from_list(*args):
    index = app.gui.getvar("sfincs_hmt", "active_boundary_point")
    app.model["sfincs_hmt"].domain.boundary_conditions.delete_point(index)
    gdf = app.model["sfincs_hmt"].domain.boundary_conditions.gdf.drop(
        ["timeseries"], axis=1
    )
    index = max(min(index, len(gdf) - 1), 0)
    app.map.layer["sfincs_hmt"].layer["boundary_points"].set_data(gdf, index)
    app.gui.setvar("sfincs_hmt", "active_boundary_point", index)
    update()


def update():
    # Update boundary point names
    nr_boundary_points = len(app.model["sfincs_hmt"].domain.boundary_conditions.gdf)
    boundary_point_names = []
    # Loop through boundary points
    for index, row in app.model["sfincs_hmt"].domain.boundary_conditions.gdf.iterrows():
        boundary_point_names.append(row["name"])
    app.gui.setvar("sfincs_hmt", "boundary_point_names", boundary_point_names)
    app.gui.setvar("sfincs_hmt", "nr_boundary_points", nr_boundary_points)
    app.gui.window.update()
