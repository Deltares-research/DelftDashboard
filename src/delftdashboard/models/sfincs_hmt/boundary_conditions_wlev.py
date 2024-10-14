from datetime import datetime
import os
import geopandas as gpd
import numpy as np
import pandas as pd

from delftdashboard.app import app
from delftdashboard.operations import map
from delftdashboard.toolboxes.observation_stations.observation_stations import (
    Toolbox as ObservationStationsToolbox,
)

import cht_observations.observation_stations as cht_station


def select(*args):
    # Set all layer inactive, except boundary_points
    map.update()
    app.map.layer["sfincs_hmt"].layer["mask"].activate()
    app.map.layer["sfincs_hmt"].layer["boundary_points"].activate()
    update_list()


def generate_boundary_points_from_msk(*args):
    """Generate boundary points from mask and add to model and map."""
    model = app.model["sfincs_hmt"].domain

    if "bzs" in model.forcing:
        ok = app.gui.window.dialog_ok_cancel(
            text="Existing boundary points will be overwritten! Continue?",
            title="Warning",
        )
        if not ok:
            return

    # distance in meters
    distance = app.gui.getvar("sfincs_hmt", "bc_dist_along_msk")

    # merge = app.gui.getvar("sfincs_hmt", "merge_bc_wlev")
    model.setup_waterlevel_bnd_from_mask(distance=distance, merge=False)

    # retrieve all boundary points as gdf from xarray
    gdf = model.forcing["bzs"].vector.to_gdf()

    # Add to map and select first point
    app.map.layer["sfincs_hmt"].layer["boundary_points"].set_data(gdf, 0)
    app.gui.setvar("sfincs_hmt", "active_boundary_point", 0)
    update_list()


def add_boundary_point(gdf, merge=True):
    model = app.model["sfincs_hmt"].domain

    nr_bnd = 0
    if "bzs" in model.forcing:
        nr_bnd = len(model.forcing["bzs"].index)
    try:
        # add to existing boundary conditions
        model.set_forcing_1d(gdf_locs=gdf, name="bzs", merge=merge)
        nr_bnd_new = len(model.forcing["bzs"].index)
        if nr_bnd_new > nr_bnd:
            app.gui.window.dialog_info(
                text="Added {} boundary points".format(nr_bnd_new - nr_bnd),
                title="Success",
            )
        else:
            app.gui.window.dialog_info(
                text="No new boundary points added ...",
                title="Failed",
            )
            return
    except ValueError as e:
        app.gui.window.dialog_warning(
            text=e.args[0],
            title="Error",
        )
        return

    # retrieve all boundary points as gdf from xarray
    gdf = model.forcing["bzs"].vector.to_gdf()

    # get the last index of the gdf
    index = len(gdf.index) - 1

    app.map.layer["sfincs_hmt"].layer["boundary_points"].set_data(gdf, index)
    app.gui.setvar("sfincs_hmt", "active_boundary_point", index)
    update_list()


def add_boundary_point_on_map(*args):
    app.map.click_point(point_clicked)


def point_clicked(x, y):
    model = app.model["sfincs_hmt"].domain

    # create gdf from xy
    geometry = gpd.points_from_xy([x], [y])
    gdf = gpd.GeoDataFrame(geometry=geometry, crs=app.crs)

    if "bzs" in model.forcing:
        # make sure new point gets an index that doesnt exist in model.forcing["bzs"]
        index = int(model.forcing["bzs"].index[-1]) + 1
        # set index of gdf
        gdf.index = [index]

    add_boundary_point(gdf)


def load_from_file(*args):
    """ " Load boundary points from file"""
    fname = app.gui.window.dialog_open_file(
        "Select file with boundary points ...",
        filter="*.geojson *.shp",
    )
    if fname[0]:
        # for .pol files we assume that they are in the coordinate system of the current map
        gdf = app.model["sfincs_hmt"].domain.data_catalog.get_geodataframe(fname[0])
        gdf = gdf.to_crs(app.crs)

        add_boundary_point(gdf)


def select_boundary_point_from_list(*args):
    model = app.model["sfincs_hmt"].domain
    index = app.gui.getvar("sfincs_hmt", "active_boundary_point")

    # get maximum values of the model
    bzs = model.forcing["bzs"].values[:, index].max()
    app.gui.setvar("sfincs_hmt", "bc_wlev_value", bzs)

    app.map.layer["sfincs_hmt"].layer["boundary_points"].select_by_index(index)


def select_boundary_point_from_map(*args):
    model = app.model["sfincs_hmt"].domain

    index = args[0]["id"]
    app.gui.setvar("sfincs_hmt", "active_boundary_point", index)

    # get maximum values of the model
    # TODO change this for isel?
    bzs = model.forcing["bzs"].values[:, index].max()
    app.gui.setvar("sfincs_hmt", "bc_wlev_value", bzs)

    app.gui.window.update()


def delete_point_from_list(*args):
    model = app.model["sfincs_hmt"].domain
    index = app.gui.getvar("sfincs_hmt", "active_boundary_point")

    # delete point from model forcing
    model.forcing["bzs"] = model.forcing["bzs"].drop_isel(index=index)

    if len(model.forcing["bzs"].index) == 0:
        # if no points are left, drop the forcing
        model.forcing.pop("bzs")
        app.map.layer["sfincs_hmt"].layer["boundary_points"].clear()
    else:
        # convert to new gdf
        gdf = model.forcing["bzs"].vector.to_gdf()

        # set new index
        index = index - 1 if index > 0 else 0

        app.map.layer["sfincs_hmt"].layer["boundary_points"].set_data(gdf, index)
        app.gui.setvar("sfincs_hmt", "active_boundary_point", index)
    update_list()


def delete_all_points_from_list(*args):
    model = app.model["sfincs_hmt"].domain
    model.forcing.pop("bzs")
    app.map.layer["sfincs_hmt"].layer["boundary_points"].clear()
    update_list()


def update_list():
    # Get boundary points
    gdf = app.map.layer["sfincs_hmt"].layer["boundary_points"].data
    boundary_point_names = []

    nr_points = 0
    if gdf is not None:
        # Loop through boundary points
        for index, row in gdf.iterrows():
            nr_points += 1
            # Get the name of the boundary point if present
            if "name" in row and not pd.isna(row["name"]):
                boundary_point_names.append(row["name"])
            else:
                boundary_point_names.append("Point {}".format(index))

    app.gui.setvar("sfincs_hmt", "boundary_point_names", boundary_point_names)
    app.gui.setvar("sfincs_hmt", "nr_boundary_points", nr_points)
    app.gui.window.update()


def go_to_observation_stations(*args):
    """Go to observation stations toolbox in popup window."""

    toolbox_name = "observation_stations"
    toolbox_path = os.path.join(app.main_path, "toolboxes", toolbox_name)

    # initialize toolboxes
    toolbox = ObservationStationsToolbox(toolbox_name)

    data = {
        "map_center": app.map.map_center,
        "active_model": app.active_model,
        "toolbbox": toolbox,
        "option": "bnd",
    }

    # Read GUI config file
    pop_win_config_path = os.path.join(
        toolbox_path, "config", "observation_stations_popup.yml"
    )
    okay, data = app.gui.popup(
        pop_win_config_path, data=data, id="observation_stations"
    )


## Add timeseries to the boundary points


def add_constant_water_level(*args):
    """Add constant waterlevel to the selected point."""
    index = app.gui.getvar("sfincs_hmt", "active_boundary_point")
    value = app.gui.getvar("sfincs_hmt", "bc_wlev_value")

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
    gdf_locs = model.forcing["bzs"].vector.to_gdf()
    model_index = gdf_locs.index[index]

    # convert to pandas dataframe
    df_ts = pd.DataFrame({model_index: ts}, index=tt)

    # replace the boundary condition of the selected point
    model.set_forcing_1d(df_ts=df_ts, name="bzs")


def add_synthetical_water_level(*args):
    """Add a guassian shaped water level (based on peak and tstart/tstop) to selected point"""
    index = app.gui.getvar("sfincs_hmt", "active_boundary_point")
    value = app.gui.getvar("sfincs_hmt", "bc_wlev_value")

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
    gdf_locs = model.forcing["bzs"].vector.to_gdf()
    model_index = gdf_locs.index[index]

    # convert to pandas dataframe
    df_ts = pd.DataFrame({model_index: ts}, index=tt)

    # replace the boundary condition of the selected point
    model.set_forcing_1d(df_ts=df_ts, name="bzs")


def add_tidal_constituents():
    """Retrieve tidal constituents and save them in a .bca-file."""
    # TODO import cht_tide and generate bca-files
    # use bca-files to generate tidal water levels
    pass


def download_water_level(*args):
    """Download historical water levels from the API (if available) ..."""
    index = app.gui.getvar("sfincs_hmt", "active_boundary_point")

    # get the model
    model = app.model["sfincs_hmt"].domain

    # get the active station
    # get forcing locations in the model
    gdf_locs = model.forcing["bzs"].vector.to_gdf()
    model_index = gdf_locs.index[index]

    # check if source is available (for now only NOAA)
    if "source" in gdf_locs:
        source = gdf_locs.source[model_index]
    else:
        app.gui.window.dialog_info(
            text="No API available to retreive timeseries for this boundary point",
            title="Error",
        )
        return

    if source == "noaa_coops":
        # get the station_id
        station_id = gdf_locs.id[model_index]

        # convert start and stop time to seconds
        tstart = model.config["tstart"]
        tstop = model.config["tstop"]

        # Get NOAA data
        try:
            source = cht_station.source(source)
            df = source.get_data(station_id, tstart, tstop)
            df = pd.DataFrame(df)  # Convert series to dataframe
            df_ts = df.rename(columns={"v": model_index})

            # replace the boundary condition of the selected point
            model.set_forcing_1d(df_ts=df_ts, name="bzs")

            app.gui.window.dialog_info(
                text="Downloaded water level timeseries from NOAA for station {}".format(
                    station_id
                ),
                title="Success",
            )
            return
        except Exception as e:
            app.gui.window.dialog_info(
                text=e.args[0],
                title="Error",
            )
            return
    else:
        app.gui.window.dialog_info(
            text="No API available to retreive timeseries for this boundary point",
            title="Error",
        )
        return


def copy_to_all(*args):
    """Copy the water levels of the selected station and copy to all boundary points."""
    index = app.gui.getvar("sfincs_hmt", "active_boundary_point")

    # get the model
    model = app.model["sfincs_hmt"].domain

    # get the boundary conditions of this point
    bzs = model.forcing["bzs"].isel(index=index)

    # copy the boundary conditions to all other points
    model.forcing["bzs"][:] = bzs
