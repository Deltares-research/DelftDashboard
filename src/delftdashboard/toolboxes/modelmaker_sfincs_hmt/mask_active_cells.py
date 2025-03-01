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
    app.map.layer["modelmaker_sfincs_cht"].layer["include_polygon"].activate()
    app.map.layer["modelmaker_sfincs_cht"].layer["exclude_polygon"].activate()
    # Show the grid and mask
    app.map.layer["sfincs_cht"].layer["grid"].activate()
    app.map.layer["sfincs_cht"].layer["mask"].activate()
    update()

def draw_include_polygon(*args):
    app.map.layer["modelmaker_sfincs_cht"].layer["include_polygon"].crs = app.crs
    app.map.layer["modelmaker_sfincs_cht"].layer["include_polygon"].draw()

def delete_include_polygon(*args):
    if len(app.toolbox["modelmaker_sfincs_cht"].include_polygon) == 0:
        return
    index = app.gui.getvar("modelmaker_sfincs_cht", "include_polygon_index")
    gdf = app.map.layer["modelmaker_sfincs_cht"].layer["include_polygon"].delete_feature(index)
    app.toolbox["modelmaker_sfincs_cht"].include_polygon = gdf
    update()

def load_include_polygon(*args):
    full_name, path, name, ext, fltr = app.gui.window.dialog_open_file("Select include polygon file ...", filter="*.geojson")
    if not full_name:
        return
    append = False
    if app.gui.getvar("modelmaker_sfincs_cht", "nr_include_polygons"):
        append = app.gui.window.dialog_yes_no("Add to existing include polygons?", " ")
    app.toolbox["modelmaker_sfincs_cht"].read_include_polygon(full_name, append)
    app.toolbox["modelmaker_sfincs_cht"].plot_include_polygon()
    update()

def save_include_polygon(*args):
    app.toolbox["modelmaker_sfincs_cht"].write_include_polygon()

def select_include_polygon(*args):
    index = args[0]
    app.map.layer["modelmaker_sfincs_cht"].layer["include_polygon"].activate_feature(index)

def include_polygon_created(gdf, index, id):
    app.toolbox["modelmaker_sfincs_cht"].include_polygon = gdf
    nrp = len(app.toolbox["modelmaker_sfincs_cht"].include_polygon)
    app.gui.setvar("modelmaker_sfincs_cht", "include_polygon_index", nrp - 1)
    update()

def include_polygon_modified(gdf, index, id):
    app.toolbox["modelmaker_sfincs_cht"].include_polygon = gdf

def include_polygon_selected(index):
    # Selected from map
    app.gui.setvar("modelmaker_sfincs_cht", "include_polygon_index", index)
    update()

def draw_exclude_polygon(*args):
#    app.map.layer["modelmaker_sfincs_cht"].layer["include_polygon"].crs = app.crs
    app.map.layer["modelmaker_sfincs_cht"].layer["exclude_polygon"].draw()

def delete_exclude_polygon(*args):
    if len(app.toolbox["modelmaker_sfincs_cht"].exclude_polygon) == 0:
        return
    index = app.gui.getvar("modelmaker_sfincs_cht", "exclude_polygon_index")
    # Delete from map
    gdf = app.map.layer["modelmaker_sfincs_cht"].layer["exclude_polygon"].delete_feature(index)
    app.toolbox["modelmaker_sfincs_cht"].exclude_polygon = gdf
    update()

def load_exclude_polygon(*args):
    full_name, path, name, ext, fltr = app.gui.window.dialog_open_file("Select exclude polygon file ...", filter="*.geojson")
    if not full_name:
        return
    append = False
    if app.gui.getvar("modelmaker_sfincs_cht", "nr_exclude_polygons"):
        append = app.gui.window.dialog_yes_no("Add to existing exclude polygons?", " ")
    app.toolbox["modelmaker_sfincs_cht"].read_exclude_polygon(full_name, append)
    app.toolbox["modelmaker_sfincs_cht"].plot_exclude_polygon()
    update()

def save_exclude_polygon(*args):
    app.toolbox["modelmaker_sfincs_cht"].write_exclude_polygon()

def select_exclude_polygon(*args):
    index = args[0]
    app.map.layer["modelmaker_sfincs_cht"].layer["exclude_polygon"].activate_feature(index)

def exclude_polygon_created(gdf, index, id):
    app.toolbox["modelmaker_sfincs_cht"].exclude_polygon = gdf
    nrp = len(app.toolbox["modelmaker_sfincs_cht"].exclude_polygon)
    app.gui.setvar("modelmaker_sfincs_cht", "exclude_polygon_index", nrp - 1)
    update()

def exclude_polygon_modified(gdf, index, id):
    app.toolbox["modelmaker_sfincs_cht"].exclude_polygon = gdf

def exclude_polygon_selected(index):
    app.gui.setvar("modelmaker_sfincs_cht", "exclude_polygon_index", index)
    update()

def update():
    # Include
    nrp = len(app.toolbox["modelmaker_sfincs_cht"].include_polygon)
    incnames = []
    for ip in range(nrp):
        incnames.append(str(ip + 1))
    app.gui.setvar("modelmaker_sfincs_cht", "nr_include_polygons", nrp)
    app.gui.setvar("modelmaker_sfincs_cht", "include_polygon_names", incnames)
    index = app.gui.getvar("modelmaker_sfincs_cht", "include_polygon_index")
    if index > nrp - 1:
        index = max(nrp - 1, 0)
    app.gui.setvar("modelmaker_sfincs_cht", "include_polygon_index", index)

    # Exclude
    nrp = len(app.toolbox["modelmaker_sfincs_cht"].exclude_polygon)
    excnames = []
    for ip in range(nrp):
        excnames.append(str(ip + 1))
    app.gui.setvar("modelmaker_sfincs_cht", "nr_exclude_polygons", nrp)
    app.gui.setvar("modelmaker_sfincs_cht", "exclude_polygon_names", excnames)
    index = app.gui.getvar("modelmaker_sfincs_cht", "exclude_polygon_index")
    if index > nrp - 1:
        index = max(nrp - 1, 0)
    app.gui.setvar("modelmaker_sfincs_cht", "exclude_polygon_index", index)
    # Update GUI
    app.gui.window.update()

def update_mask(*args):
    app.toolbox["modelmaker_sfincs_cht"].update_mask()

def cut_inactive_cells(*args):
    app.toolbox["modelmaker_sfincs_cht"].cut_inactive_cells()

