# -*- coding: utf-8 -*-
"""
GUI methods for modelmaker_sfincs_cht -> mask_active_cells

Created on Mon May 10 12:18:09 2021

@author: Maarten van Ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations import map

def select(*args):
    # De-activate() existing layers
    map.update()
    # Show the mask include and exclude polygons
    app.map.layer["modelmaker_sfincs_cht"].layer["include_polygon_snapwave"].activate()
    app.map.layer["modelmaker_sfincs_cht"].layer["exclude_polygon_snapwave"].activate()
    # Show the grid and mask
    app.map.layer["sfincs_cht"].layer["grid"].activate()
    app.map.layer["sfincs_cht"].layer["mask_include_snapwave"].activate()

def draw_include_polygon_snapwave(*args):
    app.map.layer["modelmaker_sfincs_cht"].layer["include_polygon_snapwave"].crs = app.crs
    app.map.layer["modelmaker_sfincs_cht"].layer["include_polygon_snapwave"].draw()

def delete_include_polygon_snapwave(*args):
    if len(app.toolbox["modelmaker_sfincs_cht"].include_polygon_snapwave) == 0:
        return
    index = app.gui.getvar("modelmaker_sfincs_cht", "include_polygon_index_snapwave")
    # or: iac = args[0]
    feature_id = app.toolbox["modelmaker_sfincs_cht"].include_polygon_snapwave.loc[index, "id"]
    # Delete from map
    app.map.layer["modelmaker_sfincs_cht"].layer["include_polygon_snapwave"].delete_feature(feature_id)
    # Delete from app
    app.toolbox["modelmaker_sfincs_cht"].include_polygon_snapwave = app.toolbox["modelmaker_sfincs_cht"].include_polygon_snapwave.drop(index).reset_index()

    # If the last polygon was deleted, set index to last available polygon
    if index > len(app.toolbox["modelmaker_sfincs_cht"].include_polygon_snapwave) - 1:
        app.gui.setvar("modelmaker_sfincs_cht", "include_polygon_index_snapwave", len(app.toolbox["modelmaker_sfincs_cht"].include_polygon_snapwave) - 1)
    update()

def load_include_polygon_snapwave(*args):
    fname = app.gui.window.dialog_open_file("Select include polygon file ...", filter="*.geojson")
    if fname[0]:
        app.toolbox["modelmaker_sfincs_cht"].include_file_name_snapwave = fname[2]
    app.toolbox["modelmaker_sfincs_cht"].read_include_polygon_snapwave()
    app.toolbox["modelmaker_sfincs_cht"].plot_include_polygon_snapwave()

def save_include_polygon_snapwave(*args):
    app.toolbox["modelmaker_sfincs_cht"].write_include_polygon_snapwave()

def select_include_polygon_snapwave(*args):
    index = args[0]
    feature_id = app.toolbox["modelmaker_sfincs_cht"].include_polygon_snapwave.loc[index, "id"]
    app.map.layer["modelmaker_sfincs_cht"].layer["include_polygon_snapwave"].activate_feature(feature_id)

def include_polygon_created_snapwave(gdf, index, id):
    app.toolbox["modelmaker_sfincs_cht"].include_polygon_snapwave = gdf
    nrp = len(app.toolbox["modelmaker_sfincs_cht"].include_polygon_snapwave)
    app.gui.setvar("modelmaker_sfincs_cht", "include_polygon_index_snapwave", nrp - 1)
    update()

def include_polygon_modified_snapwave(gdf, index, id):
    app.toolbox["modelmaker_sfincs_cht"].include_polygon_snapwave = gdf

def include_polygon_selected_snapwave(index):
    app.gui.setvar("modelmaker_sfincs_cht", "include_polygon_index_snapwave", index)
    update()

def draw_exclude_polygon_snapwave(*args):
    app.map.layer["modelmaker_sfincs_cht"].layer["include_polygon_snapwave"].crs = app.crs
    app.map.layer["modelmaker_sfincs_cht"].layer["exclude_polygon_snapwave"].draw()

def delete_exclude_polygon_snapwave(*args):
    if len(app.toolbox["modelmaker_sfincs_cht"].exclude_polygon_snapwave) == 0:
        return
    index = app.gui.getvar("modelmaker_sfincs_cht", "exclude_polygon_index_snapwave")
    # or: iac = args[0]
    feature_id = app.toolbox["modelmaker_sfincs_cht"].exclude_polygon_snapwave.loc[index, "id"]
    # Delete from map
    app.map.layer["modelmaker_sfincs_cht"].layer["exclude_polygon_snapwave"].delete_feature(feature_id)
    # Delete from app
    app.toolbox["modelmaker_sfincs_cht"].exclude_polygon_snapwave = app.toolbox["modelmaker_sfincs_cht"].exclude_polygon_snapwave.drop(index).reset_index()
    # If the last polygon was deleted, set index to last available polygon
    if index > len(app.toolbox["modelmaker_sfincs_cht"].exclude_polygon_snapwave) - 1:
        app.gui.setvar("modelmaker_sfincs_cht", "exclude_polygon_index_snapwave", len(app.toolbox["modelmaker_sfincs_cht"].exclude_polygon_snapwave) - 1)
    update()

def load_exclude_polygon_snapwave(*args):
    fname = app.gui.window.dialog_open_file("Select exclude polygon file ...", filter="*.geojson")
    if fname[0]:
        app.toolbox["modelmaker_sfincs_cht"].exclude_file_name_snapwave = fname[2]
    app.toolbox["modelmaker_sfincs_cht"].read_exclude_polygon_snapwave()
    app.toolbox["modelmaker_sfincs_cht"].plot_exclude_polygon_snapwave()

def save_exclude_polygon_snapwave(*args):
    app.toolbox["modelmaker_sfincs_cht"].write_exclude_polygon_snapwave()

def select_exclude_polygon_snapwave(*args):
    index = args[0]
    feature_id = app.toolbox["modelmaker_sfincs_cht"].exclude_polygon_snapwave.loc[index, "id"]
    app.map.layer["modelmaker_sfincs_cht"].layer["exclude_polygon_snapwave"].activate_feature(feature_id)

def exclude_polygon_created_snapwave(gdf, index, id):
    app.toolbox["modelmaker_sfincs_cht"].exclude_polygon_snapwave = gdf
    nrp = len(app.toolbox["modelmaker_sfincs_cht"].exclude_polygon_snapwave)
    app.gui.setvar("modelmaker_sfincs_cht", "exclude_polygon_index_snapwave", nrp - 1)
    update()

def exclude_polygon_modified_snapwave(gdf, index, id):
    app.toolbox["modelmaker_sfincs_cht"].exclude_polygon_snapwave = gdf

def exclude_polygon_selected_snapwave(index):
    app.gui.setvar("modelmaker_sfincs_cht", "exclude_polygon_index_snapwave", index)
    update()

def update():
    app.toolbox["modelmaker_sfincs_cht"].update_polygons()
    app.gui.window.update()

def update_mask(*args):
    app.toolbox["modelmaker_sfincs_cht"].update_mask_snapwave()

def cut_inactive_cells(*args):
    app.toolbox["modelmaker_sfincs_cht"].cut_inactive_cells()

