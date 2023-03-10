# -*- coding: utf-8 -*-
"""
GUI methods for modelmaker_hurrywave -> mask_active_cells

Created on Mon May 10 12:18:09 2021

@author: Maarten van Ormondt
"""

from ddb import ddb

def select(*args):
    # De-activate existing layers
    ddb.update_map()
    # Show the mask include and exclude polygons
    ddb.map.layer["modelmaker_hurrywave"].layer["mask_include"].set_mode("active")
    ddb.map.layer["modelmaker_hurrywave"].layer["mask_exclude"].set_mode("active")
    # Show the grid and mask
    ddb.map.layer["hurrywave"].layer["grid"].set_mode("active")
    ddb.map.layer["hurrywave"].layer["mask_include"].set_mode("active")
    ddb.map.layer["hurrywave"].layer["mask_boundary"].set_mode("active")


def draw_include_polygon(*args):
    ddb.map.layer["modelmaker_hurrywave"].layer["mask_include"].crs = ddb.crs
    ddb.map.layer["modelmaker_hurrywave"].layer["mask_include"].draw()

def delete_include_polygon(*args):
    if len(ddb.toolbox["modelmaker_hurrywave"].include_polygon) == 0:
        return
    index = ddb.gui.getvar("modelmaker_hurrywave", "include_polygon_index")
    # or: iac = args[0]
    feature_id = ddb.toolbox["modelmaker_hurrywave"].include_polygon.loc[index, "id"]
    # Delete from map
    ddb.map.layer["modelmaker_hurrywave"].layer["mask_include"].delete_feature(feature_id)
    # Delete from app
    ddb.toolbox["modelmaker_hurrywave"].include_polygon = ddb.toolbox["modelmaker_hurrywave"].include_polygon.drop(index)
    # If the last polygon was deleted, set index to last available polygon
    if index > len(ddb.toolbox["modelmaker_hurrywave"].include_polygon) - 1:
        ddb.gui.setvar("modelmaker_hurrywave", "include_polygon_index", len(ddb.toolbox["modelmaker_hurrywave"].include_polygon) - 1)
    update()

def load_include_polygon(*args):
    pass

def save_include_polygon(*args):
    pass

def select_include_polygon(*args):
    index = args[0]
    feature_id = ddb.toolbox["modelmaker_hurrywave"].include_polygon.loc[index, "id"]
    ddb.map.layer["modelmaker_hurrywave"].layer["mask_include"].activate_feature(feature_id)

def include_polygon_created(gdf, index, id):
    ddb.toolbox["modelmaker_hurrywave"].include_polygon = gdf
    nrp = len(ddb.toolbox["modelmaker_hurrywave"].include_polygon)
    ddb.gui.setvar("modelmaker_hurrywave", "include_polygon_index", nrp - 1)
    update()

def include_polygon_modified(gdf, index, id):
    ddb.toolbox["modelmaker_hurrywave"].include_polygon = gdf

def include_polygon_selected(index):
    ddb.gui.setvar("modelmaker_hurrywave", "include_polygon_index", index)
    update()

def draw_exclude_polygon(*args):
    ddb.map.layer["modelmaker_hurrywave"].layer["mask_exclude"].draw()

def delete_exclude_polygon(*args):
    if len(ddb.toolbox["modelmaker_hurrywave"].exclude_polygon) == 0:
        return
    index = ddb.gui.getvar("modelmaker_hurrywave", "exclude_polygon_index")
    # or: iac = args[0]
    feature_id = ddb.toolbox["modelmaker_hurrywave"].exclude_polygon.loc[index, "id"]
    # Delete from map
    ddb.map.layer["modelmaker_hurrywave"].layer["mask_exclude"].delete_feature(feature_id)
    # Delete from app
    ddb.toolbox["modelmaker_hurrywave"].exclude_polygon = ddb.toolbox["modelmaker_hurrywave"].exclude_polygon.drop(index)
    # If the last polygon was deleted, set index to last available polygon
    if index > len(ddb.toolbox["modelmaker_hurrywave"].exclude_polygon) - 1:
        ddb.gui.setvar("modelmaker_hurrywave", "exclude_polygon_index", len(ddb.toolbox["modelmaker_hurrywave"].exclude_polygon) - 1)
    update()

def load_exclude_polygon(*args):
    pass

def save_exclude_polygon(*args):
    pass

def select_exclude_polygon(*args):
    index = args[0]
    feature_id = ddb.toolbox["modelmaker_hurrywave"].exclude_polygon.loc[index, "id"]
    ddb.map.layer["modelmaker_hurrywave"].layer["mask_exclude"].activate_feature(feature_id)

def exclude_polygon_created(gdf, index, id):
    ddb.toolbox["modelmaker_hurrywave"].exclude_polygon = gdf
    nrp = len(ddb.toolbox["modelmaker_hurrywave"].exclude_polygon)
    ddb.gui.setvar("modelmaker_hurrywave", "exclude_polygon_index", nrp - 1)
    update()

def exclude_polygon_modified(gdf, index, id):
    ddb.toolbox["modelmaker_hurrywave"].exclude_polygon = gdf

def exclude_polygon_selected(index):
    ddb.gui.setvar("modelmaker_hurrywave", "exclude_polygon_index", index)
    update()

def update():
    nrp = len(ddb.toolbox["modelmaker_hurrywave"].include_polygon)
    incnames = []
    for ip in range(nrp):
        incnames.append(str(ip + 1))
    ddb.gui.setvar("modelmaker_hurrywave", "nr_include_polygons", nrp)
    ddb.gui.setvar("modelmaker_hurrywave", "include_polygon_names", incnames)

    nrp = len(ddb.toolbox["modelmaker_hurrywave"].exclude_polygon)
    excnames = []
    for ip in range(nrp):
        excnames.append(str(ip + 1))
    ddb.gui.setvar("modelmaker_hurrywave", "nr_exclude_polygons", nrp)
    ddb.gui.setvar("modelmaker_hurrywave", "exclude_polygon_names", excnames)

    ddb.gui.window.update()

def update_mask(*args):
    ddb.toolbox["modelmaker_hurrywave"].update_mask()
