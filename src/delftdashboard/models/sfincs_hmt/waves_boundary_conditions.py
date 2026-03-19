# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
# import shapely
# import pandas as pd
# import geopandas as gpd

import os

from delftdashboard.app import app
from delftdashboard.operations import map

def select(*args):
    # Set all layer inactive, except boundary_points
    map.update()
    app.map.layer["sfincs_hmt"].layer["boundary_points_snapwave"].activate()
    update_list()

def deselect(*args):
    if app.model["sfincs_hmt"].wave_boundaries_changed:
        ok = app.gui.window.dialog_yes_no("The boundary conditions have changed. Would you like to save the changes?")
        if ok:
            save()

def load(*args):
    """"""
    # Called by "Load" push button. Read both bnd and time series files.
    map.reset_cursor()
    # bnd file
    rsp = app.gui.window.dialog_open_file("Select file ...",
                                          file_name="snapwave.bnd",
                                          filter="*.bnd",
                                          allow_directory_change=False)
    if rsp[0]:
        app.model["sfincs_hmt"].domain.config.set("snapwave_bndfile", rsp[2])
    else:
        # User pressed cancel
        return
    
    # Check if current time series file is netcdf or ascii, and set filter accordingly
    current_bhsfile = app.model["sfincs_hmt"].domain.config.get("snapwave_bhsfile")
    current_ncfile = app.model["sfincs_hmt"].domain.config.get("netsnapwavefile")

    if current_bhsfile:
        # ASCII
        current_file = current_bhsfile
    elif current_ncfile:
        # NetCDF
        current_file = current_ncfile
    else:
        # No current file, set default filter
        current_file = None

    rsp = app.gui.window.dialog_open_file("Select file ...",
                                          file_name=current_file,
                                          filter="*.bhs;*.nc",
                                          allow_directory_change=False)
    if rsp[0]:

        # Determine if selected file is netcdf or ascii
        if rsp[2].endswith(".bhs"):
            # ASCII
            root, ext = os.path.splitext(rsp[2])            
            app.model["sfincs_hmt"].domain.config.set("snapwave_bhsfile", rsp[2])
            app.model["sfincs_hmt"].domain.config.set("snapwave_btpfile", root + ".btp")
            app.model["sfincs_hmt"].domain.config.set("snapwave_bwdfile", root + ".bwd")
            app.model["sfincs_hmt"].domain.config.set("snapwave_bdsfile", root + ".bds")
            app.model["sfincs_hmt"].domain.config.set("netsnapwavefile", None)

        elif rsp[2].endswith(".nc"):
            # NetCDF
            app.model["sfincs_hmt"].domain.config.set("snapwave_bhsfile", None)
            app.model["sfincs_hmt"].domain.config.set("snapwave_btpfile", None)
            app.model["sfincs_hmt"].domain.config.set("snapwave_bwdfile", None)
            app.model["sfincs_hmt"].domain.config.set("snapwave_bdsfile", None)
            app.model["sfincs_hmt"].domain.config.set("netsnapwavefile", rsp[2])

        read_bhs_file = True

    else:

        # User pressed cancel. Do not read bzs file, but initialize boundary conditions anyway.
        read_bhs_file = False

    # Read boundary conditions
    app.model["sfincs_hmt"].domain.snapwave_boundary_conditions.read()

    if read_bhs_file:
        # Read boundary conditions from bzs file
        app.model["sfincs_hmt"].wave_boundaries_changed = False
    else:
        # Set uniform conditions
        set_uniform_conditions()
        app.model["sfincs_hmt"].wave_boundaries_changed = True

    # Add boundary points to map
    gdf = app.model["sfincs_hmt"].domain.snapwave_boundary_conditions.gdf
    app.map.layer["sfincs_hmt"].layer["boundary_points_snapwave"].set_data(gdf, 0)

    # Set active boundary point and update list
    app.gui.setvar("sfincs_hmt", "active_boundary_point_snapwave", 0)
    update_list()

def save(*args, **kwargs):

    map.reset_cursor()

    # Save all files (bnd, bhs, btp, etc) related to boundary conditions

    bndfile = get_bnd_file_name()
    if bndfile is None:
        # User pressed cancel
        return
    
    bcfile = get_bhs_file_name()
    if bcfile is None:
        # User pressed cancel
        return
    
    # Write bnd files
    app.model["sfincs_hmt"].domain.snapwave_boundary_conditions.write_boundary_points()
    app.model["sfincs_hmt"].domain.config.set("snapwave_bndfile", bndfile)
    app.gui.setvar("sfincs_hmt", "snapwave_bndfile", bndfile)

    # And now the time series

    # Get the file extension
    if bcfile.endswith(".bhs"):
        frmt = "ascii"
    elif bcfile.endswith(".nc"):
        frmt = "netcdf"
    else:
        app.gui.window.dialog_info("Unsupported file format for time series file. Please select a .bhs or .nc file.", title="Error")
        return

    # Get the root name of the time series file (without path and extension) to use for the other files
    bc_root = os.path.splitext(os.path.basename(bcfile))[0]

    if frmt == "ascii":

        app.model["sfincs_hmt"].domain.config.set("snapwave_bhsfile", bc_root + ".bhs")
        app.model["sfincs_hmt"].domain.config.set("snapwave_btpfile", bc_root + ".btp")
        app.model["sfincs_hmt"].domain.config.set("snapwave_bwdfile", bc_root + ".bwd")
        app.model["sfincs_hmt"].domain.config.set("snapwave_bdsfile", bc_root + ".bds")

        app.model["sfincs_hmt"].domain.config.set("netsnapwavefile", None)

        app.model["sfincs_hmt"].domain.snapwave_boundary_conditions.write_boundary_conditions_timeseries_all()

    else:

        app.model["sfincs_hmt"].domain.snapwave_boundary_conditions.write_boundary_conditions_netcdf()

        app.model["sfincs_hmt"].domain.config.set("netsnapwavefile", bcfile)

        app.model["sfincs_hmt"].domain.config.set("snapwave_bhsfile", None)
        app.model["sfincs_hmt"].domain.config.set("snapwave_btpfile", None)
        app.model["sfincs_hmt"].domain.config.set("snapwave_bwdfile", None)
        app.model["sfincs_hmt"].domain.config.set("snapwave_bdsfile", None)

    app.model["sfincs_hmt"].wave_boundaries_changed = False

def add_boundary_point_on_map_snapwave(*args):
    app.map.click_point(point_clicked)

def point_clicked(x, y):
    # Point clicked on map. Add boundary point with constant wave conditions.
    app.model["sfincs_hmt"].domain.snapwave_boundary_conditions.add_point(x, y)
    index = len(app.model["sfincs_hmt"].domain.snapwave_boundary_conditions.gdf) - 1
    set_uniform_conditions(index=index)
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
    app.model["sfincs_hmt"].domain.snapwave_boundary_conditions.delete(index)
    gdf = app.model["sfincs_hmt"].domain.snapwave_boundary_conditions.gdf
    index = max(min(index, len(gdf) - 1), 0)
    app.map.layer["sfincs_hmt"].layer["boundary_points_snapwave"].set_data(gdf, index)
    app.gui.setvar("sfincs_hmt", "active_boundary_point_snapwave", index)
    update_list()
    app.model["sfincs_hmt"].wave_boundaries_changed = True

def update_list():
    # Update boundary point names
    nr_boundary_points = app.model["sfincs_hmt"].domain.snapwave_boundary_conditions.nr_points
    boundary_point_names = app.model["sfincs_hmt"].domain.snapwave_boundary_conditions.list_names
    # # Loop through boundary points
    # for index, row in app.model["sfincs_hmt"].domain.snapwave_boundary_conditions.gdf.iterrows():
    #     boundary_point_names.append(row["name"])
    app.gui.setvar("sfincs_hmt", "boundary_point_names_snapwave", boundary_point_names)
    app.gui.setvar("sfincs_hmt", "nr_boundary_points_snapwave", nr_boundary_points)
    app.gui.window.update()

def set_boundary_conditions_snapwave(*args):
    """Callback to set boundary conditions for ALL points based on the values in the GUI"""
    set_uniform_conditions()
    app.model["sfincs_hmt"].wave_boundaries_changed = True

def set_uniform_conditions(index=None):
    """Set uniform boundary conditions for the given index (or all if index is None) based on the values in the GUI"""
    hm0 = app.gui.getvar("sfincs_hmt", "boundary_conditions_timeseries_hm0_snapwave")
    tp  = app.gui.getvar("sfincs_hmt", "boundary_conditions_timeseries_tp_snapwave")
    wd  = app.gui.getvar("sfincs_hmt", "boundary_conditions_timeseries_wd_snapwave")
    ds  = app.gui.getvar("sfincs_hmt", "boundary_conditions_timeseries_ds_snapwave")
    app.model["sfincs_hmt"].domain.snapwave_boundary_conditions.set_uniform_conditions(hm0, tp, wd, ds, index=index)

def view_boundary_conditions_snapwave(*args):
    print("Viewing boundary conditions not implemented yet")    

def create_boundary_points_snapwave(*args):
    
    # First check if there are already boundary points
    if app.model["sfincs_hmt"].domain.snapwave_boundary_conditions.nr_points > 0:
        ok = app.gui.window.dialog_ok_cancel("Existing boundary points will be overwritten! Continue?",                                
                                    title="Warning")
        if not ok:
            return
    # Check for open boundary points in mask
    mask = app.model["sfincs_hmt"].domain.quadtree_grid.data["snapwave_mask"]
    if mask is None:
        ok = app.gui.window.dialog_info("Please first create a mask for this domain.",                                
                                    title=" ")
        return
    if not app.model["sfincs_hmt"].domain.quadtree_snapwave_mask.has_open_boundaries:
        ok = app.gui.window.dialog_info("The mask for this domain does not have any open boundary points !",                                
                                    title=" ")
        return

    bndfile = get_bnd_file_name()
    if bndfile is None:
        return

    # Create points from mask
    bnd_dist = app.gui.getvar("sfincs_hmt", "boundary_dx_snapwave")
    # Use old "cht_sfincs" method for now.
    app.model["sfincs_hmt"].domain.snapwave_boundary_conditions.create_boundary_points_from_mask(bnd_dist=bnd_dist)
    gdf = app.model["sfincs_hmt"].domain.snapwave_boundary_conditions.gdf
    if app.model["sfincs_hmt"].domain.snapwave_boundary_conditions.nr_points == 0:
        app.gui.window.dialog_info("No boundary points found in mask. Please check mask settings.", title="Warning")        
        return
    
    app.map.layer["sfincs_hmt"].layer["boundary_points_snapwave"].set_data(gdf, 0)
    # # Set uniform conditions
    # app.gui.setvar("sfincs_hmt", "boundary_conditions_timeseries_shape_snapwave", "constant")

    # Set uniform conditions
    set_boundary_conditions_snapwave()

    # And save everything
    save()

    # # Write bnd file
    # app.model["sfincs_hmt"].domain.config.set(["snapwave_bndfile"], bndfile) # file name without path
    # app.gui.setvar("sfincs_hmt", "snapwave_bndfile", bndfile)
    # app.model["sfincs_hmt"].domain.snapwave_boundary_conditions.write_boundary_points()

    app.gui.setvar("sfincs_hmt", "active_boundary_point_snapwave", 0)
    update_list()

def get_bnd_file_name(*args):
    filename = app.model["sfincs_hmt"].domain.config.get("snapwave_bndfile")
    if not filename:
        filename = "snapwave.bnd"
    rsp = app.gui.window.dialog_save_file("Select file ...",
                                        file_name=filename,
                                        filter="*.bnd",
                                        allow_directory_change=False)
    if rsp[0]:
        return rsp[2]
    else:
        # User pressed cancel
        return None

def get_bhs_file_name(*args):
    filename = app.model["sfincs_hmt"].domain.config.get("snapwave_bhsfile")
    if not filename:
        filename = "snapwave.bhs"
    rsp = app.gui.window.dialog_save_file("Select file ...",
                                        file_name=filename,
                                        filter="*.bhs;*.nc",
                                        allow_directory_change=False)
    if rsp[0]:
        return rsp[2]
    else:
        # User pressed cancel
        return None
