# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations import map

def select(*args):
    # De-activate existing layers
    map.update()
    # Activate draw layer
    app.map.layer["sfincs_cht"].layer["thin_dams"].layer["polylines"].activate()
    app.map.layer["sfincs_cht"].layer["thin_dams"].layer["snapped"].activate()
    update()

# def deselect(*args):
#     if app.model["sfincs_cht"].thin_dams_changed:
#         ok = app.gui.window.dialog_yes_no("The thin dams have changed. Would you like to save the changes?")
#         if ok:
#             save()

def load(*args):
    map.reset_cursor()
    rsp = app.gui.window.dialog_open_file("Select file ...",
                                          file_name="sfincs.thd",
                                          filter="*.thd",
                                          allow_directory_change=False)
    if rsp[0]:
        app.model["sfincs_cht"].domain.input.variables.thdfile = rsp[2] # file name without path
        app.model["sfincs_cht"].domain.thin_dams.read()
        gdf = app.model["sfincs_cht"].domain.thin_dams.gdf
        app.map.layer["sfincs_cht"].layer["thin_dams"].layer["polylines"].set_data(gdf)
        app.gui.setvar("sfincs_cht", "active_thin_dam", 0)
        update()
    app.model["sfincs_cht"].thin_dams_changed = False

def save(*args):
    map.reset_cursor()
    filename = app.model["sfincs_cht"].domain.input.variables.thdfile
    if not filename:
        filename = "sfincs.thd"
    rsp = app.gui.window.dialog_save_file("Select file ...",
                                          file_name=filename,
                                          filter="*.thd",
                                          allow_directory_change=False)
    if rsp[0]:
        app.model["sfincs_cht"].domain.input.variables.thdfile = rsp[2] # file name without path
        app.model["sfincs_cht"].domain.thin_dams.write()
    app.model["sfincs_cht"].thin_dams_changed = False

def draw_thin_dam(*args):
    app.map.layer["sfincs_cht"].layer["thin_dams"].layer["polylines"].draw()

def delete_thin_dam(*args):
    gdf = app.model["sfincs_cht"].domain.thin_dams.gdf
    if len(gdf) == 0:
        return
    index = app.gui.getvar("sfincs_cht", "thin_dam_index")
    # Delete from map
    app.map.layer["sfincs_cht"].layer["thin_dams"].layer["polylines"].delete_feature(index)
    # Delete from app
    app.model["sfincs_cht"].domain.thin_dams.delete(index)
    app.model["sfincs_cht"].thin_dams_changed = True
    update()

    # update_grid_snapper()

def select_thin_dam(*args):
    pass
    
def thin_dam_created(gdf, index, id):
    app.model["sfincs_cht"].domain.thin_dams.gdf = gdf
    nrt = len(gdf)
    app.gui.setvar("sfincs_cht", "thin_dam_index", nrt - 1)
    app.model["sfincs_cht"].thin_dams_changed = True
    update()
    # update_grid_snapper()

def thin_dam_modified(gdf, index, id):
    app.model["sfincs_cht"].domain.thin_dams.gdf = gdf
    app.model["sfincs_cht"].thin_dams_changed = True
    # update_grid_snapper()

def thin_dam_selected(index):
    app.gui.setvar("sfincs_cht", "thin_dam_index", index)
    update()

def set_model_variables(*args):
    # All variables will be set
    app.model["sfincs_cht"].set_model_variables()

def update_grid_snapper():
    snap_gdf = app.model["sfincs_cht"].domain.thin_dams.snap_to_grid()
    if len(snap_gdf) > 0:
        app.map.layer["sfincs_cht"].layer["thin_dams"].layer["snapped"].set_data(snap_gdf)

def update():
    nrt = len(app.model["sfincs_cht"].domain.thin_dams.gdf)
    app.gui.setvar("sfincs_cht", "nr_thin_dams", nrt)
    if app.gui.getvar("sfincs_cht", "thin_dam_index" ) > nrt - 1:
        app.gui.setvar("sfincs_cht", "thin_dam_index", max(nrt - 1, 0) )
    app.gui.setvar("sfincs_cht", "thin_dam_names", app.model["sfincs_cht"].domain.thin_dams.list_names())
    app.gui.window.update()
