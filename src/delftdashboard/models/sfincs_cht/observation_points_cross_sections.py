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
    app.map.layer["sfincs_cht"].layer["cross_sections"].layer["polylines"].activate()
    app.map.layer["sfincs_cht"].layer["cross_sections"].layer["snapped"].activate()
    update()

def deselect(*args):
    if app.model["sfincs_cht"].cross_sections_changed:
        ok = app.gui.window.dialog_yes_no("The cross sections have changed. Would you like to save the changes?")
        if ok:
            save()

def load(*args):
    map.reset_cursor()
    rsp = app.gui.window.dialog_open_file("Select file ...",
                                          file_name="sfincs.crs",
                                          filter="*.crs",
                                          allow_directory_change=False)
    if rsp[0]:
        app.model["sfincs_cht"].domain.input.variables.crsfile = rsp[2] # file name without path
        app.model["sfincs_cht"].domain.cross_sections.read()
        gdf = app.model["sfincs_cht"].domain.cross_sections.gdf
        app.map.layer["sfincs_cht"].layer["cross_sections"].layer["polylines"].set_data(gdf)
        app.gui.setvar("sfincs_cht", "active_cross_section", 0)
        update()
    app.model["sfincs_cht"].cross_sections_changed = False    

def save(*args):
    map.reset_cursor()
    filename = app.model["sfincs_cht"].domain.input.variables.crsfile
    if not filename:
        filename = "sfincs.crs"
    rsp = app.gui.window.dialog_save_file("Select file ...",
                                          file_name=filename,
                                          filter="*.crs",
                                          allow_directory_change=False)
    if rsp[0]:
        app.model["sfincs_cht"].domain.input.variables.crsfile = rsp[2] # file name without path
        app.model["sfincs_cht"].domain.cross_sections.write()
    app.model["sfincs_cht"].cross_sections_changed = False

def draw_cross_section(*args):
    app.map.layer["sfincs_cht"].layer["cross_sections"].layer["polylines"].draw()

def delete_cross_section(*args):
    gdf = app.model["sfincs_cht"].domain.cross_sections.gdf
    if len(gdf) == 0:
        return
    index = app.gui.getvar("sfincs_cht", "active_cross_section")
    # Delete from map
    app.map.layer["sfincs_cht"].layer["cross_sections"].layer["polylines"].delete_feature(index)
    # Delete from app
    app.model["sfincs_cht"].domain.cross_sections.delete(index)
    app.model["sfincs_cht"].cross_sections_changed = True
    update()

    # update_grid_snapper()

def select_cross_section_from_list(*args):
    map.reset_cursor()
    index = app.gui.getvar("sfincs_cht", "active_cross_section")
    app.map.layer["sfincs_cht"].layer["cross_sections"].layer["polylines"].activate_feature(index)
    update()
    
def edit_name(*args):
    name = app.gui.getvar("sfincs_cht", "cross_section_name")
    index = app.gui.getvar("sfincs_cht", "active_cross_section")
    gdf = app.model["sfincs_cht"].domain.cross_sections.gdf
    gdf.at[index, "name"] = name
    app.map.layer["sfincs_cht"].layer["cross_sections"].layer["polylines"].set_data(gdf)
    update()

def cross_section_created(gdf, index, id):
    name, okay = app.gui.window.dialog_string("Edit name for new cross section")
    if not okay:
        # Cancel was clicked
        return    
    if name in app.gui.getvar("sfincs_cht", "cross_section_names"):
        app.gui.window.dialog_info("A cross section with this name already exists !")
        # Keep asking until a unique name is given or cancel is clicked
        while name in app.gui.getvar("sfincs_cht", "cross_section_names"):
            name, okay = app.gui.window.dialog_string("Edit name for new cross section")
            if not okay:
                # Cancel was clicked
                return
    new_crs = gdf.loc[[index]]        
    # add "name" to gdf
    new_crs["name"] = name         
    app.model["sfincs_cht"].domain.cross_sections.add(new_crs)
    # Need to update map layer because name has changed
    gdf = app.model["sfincs_cht"].domain.cross_sections.gdf
    app.map.layer["sfincs_cht"].layer["cross_sections"].layer["polylines"].set_data(gdf)
    nrt = len(gdf)
    app.gui.setvar("sfincs_cht", "active_cross_section", nrt - 1)
    app.model["sfincs_cht"].cross_sections_changed = True
    update()
    # update_grid_snapper()

def cross_section_modified(gdf, index, id):
    app.model["sfincs_cht"].domain.cross_sections.gdf = gdf
    app.model["sfincs_cht"].cross_sections_changed = True
    # update_grid_snapper()
    update()

def cross_section_selected(index):
    app.gui.setvar("sfincs_cht", "active_cross_section", index)
    update()

def set_model_variables(*args):
    # All variables will be set
    app.model["sfincs_cht"].set_model_variables()

def update_grid_snapper():
    snap_gdf = app.model["sfincs_cht"].domain.cross_sections.snap_to_grid()
    if len(snap_gdf) > 0:
        app.map.layer["sfincs_cht"].layer["cross_sections"].layer["snapped"].set_data(snap_gdf)

def update():
    nrt = len(app.model["sfincs_cht"].domain.cross_sections.gdf)
    app.gui.setvar("sfincs_cht", "nr_cross_sections", nrt)
    if app.gui.getvar("sfincs_cht", "active_cross_section" ) > nrt - 1:
        app.gui.setvar("sfincs_cht", "active_cross_section", max(nrt - 1, 0) )
    iac = app.gui.getvar("sfincs_cht", "active_cross_section")    
    names = app.model["sfincs_cht"].domain.cross_sections.list_names()
    app.gui.setvar("sfincs_cht", "cross_section_names", names)
    if nrt > 0:
        app.gui.setvar("sfincs_cht", "cross_section_name", names[iac])
    else:
        app.gui.setvar("sfincs_cht", "cross_section_name", "")
    app.gui.window.update()
