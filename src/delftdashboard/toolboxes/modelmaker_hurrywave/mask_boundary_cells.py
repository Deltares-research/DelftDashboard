# -*- coding: utf-8 -*-
"""
GUI methods for modelmaker_hurrywave -> mask_boundary_cells

Created on Mon May 10 12:18:09 2021

@author: Maarten van Ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations import map

def select(*args):
    # De-activate existing layers
    map.update()
    # Show the boundary polygons
    app.map.layer["modelmaker_hurrywave"].layer["mask_boundary"].set_mode("active")
    # Show the grid and mask
    app.map.layer["hurrywave"].layer["grid"].set_mode("active")
    app.map.layer["hurrywave"].layer["mask_include"].set_mode("active")
    app.map.layer["hurrywave"].layer["mask_boundary"].set_mode("active")

def draw_boundary_polygon(*args):
    app.map.layer["modelmaker_hurrywave"].layer["mask_boundary"].crs = app.crs
    app.map.layer["modelmaker_hurrywave"].layer["mask_boundary"].draw()

def delete_boundary_polygon(*args):
    if len(app.toolbox["modelmaker_hurrywave"].boundary_polygon) == 0:
        return
    index = app.gui.getvar("modelmaker_hurrywave", "boundary_polygon_index")
    # or: iac = args[0]
    feature_id = app.toolbox["modelmaker_hurrywave"].boundary_polygon.loc[index, "id"]
    # Delete from map
    app.map.layer["modelmaker_hurrywave"].layer["mask_boundary"].delete_feature(feature_id)
    # Delete from app
    app.toolbox["modelmaker_hurrywave"].boundary_polygon = app.toolbox["modelmaker_hurrywave"].boundary_polygon.drop(index).reset_index()

    # If the last polygon was deleted, set index to last available polygon
    if index > len(app.toolbox["modelmaker_hurrywave"].boundary_polygon) - 1:
        app.gui.setvar("modelmaker_hurrywave", "boundary_polygon_index", len(app.toolbox["modelmaker_hurrywave"].boundary_polygon) - 1)
    update()

def load_boundary_polygon(*args):
    fname = app.gui.window.dialog_open_file("Select boundary polygon file ...", filter="*.geojson")
    if fname[0]:
        app.toolbox["modelmaker_hurrywave"].boundary_file_name = fname[2]
    app.toolbox["modelmaker_hurrywave"].read_boundary_polygon()
    app.toolbox["modelmaker_hurrywave"].plot_boundary_polygon()

def save_boundary_polygon(*args):
    app.toolbox["modelmaker_hurrywave"].write_boundary_polygon()

def select_boundary_polygon(*args):
    index = args[0]
    feature_id = app.toolbox["modelmaker_hurrywave"].boundary_polygon.loc[index, "id"]
    app.map.layer["modelmaker_hurrywave"].layer["mask_boundary"].activate_feature(feature_id)

def boundary_polygon_created(gdf, index, id):
    app.toolbox["modelmaker_hurrywave"].boundary_polygon = gdf
    nrp = len(app.toolbox["modelmaker_hurrywave"].boundary_polygon)
    app.gui.setvar("modelmaker_hurrywave", "boundary_polygon_index", nrp - 1)
    update()

def boundary_polygon_modified(gdf, index, id):
    app.toolbox["modelmaker_hurrywave"].boundary_polygon = gdf

def boundary_polygon_selected(index):
    app.gui.setvar("modelmaker_hurrywave", "boundary_polygon_index", index)
    update()

def update():
    app.toolbox["modelmaker_hurrywave"].update_polygons()
    app.gui.window.update()
    # nrp = len(app.toolbox["modelmaker_hurrywave"].boundary_polygon)
    # incnames = []
    # for ip in range(nrp):
    #     incnames.append(str(ip + 1))
    # app.gui.setvar("modelmaker_hurrywave", "nr_boundary_polygons", nrp)
    # app.gui.setvar("modelmaker_hurrywave", "boundary_polygon_names", incnames)
    # app.gui.window.update()

def update_mask(*args):
    app.toolbox["modelmaker_hurrywave"].update_mask()
