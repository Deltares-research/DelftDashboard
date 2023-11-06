# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args):
    map.update()
    app.map.layer["hurrywave"].layer["observation_points_regular"].activate()
    update()

def edit(*args):
    app.model["hurrywave"].set_model_variables()

def load(*args):
    map.reset_cursor()
    rsp = app.gui.window.dialog_open_file("Select file ...",
                                          file_name="hurrywave.obs",
                                          filter="*.obs",
                                          allow_directory_change=False)
    if rsp[0]:
        app.model["hurrywave"].domain.input.variables.obsfile = rsp[2] # file name without path
        app.model["hurrywave"].domain.observation_points_regular.read()
        gdf = app.model["hurrywave"].domain.observation_points_regular.gdf
        app.map.layer["hurrywave"].layer["observation_points_regular"].set_data(gdf, 0)
        app.gui.setvar("hurrywave", "active_observation_point_regular", 0)
        update()

def save(*args):
    map.reset_cursor()
    file_name = app.model["hurrywave"].domain.input.variables.obsfile
    if not file_name:
        file_name = "hurrywave.obs"
    rsp = app.gui.window.dialog_save_file("Select file ...",
                                          file_name=file_name,
                                          filter="*.obs",
                                          allow_directory_change=False)
    if rsp[0]:
        app.model["hurrywave"].domain.input.variables.obsfile = rsp[2] # file name without path
        app.model["hurrywave"].domain.observation_points_regular.write()

def update():
    gdf = app.active_model.domain.observation_points_regular.gdf
    names = []
    for index, row in gdf.iterrows():
        names.append(row["name"])
    app.gui.setvar("hurrywave", "observation_point_names_regular", names)
    app.gui.setvar("hurrywave", "nr_observation_points_regular", len(gdf))
    app.gui.window.update()

def add_observation_point_on_map(*args):
    app.map.click_point(point_clicked)

def point_clicked(x, y):
    # Point clicked on map. Add observation point.
    name, okay = app.gui.window.dialog_string("Edit name for new observation point")
    if not okay:
        # Cancel was clicked
        return    
    if name in app.gui.getvar("hurrywave", "observation_point_names_regular"):
        app.gui.window.dialog_info("An observation point with this name already exists !")
        return
    app.model["hurrywave"].domain.observation_points_regular.add_point(x, y, name=name)
    index = len(app.model["hurrywave"].domain.observation_points_regular.gdf) - 1
    gdf = app.model["hurrywave"].domain.observation_points_regular.gdf
    app.map.layer["hurrywave"].layer["observation_points_regular"].set_data(gdf, index)
    app.gui.setvar("hurrywave", "active_observation_point_regular", index)
    update()
#    write()


def select_observation_point_from_list(*args):
    map.reset_cursor()
    index = app.gui.getvar("hurrywave", "active_observation_point_regular")
    app.map.layer["hurrywave"].layer["observation_points_regular"].select_by_index(index)

def select_observation_point_from_map_regular(*args):
    map.reset_cursor()
    index = args[0]["id"]
    app.gui.setvar("hurrywave", "active_observation_point_regular", index)
    app.gui.window.update()

def delete_point_from_list(*args):
    map.reset_cursor()
    index = app.gui.getvar("hurrywave", "active_observation_point_regular")
    app.model["hurrywave"].domain.observation_points_regular.delete_point(index)
    gdf = app.model["hurrywave"].domain.observation_points_regular.gdf
    index = max(min(index, len(gdf) - 1), 0)
    app.map.layer["hurrywave"].layer["observation_points_regular"].set_data(gdf, index)
    app.gui.setvar("hurrywave", "active_observation_point_regular", index)
    update()
#    write()
