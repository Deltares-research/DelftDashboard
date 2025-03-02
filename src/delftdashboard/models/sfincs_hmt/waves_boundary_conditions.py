# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
# import shapely
# import pandas as pd
# import geopandas as gpd

from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args):
    # Set all layer inactive, except boundary_points
    map.update()
    app.map.layer["sfincs_hmt"].layer["boundary_points_snapwave"].activate()
    update_list()


def deselect(*args):
    if app.model["sfincs_hmt"].wave_boundaries_changed:
        ok = app.gui.window.dialog_yes_no(
            "The boundary conditions have changed. Would you like to save the changes?"
        )
        if ok:
            save()


def load(*args):
    """"""
    # Called by "Load" push button. Read both bnd and bzs files.
    map.reset_cursor()
    # bnd file
    rsp = app.gui.window.dialog_open_file(
        "Select file ...",
        file_name="snapwave.bnd",
        filter="*.bnd",
        allow_directory_change=False,
    )
    if rsp[0]:
        app.model["sfincs_hmt"].domain.input.variables.snapwave_bndfile = rsp[
            2
        ]  # file name without path
    else:
        # User pressed cancel
        return
    rsp = app.gui.window.dialog_open_file(
        "Select file ...",
        file_name="sfincs.bhs",
        filter="*.bhs",
        allow_directory_change=False,
    )
    if rsp[0]:
        app.model["sfincs_hmt"].domain.input.variables.snapwave_bhsfile = rsp[
            2
        ]  # file name without path
        read_bhs_file = True
    else:
        # User pressed cancel. Do not read bzs file, but initialize boundary conditions anyway.
        read_bhs_file = False

    # Read boundary points from bnd file
    app.model["sfincs_hmt"].domain.snapwave_boundary_conditions.read_boundary_points()

    if read_bhs_file:
        # Read boundary conditions from bhs file
        app.model[
            "sfincs_hmt"
        ].domain.snapwave_boundary_conditions.read_boundary_conditions_timeseries()
    else:
        # Set uniform conditions
        pass
        # set_boundary_conditions()

    # Add boundary points to map
    gdf = app.model["sfincs_hmt"].domain.snapwave_boundary_conditions.gdf
    app.map.layer["sfincs_hmt"].layer["boundary_points_snapwave"].set_data(gdf, 0)

    # Set active boundary point and update list
    app.gui.setvar("sfincs_hmt", "active_boundary_point_snapwave", 0)
    update_list()
    app.model["sfincs_hmt"].wave_boundaries_changed = False


def save(*args, **kwargs):
    map.reset_cursor()

    # Save both bnd and bzs files (not the bca file for now)

    bndfile = get_bnd_file_name()
    # bhsfile = get_bhs_file_name()

    # if bndfile is None or bhsfile is None:
    #     return

    app.model["sfincs_hmt"].domain.input.variables.snapwave_bndfile = (
        bndfile  # file name without path
    )
    app.gui.setvar("sfincs_hmt", "snapwave_bndfile", bndfile)

    # Write bnd and bhs files
    app.model["sfincs_hmt"].domain.snapwave_boundary_conditions.write_boundary_points()
    app.model[
        "sfincs_hmt"
    ].domain.snapwave_boundary_conditions.write_boundary_conditions_timeseries()
    app.model["sfincs_hmt"].wave_boundaries_changed = False


def add_boundary_point_on_map_snapwave(*args):
    app.map.click_point(point_clicked)


def point_clicked(x, y):
    # Point clicked on map. Add boundary point with constant water level.
    hs = app.gui.getvar("sfincs_hmt", "boundary_conditions_timeseries_hs_snapwave")
    tp = app.gui.getvar("sfincs_hmt", "boundary_conditions_timeseries_tp_snapwave")
    wd = app.gui.getvar("sfincs_hmt", "boundary_conditions_timeseries_wd_snapwave")
    ds = app.gui.getvar("sfincs_hmt", "boundary_conditions_timeseries_ds_snapwave")
    app.model["sfincs_hmt"].domain.snapwave_boundary_conditions.add_point(
        x=x, y=y, hs=hs, tp=tp, wd=wd, ds=ds
    )
    index = len(app.model["sfincs_hmt"].domain.snapwave_boundary_conditions.gdf) - 1
    gdf = app.model["sfincs_hmt"].domain.snapwave_boundary_conditions.gdf
    app.map.layer["sfincs_hmt"].layer["boundary_points_snapwave"].set_data(gdf, index)
    app.gui.setvar("sfincs_hmt", "active_boundary_point_snapwave", index)
    update_list()
    app.model["sfincs_hmt"].wave_boundaries_changed = True


def select_boundary_point_from_list_snapwave(*args):
    index = app.gui.getvar("sfincs_hmt", "active_boundary_point_snapwave")
    app.map.layer["sfincs_hmt"].layer["boundary_points_snapwave"].select_by_index(index)


def select_boundary_point_from_map_snapwave(*args):
    index = args[0]["id"]
    app.gui.setvar("sfincs_hmt", "active_boundary_point_snapwave", index)
    app.gui.window.update()


def delete_point_from_list_snapwave(*args):
    index = app.gui.getvar("sfincs_hmt", "active_boundary_point_snapwave")
    app.model["sfincs_hmt"].domain.snapwave_boundary_conditions.delete_point(index)
    gdf = app.model["sfincs_hmt"].domain.snapwave_boundary_conditions.gdf
    index = max(min(index, len(gdf) - 1), 0)
    app.map.layer["sfincs_hmt"].layer["boundary_points_snapwave"].set_data(gdf, index)
    app.gui.setvar("sfincs_hmt", "active_boundary_point_snapwave", index)
    update_list()
    app.model["sfincs_hmt"].wave_boundaries_changed = True


def update_list():
    # Update boundary point names
    nr_boundary_points = len(
        app.model["sfincs_hmt"].domain.snapwave_boundary_conditions.gdf
    )
    boundary_point_names = []
    # Loop through boundary points
    for index, row in app.model[
        "sfincs_hmt"
    ].domain.snapwave_boundary_conditions.gdf.iterrows():
        boundary_point_names.append(row["name"])
    app.gui.setvar("sfincs_hmt", "boundary_point_names_snapwave", boundary_point_names)
    app.gui.setvar("sfincs_hmt", "nr_boundary_points_snapwave", nr_boundary_points)
    app.gui.window.update()


def set_boundary_conditions_snapwave(*args):
    """Set boundary conditions based on the values in the GUI"""
    dlg = app.gui.window.dialog_wait("Generating boundary conditions ...")

    shape = app.gui.getvar(
        "sfincs_hmt", "boundary_conditions_timeseries_shape_snapwave"
    )
    timestep = app.gui.getvar(
        "sfincs_hmt", "boundary_conditions_timeseries_time_step_snapwave"
    )
    hs = app.gui.getvar("sfincs_hmt", "boundary_conditions_timeseries_hs_snapwave")
    tp = app.gui.getvar("sfincs_hmt", "boundary_conditions_timeseries_tp_snapwave")
    wd = app.gui.getvar("sfincs_hmt", "boundary_conditions_timeseries_wd_snapwave")
    ds = app.gui.getvar("sfincs_hmt", "boundary_conditions_timeseries_ds_snapwave")
    app.model["sfincs_hmt"].domain.snapwave_boundary_conditions.set_timeseries(
        shape="constant", hs=hs, tp=tp, wd=wd, ds=ds
    )
    dlg.close()

    # Save the bzs file
    app.model[
        "sfincs_hmt"
    ].domain.snapwave_boundary_conditions.write_boundary_conditions_timeseries()
    app.model["sfincs_hmt"].wave_boundaries_changed = False


def view_boundary_conditions_snapwave(*args):
    print("Viewing boundary conditions not implemented yet")


def create_boundary_points_snapwave(*args):

    # First check if there are already boundary points
    if len(app.model["sfincs_hmt"].domain.snapwave_boundary_conditions.gdf.index) > 0:
        ok = app.gui.window.dialog_ok_cancel(
            "Existing boundary points will be overwritten! Continue?", title="Warning"
        )
        if not ok:
            return
    # Check for open boundary points in mask
    mask = app.model["sfincs_hmt"].domain.quadtree_grid.data["snapwave_mask"]
    if mask is None:
        ok = app.gui.window.dialog_info(
            "Please first create a mask for this domain.", title=" "
        )
        return
    if not app.model["sfincs_hmt"].domain.snapwave.mask.has_open_boundaries():
        ok = app.gui.window.dialog_info(
            "The mask for this domain does not have any open boundary points !",
            title=" ",
        )
        return

    bndfile = get_bnd_file_name()
    if bndfile is None:
        return

    # Create points from mask
    bnd_dist = app.gui.getvar("sfincs_hmt", "boundary_dx_snapwave")
    app.model[
        "sfincs_hmt"
    ].domain.snapwave_boundary_conditions.get_boundary_points_from_mask(
        bnd_dist=bnd_dist
    )
    gdf = app.model["sfincs_hmt"].domain.snapwave_boundary_conditions.gdf
    if len(gdf) == 0:
        app.gui.window.dialog_info(
            "No boundary points found in mask. Please check mask settings.",
            title="Warning",
        )
        return

    app.map.layer["sfincs_hmt"].layer["boundary_points_snapwave"].set_data(gdf, 0)
    # Set uniform conditions
    app.gui.setvar(
        "sfincs_hmt", "boundary_conditions_timeseries_shape_snapwave", "constant"
    )

    # Write bnd file
    app.model["sfincs_hmt"].domain.input.variables.snapwave_bndfile = (
        bndfile  # file name without path
    )
    app.gui.setvar("sfincs_hmt", "snapwave_bndfile", bndfile)
    app.model["sfincs_hmt"].domain.snapwave_boundary_conditions.write_boundary_points()

    set_boundary_conditions_snapwave()

    app.gui.setvar("sfincs_hmt", "active_boundary_point_snapwave", 0)
    update_list()


def get_bnd_file_name(*args):
    filename = app.model["sfincs_hmt"].domain.input.variables.snapwave_bndfile
    if not filename:
        filename = "snapwave.bnd"
    rsp = app.gui.window.dialog_save_file(
        "Select file ...",
        file_name=filename,
        filter="*.bnd",
        allow_directory_change=False,
    )
    if rsp[0]:
        return rsp[2]
    else:
        # User pressed cancel
        return None


def get_bhs_file_name(*args):
    filename = app.model["sfincs_hmt"].domain.input.variables.bhsfile
    if not filename:
        filename = "sfincs.bhs"
    rsp = app.gui.window.dialog_save_file(
        "Select file ...",
        file_name=filename,
        filter="*.bhs",
        allow_directory_change=False,
    )
    if rsp[0]:
        return rsp[2]
    else:
        # User pressed cancel
        return None
