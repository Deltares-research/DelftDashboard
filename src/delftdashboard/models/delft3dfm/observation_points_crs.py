# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations import map
from pathlib import Path
import pandas as pd

def select(*args):
    map.update()
    app.map.layer["delft3dfm"].layer["observation_lines"].activate()
    update()

def deselect(*args):
    if app.model["delft3dfm"].observation_lines_changed:
        ok = app.gui.window.dialog_yes_no("The cross sections have changed. Would you like to save the changes?")
        if ok:
            save()

def edit(*args):
    app.model["delft3dfm"].set_model_variables()

def load(*args):
    map.reset_cursor()
    rsp = app.gui.window.dialog_open_file("Select file ...",
                                          file_name="obs_crs.pli",
                                          filter="*_crs.pli",
                                          allow_directory_change=False)
    if rsp[0]:
        app.model["delft3dfm"].domain.input.output.crsfile = rsp[0] # file name without path
        app.model["delft3dfm"].domain.read_observation_lines()
        gdf = app.model["delft3dfm"].domain.observation_line_gdf
        app.map.layer["delft3dfm"].layer["observation_lines"].set_data(gdf, 0)
        app.gui.setvar("delft3dfm", "active_observation_line", 0)
        update()
    app.model["delft3dfm"].observation_lines_changed = False

def save(*args):
    from hydrolib.core.dflowfm import ObservationCrossSectionModel

    map.reset_cursor()
    # file_name = app.model["delft3dfm"].domain.input.output.obsfile[0].filepath
    rsp = app.gui.window.dialog_save_file("Select file ...",
                                          file_name='delft3dfm_crs.pli',
                                          filter = None,
                                          allow_directory_change=False)
    if rsp[0]:
        app.model["delft3dfm"].domain.input.output.crsfile = [] # first clear obsfile list to add combined / new crs
        app.model["delft3dfm"].domain.input.output.crsfile.append(ObservationCrossSectionModel())
        app.model["delft3dfm"].domain.input.output.crsfile[0].filepath=Path(rsp[2]) # save all obs crss in 1 file
        app.model["delft3dfm"].domain.write_observation_lines()
    app.model["delft3dfm"].observation_lines_changed = False

def update():
    gdf = app.model["delft3dfm"].domain.observation_line_gdf
    nrt = len(gdf)
    names = []
    for index, row in gdf.iterrows():
        names.append(row["name"])
    app.gui.setvar("delft3dfm", "observation_line_names", names)
    app.gui.setvar("delft3dfm", "nr_observation_lines", nrt)
    if app.gui.getvar("delft3dfm", "active_observation_line" ) > nrt - 1:
        app.gui.setvar("delft3dfm", "active_observation_line", max(nrt - 1, 0) )
    app.gui.window.update()

def draw_obs_line(*args):
    app.map.layer["delft3dfm"].layer["observation_lines"].draw()
    
def delete_obs_line(*args):
    gdf = app.model["delft3dfm"].domain.observation_line_gdf
    if len(gdf) == 0:
        return
    index = app.gui.getvar("delft3dfm", "active_observation_line")
    # # Delete from map
    # app.map.layer["delft3dfm"].layer["observation_lines"].delete_feature(index)
    # Delete from app
    app.model["delft3dfm"].domain.observation_line_gdf = app.model["delft3dfm"].domain.observation_line_gdf.drop(index).reset_index(drop=True)
    gdf = app.model["delft3dfm"].domain.observation_line_gdf
    index = max(min(index, len(gdf) - 1), 0)
    app.map.layer["delft3dfm"].layer["observation_lines"].set_data(gdf)
    app.gui.setvar("delft3dfm", "active_observation_line", index)
    app.model["delft3dfm"].observation_lines_changed = True
    update()

def select_obs_line(*args):
    map.reset_cursor()
    index = app.gui.getvar("delft3dfm", "active_observation_line")
    app.map.layer["delft3dfm"].layer["observation_lines"].activate_feature(index)
    # app.map.layer["delft3dfm"].layer["observation_lines"].select_by_index(index)
    update()
    
def obs_lines_created(gdf, index, id):
    name, okay = app.gui.window.dialog_string("Edit name for new observation line")
    if not okay:
        # Cancel was clicked
        # Delete from map
        app.map.layer["delft3dfm"].layer["observation_lines"].delete_feature(index)
        return    
    if name in app.gui.getvar("delft3dfm", "observation_line_names"):
        app.gui.window.dialog_info("An observation line with this name already exists !")
        return
    gdf.loc[index, "name"] = name
    existing_gdf = app.model["delft3dfm"].domain.observation_line_gdf
    if existing_gdf is None or existing_gdf.empty:
        app.model["delft3dfm"].domain.observation_line_gdf = gdf
    else:
        app.model["delft3dfm"].domain.observation_line_gdf = pd.concat([existing_gdf, gdf.loc[[index]]], ignore_index=True)
    nrt = len(gdf)
    app.gui.setvar("delft3dfm", "observation_line_index", nrt - 1)
    app.gui.setvar("delft3dfm", "active_observation_line", nrt - 1)
    app.model["delft3dfm"].observation_lines_changed = True
    update()
    # update_grid_snapper()

def obs_lines_modified(gdf, index, id):
    app.model["delft3dfm"].domain.observation_line_gdf = gdf
    app.model["delft3dfm"].observation_lines_changed = True
    # update_grid_snapper()

def obs_lines_selected(index):
    app.gui.setvar("delft3dfm", "observation_line_index", index)
    app.gui.setvar("delft3dfm", "active_observation_line", index)
    update()

def set_model_variables(*args):
    # All variables will be set
    app.model["delft3dfm"].set_model_variables()


    # nrt = len(app.model["delft3dfm"].domain.observation_lines_gdf)
    # app.gui.setvar("delft3dfm", "nr_thin_dams", nrt)
    # app.gui.setvar("delft3dfm", "thin_dam_names", app.model["delft3dfm"].domain.observation_lines.list_names())
    # app.gui.window.update()
###################

# def add_observation_crs_on_map(*args):
#     app.map.click_point(point_clicked)

# def point_clicked(x, y):
#     # Point clicked on map. Add observation point.
#     name, okay = app.gui.window.dialog_string("Edit name for new observation point")
#     if not okay:
#         # Cancel was clicked
#         return    
#     if name in app.gui.getvar("delft3dfm", "observation_point_names"):
#         app.gui.window.dialog_info("An observation point with this name already exists !")
#         return
#     app.model["delft3dfm"].domain.add_observation_point(x, y, name=name)
#     app.model["delft3dfm"].domain.add_observation_point_gdf(x, y, name=name)
#     index = len(app.model["delft3dfm"].domain.observation_point_gdf) - 1
#     gdf = app.model["delft3dfm"].domain.observation_point_gdf
#     app.map.layer["delft3dfm"].layer["observation_points"].set_data(gdf, index)
#     app.gui.setvar("delft3dfm", "active_observation_point", index)
#     update()
# #    write()


# def select_observation_crs_from_list(*args):
#     map.reset_cursor()
#     index = app.gui.getvar("delft3dfm", "active_observation_crs")
#     app.map.layer["delft3dfm"].layer["observation_points"].select_by_index(index)

# def select_observation_crs_from_map(*args):
#     map.reset_cursor()
#     index = args[0]["id"]
#     app.gui.setvar("delft3dfm", "active_observation_crs", index)
#     app.gui.window.update()

# def delete_crs_from_list(*args):
#     map.reset_cursor()
#     index = app.gui.getvar("delft3dfm", "active_observation_crs")
#     app.model["delft3dfm"].domain.delete_observation_point(index)
#     gdf = app.model["delft3dfm"].domain.observation_crs_gdf
#     index = max(min(index, len(gdf) - 1), 0)
#     app.map.layer["delft3dfm"].layer["observation_points"].set_data(gdf, index)
#     app.gui.setvar("delft3dfm", "active_observation_crs", index)
#     update()
# #    write()