# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations import map

def select(*args):
    map.update()
    app.map.layer["sfincs_hmt"].layer["observation_points"].activate()
    update()

def deselect(*args):
    if app.model["sfincs_hmt"].observation_points_changed:
        ok = app.gui.window.dialog_yes_no("The observation points have changed. Would you like to save the changes?")
        if ok:
            save()

def edit(*args):
    app.model["sfincs_hmt"].set_model_variables()

def load(*args):
    map.reset_cursor()
    rsp = app.gui.window.dialog_open_file("Select file ...",
                                          file_name="sfincs.obs",
                                          filter="*.obs",
                                          allow_directory_change=False)
    if rsp[0]:
        app.model["sfincs_hmt"].domain.config.set("obsfile", rsp[2]) # file name without path
        app.gui.setvar("sfincs_hmt", "obsfile", rsp[2])
        app.model["sfincs_hmt"].domain.observation_points.read()
        gdf = app.model["sfincs_hmt"].domain.observation_points.data
        app.map.layer["sfincs_hmt"].layer["observation_points"].set_data(gdf, 0)
        app.gui.setvar("sfincs_hmt", "active_observation_point", 0)
        update()
    app.model["sfincs_hmt"].observation_points_changed = False

def save(*args):
    map.reset_cursor()
    file_name = app.model["sfincs_hmt"].domain.config.get("obsfile")
    if not file_name:
        file_name = "sfincs.obs"
    rsp = app.gui.window.dialog_save_file("Select file ...",
                                          file_name=file_name,
                                          filter="*.obs",
                                          allow_directory_change=False)
    if rsp[0]:
        app.model["sfincs_hmt"].domain.config.set("obsfile", rsp[2]) # file name without path
        app.gui.setvar("sfincs_hmt", "obsfile", rsp[2])
        app.model["sfincs_hmt"].domain.observation_points.write()
    app.model["sfincs_hmt"].observation_points_changed = False


def add_observation_point_on_map(*args):
    app.map.click_point(point_clicked)

def point_clicked(x, y):
    # Point clicked on map. Add observation point.
    name, okay = app.gui.window.dialog_string("Edit name for new observation point")
    if not okay:
        # Cancel was clicked
        return    
    if name in app.gui.getvar("sfincs_hmt", "observation_point_names"):
        app.gui.window.dialog_info("An observation point with this name already exists !")
        return
    app.model["sfincs_hmt"].domain.observation_points.add_point(x, y, name=name)
    index = len(app.model["sfincs_hmt"].domain.observation_points.data) - 1
    gdf = app.model["sfincs_hmt"].domain.observation_points.data
    app.map.layer["sfincs_hmt"].layer["observation_points"].set_data(gdf, index)
    app.gui.setvar("sfincs_hmt", "active_observation_point", index)
    update()
    app.model["sfincs_hmt"].observation_points_changed = True

def select_observation_point_from_list(*args):
    map.reset_cursor()
    index = app.gui.getvar("sfincs_hmt", "active_observation_point")
    app.map.layer["sfincs_hmt"].layer["observation_points"].select_by_index(index)
    update()

def select_observation_point_from_map(*args):
    map.reset_cursor()
    index = args[0]["id"]
    app.gui.setvar("sfincs_hmt", "active_observation_point", index)
    app.gui.window.update()

def delete_point_from_list(*args):
    map.reset_cursor()
    index = app.gui.getvar("sfincs_hmt", "active_observation_point")
    app.model["sfincs_hmt"].domain.observation_points.delete(index)
    gdf = app.model["sfincs_hmt"].domain.observation_points.data
    index = max(min(index, len(gdf) - 1), 0)
    app.map.layer["sfincs_hmt"].layer["observation_points"].set_data(gdf, index)
    app.gui.setvar("sfincs_hmt", "active_observation_point", index)
    app.model["sfincs_hmt"].observation_points_changed = True
    update()

def edit_name(*args):
    name = app.gui.getvar("sfincs_hmt", "observation_point_name")
    index = app.gui.getvar("sfincs_hmt", "active_observation_point")
    gdf = app.model["sfincs_hmt"].domain.observation_points.data
    gdf.at[index, "name"] = name
    app.map.layer["sfincs_hmt"].layer["observation_points"].set_data(gdf, index)
    app.model["sfincs_hmt"].observation_points_changed = True
    update()

def update():
    gdf = app.active_model.domain.observation_points.data
    iac = app.gui.getvar("sfincs_hmt", "active_observation_point")
    names = []
    for index, row in gdf.iterrows():
        names.append(row["name"])
    app.gui.setvar("sfincs_hmt", "observation_point_names", names)
    app.gui.setvar("sfincs_hmt", "nr_observation_points", len(gdf))
    if len(gdf) > 0:
        app.gui.setvar("sfincs_hmt", "observation_point_name", names[iac])
    else:
        app.gui.setvar("sfincs_hmt", "observation_point_name", "")
    app.gui.window.update()
