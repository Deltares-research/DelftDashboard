import os
import geopandas as gpd

from delftdashboard.app import app
from delftdashboard.operations import map
from delftdashboard.toolboxes.observation_stations.observation_stations import Toolbox as ObservationStationsToolbox

def select(*args):
    # Set all layer inactive, except boundary_points
    map.update()
    app.map.layer["sfincs_hmt"].layer["mask"].activate()
    app.map.layer["sfincs_hmt"].layer["boundary_points"].activate()
    update_list()

def generate_boundary_points_from_msk():
    """Generate boundary points from mask and add to model and map."""
    model = app.model["sfincs_hmt"].domain

    if "bzs" in model.forcing:
        ok = app.gui.window.dialog_ok_cancel(
            text = "Existing boundary points will be overwritten! Continue?",                                
            title="Warning"
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
        app.gui.window.dialog_info(
            text=e.args[0],
            title="Error",
        )
        return

    # retrieve all boundary points as gdf from xarray
    gdf = model.forcing["bzs"].vector.to_gdf()

    # get the last index of the gdf
    index = int(gdf.index[-1])

    app.map.layer["sfincs_hmt"].layer["boundary_points"].set_data(gdf, index)
    app.gui.setvar("sfincs_hmt", "active_boundary_point", index)
    update_list()


def add_boundary_point_on_map(*args):
    app.map.click_point(point_clicked)


def point_clicked(x, y):
    # Add point to boundary conditions
    model = app.model["sfincs_hmt"].domain

    # create gdf from xy
    geometry = gpd.points_from_xy([x], [y])
    gdf = gpd.GeoDataFrame(geometry=geometry, crs=app.crs)

    if "bzs" in model.forcing:
        # make sure new point gets an index that doesnt exist in model.forcing["bzs"]
        index = int(model.forcing["bzs"].index[-1]) + 1
        # set index of gdf
        gdf.index = [index]

    # add to existing boundary conditions
    model.set_forcing_1d(gdf_locs=gdf, name="bzs", merge=True)

    # retrieve all boundary points as gdf from xarray
    gdf = model.forcing["bzs"].vector.to_gdf()

    # get the last index of the gdf
    index = int(gdf.index[-1])

    app.map.layer["sfincs_hmt"].layer["boundary_points"].set_data(gdf, index)
    app.gui.setvar("sfincs_hmt", "active_boundary_point", index)
    update_list()


def select_boundary_point_from_list(*args):
    index = app.gui.getvar("sfincs_hmt", "active_boundary_point")
    app.map.layer["sfincs_hmt"].layer["boundary_points"].select_by_index(index)


def select_boundary_point_from_map(*args):
    index = args[0]["id"]
    app.gui.setvar("sfincs_hmt", "active_boundary_point", index)
    app.gui.window.update()


def delete_point_from_list(*args):
    model = app.model["sfincs_hmt"].domain
    index = app.gui.getvar("sfincs_hmt", "active_boundary_point")

    # delete point from model forcing
    model.forcing["bzs"] = model.forcing["bzs"].drop_sel(index=index)

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

    if gdf is None:
        index = 0
    else:
        # Loop through boundary points
        for index, row in gdf.iterrows():
            # Get the name of the boundary point if present
            if "name" in row:
                boundary_point_names.append(row["name"])
            else:
                boundary_point_names.append("Point {}".format(index))

    app.gui.setvar("sfincs_hmt", "boundary_point_names", boundary_point_names)
    app.gui.setvar("sfincs_hmt", "nr_boundary_points", index)
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
    pop_win_config_path  = os.path.join(toolbox_path,"config", "observation_stations_popup.yml")
    okay, data = app.gui.popup(
        pop_win_config_path, data=data, id="observation_stations"
    )    