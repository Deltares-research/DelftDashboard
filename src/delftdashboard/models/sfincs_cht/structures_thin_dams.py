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
    update()
    update_grid_snapper()

def select_thin_dam(*args):
    pass
    
def thin_dam_created(gdf, index, id):
    app.model["sfincs_cht"].domain.thin_dams.gdf = gdf
    nrt = len(gdf)
    app.gui.setvar("sfincs_cht", "thin_dam_index", nrt - 1)
    update()
    update_grid_snapper()

def thin_dam_modified(gdf, index, id):
    app.model["sfincs_cht"].domain.thin_dams.gdf = gdf
    update_grid_snapper()

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
