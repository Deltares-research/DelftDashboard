# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations import map

def select(*args):
    map.update()
    app.map.layer["fiat"].layer["observation_points_spectra"].set_mode("active")
    update()

def edit(*args):
    app.model["fiat"].set_model_variables()

def load(*args):
    map.reset_cursor()
    rsp = app.gui.window.dialog_open_file("Select file ...",
                                          file_name="fiat.osp",
                                          filter="*.osp",
                                          allow_directory_change=False)
    if rsp[0]:
        app.model["fiat"].domain.input.variables.ospfile = rsp[2] # file name without path
        app.model["fiat"].domain.observation_points_sp2.read()
        gdf = app.model["fiat"].domain.observation_points_sp2.gdf
        app.map.layer["fiat"].layer["observation_points_spectra"].set_data(gdf, 0)
        app.gui.setvar("fiat", "active_observation_point_spectra", 0)
        update()

def save(*args):
    map.reset_cursor()
    file_name = app.model["fiat"].domain.input.variables.ospfile
    if not file_name:
        file_name = "fiat.osp"
    rsp = app.gui.window.dialog_save_file("Select file ...",
                                          file_name=file_name,
                                          filter="*.osp",
                                          allow_directory_change=False)
    if rsp[0]:
        app.model["fiat"].domain.input.variables.ospfile = rsp[2] # file name without path
        app.model["fiat"].domain.observation_points_sp2.write()

def update():
    gdf = app.active_model.domain.observation_points_sp2.gdf
    names = []
    for index, row in gdf.iterrows():
        names.append(row["name"])
    app.gui.setvar("fiat", "observation_point_names_spectra", names)
    app.gui.setvar("fiat", "nr_observation_points_spectra", len(gdf))
    app.gui.window.update()

def add_observation_point_on_map(*args):
    app.map.click_point(point_clicked)

def point_clicked(coords):
    # Point clicked on map. Add observation point.
    x = coords["lng"]
    y = coords["lat"]
    name, okay = app.gui.window.dialog_string("Edit name for new observation point")
    if not okay:
        # Cancel was clicked
        return    
    if name in app.gui.getvar("fiat", "observation_point_names_spectra"):
        app.gui.window.dialog_info("An observation point with this name already exists !")
        return
    app.model["fiat"].domain.observation_points_sp2.add_point(x, y, name=name)
    index = len(app.model["fiat"].domain.observation_points_sp2.gdf) - 1
    gdf = app.model["fiat"].domain.observation_points_sp2.gdf
    app.map.layer["fiat"].layer["observation_points_spectra"].set_data(gdf, index)
    app.gui.setvar("fiat", "active_observation_point_spectra", index)
    update()
#    write()


def select_observation_point_from_list(*args):
    map.reset_cursor()
    index = app.gui.getvar("fiat", "active_observation_point_spectra")
    app.map.layer["fiat"].layer["observation_points_spectra"].select_by_index(index)

def select_observation_point_from_map_spectra(*args):
    map.reset_cursor()
    index = args[0]["id"]
    app.gui.setvar("fiat", "active_observation_point_spectra", index)
    app.gui.window.update()

def delete_point_from_list(*args):
    map.reset_cursor()
    index = app.gui.getvar("fiat", "active_observation_point_spectra")
    app.model["fiat"].domain.observation_points_sp2.delete_point(index)
    gdf = app.model["fiat"].domain.observation_points_sp2.gdf
    index = max(min(index, len(gdf) - 1), 0)
    app.map.layer["fiat"].layer["observation_points_spectra"].set_data(gdf, index)
    app.gui.setvar("fiat", "active_observation_point_spectra", index)
    update()
#    write()
