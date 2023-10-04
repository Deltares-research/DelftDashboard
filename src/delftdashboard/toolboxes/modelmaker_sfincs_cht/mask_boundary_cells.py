# -*- coding: utf-8 -*-
"""
GUI methods for modelmaker_sfincs_cht -> mask_boundary_cells

Created on Mon May 10 12:18:09 2021

@author: Maarten van Ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations import map

def select(*args):
    # De-activate existing layers
    map.update()
    # Show the boundary polygons
    app.map.layer["modelmaker_sfincs_cht"].layer["open_boundary_polygon"].set_activity(True)
    app.map.layer["modelmaker_sfincs_cht"].layer["outflow_boundary_polygon"].set_activity(True)
    # Show the grid and mask
    app.map.layer["sfincs_cht"].layer["grid"].set_activity(True)
    app.map.layer["sfincs_cht"].layer["mask_include"].set_activity(True)
    app.map.layer["sfincs_cht"].layer["mask_open_boundary"].set_activity(True)
    app.map.layer["sfincs_cht"].layer["mask_outflow_boundary"].set_activity(True)

def draw_open_boundary_polygon(*args):
#    app.map.layer["modelmaker_sfincs_cht"].layer["open_boundary_polygon"].crs = app.crs
    app.map.layer["modelmaker_sfincs_cht"].layer["open_boundary_polygon"].draw()

def delete_open_boundary_polygon(*args):
    if len(app.toolbox["modelmaker_sfincs_cht"].open_boundary_polygon) == 0:
        return
    index = app.gui.getvar("modelmaker_sfincs_cht", "open_boundary_polygon_index")
    # or: iac = args[0]
    feature_id = app.toolbox["modelmaker_sfincs_cht"].open_boundary_polygon.loc[index, "id"]
    # Delete from map
    app.map.layer["modelmaker_sfincs_cht"].layer["open_boundary_polygon"].delete_feature(feature_id)
    # Delete from app
    app.toolbox["modelmaker_sfincs_cht"].open_boundary_polygon = app.toolbox["modelmaker_sfincs_cht"].open_boundary_polygon.drop(index).reset_index()

    # If the last polygon was deleted, set index to last available polygon
    if index > len(app.toolbox["modelmaker_sfincs_cht"].open_boundary_polygon) - 1:
        app.gui.setvar("modelmaker_sfincs_cht", "open_boundary_polygon_index", len(app.toolbox["modelmaker_sfincs_cht"].open_boundary_polygon) - 1)
    update()

def load_open_boundary_polygon(*args):
    fname = app.gui.window.dialog_open_file("Select open boundary polygon file ...", filter="*.geojson")
    if fname[0]:
        app.toolbox["modelmaker_sfincs_cht"].open_boundary_file_name = fname[2]
    app.toolbox["modelmaker_sfincs_cht"].read_open_boundary_polygon()
    app.toolbox["modelmaker_sfincs_cht"].plot_open_boundary_polygon()

def save_open_boundary_polygon(*args):
    app.toolbox["modelmaker_sfincs_cht"].write_open_boundary_polygon()

def select_open_boundary_polygon(*args):
    index = args[0]
    feature_id = app.toolbox["modelmaker_sfincs_cht"].boundary_open_polygon.loc[index, "id"]
    app.map.layer["modelmaker_sfincs_cht"].layer["open_boundary_polygon"].activate_feature(feature_id)

def open_boundary_polygon_created(gdf, index, id):
    app.toolbox["modelmaker_sfincs_cht"].open_boundary_polygon = gdf
    nrp = len(app.toolbox["modelmaker_sfincs_cht"].open_boundary_polygon)
    app.gui.setvar("modelmaker_sfincs_cht", "open_boundary_polygon_index", nrp - 1)
    update()

def open_boundary_polygon_modified(gdf, index, id):
    app.toolbox["modelmaker_sfincs_cht"].open_boundary_polygon = gdf

def open_boundary_polygon_selected(index):
    app.gui.setvar("modelmaker_sfincs_cht", "open_boundary_polygon_index", index)
    update()


def draw_outflow_boundary_polygon(*args):
    app.map.layer["modelmaker_sfincs_cht"].layer["outflow_boundary_polygon"].crs = app.crs
    app.map.layer["modelmaker_sfincs_cht"].layer["outflow_boundary_polygon"].draw()

def delete_outflow_boundary_polygon(*args):
    if len(app.toolbox["modelmaker_sfincs_cht"].outflow_boundary_polygon) == 0:
        return
    index = app.gui.getvar("modelmaker_sfincs_cht", "outflow_boundary_polygon_index")
    # or: iac = args[0]
    feature_id = app.toolbox["modelmaker_sfincs_cht"].outflow_boundary_polygon.loc[index, "id"]
    # Delete from map
    app.map.layer["modelmaker_sfincs_cht"].layer["outflow_boundary_polygon"].delete_feature(feature_id)
    # Delete from app
    app.toolbox["modelmaker_sfincs_cht"].outflow_boundary_polygon = app.toolbox["modelmaker_sfincs_cht"].outflow_boundary_polygon.drop(index).reset_index()

    # If the last polygon was deleted, set index to last available polygon
    if index > len(app.toolbox["modelmaker_sfincs_cht"].outflow_boundary_polygon) - 1:
        app.gui.setvar("modelmaker_sfincs_cht", "outflow_boundary_polygon_index", len(app.toolbox["modelmaker_sfincs_cht"].outflow_boundary_polygon) - 1)
    update()

def load_outflow_boundary_polygon(*args):
    fname = app.gui.window.dialog_open_file("Select outflow boundary polygon file ...", filter="*.geojson")
    if fname[0]:
        app.toolbox["modelmaker_sfincs_cht"].outflow_boundary_file_name = fname[2]
    app.toolbox["modelmaker_sfincs_cht"].read_outflow_boundary_polygon()
    app.toolbox["modelmaker_sfincs_cht"].plot_outflow_boundary_polygon()

def save_outflow_boundary_polygon(*args):
    app.toolbox["modelmaker_sfincs_cht"].write_outflow_boundary_polygon()

def select_outflow_boundary_polygon(*args):
    index = args[0]
    feature_id = app.toolbox["modelmaker_sfincs_cht"].outflow_boundary_polygon.loc[index, "id"]
    app.map.layer["modelmaker_sfincs_cht"].layer["outflow_boundary_polygon"].activate_feature(feature_id)

def outflow_boundary_polygon_created(gdf, index, id):
    app.toolbox["modelmaker_sfincs_cht"].outflow_boundary_polygon = gdf
    nrp = len(app.toolbox["modelmaker_sfincs_cht"].outflow_boundary_polygon)
    app.gui.setvar("modelmaker_sfincs_cht", "outflow_boundary_polygon_index", nrp - 1)
    update()

def outflow_boundary_polygon_modified(gdf, index, id):
    app.toolbox["modelmaker_sfincs_cht"].outflow_boundary_polygon = gdf

def outflow_boundary_polygon_selected(index):
    app.gui.setvar("modelmaker_sfincs_cht", "outflow_boundary_polygon_index", index)
    update()



def update():
    app.toolbox["modelmaker_sfincs_cht"].update_polygons()
    app.gui.window.update()

def update_mask(*args):
    app.toolbox["modelmaker_sfincs_cht"].update_mask()

def cut_inactive_cells(*args):
    app.toolbox["modelmaker_sfincs_cht"].cut_inactive_cells()
