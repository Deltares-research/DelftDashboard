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
    app.map.layer["modelmaker_sfincs_cht"].layer["open_boundary_polygon_snapwave"].activate()
    app.map.layer["modelmaker_sfincs_cht"].layer["neumann_boundary_polygon_snapwave"].activate()
    # Show the grid and mask
    app.map.layer["sfincs_cht"].layer["grid"].activate()
    app.map.layer["sfincs_cht"].layer["mask_snapwave"].activate()
    update()

def draw_open_boundary_polygon_snapwave(*args):
    app.map.layer["modelmaker_sfincs_cht"].layer["open_boundary_polygon_snapwave"].draw()

def delete_open_boundary_polygon_snapwave(*args):
    if len(app.toolbox["modelmaker_sfincs_cht"].open_boundary_polygon_snapwave) == 0:
        return
    index = app.gui.getvar("modelmaker_sfincs_cht", "open_boundary_polygon_index_snapwave")
    # Delete from map
    gdf = app.map.layer["modelmaker_sfincs_cht"].layer["open_boundary_polygon_snapwave"].delete_feature(index)
    app.toolbox["modelmaker_sfincs_cht"].open_boundary_polygon_snapwave = gdf
    update()

def load_open_boundary_polygon_snapwave(*args):
    full_name, path, name, ext, fltr = app.gui.window.dialog_open_file("Select open boundary polygon file ...", filter="*.geojson")
    if not full_name:
        return
    append = False
    if app.gui.getvar("modelmaker_sfincs_cht", "nr_open_boundary_polygons_snapwave"):
        append = app.gui.window.dialog_yes_no("Add to existing open boundary polygons?", " ")
    app.toolbox["modelmaker_sfincs_cht"].read_open_boundary_polygon_snapwave(full_name, append)
    app.toolbox["modelmaker_sfincs_cht"].plot_open_boundary_polygon_snapwave()
    update()


def save_open_boundary_polygon_snapwave(*args):
    app.toolbox["modelmaker_sfincs_cht"].write_open_boundary_polygon_snapwave()

def select_open_boundary_polygon_snapwave(*args):
    index = args[0]
    app.map.layer["modelmaker_sfincs_cht"].layer["open_boundary_polygon_snapwave"].activate_feature(index)

def open_boundary_polygon_created_snapwave(gdf, index, id):
    app.toolbox["modelmaker_sfincs_cht"].open_boundary_polygon_snapwave = gdf
    nrp = len(app.toolbox["modelmaker_sfincs_cht"].open_boundary_polygon_snapwave)
    app.gui.setvar("modelmaker_sfincs_cht", "open_boundary_polygon_index_snapwave", nrp - 1)
    update()

def open_boundary_polygon_modified_snapwave(gdf, index, id):
    app.toolbox["modelmaker_sfincs_cht"].open_boundary_polygon_snapwave = gdf

def open_boundary_polygon_selected_snapwave(index):
    app.gui.setvar("modelmaker_sfincs_cht", "open_boundary_polygon_index_snapwave", index)
    update()


def draw_neumann_boundary_polygon_snapwave(*args):
    app.map.layer["modelmaker_sfincs_cht"].layer["neumann_boundary_polygon_snapwave"].crs = app.crs
    app.map.layer["modelmaker_sfincs_cht"].layer["neumann_boundary_polygon_snapwave"].draw()

def delete_neumann_boundary_polygon_snapwave(*args):
    if len(app.toolbox["modelmaker_sfincs_cht"].neumann_boundary_polygon_snapwave) == 0:
        return
    index = app.gui.getvar("modelmaker_sfincs_cht", "neumann_boundary_polygon_index_snapwave")
    # Delete from map
    gdf = app.map.layer["modelmaker_sfincs_cht"].layer["neumann_boundary_polygon_snapwave"].delete_feature(index)
    app.toolbox["modelmaker_sfincs_cht"].neumann_boundary_polygon_snapwave = gdf
    update()

def load_neumann_boundary_polygon_snapwave(*args):
    full_name, path, name, ext, fltr = app.gui.window.dialog_open_file("Select neumann boundary polygon file ...", filter="*.geojson")
    if not full_name:
        return
    append = False
    if app.gui.getvar("modelmaker_sfincs_cht", "nr_neumann_boundary_polygons_snapwave"):
        append = app.gui.window.dialog_yes_no("Add to existing neumann boundary polygons?", " ")
    app.toolbox["modelmaker_sfincs_cht"].read_neumann_boundary_polygon_snapwave(full_name, append)
    app.toolbox["modelmaker_sfincs_cht"].plot_neumann_boundary_polygon_snapwave()
    update()

def save_neumann_boundary_polygon_snapwave(*args):
    app.toolbox["modelmaker_sfincs_cht"].write_neumann_boundary_polygon_snapwave()

def select_neumann_boundary_polygon_snapwave(*args):
    index = args[0]
    app.map.layer["modelmaker_sfincs_cht"].layer["neumann_boundary_polygon_snapwave"].activate_feature(index)

def neumann_boundary_polygon_created_snapwave(gdf, index, id):
    app.toolbox["modelmaker_sfincs_cht"].neumann_boundary_polygon_snapwave = gdf
    nrp = len(app.toolbox["modelmaker_sfincs_cht"].neumann_boundary_polygon_snapwave)
    app.gui.setvar("modelmaker_sfincs_cht", "neumann_boundary_polygon_index_snapwave", nrp - 1)
    update()

def neumann_boundary_polygon_modified_snapwave(gdf, index, id):
    app.toolbox["modelmaker_sfincs_cht"].neumann_boundary_polygon_snapwave = gdf

def neumann_boundary_polygon_selected_snapwave(index):
    app.gui.setvar("modelmaker_sfincs_cht", "neumann_boundary_polygon_index_snapwave", index)
    update()



def update():
    # Open
    nrp = len(app.toolbox["modelmaker_sfincs_cht"].open_boundary_polygon_snapwave)
    names = []
    for ip in range(nrp):
        names.append(str(ip + 1))
    app.gui.setvar("modelmaker_sfincs_cht", "nr_open_boundary_polygons_snapwave", nrp)
    app.gui.setvar("modelmaker_sfincs_cht", "open_boundary_polygon_names_snapwave", names)
    index = app.gui.getvar("modelmaker_sfincs_cht", "open_boundary_polygon_index_snapwave")
    if index > nrp - 1:
        index = max(nrp - 1, 0)
    app.gui.setvar("modelmaker_sfincs_cht", "open_boundary_polygon_index_snapwave", index)

    # neumann
    nrp = len(app.toolbox["modelmaker_sfincs_cht"].neumann_boundary_polygon_snapwave)
    names = []
    for ip in range(nrp):
        names.append(str(ip + 1))
    app.gui.setvar("modelmaker_sfincs_cht", "nr_neumann_boundary_polygons_snapwave", nrp)
    app.gui.setvar("modelmaker_sfincs_cht", "neumann_boundary_polygon_names_snapwave", names)
    index = app.gui.getvar("modelmaker_sfincs_cht", "neumann_boundary_polygon_index_snapwave")
    if index > nrp - 1:
        index = max(nrp - 1, 0)
    app.gui.setvar("modelmaker_sfincs_cht", "neumann_boundary_polygon_index_snapwave", index)
    # Update GUI
    app.gui.window.update()

def update_mask_snapwave(*args):
    app.toolbox["modelmaker_sfincs_cht"].update_mask_snapwave()

def cut_inactive_cells(*args):
    app.toolbox["modelmaker_sfincs_cht"].cut_inactive_cells()
