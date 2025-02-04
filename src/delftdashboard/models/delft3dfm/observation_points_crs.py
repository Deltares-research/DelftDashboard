# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations import map
from pathlib import Path

def select(*args):
    map.update()
    app.map.layer["delft3dfm"].layer["observation_crs"].activate()
    update()

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
        app.model["delft3dfm"].domain.read_observation_crs()
        gdf = app.model["delft3dfm"].domain.observation_crs_gdf
        app.map.layer["delft3dfm"].layer["observation_crs"].set_data(gdf, 0)
        app.gui.setvar("delft3dfm", "active_observation_crs", 0)
        update()

def save(*args):
    from hydrolib.core.dflowfm.ObservationCrossSectionModel.models import ObservationCrossSectionModel

    map.reset_cursor()
    # file_name = app.model["delft3dfm"].domain.input.output.obsfile[0].filepath
    rsp = app.gui.window.dialog_save_file("Select file ...",
                                          file_name='delft3dfm_crs.pli',
                                          filter = None,
                                          allow_directory_change=False)
    if rsp[0]:
        app.model["delft3dfm"].domain.input.output.crsfile = [] # first clear obsfile list to add combined / new points
        app.model["delft3dfm"].domain.input.output.crsfile.append(ObservationCrossSectionModel())
        app.model["delft3dfm"].domain.input.output.crsfile[0].filepath=Path(rsp[2]) # save all obs points in 1 file
        app.model["delft3dfm"].domain.write_observation_crs()

def update():
    nrt = len(app.model["delft3dfm"].domain.observation_crs.gdf)
    app.gui.setvar("delft3dfm", "nr_observation_crs", nrt)
    if app.gui.getvar("delft3dfm", "observation_crs_index" ) > nrt - 1:
        app.gui.setvar("delft3dfm", "observation_crs_index", max(nrt - 1, 0) )
    app.gui.setvar("delft3dfm", "observation_crs_names", app.model["delft3dfm"].domain.observation_crs.list_names())
    app.gui.window.update()

def draw(*args):
    app.map.layer["delft3dfm"].layer["observation_crs"].draw()

def delete(*args):
    gdf = app.model["delft3dfm"].domain.observation_crs.gdf
    if len(gdf) == 0:
        return
    index = app.gui.getvar("delft3dfm", "observation_crs_index")
    # Delete from map
    app.map.layer["delft3dfm"].layer["observation_crs"].delete_feature(index)
    # Delete from app
    app.model["delft3dfm"].domain.observation_crs.delete(index)
    update()
    
def crs_created(gdf, index, id):
    app.model["delft3dfm"].domain.observation_crs.gdf = gdf
    nrt = len(gdf)
    app.gui.setvar("delft3dfm", "observation_crs_index", nrt - 1)
    update()
    # update_grid_snapper()

def crs_modified(gdf, index, id):
    app.model["delft3dfm"].domain.observation_crs.gdf = gdf
    # update_grid_snapper()

def crs_selected(index):
    app.gui.setvar("delft3dfm", "observation_crs_index", index)
    update()

def set_model_variables(*args):
    # All variables will be set
    app.model["delft3dfm"].set_model_variables()

###################

def add_observation_point_on_map(*args):
    app.map.click_point(point_clicked)

def point_clicked(x, y):
    # Point clicked on map. Add observation point.
    name, okay = app.gui.window.dialog_string("Edit name for new observation point")
    if not okay:
        # Cancel was clicked
        return    
    if name in app.gui.getvar("delft3dfm", "observation_point_names"):
        app.gui.window.dialog_info("An observation point with this name already exists !")
        return
    app.model["delft3dfm"].domain.add_observation_point(x, y, name=name)
    app.model["delft3dfm"].domain.add_observation_point_gdf(x, y, name=name)
    index = len(app.model["delft3dfm"].domain.observation_point_gdf) - 1
    gdf = app.model["delft3dfm"].domain.observation_point_gdf
    app.map.layer["delft3dfm"].layer["observation_points"].set_data(gdf, index)
    app.gui.setvar("delft3dfm", "active_observation_point", index)
    update()
#    write()


def select_observation_point_from_list(*args):
    map.reset_cursor()
    index = app.gui.getvar("delft3dfm", "active_observation_point")
    app.map.layer["delft3dfm"].layer["observation_points"].select_by_index(index)

def select_observation_point_from_map(*args):
    map.reset_cursor()
    index = args[0]["id"]
    app.gui.setvar("delft3dfm", "active_observation_point", index)
    app.gui.window.update()

def delete_point_from_list(*args):
    map.reset_cursor()
    index = app.gui.getvar("delft3dfm", "active_observation_point")
    app.model["delft3dfm"].domain.delete_observation_point(index)
    gdf = app.model["delft3dfm"].domain.observation_point_gdf
    index = max(min(index, len(gdf) - 1), 0)
    app.map.layer["delft3dfm"].layer["observation_points"].set_data(gdf, index)
    app.gui.setvar("delft3dfm", "active_observation_point", index)
    update()
#    write()
