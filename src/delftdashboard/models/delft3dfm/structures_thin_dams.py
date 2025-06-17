# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations import map
from pathlib import Path

def select(*args):
    # De-activate existing layers
    map.update()
    # Activate draw layer
    app.map.layer["delft3dfm"].layer["thin_dams"].activate()
    update()

def deselect(*args):
    if app.model["delft3dfm"].thin_dams_changed:
        ok = app.gui.window.dialog_yes_no("The thin dams have changed. Would you like to save the changes?")
        if ok:
            save()
        else:
            app.model["delft3dfm"].thin_dams_changed = False
    app.map.layer["delft3dfm"].layer["thin_dams"].hide()
    update()

def load(*args):
    map.reset_cursor()
    rsp = app.gui.window.dialog_open_file("Select file ...",
                                        #   file_name="sfincs.thd",
                                          filter="*_thd.pli",
                                          allow_directory_change=False)
    if rsp[0]:
        app.model["delft3dfm"].domain.input.geometry.thindamfile = rsp[0] # file name without path
        app.model["delft3dfm"].domain.thin_dams.read()
        gdf = app.model["delft3dfm"].domain.thin_dams.gdf
        app.map.layer["delft3dfm"].layer["thin_dams"].set_data(gdf)
        app.gui.setvar("delft3dfm", "active_thin_dam", 0)
        update()
    app.model["delft3dfm"].thin_dams_changed = False

def save(*args):
    from hydrolib.core.dflowfm import ObservationCrossSectionModel

    map.reset_cursor()
    filename = app.model["delft3dfm"].domain.input.geometry.thindamfile
    if not filename:
        filename = "delft3dfm_thd.pli"
    rsp = app.gui.window.dialog_save_file("Select file ...",
                                          file_name=filename,
                                          filter="*.pli",
                                          allow_directory_change=False)
    if rsp[0]:
        app.model["delft3dfm"].domain.input.geometry.thindamfile = []# file name without path
        app.model["delft3dfm"].domain.input.geometry.thindamfile.append(ObservationCrossSectionModel())
        app.model["delft3dfm"].domain.input.geometry.thindamfile[0].filepath = Path(rsp[2]) # file name without path
        app.model["delft3dfm"].domain.thin_dams.write()
    app.model["delft3dfm"].thin_dams_changed = False

def draw_thin_dam(*args):
    app.map.layer["delft3dfm"].layer["thin_dams"].draw()

def delete_thin_dam(*args):
    gdf = app.model["delft3dfm"].domain.thin_dams.gdf
    if len(gdf) == 0:
        return
    index = app.gui.getvar("delft3dfm", "active_thin_dam")
    # Delete from map
    app.map.layer["delft3dfm"].layer["thin_dams"].delete_feature(index)
    # Delete from app
    app.model["delft3dfm"].domain.thin_dams.delete(index)
    app.gui.setvar("delft3dfm", "active_thin_dam", index)
    app.model["delft3dfm"].thin_dams_changed = True
    update()

    # update_grid_snapper()

def select_thin_dam(*args):
    map.reset_cursor()
    index = app.gui.getvar("delft3dfm", "active_thin_dam")
    app.map.layer["delft3dfm"].layer["thin_dams"].activate_feature(index)
    update()
    
def thin_dam_created(gdf, index, id):
    # app.model["delft3dfm"].domain.thin_dams.gdf = gdf
    while True:
        name, okay = app.gui.window.dialog_string("Edit name for new thin dam")
        if not okay:
            # Cancel was clicked
            app.map.layer["delft3dfm"].layer["thin_dams"].delete_feature(index)
            return    
        if name in app.gui.getvar("delft3dfm", "thin_dam_names"):
            app.gui.window.dialog_info("A thin dam with this name already exists !")
        else:
            break
    new_thd = gdf.loc[[index]]        
    # add "name" to gdf
    new_thd["name"] = name         
    app.model["delft3dfm"].domain.thin_dams.add(new_thd)
    # Need to update map layer because name has changed
    gdf = app.model["delft3dfm"].domain.thin_dams.gdf
    app.map.layer["delft3dfm"].layer["thin_dams"].set_data(gdf)
    nrt = len(gdf)
    app.gui.setvar("delft3dfm", "active_thin_dam", nrt - 1)
    app.model["delft3dfm"].thin_dams_changed = True
    update()
    # update_grid_snapper()

def thin_dam_modified(gdf, index, id):
    app.model["delft3dfm"].domain.thin_dams.gdf = gdf
    app.model["delft3dfm"].thin_dams_changed = True
    # update_grid_snapper()
    update()

def thin_dam_selected(index):
    app.gui.setvar("delft3dfm", "active_thin_dam", index)
    update()

def set_model_variables(*args):
    # All variables will be set
    app.model["delft3dfm"].set_model_variables()

# def update_grid_snapper():
#     snap_gdf = app.model["delft3dfm"].domain.thin_dams.snap_to_grid()
#     if len(snap_gdf) > 0:
#         app.map.layer["delft3dfm"].layer["thin_dams"].layer["snapped"].set_data(snap_gdf)

def update():
    nrt = len(app.model["delft3dfm"].domain.thin_dams.gdf)
    app.gui.setvar("delft3dfm", "nr_thin_dams", nrt)
    if app.gui.getvar("delft3dfm", "active_thin_dam" ) > nrt - 1:
        app.gui.setvar("delft3dfm", "active_thin_dam", max(nrt - 1, 0) )
    iac = app.gui.getvar("delft3dfm", "active_thin_dam")
    names = app.model["delft3dfm"].domain.thin_dams.list_names()
    app.gui.setvar("delft3dfm", "thin_dam_names", names)
    if nrt > 0:
        app.gui.setvar("delft3dfm", "thin_dam_name", names[iac])
    else:
        app.gui.setvar("delft3dfm", "thin_dam_name", "")
    app.gui.window.update()
