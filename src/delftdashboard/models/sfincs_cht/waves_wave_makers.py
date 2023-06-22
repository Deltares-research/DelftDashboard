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
    app.map.layer["sfincs_cht"].layer["wave_makers"].set_mode("active")
    update()

def set_model_variables(*args):
    # All variables will be set
    app.model["sfincs_cht"].set_model_variables()

def add_on_map(*args):
    app.map.layer["sfincs_cht"].layer["wave_makers"].draw()

def select_from_list(*args):
    index = args[0]
    feature_id = app.model["sfincs_cht"].domain.wave_makers.gdf.loc[index, "id"]
    app.map.layer["sfincs_cht"].layer["wave_makers"].activate_feature(feature_id)

def delete_from_list(*args):
    map.reset_cursor()
    index = app.gui.getvar("sfincs_cht", "active_wave_maker")
    app.model["sfincs_cht"].domain.wave_makers.delete_polyline(index)
    gdf = app.model["sfincs_cht"].domain.wave_makers.gdf
    index = max(min(index, len(gdf) - 1), 0)
    app.model["sfincs_cht"].plot_wave_makers()
    app.gui.setvar("sfincs_cht", "active_wave_maker", index)
    update()

def wave_maker_created(gdf, index, id):
    app.model["sfincs_cht"].domain.wave_makers.gdf = gdf
    nrp = len(app.model["sfincs_cht"].domain.wave_makers.gdf)
    app.gui.setvar("sfincs_cht", "active_wave_maker", nrp - 1)
    update()

def wave_maker_modified(gdf, index, id):
    app.model["sfincs_cht"].domain.wave_makers.gdf = gdf

def wave_maker_selected(index):
    app.gui.setvar("sfincs_cht", "active_wave_maker", index)
    update()

def load(*args):
    map.reset_cursor()
    rsp = app.gui.window.dialog_open_file("Select file ...",
                                          file_name="sfincs.wvm",
                                          filter="*.wvm",
                                          allow_directory_change=False)
    if rsp[0]:
        app.model["sfincs_cht"].domain.input.variables.wvmfile = rsp[2] # file name without path
        app.model["sfincs_cht"].domain.wave_makers.read()
        app.gui.setvar("sfincs_cht", "active_wave_maker", 0)
        app.model["sfincs_cht"].plot_wave_makers()
        update()

def save(*args):
    app.model["sfincs_cht"].domain.input.variables.wvmfile = "sfincs.wvm"
    app.model["sfincs_cht"].domain.wave_makers.write()

def update():
    gdf = app.model["sfincs_cht"].domain.wave_makers.gdf
    app.gui.setvar("sfincs_cht", "wave_maker_names", app.model["sfincs_cht"].domain.wave_makers.list_names())
    app.gui.setvar("sfincs_cht", "nr_wave_makers", len(gdf))
    app.gui.window.update()
    
