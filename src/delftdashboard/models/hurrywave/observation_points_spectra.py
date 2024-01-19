# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations import map

def select(*args):
    map.update()
    app.map.layer["hurrywave"].layer["observation_points_spectra"].activate()
    update()

def edit(*args):
    app.model["hurrywave"].set_model_variables()

def load(*args):
    map.reset_cursor()
    rsp = app.gui.window.dialog_open_file("Select file ...",
                                          file_name="hurrywave.osp",
                                          filter="*.osp",
                                          allow_directory_change=False)
    if rsp[0]:
        app.model["hurrywave"].domain.input.variables.ospfile = rsp[2] # file name without path
        app.model["hurrywave"].domain.observation_points_sp2.read()
        gdf = app.model["hurrywave"].domain.observation_points_sp2.gdf
        app.map.layer["hurrywave"].layer["observation_points_spectra"].set_data(gdf, 0)
        app.gui.setvar("hurrywave", "active_observation_point_spectra", 0)
        update()

def save(*args):
    map.reset_cursor()
    file_name = app.model["hurrywave"].domain.input.variables.ospfile
    if not file_name:
        file_name = "hurrywave.osp"
    rsp = app.gui.window.dialog_save_file("Select file ...",
                                          file_name=file_name,
                                          filter="*.osp",
                                          allow_directory_change=False)
    if rsp[0]:
        app.model["hurrywave"].domain.input.variables.ospfile = rsp[2] # file name without path
        app.model["hurrywave"].domain.observation_points_sp2.write()

def update():
    gdf = app.active_model.domain.observation_points_sp2.gdf
    names = []
    for index, row in gdf.iterrows():
        names.append(row["name"])
    app.gui.setvar("hurrywave", "observation_point_names_spectra", names)
    app.gui.setvar("hurrywave", "nr_observation_points_spectra", len(gdf))
    app.gui.window.update()

def add_observation_point_on_map(*args):
    app.map.click_point(point_clicked)

def point_clicked(x, y):
    # Point clicked on map. Add observation point.
    name, okay = app.gui.window.dialog_string("Edit name for new observation point")
    if not okay:
        # Cancel was clicked
        return    
    if name in app.gui.getvar("hurrywave", "observation_point_names_spectra"):
        app.gui.window.dialog_info("An observation point with this name already exists !")
        return
    app.model["hurrywave"].domain.observation_points_sp2.add_point(x, y, name=name)
    index = len(app.model["hurrywave"].domain.observation_points_sp2.gdf) - 1
    gdf = app.model["hurrywave"].domain.observation_points_sp2.gdf
    app.map.layer["hurrywave"].layer["observation_points_spectra"].set_data(gdf, index)
    app.gui.setvar("hurrywave", "active_observation_point_spectra", index)
    update()
#    write()


def select_observation_point_from_list(*args):
    map.reset_cursor()
    index = app.gui.getvar("hurrywave", "active_observation_point_spectra")
    app.map.layer["hurrywave"].layer["observation_points_spectra"].select_by_index(index)

def select_observation_point_from_map_spectra(*args):
    map.reset_cursor()
    index = args[0]["id"]
    app.gui.setvar("hurrywave", "active_observation_point_spectra", index)
    app.gui.window.update()

def delete_point_from_list(*args):
    map.reset_cursor()
    index = app.gui.getvar("hurrywave", "active_observation_point_spectra")
    app.model["hurrywave"].domain.observation_points_sp2.delete_point(index)
    gdf = app.model["hurrywave"].domain.observation_points_sp2.gdf
    index = max(min(index, len(gdf) - 1), 0)
    app.map.layer["hurrywave"].layer["observation_points_spectra"].set_data(gdf, index)
    app.gui.setvar("hurrywave", "active_observation_point_spectra", index)
    update()
#    write()
