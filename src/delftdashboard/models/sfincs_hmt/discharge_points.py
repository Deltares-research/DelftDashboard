# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations import map

def select(*args):
    map.update()
    app.map.layer["sfincs_hmt"].layer["discharge_points"].activate()
    update()

def deselect(*args):
    if app.model["sfincs_hmt"].discharge_points_changed:
        ok = app.gui.window.dialog_yes_no("The discharge points have changed. Would you like to save the changes?")
        if ok:
            save()

def edit(*args):
    app.model["sfincs_hmt"].set_model_variables()

def load(*args):
    map.reset_cursor()

    # Always load both the src and dis file

    # Src file
    rsp = app.gui.window.dialog_open_file("Select file ...",
                                          file_name="sfincs.src",
                                          filter="*.src",
                                          allow_directory_change=False)

    # Src file
    if rsp[0]:
        app.model["sfincs_hmt"].domain.config.set("srcfile", rsp[2]) # file name without path
    else:
        return    

    # Dis file
    rsp = app.gui.window.dialog_open_file("Select file ...",
                                          file_name="sfincs.dis",
                                          filter="*.dis",
                                          allow_directory_change=False)
    if rsp[0]:
        app.model["sfincs_hmt"].domain.config.set("disfile", rsp[2]) # file name without path
    else:
        return

    app.model["sfincs_hmt"].domain.discharge_points.read()
    gdf = app.model["sfincs_hmt"].domain.discharge_points.data
    app.map.layer["sfincs_hmt"].layer["discharge_points"].set_data(gdf, 0)
    app.gui.setvar("sfincs_hmt", "active_discharge_point", 0)
    update()

    app.model["sfincs_hmt"].discharge_points_changed = False

def save(*args):
    map.reset_cursor()

    # Always save both the src and dis file

    # Src file
    filename = app.model["sfincs_hmt"].domain.config.get("srcfile")
    if not filename:
        filename = "sfincs.src"
    rsp = app.gui.window.dialog_save_file("Select file ...",
                                          file_name=filename,
                                          filter="*.src",
                                          allow_directory_change=False)
    if rsp[0]:
        app.model["sfincs_hmt"].domain.config.set("srcfile", rsp[2]) # file name without path
    else:
        return

    # Dis file
    filename = app.model["sfincs_hmt"].domain.config.get("disfile")
    if not filename:
        filename = "sfincs.dis"
    rsp = app.gui.window.dialog_save_file("Select file ...",
                                            file_name=filename,
                                            filter="*.dis",
                                            allow_directory_change=False)
    if rsp[0]:
        app.model["sfincs_hmt"].domain.config.set("disfile", rsp[2])
    else:
        return

    app.model["sfincs_hmt"].domain.discharge_points.write()

    app.model["sfincs_hmt"].discharge_points_changed = False

def update():
    gdf = app.active_model.domain.discharge_points.data
    names = []
    for index, row in gdf.iterrows():
        names.append(row["name"])
    app.gui.setvar("sfincs_hmt", "discharge_point_names", names)
    app.gui.setvar("sfincs_hmt", "nr_discharge_points", len(gdf))
    app.gui.window.update()

def add_discharge_point_on_map(*args):
    app.map.click_point(point_clicked)

def point_clicked(x, y):
    # Point clicked on map.
    # Name
    name, okay = app.gui.window.dialog_string("Edit name for new discharge point")
    if not okay:
        # Cancel was clicked
        return    
    if name in app.gui.getvar("sfincs_hmt", "discharge_point_names"):
        app.gui.window.dialog_info("A discharge point with this name already exists !")
        return
    # Discharge
    qstr, okay = app.gui.window.dialog_string("Edit discharge for new discharge point (m3/s)")
    if not okay:
        # Cancel was clicked
        return
    # Try to convert qstr to float
    try:
        q = float(qstr)
    except:
        app.gui.window.dialog_info("Invalid discharge value !")
        return
    app.model["sfincs_hmt"].domain.discharge_points.add_point(x=x, y=y, name=name, q=q)
    gdf = app.model["sfincs_hmt"].domain.discharge_points.data
    index = len(gdf) - 1
    app.map.layer["sfincs_hmt"].layer["discharge_points"].set_data(gdf, index)
    app.gui.setvar("sfincs_hmt", "active_discharge_point", index)
    update()
    app.model["sfincs_hmt"].discharge_points_changed = True

def select_discharge_point_from_list(*args):
    map.reset_cursor()
    index = app.gui.getvar("sfincs_hmt", "active_discharge_point")
    app.map.layer["sfincs_hmt"].layer["discharge_points"].select_by_index(index)

def select_discharge_point_from_map(*args):
    map.reset_cursor()
    index = args[0]["id"]
    app.gui.setvar("sfincs_hmt", "active_discharge_point", index)
    app.gui.window.update()

def delete_point_from_list(*args):
    map.reset_cursor()
    index = app.gui.getvar("sfincs_hmt", "active_discharge_point")
    app.model["sfincs_hmt"].domain.discharge_points.delete(index)
    gdf = app.model["sfincs_hmt"].domain.discharge_points.data
    index = max(min(index, len(gdf) - 1), 0)
    app.map.layer["sfincs_hmt"].layer["discharge_points"].set_data(gdf, index)
    app.gui.setvar("sfincs_hmt", "active_discharge_point", index)
    app.model["sfincs_hmt"].discharge_points_changed = True
    update()
