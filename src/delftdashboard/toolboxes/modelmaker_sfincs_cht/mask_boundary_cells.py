# -*- coding: utf-8 -*-
"""
GUI methods for modelmaker_sfincs_cht -> mask_boundary_cells

Created on Mon May 10 12:18:09 2021

@author: Maarten van Ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations import map

def select(*args):
    # De-activate() existing layers
    map.update()
    # Show the boundary polygons
    app.map.layer["modelmaker_sfincs_cht"].layer["open_boundary_polygon"].activate()
    app.map.layer["modelmaker_sfincs_cht"].layer["outflow_boundary_polygon"].activate()
    # Show the grid and mask
    app.map.layer["sfincs_cht"].layer["grid"].activate()
    app.map.layer["sfincs_cht"].layer["mask"].activate()
    update()

def draw_open_boundary_polygon(*args):
#    app.map.layer["modelmaker_sfincs_cht"].layer["open_boundary_polygon"].crs = app.crs
    app.map.layer["modelmaker_sfincs_cht"].layer["open_boundary_polygon"].draw()

def delete_open_boundary_polygon(*args):
    if len(app.toolbox["modelmaker_sfincs_cht"].open_boundary_polygon) == 0:
        return
    index = app.gui.getvar("modelmaker_sfincs_cht", "open_boundary_polygon_index")
    # Delete from map
    gdf = app.map.layer["modelmaker_sfincs_cht"].layer["open_boundary_polygon"].delete_feature(index)
    app.toolbox["modelmaker_sfincs_cht"].open_boundary_polygon = gdf
    update()

def load_open_boundary_polygon(*args):
    full_name, path, name, ext, fltr = app.gui.window.dialog_open_file("Select open boundary polygon file ...", filter="*.geojson")
    if not full_name:
        return
    append = False
    if app.gui.getvar("modelmaker_sfincs_cht", "nr_open_boundary_polygons"):
        append = app.gui.window.dialog_yes_no("Add to existing open boundary polygons?", " ")
    app.toolbox["modelmaker_sfincs_cht"].read_open_boundary_polygon(full_name, append)
    app.toolbox["modelmaker_sfincs_cht"].plot_open_boundary_polygon()
    update()


def save_open_boundary_polygon(*args):
    app.toolbox["modelmaker_sfincs_cht"].write_open_boundary_polygon()

def select_open_boundary_polygon(*args):
    index = args[0]
    app.map.layer["modelmaker_sfincs_cht"].layer["open_boundary_polygon"].activate_feature(index)

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
    # Delete from map
    gdf = app.map.layer["modelmaker_sfincs_cht"].layer["outflow_boundary_polygon"].delete_feature(index)
    app.toolbox["modelmaker_sfincs_cht"].outflow_boundary_polygon = gdf
    update()

def load_outflow_boundary_polygon(*args):
    full_name, path, name, ext, fltr = app.gui.window.dialog_open_file("Select outflow boundary polygon file ...", filter="*.geojson")
    if not full_name:
        return
    append = False
    if app.gui.getvar("modelmaker_sfincs_cht", "nr_outflow_boundary_polygons"):
        append = app.gui.window.dialog_yes_no("Add to existing outflow boundary polygons?", " ")
    app.toolbox["modelmaker_sfincs_cht"].read_outflow_boundary_polygon(full_name, append)
    app.toolbox["modelmaker_sfincs_cht"].plot_outflow_boundary_polygon()
    update()

def save_outflow_boundary_polygon(*args):
    app.toolbox["modelmaker_sfincs_cht"].write_outflow_boundary_polygon()

def select_outflow_boundary_polygon(*args):
    index = args[0]
    app.map.layer["modelmaker_sfincs_cht"].layer["outflow_boundary_polygon"].activate_feature(index)

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
    # Open
    nrp = len(app.toolbox["modelmaker_sfincs_cht"].open_boundary_polygon)
    names = []
    for ip in range(nrp):
        names.append(str(ip + 1))
    app.gui.setvar("modelmaker_sfincs_cht", "nr_open_boundary_polygons", nrp)
    app.gui.setvar("modelmaker_sfincs_cht", "open_boundary_polygon_names", names)
    index = app.gui.getvar("modelmaker_sfincs_cht", "open_boundary_polygon_index")
    if index > nrp - 1:
        index = max(nrp - 1, 0)
    app.gui.setvar("modelmaker_sfincs_cht", "open_boundary_polygon_index", index)

    # Outflow
    nrp = len(app.toolbox["modelmaker_sfincs_cht"].outflow_boundary_polygon)
    names = []
    for ip in range(nrp):
        names.append(str(ip + 1))
    app.gui.setvar("modelmaker_sfincs_cht", "nr_outflow_boundary_polygons", nrp)
    app.gui.setvar("modelmaker_sfincs_cht", "outflow_boundary_polygon_names", names)
    index = app.gui.getvar("modelmaker_sfincs_cht", "outflow_boundary_polygon_index")
    if index > nrp - 1:
        index = max(nrp - 1, 0)
    app.gui.setvar("modelmaker_sfincs_cht", "outflow_boundary_polygon_index", index)
    # Update GUI
    app.gui.window.update()

def update_mask(*args):
    app.toolbox["modelmaker_sfincs_cht"].update_mask()

def cut_inactive_cells(*args):
    app.toolbox["modelmaker_sfincs_cht"].cut_inactive_cells()
