import shapely
import pandas as pd
import geopandas as gpd

from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args):
    # Set all layer inactive, except discharge_points
    map.update()
    app.map.layer["sfincs_hmt"].layer["discharge_points"].activate()
    app.map.layer["sfincs_hmt"].layer["mask"].activate()
    update_list()


def add_discharge_point(gdf, merge=True):
    model = app.model["sfincs_hmt"].domain

    # add to existing discharge conditions
    model.set_forcing_1d(gdf_locs=gdf, name="dis", merge=merge)

    # retrieve all discharge points as gdf from xarray
    gdf = model.forcing["dis"].vector.to_gdf()

    # get the last index of the gdf
    index = int(gdf.index[-1])

    app.map.layer["sfincs_hmt"].layer["discharge_points"].set_data(gdf, index)
    app.gui.setvar("sfincs_hmt", "active_discharge_point", index)
    update_list()


def add_discharge_point_on_map(*args):
    app.map.click_point(point_clicked)


def point_clicked(x, y):
    # Add point to discharge conditions
    model = app.model["sfincs_hmt"].domain

    # create gdf from xy
    geometry = gpd.points_from_xy([x], [y])
    gdf = gpd.GeoDataFrame(geometry=geometry, crs=app.crs)

    if "dis" in model.forcing:
        # make sure new point gets an index that doesnt exist in model.forcing["dis"]
        index = int(model.forcing["dis"].index[-1]) + 1
        # set index of gdf
        gdf.index = [index]

    # add to existing discharge conditions
    model.set_forcing_1d(gdf_locs=gdf, name="dis", merge=True)

    # retrieve all discharge points as gdf from xarray
    gdf = model.forcing["dis"].vector.to_gdf()

    # get the last index of the gdf
    index = int(gdf.index[-1])

    app.map.layer["sfincs_hmt"].layer["discharge_points"].set_data(gdf, index)
    app.gui.setvar("sfincs_hmt", "active_discharge_point", index)
    update_list()


def select_discharge_point_from_list(*args):
    index = app.gui.getvar("sfincs_hmt", "active_discharge_point")
    app.map.layer["sfincs_hmt"].layer["discharge_points"].select_by_index(index)


def select_discharge_point_from_map(*args):
    index = args[0]["id"]
    app.gui.setvar("sfincs_hmt", "active_discharge_point", index)
    app.gui.window.update()


def delete_point_from_list(*args):
    model = app.model["sfincs_hmt"].domain
    index = app.gui.getvar("sfincs_hmt", "active_discharge_point")

    # delete point from model forcing
    model.forcing["dis"] = model.forcing["dis"].drop_sel(index=index)

    if len(model.forcing["dis"].index) == 0:
        # if no points are left, drop the forcing
        model.forcing.pop("dis")
        app.map.layer["sfincs_hmt"].layer["discharge_points"].clear()
    else:
        # convert to new gdf
        gdf = model.forcing["dis"].vector.to_gdf()

        # set new index
        index = index - 1 if index > 0 else 0

        app.map.layer["sfincs_hmt"].layer["discharge_points"].set_data(gdf, index)
        app.gui.setvar("sfincs_hmt", "active_discharge_point", index)
    update_list()


def delete_all_points_from_list(*args):
    model = app.model["sfincs_hmt"].domain
    model.forcing.pop("dis")
    app.map.layer["sfincs_hmt"].layer["discharge_points"].clear()
    update_list()


def update_list():
    # Get discharge points
    gdf = app.map.layer["sfincs_hmt"].layer["discharge_points"].data
    discharge_point_names = []

    if gdf is None:
        index = 0
    else:
        # Loop through discharge points
        for index, row in gdf.iterrows():
            # Get the name of the discharge point if present
            if "name" in row:
                discharge_point_names.append(row["name"])
            else:
                discharge_point_names.append("Point {}".format(index))

    app.gui.setvar("sfincs_hmt", "discharge_point_names", discharge_point_names)
    app.gui.setvar("sfincs_hmt", "nr_discharge_points", index)
    app.gui.window.update()


def go_to_observation_stations(*args):

    toolbox_name = "observation_stations"

    # switch to observation stations toolbox
    app.active_toolbox = app.toolbox[toolbox_name]
    app.active_toolbox.select()

    # TODO back to observations model-tab
    # app.active_toolbox.select_tab("observations")
