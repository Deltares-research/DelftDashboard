# -*- coding: utf-8 -*-
"""
GUI methods for modelmaker_hurrywave -> mask_boundary_cells

Created on Mon May 10 12:18:09 2021

@author: Maarten van Ormondt
"""

from ddb import ddb

def select(*args):
    # De-activate existing layers
    ddb.update_map()
    # Show the mask boundary layer
    ddb.map.layer["modelmaker_hurrywave"].layer["mask_boundary"].set_mode("active")

def draw_boundary_polygon(*args):
    ddb.map.layer["modelmaker_hurrywave"].layer["mask_boundary"].draw()

def delete_boundary_polygon(*args):
    if len(ddb.toolbox["modelmaker_hurrywave"].boundary_polygon) == 0:
        return
    index = ddb.gui.getvar("modelmaker_hurrywave", "boundary_polygon_index")
    # or: iac = args[0]
    feature_id = ddb.toolbox["modelmaker_hurrywave"].boundary_polygon.loc[index, "id"]
    # Delete from map
    ddb.map.layer["modelmaker_hurrywave"].layer["mask_boundary"].delete_feature(feature_id)
    # Delete from app
    ddb.toolbox["modelmaker_hurrywave"].boundary_polygon = ddb.toolbox["modelmaker_hurrywave"].boundary_polygon.drop(index)
    # If the last polygon was deleted, set index to last available polygon
    if index > len(ddb.toolbox["modelmaker_hurrywave"].boundary_polygon) - 1:
        ddb.gui.setvar("modelmaker_hurrywave", "boundary_polygon_index", len(ddb.toolbox["modelmaker_hurrywave"].boundary_polygon) - 1)
    update()

def load_boundary_polygon(*args):
    pass

def save_boundary_polygon(*args):
    pass

def select_boundary_polygon(*args):
    index = args[0]
    feature_id = ddb.toolbox["modelmaker_hurrywave"].boundary_polygon.loc[index, "id"]
    ddb.map.layer["modelmaker_hurrywave"].layer["mask_boundary"].activate_feature(feature_id)

def boundary_polygon_created(gdf, index, id):
    ddb.toolbox["modelmaker_hurrywave"].boundary_polygon = gdf
    nrp = len(ddb.toolbox["modelmaker_hurrywave"].boundary_polygon)
    ddb.gui.setvar("modelmaker_hurrywave", "boundary_polygon_index", nrp - 1)
    update()

def boundary_polygon_modified(gdf, index, id):
    ddb.toolbox["modelmaker_hurrywave"].boundary_polygon = gdf

def boundary_polygon_selected(index):
    ddb.gui.setvar("modelmaker_hurrywave", "boundary_polygon_index", index)
    update()


def update():
    nrp = len(ddb.toolbox["modelmaker_hurrywave"].boundary_polygon)
    incnames = []
    for ip in range(nrp):
        incnames.append(str(ip + 1))
    ddb.gui.setvar("modelmaker_hurrywave", "nr_boundary_polygons", nrp)
    ddb.gui.setvar("modelmaker_hurrywave", "boundary_polygon_names", incnames)
    ddb.gui.window.update()

def update_mask(*args):
    ddb.toolbox["modelmaker_hurrywave"].update_mask()
