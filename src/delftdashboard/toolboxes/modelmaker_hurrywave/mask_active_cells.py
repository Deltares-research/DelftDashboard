# -*- coding: utf-8 -*-
"""
GUI methods for modelmaker_hurrywave -> mask_active_cells

Created on Mon May 10 12:18:09 2021

@author: Maarten van Ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations import map

def select(*args):
    # De-activate() existing layers
    map.update()
    # Show the mask include and exclude polygons
    app.map.layer["modelmaker_hurrywave"].layer["mask_include"].activate()
    app.map.layer["modelmaker_hurrywave"].layer["mask_exclude"].activate()
    # Show the grid and mask
    app.map.layer["hurrywave"].layer["grid"].activate()
    app.map.layer["hurrywave"].layer["mask_include"].activate()
    app.map.layer["hurrywave"].layer["mask_boundary"].activate()

def draw_include_polygon(*args):
    app.map.layer["modelmaker_hurrywave"].layer["mask_include"].crs = app.crs
    app.map.layer["modelmaker_hurrywave"].layer["mask_include"].draw()

def delete_include_polygon(*args):
    if len(app.toolbox["modelmaker_hurrywave"].include_polygon) == 0:
        return
    index = app.gui.getvar("modelmaker_hurrywave", "include_polygon_index")
    # or: iac = args[0]
    feature_id = app.toolbox["modelmaker_hurrywave"].include_polygon.loc[index, "id"]
    # Delete from map
    app.map.layer["modelmaker_hurrywave"].layer["mask_include"].delete_feature(feature_id)
    # Delete from app
    app.toolbox["modelmaker_hurrywave"].include_polygon = app.toolbox["modelmaker_hurrywave"].include_polygon.drop(index).reset_index()

    # If the last polygon was deleted, set index to last available polygon
    if index > len(app.toolbox["modelmaker_hurrywave"].include_polygon) - 1:
        app.gui.setvar("modelmaker_hurrywave", "include_polygon_index", len(app.toolbox["modelmaker_hurrywave"].include_polygon) - 1)
    update()

def load_include_polygon(*args):
    fname = app.gui.window.dialog_open_file("Select include polygon file ...", filter="*.geojson")
    if fname[0]:
        app.toolbox["modelmaker_hurrywave"].include_file_name = fname[2]
    app.toolbox["modelmaker_hurrywave"].read_include_polygon()
    app.toolbox["modelmaker_hurrywave"].plot_include_polygon()

def save_include_polygon(*args):
    app.toolbox["modelmaker_hurrywave"].write_include_polygon()

def select_include_polygon(*args):
    index = args[0]
    feature_id = app.toolbox["modelmaker_hurrywave"].include_polygon.loc[index, "id"]
    app.map.layer["modelmaker_hurrywave"].layer["mask_include"].activate_feature(feature_id)

def include_polygon_created(gdf, index, id):
    app.toolbox["modelmaker_hurrywave"].include_polygon = gdf
    nrp = len(app.toolbox["modelmaker_hurrywave"].include_polygon)
    app.gui.setvar("modelmaker_hurrywave", "include_polygon_index", nrp - 1)
    update()

def include_polygon_modified(gdf, index, id):
    app.toolbox["modelmaker_hurrywave"].include_polygon = gdf

def include_polygon_selected(index):
    app.gui.setvar("modelmaker_hurrywave", "include_polygon_index", index)
    update()

def draw_exclude_polygon(*args):
    app.map.layer["modelmaker_hurrywave"].layer["mask_exclude"].draw()

def delete_exclude_polygon(*args):
    if len(app.toolbox["modelmaker_hurrywave"].exclude_polygon) == 0:
        return
    index = app.gui.getvar("modelmaker_hurrywave", "exclude_polygon_index")
    # or: iac = args[0]
    feature_id = app.toolbox["modelmaker_hurrywave"].exclude_polygon.loc[index, "id"]
    # Delete from map
    app.map.layer["modelmaker_hurrywave"].layer["mask_exclude"].delete_feature(feature_id)
    # Delete from app
    app.toolbox["modelmaker_hurrywave"].exclude_polygon = app.toolbox["modelmaker_hurrywave"].exclude_polygon.drop(index).reset_index()
    # If the last polygon was deleted, set index to last available polygon
    if index > len(app.toolbox["modelmaker_hurrywave"].exclude_polygon) - 1:
        app.gui.setvar("modelmaker_hurrywave", "exclude_polygon_index", len(app.toolbox["modelmaker_hurrywave"].exclude_polygon) - 1)
    update()

def load_exclude_polygon(*args):
    fname = app.gui.window.dialog_open_file("Select exclude polygon file ...", filter="*.geojson")
    if fname[0]:
        app.toolbox["modelmaker_hurrywave"].exclude_file_name = fname[2]
    app.toolbox["modelmaker_hurrywave"].read_exclude_polygon()
    app.toolbox["modelmaker_hurrywave"].plot_exclude_polygon()

def save_exclude_polygon(*args):
    app.toolbox["modelmaker_hurrywave"].write_include_polygon()

def select_exclude_polygon(*args):
    index = args[0]
    feature_id = app.toolbox["modelmaker_hurrywave"].exclude_polygon.loc[index, "id"]
    app.map.layer["modelmaker_hurrywave"].layer["mask_exclude"].activate_feature(feature_id)

def exclude_polygon_created(gdf, index, id):
    app.toolbox["modelmaker_hurrywave"].exclude_polygon = gdf
    nrp = len(app.toolbox["modelmaker_hurrywave"].exclude_polygon)
    app.gui.setvar("modelmaker_hurrywave", "exclude_polygon_index", nrp - 1)
    update()

def exclude_polygon_modified(gdf, index, id):
    app.toolbox["modelmaker_hurrywave"].exclude_polygon = gdf

def exclude_polygon_selected(index):
    app.gui.setvar("modelmaker_hurrywave", "exclude_polygon_index", index)
    update()

def update():
    app.toolbox["modelmaker_hurrywave"].update_polygons()
    app.gui.window.update()

def update_mask(*args):
    app.toolbox["modelmaker_hurrywave"].update_mask()


