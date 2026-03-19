# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
import geopandas as gpd

from delftdashboard.app import app
from delftdashboard.operations import map

def select(*args):
    # De-activate() existing layers
    map.update()
    app.map.layer["sfincs_hmt"].layer["wave_makers"].activate()
    update()

def deselect(*args):
    """Called when leaving the wave makers tab. If there are unsaved changes, ask the user if they want to save."""
    if app.model["sfincs_hmt"].wave_makers_changed:
        if app.model["sfincs_hmt"].domain.wave_makers.nr_lines == 0:
            # No wave makers, so just reset the flag and return
            app.model["sfincs_hmt"].wave_makers_changed = False
            return
        ok = app.gui.window.dialog_yes_no("The wave makers have changed. Would you like to save the changes?")
        if ok:
            save()

def set_model_variables(*args):
    # All variables will be set
    app.model["sfincs_hmt"].set_model_variables()

def add_on_map(*args):
    app.map.layer["sfincs_hmt"].layer["wave_makers"].draw()

def select_from_list(*args):
    index = args[0]
    feature_id = app.model["sfincs_hmt"].domain.wave_makers.gdf.loc[index, "id"]
    app.map.layer["sfincs_hmt"].layer["wave_makers"].activate_feature(feature_id)

def delete_from_list(*args):
    map.reset_cursor()
    index = app.gui.getvar("sfincs_hmt", "active_wave_maker")
    app.model["sfincs_hmt"].domain.wave_makers.delete(index)
    gdf = app.model["sfincs_hmt"].domain.wave_makers.gdf
    index = max(min(index, len(gdf) - 1), 0)
    app.map.layer["sfincs_hmt"].layer["wave_makers"].set_data(gdf)
    app.gui.setvar("sfincs_hmt", "active_wave_maker", index)
    app.model["sfincs_hmt"].wave_makers_changed = True
    update()

def wave_maker_created(gdf, index, id):
    app.model["sfincs_hmt"].domain.wave_makers.set(gdf, merge=False)
    nrp = len(app.model["sfincs_hmt"].domain.wave_makers.gdf)
    app.gui.setvar("sfincs_hmt", "active_wave_maker", nrp - 1)
    app.model["sfincs_hmt"].wave_makers_changed = True
    update()

def wave_maker_modified(gdf, index, id):
    app.model["sfincs_hmt"].domain.wave_makers.set(gdf, merge=False)
    app.model["sfincs_hmt"].wave_makers_changed = True

def wave_maker_selected(index):
    app.gui.setvar("sfincs_hmt", "active_wave_maker", index)
    update()

def load(*args):
    map.reset_cursor()
    rsp = app.gui.window.dialog_open_file("Select file ...",
                                          file_name="sfincs.wvm",
                                          filter="*.wvm",
                                          allow_directory_change=False)
    if rsp[0]:
        app.model["sfincs_hmt"].domain.config.set("wvmfile", rsp[2]) # file name without path
        app.model["sfincs_hmt"].domain.wave_makers.read()
        gdf = app.model["sfincs_hmt"].domain.wave_makers.gdf
        app.map.layer["sfincs_hmt"].layer["wave_makers"].set_data(gdf)
        app.gui.setvar("sfincs_hmt", "active_wave_maker", 0)
        app.model["sfincs_hmt"].wave_makers_changed = False
        update()

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
        app.model["sfincs_hmt"].domain.wave_makers.set(gdf, merge=False)
        app.map.layer["sfincs_hmt"].layer["wave_makers"].set_data(gdf)
        app.gui.setvar("sfincs_hmt", "active_wave_maker", 0)
        app.model["sfincs_hmt"].wave_makers_changed = True
        update()

def save(*args):
    filename = app.model["sfincs_hmt"].domain.config.get("wvmfile")
    if not filename:
        filename = "sfincs.wvm"
    rsp = app.gui.window.dialog_save_file("Select file ...",
                                          file_name=filename,
                                          filter="*.wvm",
                                          allow_directory_change=False)
    if rsp[0]:
        app.model["sfincs_hmt"].domain.config.set("wvmfile", rsp[2]) # file name without path
        app.model["sfincs_hmt"].domain.wave_makers.write()
    app.model["sfincs_hmt"].wave_makers_changed = False

def update():
    gdf = app.model["sfincs_hmt"].domain.wave_makers.gdf
    app.gui.setvar("sfincs_hmt", "wave_maker_names", app.model["sfincs_hmt"].domain.wave_makers.list_names)
    app.gui.setvar("sfincs_hmt", "nr_wave_makers", len(gdf))
    app.gui.window.update()
    
