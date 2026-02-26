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
    app.map.layer["sfincs_cht"].layer["mask_snapwave"].activate()
    update()

def deselect(*args):
    # Check if there are include polygons
    changed = False
    if app.toolbox["modelmaker_sfincs_cht"].include_polygon_snapwave_changed and len(app.toolbox["modelmaker_sfincs_cht"].include_polygon_snapwave) > 0:
        changed = True
    if app.toolbox["modelmaker_sfincs_cht"].exclude_polygon_snapwave_changed and len(app.toolbox["modelmaker_sfincs_cht"].exclude_polygon_snapwave) > 0:
        changed = True
    if changed:    
        ok = app.gui.window.dialog_yes_no("Your polygons have changed. Would you like to save the changes?")
        if ok:
            if app.toolbox["modelmaker_sfincs_cht"].include_polygon_snapwave_changed and len(app.toolbox["modelmaker_sfincs_cht"].include_polygon_snapwave) > 0:
                save_include_polygon_snapwave()
            if app.toolbox["modelmaker_sfincs_cht"].exclude_polygon_snapwave_changed and len(app.toolbox["modelmaker_sfincs_cht"].exclude_polygon_snapwave) > 0:
                save_exclude_polygon_snapwave()

def draw_include_polygon_snapwave(*args):
    app.map.layer["modelmaker_sfincs_cht"].layer["include_polygon_snapwave"].crs = app.crs
    app.map.layer["modelmaker_sfincs_cht"].layer["include_polygon_snapwave"].draw()

def delete_include_polygon_snapwave(*args):
    if len(app.toolbox["modelmaker_sfincs_cht"].include_polygon_snapwave) == 0:
        return
    index = app.gui.getvar("modelmaker_sfincs_cht", "include_polygon_index_snapwave")
    gdf = app.map.layer["modelmaker_sfincs_cht"].layer["include_polygon_snapwave"].delete_feature(index)
    app.toolbox["modelmaker_sfincs_cht"].include_polygon_snapwave = gdf
    app.toolbox["modelmaker_sfincs_cht"].include_polygon_snapwave_changed = True
    update()

def load_include_polygon_snapwave(*args):
    full_name, path, name, ext, fltr = app.gui.window.dialog_open_file("Select include polygon file ...", filter="*.geojson")
    if not full_name:
        return
    append = False
    if app.gui.getvar("modelmaker_sfincs_cht", "nr_include_polygons_snapwave"):
        append = app.gui.window.dialog_yes_no("Add to existing include polygons?", " ")
    app.toolbox["modelmaker_sfincs_cht"].read_include_polygon_snapwave(full_name, append)
    app.toolbox["modelmaker_sfincs_cht"].plot_include_polygon_snapwave()
    if append:
        app.toolbox["modelmaker_sfincs_cht"].include_polygon_snapwave_changed = True
    else:
        save_include_polygon_snapwave()
    update()

def save_include_polygon_snapwave(*args):
    app.gui.window.dialog_fade_label("Saving include polygons to include_snapwave.geojson ...")
    app.toolbox["modelmaker_sfincs_cht"].include_polygon_snapwave_changed = False    
    app.toolbox["modelmaker_sfincs_cht"].write_include_polygon_snapwave()

def select_include_polygon_snapwave(*args):
    index = args[0]
    app.map.layer["modelmaker_sfincs_cht"].layer["include_polygon_snapwave"].activate_feature(index)

def include_polygon_created_snapwave(gdf, index, id):
    app.toolbox["modelmaker_sfincs_cht"].include_polygon_snapwave = gdf
    nrp = len(app.toolbox["modelmaker_sfincs_cht"].include_polygon_snapwave)
    app.gui.setvar("modelmaker_sfincs_cht", "include_polygon_index_snapwave", nrp - 1)
    app.toolbox["modelmaker_sfincs_cht"].include_polygon_snapwave_changed = True
    update()

def include_polygon_modified_snapwave(gdf, index, id):
    app.toolbox["modelmaker_sfincs_cht"].include_polygon_snapwave = gdf
    app.toolbox["modelmaker_sfincs_cht"].include_polygon_snapwave_changed = True

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
    app.toolbox["modelmaker_sfincs_cht"].exclude_polygon_snapwave_changed = True
    update()

def load_exclude_polygon_snapwave(*args):
    full_name, path, name, ext, fltr = app.gui.window.dialog_open_file("Select exclude polygon file ...", filter="*.geojson")
    if not full_name:
        return
    append = False
    if app.gui.getvar("modelmaker_sfincs_cht", "nr_exclude_polygons_snapwave"):
        append = app.gui.window.dialog_yes_no("Add to existing exclude polygons?", " ")
    app.toolbox["modelmaker_sfincs_cht"].read_exclude_polygon_snapwave(full_name, append)
    app.toolbox["modelmaker_sfincs_cht"].plot_exclude_polygon_snapwave()
    if append:
        app.toolbox["modelmaker_sfincs_cht"].exclude_polygon_snapwave_changed = True
    else:
        save_exclude_polygon_snapwave()
    update()

def save_exclude_polygon_snapwave(*args):
    app.gui.window.dialog_fade_label("Saving exclude polygons to exclude_snapwave.geojson ...")
    app.toolbox["modelmaker_sfincs_cht"].exclude_polygon_snapwave_changed = False
    app.toolbox["modelmaker_sfincs_cht"].write_exclude_polygon_snapwave()

def select_exclude_polygon_snapwave(*args):
    index = args[0]
    app.map.layer["modelmaker_sfincs_cht"].layer["exclude_polygon_snapwave"].activate_feature(index)

def exclude_polygon_created_snapwave(gdf, index, id):
    app.toolbox["modelmaker_sfincs_cht"].exclude_polygon_snapwave = gdf
    nrp = len(app.toolbox["modelmaker_sfincs_cht"].exclude_polygon_snapwave)
    app.gui.setvar("modelmaker_sfincs_cht", "exclude_polygon_index_snapwave", nrp - 1)
    app.toolbox["modelmaker_sfincs_cht"].exclude_polygon_snapwave_changed = True
    update()

def exclude_polygon_modified_snapwave(gdf, index, id):
    app.toolbox["modelmaker_sfincs_cht"].exclude_polygon_snapwave = gdf
    app.toolbox["modelmaker_sfincs_cht"].exclude_polygon_snapwave_changed = True

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

