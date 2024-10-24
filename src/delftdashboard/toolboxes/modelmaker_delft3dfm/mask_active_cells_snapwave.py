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
    update()

def draw_include_polygon_snapwave(*args):
    app.map.layer["modelmaker_sfincs_cht"].layer["include_polygon_snapwave"].crs = app.crs
    app.map.layer["modelmaker_sfincs_cht"].layer["include_polygon_snapwave"].draw()

def delete_include_polygon_snapwave(*args):
    if len(app.toolbox["modelmaker_sfincs_cht"].include_polygon_snapwave) == 0:
        return
    index = app.gui.getvar("modelmaker_sfincs_cht", "include_polygon_index_snapwave")
    gdf = app.map.layer["modelmaker_sfincs_cht"].layer["include_polygon_snapwave"].delete_feature(index)
    app.toolbox["modelmaker_sfincs_cht"].include_polygon_snapwave = gdf
    update()

def load_include_polygon_snapwave(*args):
    fname, okay = app.gui.window.dialog_open_file("Select include polygon file ...", filter="*.geojson")
    if not okay:
        return
    app.gui.setvar("modelmaker_sfincs_cht", "include_polygon_file_snapwave", fname[2])
    app.toolbox["modelmaker_sfincs_cht"].read_include_polygon_snapwave()
    app.toolbox["modelmaker_sfincs_cht"].plot_include_polygon_snapwave()

def save_include_polygon_snapwave(*args):
    app.toolbox["modelmaker_sfincs_cht"].write_include_polygon_snapwave()

def select_include_polygon_snapwave(*args):
    index = args[0]
    app.map.layer["modelmaker_sfincs_cht"].layer["include_polygon_snapwave"].activate_feature(index)

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
    gdf = app.map.layer["modelmaker_sfincs_cht"].layer["exclude_polygon_snapwave"].delete_feature(index)
    app.toolbox["modelmaker_sfincs_cht"].exclude_polygon_snapwave = gdf
    update()

def load_exclude_polygon_snapwave(*args):
    fname, okay = app.gui.window.dialog_open_file("Select exclude polygon file ...", filter="*.geojson")
    if not okay:
        return
    app.gui.setvar("modelmaker_sfincs_cht", "exclude_polygon_file_snapwave", fname[2])
    app.toolbox["modelmaker_sfincs_cht"].read_exclude_polygon_snapwave()
    app.toolbox["modelmaker_sfincs_cht"].plot_exclude_polygon_snapwave()

def save_exclude_polygon_snapwave(*args):
    app.toolbox["modelmaker_sfincs_cht"].write_exclude_polygon_snapwave()

def select_exclude_polygon_snapwave(*args):
    index = args[0]
    app.map.layer["modelmaker_sfincs_cht"].layer["exclude_polygon_snapwave"].activate_feature(index)

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
    # Include
    nrp = len(app.toolbox["modelmaker_sfincs_cht"].include_polygon_snapwave)
    incnames = []
    for ip in range(nrp):
        incnames.append(str(ip + 1))
    app.gui.setvar("modelmaker_sfincs_cht", "nr_include_polygons_snapwave", nrp)
    app.gui.setvar("modelmaker_sfincs_cht", "include_polygon_names_snapwave", incnames)
    index = app.gui.getvar("modelmaker_sfincs_cht", "include_polygon_index_snapwave")
    if index > nrp - 1:
        index = max(nrp - 1, 0)
    app.gui.setvar("modelmaker_sfincs_cht", "include_polygon_index_snapwave", index)
    # Exclude
    nrp = len(app.toolbox["modelmaker_sfincs_cht"].exclude_polygon_snapwave)
    excnames = []
    for ip in range(nrp):
        excnames.append(str(ip + 1))
    app.gui.setvar("modelmaker_sfincs_cht", "nr_exclude_polygons_snapwave", nrp)
    app.gui.setvar("modelmaker_sfincs_cht", "exclude_polygon_names_snapwave", excnames)
    index = app.gui.getvar("modelmaker_sfincs_cht", "exclude_polygon_index_snapwave")
    if index > nrp - 1:
        index = max(nrp - 1, 0)
    app.gui.setvar("modelmaker_sfincs_cht", "exclude_polygon_index_snapwave", index)
    # Update GUI
    app.gui.window.update()

def update_mask(*args):
    app.toolbox["modelmaker_sfincs_cht"].update_mask_snapwave()

def cut_inactive_cells(*args):
    app.toolbox["modelmaker_sfincs_cht"].cut_inactive_cells()

