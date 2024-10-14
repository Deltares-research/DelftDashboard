import geopandas as gpd
import numpy as np
import pandas as pd

from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args):
    # Set all layer inactive, except discharge_points
    map.update()
    app.map.layer["sfincs_hmt"].layer["mask"].activate()
    app.map.layer["sfincs_hmt"].layer["discharge_points"].activate()
    update_list()


def add_discharge_point(gdf, merge=True):
    model = app.model["sfincs_hmt"].domain

    nr_dis = 0
    if "dis" in model.forcing:
        nr_dis = len(model.forcing["dis"].index)
    try:
        # add to existing discharge conditions
        model.set_forcing_1d(gdf_locs=gdf, name="dis", merge=merge)
        nr_dis_new = len(model.forcing["dis"].index)
        if nr_dis_new > nr_dis:
            app.gui.window.dialog_info(
                text="Added {} discharge points".format(nr_dis_new - nr_dis),
                title="Success",
            )
        else:
            app.gui.window.dialog_info(
                text="No new discharge points added",
                title="Failed",
            )
    except ValueError as e:
        app.gui.window.dialog_info(
            text=e.args[0],
            title="Error",
        )
        return

    # retrieve all discharge points as gdf from xarray
    gdf = model.forcing["dis"].vector.to_gdf()

    # get the last index of the gdf
    index = len(gdf.index) - 1

    app.map.layer["sfincs_hmt"].layer["discharge_points"].set_data(gdf, index)
    app.gui.setvar("sfincs_hmt", "active_discharge_point", index)
    update_list()


def add_discharge_point_on_map(*args):
    app.map.click_point(point_clicked)


def point_clicked(x, y):
    model = app.model["sfincs_hmt"].domain

    # create gdf from xy
    geometry = gpd.points_from_xy([x], [y])
    gdf = gpd.GeoDataFrame(geometry=geometry, crs=app.crs)

    if "dis" in model.forcing:
        # make sure new point gets an index that doesnt exist in model.forcing["bzs"]
        index = int(model.forcing["dis"].index[-1]) + 1
        # set index of gdf
        gdf.index = [index]

    add_discharge_point(gdf)


def load_from_file(*args):
    """ " Load discharge points from file"""
    fname = app.gui.window.dialog_open_file(
        "Select file with discharge points ...",
        filter="*.geojson *.shp",
    )
    if fname[0]:
        # for .pol files we assume that they are in the coordinate system of the current map
        gdf = app.model["sfincs_hmt"].domain.data_catalog.get_geodataframe(fname[0])
        gdf = gdf.to_crs(app.crs)

        add_discharge_point(gdf)


def select_discharge_point_from_list(*args):
    model = app.model["sfincs_hmt"].domain
    index = app.gui.getvar("sfincs_hmt", "active_discharge_point")

    # get maximum values of the model
    dis = model.forcing["dis"].values[:, index].max()
    app.gui.setvar("sfincs_hmt", "bc_dis_value", dis)

    app.map.layer["sfincs_hmt"].layer["discharge_points"].select_by_index(index)


def select_discharge_point_from_map(*args):
    model = app.model["sfincs_hmt"].domain

    index = args[0]["id"]
    app.gui.setvar("sfincs_hmt", "active_discharge_point", index)

    # get maximum values of the model
    dis = model.forcing["dis"].values[:, index].max()
    app.gui.setvar("sfincs_hmt", "bc_dis_value", dis)

    app.gui.window.update()


def delete_point_from_list(*args):
    model = app.model["sfincs_hmt"].domain
    index = app.gui.getvar("sfincs_hmt", "active_discharge_point")

    # delete point from model forcing
    model.forcing["dis"] = model.forcing["dis"].drop_isel(index=index)

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

    nr_points = 0
    if gdf is not None:
        # Loop through discharge points
        for index, row in gdf.iterrows():
            nr_points += 1
            # Get the name of the discharge point if present
            if "name" in row and not pd.isna(row["name"]):
                discharge_point_names.append(row["name"])
            else:
                discharge_point_names.append("Point {}".format(index))

    app.gui.setvar("sfincs_hmt", "discharge_point_names", discharge_point_names)
    app.gui.setvar("sfincs_hmt", "nr_discharge_points", nr_points)
    app.gui.window.update()


## Add timeseries to the boundary points


def add_constant_discharge(*args):
    """Add constant discahrge to the selected point."""
    index = app.gui.getvar("sfincs_hmt", "active_discharge_point")
    value = app.gui.getvar("sfincs_hmt", "bc_dis_value")

    # get the model
    model = app.model["sfincs_hmt"].domain
    # convert start and stop time to seconds
    tstart = model.config["tstart"]
    tstop = model.config["tstop"]

    # make constant timeseries
    duration = (tstop - tstart).total_seconds()
    tt = np.arange(0, duration + 1, duration)
    # values with same length as tt
    ts = value * np.ones(len(tt))

    # get forcing locations in the model
    gdf_locs = model.forcing["dis"].vector.to_gdf()
    model_index = gdf_locs.index[index]

    # convert to pandas dataframe
    df_ts = pd.DataFrame({model_index: ts}, index=tt)

    # replace the boundary condition of the selected point
    model.set_forcing_1d(df_ts=df_ts, name="dis")


def add_synthetical_discharge(*args):
    """Add a guassian shaped discharge (based on peak and tstart/tstop) to selected point"""
    index = app.gui.getvar("sfincs_hmt", "active_discharge_point")
    value = app.gui.getvar("sfincs_hmt", "bc_dis_value")

    # get the model
    model = app.model["sfincs_hmt"].domain
    # convert start and stop time to seconds
    tstart = model.config["tstart"]
    tstop = model.config["tstop"]

    # make timeseries with gaussian peak
    peak = value
    duration = (tstop - tstart).total_seconds()
    time_shift = 0.5 * duration  # shift the peak to the middle of the duration
    # TODO replace with: time_vec = pd.date_range(tstart, periods=duration / 600 + 1, freq="600S")
    tt = np.arange(0, duration + 1, 600)
    ts = peak * np.exp(-(((tt - time_shift) / (0.25 * duration)) ** 2))

    # get forcing locations in the model
    gdf_locs = model.forcing["dis"].vector.to_gdf()
    model_index = gdf_locs.index[index]

    # convert to pandas dataframe
    df_ts = pd.DataFrame({model_index: ts}, index=tt)

    # replace the boundary condition of the selected point
    model.set_forcing_1d(df_ts=df_ts, name="dis")


def copy_to_all(*args):
    """Copy the discharges of the selected station and copy to all boundary points."""
    index = app.gui.getvar("sfincs_hmt", "active_discharge_point")

    # get the model
    model = app.model["sfincs_hmt"].domain

    # get the boundary conditions of this point
    dis = model.forcing["dis"].isel(index=index)

    # copy the boundary conditions to all other points
    model.forcing["dis"][:] = dis
