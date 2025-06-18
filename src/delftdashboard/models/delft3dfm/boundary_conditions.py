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
from pathlib import Path
from delftdashboard.misc.gdfutils import mline2point

def select(*args):
    # Set all layer inactive, except boundary_points
    map.update()
    app.map.layer["delft3dfm"].layer["boundary_line"].activate()
    app.map.layer["delft3dfm"].layer["grid"].activate()
    # update_list()

def deselect(*args):
    if app.model["delft3dfm"].boundaries_changed:
        ok = app.gui.window.dialog_yes_no("The boundary conditions have changed. Would you like to save the changes?")
        if ok:
            save()
        else:
            app.model["delft3dfm"].boundaries_changed = False

# def load(*args):
#     """"""
#     # Called by "Load" push button. Read both bnd and bzs files.
#     map.reset_cursor()
#     # bnd file
#     rsp = app.gui.window.dialog_open_file("Select file ...",
#                                           file_name="sfincs.bnd",
#                                           filter="*.bnd",
#                                           allow_directory_change=False)
#     if rsp[0]:
#         app.model["delft3dfm"].domain.input.variables.bndfile = rsp[2] # file name without path
#     else:
#         # User pressed cancel
#         return
#     rsp = app.gui.window.dialog_open_file("Select file ...",
#                                           file_name="sfincs.bzs",
#                                           filter="*.bzs",
#                                           allow_directory_change=False)
#     if rsp[0]:
#         app.model["delft3dfm"].domain.input.variables.bzsfile = rsp[2] # file name without path
#         read_bzs_file = True
#     else:
#         # User pressed cancel. Do not read bzs file, but initialize boundary conditions anyway.
#         read_bzs_file = False

#     # Read boundary points from bnd file
#     app.model["delft3dfm"].domain.boundary_conditions.read_boundary_points()

#     if read_bzs_file:
#         # Read boundary conditions from bzs file
#         app.model["delft3dfm"].domain.boundary_conditions.read_boundary_conditions_timeseries()
#     else:
#         # Set uniform conditions
#         set_boundary_conditions()

#     # Add boundary points to map
#     gdf = app.model["delft3dfm"].domain.boundary_conditions.gdf
#     app.map.layer["delft3dfm"].layer["boundary_points"].set_data(gdf, 0)

#     # Set active boundary point and update list
#     app.gui.setvar("delft3dfm", "active_boundary_point", 0)
#     update_list()
#     app.model["delft3dfm"].boundaries_changed = False

# def save(*args, **kwargs):
#     map.reset_cursor()

#     # Save both bnd and bzs files (not the bca file for now)

#     bndfile = get_bnd_file_name()
#     bzsfile = get_bzs_file_name()

#     if bndfile is None or bzsfile is None:
#         return

#     app.model["delft3dfm"].domain.input.variables.bndfile = bndfile # file name without path
#     app.model["delft3dfm"].domain.input.variables.bzsfile = bzsfile # file name without path
#     app.gui.setvar("delft3dfm", "bndfile", bndfile)
#     app.gui.setvar("delft3dfm", "bzsfile", bzsfile)

#     # # bca file
#     # filename = app.model["delft3dfm"].domain.input.variables.bcafile
#     # if not filename:
#     #     filename = "sfincs.bca"

#     # Bca is already saved when generating boundary conditions from tide model.
#     # However, if points were added or removed, the astro components should be generated again. But we're not doing that now. Maybe later.
#     if app.model["delft3dfm"].domain.input.variables.bcafile is not None:
#         astro_okay = True
#         for index, row in app.model["delft3dfm"].domain.boundary_conditions.gdf.iterrows():
#             if len(row["astro"]) == 0:
#                 astro_okay = False
#                 break
#         if not astro_okay:
#             # Give warning
#             app.gui.window.dialog_info("Astronomical constituents are missing in some points. You'll need to generate them again to avoid possible errors.", title="Warning")

#     # Write bnd and bzs files
#     app.model["delft3dfm"].domain.boundary_conditions.write_boundary_points()
#     app.model["delft3dfm"].domain.boundary_conditions.write_boundary_conditions_timeseries()
#     app.model["delft3dfm"].boundaries_changed = False


# def add_boundary_point_on_map(*args):
#     app.map.click_point(point_clicked)

# def point_clicked(x, y):
#     # Point clicked on map. Add boundary point with constant water level.
#     wl = app.gui.getvar("delft3dfm", "boundary_conditions_timeseries_offset")
#     app.model["delft3dfm"].domain.boundary_conditions.add_point(x, y, wl=wl)
#     index = len(app.model["delft3dfm"].domain.boundary_conditions.gdf) - 1
#     gdf = app.model["delft3dfm"].domain.boundary_conditions.gdf
#     app.map.layer["delft3dfm"].layer["boundary_points"].set_data(gdf, index)
#     app.gui.setvar("delft3dfm", "active_boundary_point", index)
#     update_list()
#     app.model["delft3dfm"].boundaries_changed = True

# def select_boundary_point_from_list(*args):
#     index = app.gui.getvar("delft3dfm", "active_boundary_point")
#     app.map.layer["delft3dfm"].layer["boundary_points"].select_by_index(index)

# def select_boundary_point_from_map(*args):
#     index = args[0]["id"]
#     app.gui.setvar("delft3dfm", "active_boundary_point", index)
#     app.gui.window.update()

# def delete_point_from_list(*args):
#     index = app.gui.getvar("delft3dfm", "active_boundary_point")
#     app.model["delft3dfm"].domain.boundary_conditions.delete_point(index)
#     gdf = app.model["delft3dfm"].domain.boundary_conditions.gdf
#     index = max(min(index, len(gdf) - 1), 0)
#     app.map.layer["delft3dfm"].layer["boundary_points"].set_data(gdf, index)
#     app.gui.setvar("delft3dfm", "active_boundary_point", index)
#     update_list()
#     app.model["delft3dfm"].boundaries_changed = True

# def update_list():
#     # Update boundary point names
#     nr_boundary_points = len(app.model["delft3dfm"].domain.boundary_conditions.gdf)
#     boundary_point_names = []
#     # Loop through boundary points
#     for index, row in app.model["delft3dfm"].domain.boundary_conditions.gdf.iterrows():
#         boundary_point_names.append(row["name"])
#     app.gui.setvar("delft3dfm", "boundary_point_names", boundary_point_names)
#     app.gui.setvar("delft3dfm", "nr_boundary_points", nr_boundary_points)
#     app.gui.window.update()

def generate_boundary_conditions_from_tide_model(*args):

    map.reset_cursor()
    rsp = app.gui.window.dialog_save_file("Select bc file file ...",
                                          file_name='bc_new.ext',
                                          filter = None,
                                          allow_directory_change=False)
    if rsp[0]:
        tide_model_name = app.gui.getvar("delft3dfm", "boundary_conditions_tide_model")
        gdf = app.model["delft3dfm"].domain.boundary_conditions.gdf
        gdf = mline2point(gdf) # convert line to points
        tide_model = app.tide_model_database.get_dataset(tide_model_name)
        app.model["delft3dfm"].domain.boundary_conditions.gdf_points = tide_model.get_data_on_points(gdf=gdf, crs=app.model["delft3dfm"].domain.crs, format="gdf", constituents="all")
        # app.model["delft3dfm"].domain.boundary_conditions.gdf = gdf

        # Save water level forcing file 
        app.model["delft3dfm"].domain.boundary_conditions.write_boundary_conditions_astro() # writes .bc file
    
        # Now save the external forcing file
        app.model["delft3dfm"].domain.boundary_conditions.write_ext_wl() # writes .bc file

        # ext_new= app.model["delft3dfm"].domain.boundary_conditions.generate_tide(tidemodel=tidemodel, ext_file_new= rsp[0])
        # app.model["delft3dfm"].domain.input.external_forcing.extforcefilenew = ext_new

        # app.model["delft3dfm"].domain.input.output.crsfile = [] # first clear obsfile list to add combined / new crs
        # app.model["delft3dfm"].domain.input.output.crsfile.append(ObservationCrossSectionModel())
        # app.model["delft3dfm"].domain.input.output.crsfile[0].filepath=Path(rsp[2]) # save all obs crss in 1 file

def generate_boundary_conditions_custom(*args):
    pass

    # # Ask for name of bca file
    # bcafile = get_bca_file_name()

    # if bcafile is None:
    #     return

    # app.model["delft3dfm"].domain.input.variables.bcafile = bcafile # file name without path
    # app.gui.setvar("delft3dfm", "bcafile", bcafile)

    # # Now interpolate tidal data to boundary points
    # tide_model_name = app.gui.getvar("delft3dfm", "boundary_conditions_tide_model")
    # gdf = app.model["delft3dfm"].domain.boundary_conditions.gdf
    # tide_model = app.tide_model_database.get_dataset(tide_model_name)
    # gdf = tide_model.get_data_on_points(gdf=gdf, crs=app.model["delft3dfm"].domain.crs, format="gdf", constituents="all")
    # app.model["delft3dfm"].domain.boundary_conditions.gdf = gdf

    # # Save bca file
    # app.model["delft3dfm"].domain.boundary_conditions.write_boundary_conditions_astro()
    # app.gui.setvar("delft3dfm", "boundary_conditions_timeseries_shape", "astronomical")

    # set_boundary_conditions() # This is where the bzs file gets saved

    # app.gui.window.update()

def set_model_variables(*args):
    # All variables will be set
    app.model["delft3dfm"].set_input_variables()

# def set_boundary_conditions(*args):
#     """Set boundary conditions based on the values in the GUI"""

#     bzsfile = get_bzs_file_name()
#     if bzsfile is None:
#         return

#     app.model["delft3dfm"].domain.input.variables.bzsfile = bzsfile # file name without path
#     app.gui.setvar("delft3dfm", "bzsfile", bzsfile)

#     dlg = app.gui.window.dialog_wait("Generating boundary conditions ...")

#     shape = app.gui.getvar("delft3dfm", "boundary_conditions_timeseries_shape")
#     timestep = app.gui.getvar("delft3dfm", "boundary_conditions_timeseries_time_step")
#     offset = app.gui.getvar("delft3dfm", "boundary_conditions_timeseries_offset")
#     amplitude = app.gui.getvar("delft3dfm", "boundary_conditions_timeseries_amplitude")
#     phase = app.gui.getvar("delft3dfm", "boundary_conditions_timeseries_phase")
#     period = app.gui.getvar("delft3dfm", "boundary_conditions_timeseries_period")
#     peak = app.gui.getvar("delft3dfm", "boundary_conditions_timeseries_peak")
#     tpeak = app.gui.getvar("delft3dfm", "boundary_conditions_timeseries_tpeak")
#     duration = app.gui.getvar("delft3dfm", "boundary_conditions_timeseries_duration")
#     app.model["delft3dfm"].domain.boundary_conditions.set_timeseries(shape=shape,
#                                                                       timestep=timestep,
#                                                                       offset=offset,
#                                                                       amplitude=amplitude,
#                                                                       phase=phase,
#                                                                       period=period,
#                                                                       peak=peak,
#                                                                       tpeak=tpeak,
#                                                                       duration=duration)
#     dlg.close()

#     # Save the bzs file
#     app.model["delft3dfm"].domain.boundary_conditions.write_boundary_conditions_timeseries()
#     app.model["delft3dfm"].boundaries_changed = False

# def view_boundary_conditions(*args):
#     print("Viewing boundary conditions not implemented yet")

# def create_boundary_points(*args):

#     # First check if there are already boundary points
#     if len(app.model["delft3dfm"].domain.boundary_conditions.gdf.index)>0:
#         ok = app.gui.window.dialog_ok_cancel("Existing boundary points will be overwritten! Continue?",
#                                     title="Warning")
#         if not ok:
#             return
#     # Check for open boundary points in mask
#     mask = app.model["delft3dfm"].domain.grid.data["mask"]
#     if mask is None:
#         ok = app.gui.window.dialog_info("Please first create a mask for this domain.",
#                                     title=" ")
#         return
#     if not app.model["delft3dfm"].domain.mask.has_open_boundaries():
#         ok = app.gui.window.dialog_info("The mask for this domain does not have any open boundary points !",
#                                     title=" ")
#         return

#     bndfile = get_bnd_file_name()
#     if bndfile is None:
#         return

#     # Create points from mask
#     bnd_dist = app.gui.getvar("delft3dfm", "boundary_dx")
#     app.model["delft3dfm"].domain.boundary_conditions.get_boundary_points_from_mask(bnd_dist=bnd_dist)
#     gdf = app.model["delft3dfm"].domain.boundary_conditions.gdf
#     if len(gdf) == 0:
#         app.gui.window.dialog_info("No boundary points found in mask. Please check mask settings.", title="Warning")
#         return

#     app.map.layer["delft3dfm"].layer["boundary_points"].set_data(gdf, 0)
#     # Set uniform conditions
#     app.gui.setvar("delft3dfm", "boundary_conditions_timeseries_shape", "constant")

#     # Write bnd file
#     app.model["delft3dfm"].domain.input.variables.bndfile = bndfile # file name without path
#     app.gui.setvar("delft3dfm", "bndfile", bndfile)
#     app.model["delft3dfm"].domain.boundary_conditions.write_boundary_points()

#     set_boundary_conditions()

#     app.gui.setvar("delft3dfm", "active_boundary_point", 0)
#     update_list()

# def get_bnd_file_name(*args):
#     filename = app.model["delft3dfm"].domain.input.variables.bndfile
#     if not filename:
#         filename = "sfincs.bnd"
#     rsp = app.gui.window.dialog_save_file("Select file ...",
#                                         file_name=filename,
#                                         filter="*.bnd",
#                                         allow_directory_change=False)
#     if rsp[0]:
#         return rsp[2]
#     else:
#         # User pressed cancel
#         return None

# def get_bzs_file_name(*args):
#     filename = app.model["delft3dfm"].domain.input.variables.bzsfile
#     if not filename:
#         filename = "sfincs.bzs"
#     rsp = app.gui.window.dialog_save_file("Select file ...",
#                                         file_name=filename,
#                                         filter="*.bzs",
#                                         allow_directory_change=False)
#     if rsp[0]:
#         return rsp[2]
#     else:
#         # User pressed cancel
#         return None

# def get_bca_file_name(*args):
#     filename = app.model["delft3dfm"].domain.input.variables.bcafile
#     if not filename:
#         filename = "sfincs.bca"
#     rsp = app.gui.window.dialog_save_file("Select file ...",
#                                         file_name=filename,
#                                         filter="*.bca",
#                                         allow_directory_change=False)
#     if rsp[0]:
#         return rsp[2]
#     else:
#         # User pressed cancel
#         return None