# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
import geopandas as gpd

from delftdashboard.app import app
from delftdashboard.operations import map

def select(*args):
    # De-activate existing layers
    map.update()
    # Activate draw layer
    app.map.layer["sfincs_hmt"].layer["weirs"].layer["polylines"].activate()
    app.map.layer["sfincs_hmt"].layer["weirs"].layer["snapped"].activate()
    update()

def deselect(*args):
    if app.model["sfincs_hmt"].weirs_changed:
        if app.model["sfincs_hmt"].domain.weirs.nr_lines == 0:
            # No weirs, so just reset the flag and return
            app.model["sfincs_hmt"].weirs_changed = False
            return
        ok = app.gui.window.dialog_yes_no("The weirs have changed. Would you like to save the changes?")
        if ok:
            save()

def load(*args):
    map.reset_cursor()
    rsp = app.gui.window.dialog_open_file("Select file ...",
                                          file_name="sfincs.weir",
                                          filter="*.weir",
                                          allow_directory_change=False)
    if rsp[0]:
        app.model["sfincs_hmt"].domain.config.set("weirfile", rsp[2]) # file name without path
        app.model["sfincs_hmt"].domain.weirs.read()
        gdf = app.model["sfincs_hmt"].domain.weirs.gdf
        app.map.layer["sfincs_hmt"].layer["weirs"].layer["polylines"].set_data(gdf)
        app.gui.setvar("sfincs_hmt", "active_weir", 0)
        update()
    app.model["sfincs_hmt"].weirs_changed = False

def import_geojson(*args):

    map.reset_cursor()

    rsp = app.gui.window.dialog_open_file("Select file ...",
                                          filter="*.geojson",
                                          allow_directory_change=False)
    if rsp[0]:
        filename = rsp[0]
        gdf = gpd.read_file(filename)
        # Extract only LineStrings
        gdf = gdf[gdf.geometry.type == "LineString"].copy()
        # Check if there are any LineStrings
        if len(gdf) == 0:
            app.gui.window.dialog_warning("No LineString geometries found in the selected file.")
            return
        merge = False
        if app.model["sfincs_hmt"].domain.weirs.nr_lines > 0:
            ok = app.gui.window.dialog_yes_no("Do you want to merge these with the existing weirs?")
            if ok:
                merge = True
        app.model["sfincs_hmt"].domain.weirs.set(gdf, merge=merge)
        app.map.layer["sfincs_hmt"].layer["weirs"].set_data(gdf)
        app.gui.setvar("sfincs_hmt", "active_weir", 0)
        app.model["sfincs_hmt"].weirs_changed = True
        update()

def save(*args):
    map.reset_cursor()
    filename = app.model["sfincs_hmt"].domain.config.get("weirfile")
    if not filename:
        filename = "sfincs.weir"
    rsp = app.gui.window.dialog_save_file("Select file ...",
                                          file_name=filename,
                                          filter="*.weir",
                                          allow_directory_change=False)
    if rsp[0]:
        app.model["sfincs_hmt"].domain.config.set("weirfile", rsp[2]) # file name without path
        app.model["sfincs_hmt"].domain.weirs.write()
    app.model["sfincs_hmt"].weirs_changed = False

def draw_weir(*args):
    app.map.layer["sfincs_hmt"].layer["weirs"].layer["polylines"].draw()

def delete_weir(*args):
    gdf = app.model["sfincs_hmt"].domain.weirs.gdf
    if len(gdf) == 0:
        return
    index = app.gui.getvar("sfincs_hmt", "weir_index")
    # Delete from map
    app.map.layer["sfincs_hmt"].layer["weirs"].layer["polylines"].delete_feature(index)
    # Delete from app
    app.model["sfincs_hmt"].domain.weirs.delete(index)
    app.model["sfincs_hmt"].weirs_changed = True
    update()

    update_grid_snapper()

def select_weir(*args):
    update()
    
def weir_created(gdf, index, id):
    """"Callback for when a weir has been drawn."""
    # Get new gdf with the new drainage structure, and update the app
    gdf_new = gdf.iloc[[index]]
    # Drop everything except geometry, and reset index to avoid issues with merging
    gdf_new = gdf_new[["geometry"]].reset_index(drop=True)
    app.model["sfincs_hmt"].domain.weirs.create(gdf_new, elevation=0.0, par1=0.6, merge=True)
    nrt = app.model["sfincs_hmt"].domain.weirs.nr_lines
    app.gui.setvar("sfincs_hmt", "weir_index", nrt - 1)
    app.model["sfincs_hmt"].weirs_changed = True
    update()
    update_grid_snapper()

def weir_modified(gdf, index, id):
    app.model["sfincs_hmt"].domain.weirs.set(gdf, merge=False)
    app.model["sfincs_hmt"].weirs_changed = True
    update_grid_snapper()

def weir_selected(index):
    app.gui.setvar("sfincs_hmt", "weir_index", index)
    update()

def edit_weir_elevation(*args):
    index = app.gui.getvar("sfincs_hmt", "weir_index")
    elevation = app.gui.getvar("sfincs_hmt", "weir_elevation")
    geom = app.model["sfincs_hmt"].domain.weirs.gdf.at[index, "geometry"]
    app.model["sfincs_hmt"].domain.weirs.data.at[index, "elevation"] = [elevation] * len(geom.coords)
    app.model["sfincs_hmt"].weirs_changed = True
    update()

def edit_weir_par1(*args):
    index = app.gui.getvar("sfincs_hmt", "weir_index")
    par1 = app.gui.getvar("sfincs_hmt", "weir_par1")
    geom = app.model["sfincs_hmt"].domain.weirs.gdf.at[index, "geometry"]
    app.model["sfincs_hmt"].domain.weirs.data.at[index, "par1"] = [par1] * len(geom.coords)
    app.model["sfincs_hmt"].weirs_changed = True
    update()

def set_model_variables(*args):
    # All variables will be set
    app.model["sfincs_hmt"].set_model_variables()

def update_grid_snapper():
    return  # Weirs are not snapped to grid for now, so just return
    snap_gdf = app.model["sfincs_hmt"].domain.weirs.snap_to_grid()
    if len(snap_gdf) > 0:
        app.map.layer["sfincs_hmt"].layer["weirs"].layer["snapped"].set_data(snap_gdf)
    else:
        app.map.layer["sfincs_hmt"].layer["weirs"].layer["snapped"].clear()

def update():
    """Called when weir data is changed, to update the GUI."""

    # Update weir list and index 
    nrt = len(app.model["sfincs_hmt"].domain.weirs.gdf)
    app.gui.setvar("sfincs_hmt", "nr_weirs", nrt)
    if app.gui.getvar("sfincs_hmt", "weir_index" ) > nrt - 1:
        app.gui.setvar("sfincs_hmt", "weir_index", max(nrt - 1, 0) )
    app.gui.setvar("sfincs_hmt", "weir_names", app.model["sfincs_hmt"].domain.weirs.list_names)

    # Check if enabling elevation and Cd editing.
    if nrt > 0:
        index = app.gui.getvar("sfincs_hmt", "weir_index")
        gdf_weir = app.model["sfincs_hmt"].domain.weirs.gdf.iloc[[index]].reset_index(drop=True)

        # Elevation
        elev = gdf_weir.at[0, "elevation"]
        app.gui.setvar("sfincs_hmt", "weir_elevation", gdf_weir.at[0, "elevation"][0])

        # Check if all values in the list are the same
        if len(set(elev)) == 1:
            # We can enable editing, and set the value to the unique value in the list
            app.gui.setvar("sfincs_hmt", "weir_enable_editing_elevation", True)
        else:
            app.gui.setvar("sfincs_hmt", "weir_enable_editing_elevation", False)

        # Par1
        par1 = gdf_weir.at[0, "par1"]
        app.gui.setvar("sfincs_hmt", "weir_par1", par1[0])

        # Check if all values in the list are the same
        if len(set(par1)) == 1:
            # We can enable editing, and set the value to the unique value in the list
            app.gui.setvar("sfincs_hmt", "weir_enable_editing_par1", True)
        else:
            app.gui.setvar("sfincs_hmt", "weir_enable_editing_par1", False)

    app.gui.window.update()
