# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args):
    map.update()
    app.map.layer["sfincs_cht"].layer["observation_points"].activate()
    update()

def edit(*args):
    app.model["sfincs_cht"].set_model_variables()

def load(*args):
    map.reset_cursor()
    rsp = app.gui.window.dialog_open_file("Select file ...",
                                          file_name="sfincs.obs",
                                          filter="*.obs",
                                          allow_directory_change=False)
    if rsp[0]:
        app.model["sfincs_cht"].domain.input.variables.obsfile = rsp[2] # file name without path
        app.model["sfincs_cht"].domain.observation_points.read()
        gdf = app.model["sfincs_cht"].domain.observation_points.gdf
        app.map.layer["sfincs_cht"].layer["observation_points"].set_data(gdf, 0)
        app.gui.setvar("sfincs_cht", "active_observation_point", 0)
        update()

def save(*args):
    map.reset_cursor()
    file_name = app.model["sfincs_cht"].domain.input.variables.obsfile
    if not file_name:
        file_name = "sfincs_cht.obs"
    rsp = app.gui.window.dialog_save_file("Select file ...",
                                          file_name=file_name,
                                          filter="*.obs",
                                          allow_directory_change=False)
    if rsp[0]:
        app.model["sfincs_cht"].domain.input.variables.obsfile = rsp[2] # file name without path
        app.model["sfincs_cht"].domain.observation_points.write()

def update():
    gdf = app.active_model.domain.observation_points.gdf
    names = []
    for index, row in gdf.iterrows():
        names.append(row["name"])
    app.gui.setvar("sfincs_cht", "observation_point_names", names)
    app.gui.setvar("sfincs_cht", "nr_observation_points", len(gdf))
    app.gui.window.update()

def add_observation_point_on_map(*args):
    app.map.click_point(point_clicked)

def point_clicked(x, y):
    # Point clicked on map. Add observation point.
    name, okay = app.gui.window.dialog_string("Edit name for new observation point")
    if not okay:
        # Cancel was clicked
        return    
    if name in app.gui.getvar("sfincs_cht", "observation_point_names"):
        app.gui.window.dialog_info("An observation point with this name already exists !")
        return
    app.model["sfincs_cht"].domain.observation_points.add_point(x, y, name=name)
    index = len(app.model["sfincs_cht"].domain.observation_points.gdf) - 1
    gdf = app.model["sfincs_cht"].domain.observation_points.gdf
    app.map.layer["sfincs_cht"].layer["observation_points"].set_data(gdf, index)
    app.gui.setvar("sfincs_cht", "active_observation_point", index)
    update()
#    write()

def select_observation_point_from_list(*args):
    map.reset_cursor()
    index = app.gui.getvar("sfincs_cht", "active_observation_point")
    app.map.layer["sfincs_cht"].layer["observation_points"].select_by_index(index)

def select_observation_point_from_map(*args):
    map.reset_cursor()
    index = args[0]["id"]
    app.gui.setvar("sfincs_cht", "active_observation_point", index)
    app.gui.window.update()

def delete_point_from_list(*args):
    map.reset_cursor()
    index = app.gui.getvar("sfincs_cht", "active_observation_point")
    app.model["sfincs_cht"].domain.observation_points.delete_point(index)
    gdf = app.model["sfincs_cht"].domain.observation_points.gdf
    index = max(min(index, len(gdf) - 1), 0)
    app.map.layer["sfincs_cht"].layer["observation_points"].set_data(gdf, index)
    app.gui.setvar("sfincs_cht", "active_observation_point", index)
    update()
#    write()
