import shapely
import pandas as pd
import geopandas as gpd

from delftdashboard.app import app
from delftdashboard.operations import map

def select(*args):
    # Set all layer inactive, except boundary_points
    map.update()
    app.map.layer["sfincs_hmt"].layer["boundary_points"].set_mode("active")
    app.map.layer["sfincs_hmt"].layer["mask_active"].set_mode("active")
    app.map.layer["sfincs_hmt"].layer["mask_bound_wlev"].set_mode("active")
    app.map.layer["sfincs_hmt"].layer["mask_bound_outflow"].set_mode("active")
    update_list()

def generate_boundary_points_from_msk(*args):
    model = app.model["sfincs_hmt"].domain

    distance = app.gui.getvar("sfincs_hmt", "bc_dist_along_msk")
    merge = app.gui.getvar("sfincs_hmt", "merge_bc_wlev")
    model.setup_waterlevel_bnd_from_mask(distance=distance, merge=merge)


def add_boundary_point_on_map(*args):
    app.map.click_point(point_clicked)


def point_clicked(x,y):
    # Add point to boundary conditions
    model = app.model["sfincs_hmt"].domain

    # create gdf from xy
    geometry = gpd.points_from_xy([x], [y])
    gdf = gpd.GeoDataFrame(geometry=geometry, crs=app.crs)

    # add to existing boundary conditions
    model.set_forcing_1d(gdf_locs=gdf, name="bzs", merge=True)

    # retrieve all boundary points as gdf from xarray
    gdf = model.forcing["bzs"]

    index = len(model.forcing["bzs"].index)

    app.map.layer["sfincs_hmt"].layer["boundary_points"].set_data(gdf, index)
    app.gui.setvar("sfincs_hmt", "active_boundary_point", index)
    update_list()


def select_boundary_point_from_list(*args):
    index = app.gui.getvar("sfincs_hmt", "active_boundary_point")
    app.map.layer["sfincs_hmt"].layer["boundary_points"].set_selected_index(index)


def select_boundary_point_from_map(*args):
    index = args[0]["id"]
    app.gui.setvar("sfincs_hmt", "active_boundary_point", index)
    map.update()


def delete_point_from_list(*args):
    index = app.gui.getvar("sfincs_hmt", "active_boundary_point")
    app.model["sfincs_hmt"].domain.boundary_conditions.delete_point(index)
    gdf = app.model["sfincs_hmt"].domain.boundary_conditions.gdf.drop(
        ["timeseries"], axis=1
    )
    index = max(min(index, len(gdf) - 1), 0)
    app.map.layer["sfincs_hmt"].layer["boundary_points"].set_data(gdf, index)
    app.gui.setvar("sfincs_hmt", "active_boundary_point", index)
    update_list()


def update_list():
    # Update boundary point names
    nr_boundary_points = len(app.model["sfincs_hmt"].domain.boundary_conditions.gdf)
    boundary_point_names = []
    # Loop through boundary points
    for index, row in app.model["sfincs_hmt"].domain.boundary_conditions.gdf.iterrows():
        boundary_point_names.append(row["name"])
    app.gui.setvar("sfincs_hmt", "boundary_point_names", boundary_point_names)
    app.gui.setvar("sfincs_hmt", "nr_boundary_points", nr_boundary_points)
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
