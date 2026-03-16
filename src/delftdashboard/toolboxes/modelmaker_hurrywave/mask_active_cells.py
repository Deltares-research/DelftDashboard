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
    app.map.layer["hurrywave"].layer["mask"].activate()

def deselect(*args):
    changed = False
    if app.toolbox["modelmaker_hurrywave"].include_polygon_changed and len(app.toolbox["modelmaker_hurrywave"].include_polygon) > 0:
        changed = True
    if app.toolbox["modelmaker_hurrywave"].exclude_polygon_changed and len(app.toolbox["modelmaker_hurrywave"].exclude_polygon) > 0:
        changed = True
    if changed:    
        ok = app.gui.window.dialog_yes_no("Your polygons have changed. Would you like to save the changes?")
        if ok:
            if app.toolbox["modelmaker_hurrywave"].include_polygon_changed and len(app.toolbox["modelmaker_hurrywave"].include_polygon) > 0:
                save_include_polygon()
            if app.toolbox["modelmaker_hurrywave"].exclude_polygon_changed and len(app.toolbox["modelmaker_hurrywave"].exclude_polygon) > 0:
                save_exclude_polygon()

def draw_include_polygon(*args):
    app.map.layer["modelmaker_hurrywave"].layer["mask_include"].crs = app.crs
    app.map.layer["modelmaker_hurrywave"].layer["mask_include"].draw()

def delete_include_polygon(*args):
    if len(app.toolbox["modelmaker_hurrywave"].include_polygon) == 0:
        return
    index = app.gui.getvar("modelmaker_hurrywave", "include_polygon_index")
    gdf = app.map.layer["modelmaker_hurrywave"].layer["mask_include"].delete_feature(index)
    app.toolbox["modelmaker_hurrywave"].include_polygon = gdf
    # If the last polygon was deleted, set index to last available polygon
    if index > len(app.toolbox["modelmaker_hurrywave"].include_polygon) - 1:
        app.gui.setvar("modelmaker_hurrywave", "include_polygon_index", len(app.toolbox["modelmaker_hurrywave"].include_polygon) - 1)
    update()

def load_include_polygon(*args):
    full_name, path, name, ext, fltr = app.gui.window.dialog_open_file("Select include polygon file ...", filter="*.geojson")
    if not full_name:
        return
    append = False
    if app.gui.getvar("modelmaker_hurrywave", "nr_include_polygons"):
        append = app.gui.window.dialog_yes_no("Add to existing include polygons?", " ")
    app.toolbox["modelmaker_hurrywave"].read_include_polygon(full_name, append)
    app.toolbox["modelmaker_hurrywave"].plot_include_polygon()
    if append:
        app.toolbox["modelmaker_hurrywave"].include_polygon_changed = True
    else:
        save_include_polygon()    
    update()

def save_include_polygon(*args):
    app.gui.window.dialog_fade_label("Saving include polygons to include.geojson ...")
    app.toolbox["modelmaker_hurrywave"].write_include_polygon()
    app.toolbox["modelmaker_hurrywave"].include_polygon_changed = False

def select_include_polygon(*args):
    index = args[0]
    feature_id = app.toolbox["modelmaker_hurrywave"].include_polygon.loc[index, "id"]
    app.map.layer["modelmaker_hurrywave"].layer["mask_include"].activate_feature(feature_id)

def include_polygon_created(gdf, index, id):
    app.toolbox["modelmaker_hurrywave"].include_polygon = gdf
    nrp = len(app.toolbox["modelmaker_hurrywave"].include_polygon)
    app.gui.setvar("modelmaker_hurrywave", "include_polygon_index", nrp - 1)
    app.toolbox["modelmaker_hurrywave"].include_polygon_changed = True
    update()

def include_polygon_modified(gdf, index, id):
    app.toolbox["modelmaker_hurrywave"].include_polygon = gdf
    app.toolbox["modelmaker_hurrywave"].include_polygon_changed = True

def include_polygon_selected(index):
    app.gui.setvar("modelmaker_hurrywave", "include_polygon_index", index)
    update()

def draw_exclude_polygon(*args):
    app.map.layer["modelmaker_hurrywave"].layer["mask_exclude"].draw()

def delete_exclude_polygon(*args):
    if len(app.toolbox["modelmaker_hurrywave"].exclude_polygon) == 0:
        return
    index = app.gui.getvar("modelmaker_hurrywave", "exclude_polygon_index")
    gdf = app.map.layer["modelmaker_hurrywave"].layer["mask_exclude"].delete_feature(index)
    app.toolbox["modelmaker_hurrywave"].exclude_polygon = gdf
    # If the last polygon was deleted, set index to last available polygon
    if index > len(app.toolbox["modelmaker_hurrywave"].exclude_polygon) - 1:
        app.gui.setvar("modelmaker_hurrywave", "exclude_polygon_index", len(app.toolbox["modelmaker_hurrywave"].exclude_polygon) - 1)
    update()

def load_exclude_polygon(*args):
    full_name, path, name, ext, fltr = app.gui.window.dialog_open_file("Select exclude polygon file ...", filter="*.geojson")
    if not full_name:
        return
    append = False
    if app.gui.getvar("modelmaker_hurrywave", "nr_exclude_polygons"):
        append = app.gui.window.dialog_yes_no("Add to existing exclude polygons?", " ")
    app.toolbox["modelmaker_hurrywave"].read_exclude_polygon(full_name, append)
    app.toolbox["modelmaker_hurrywave"].plot_exclude_polygon()
    if append:
        app.toolbox["modelmaker_hurrywave"].exclude_polygon_changed = True
    else:
        save_exclude_polygon()    
    update()

def save_exclude_polygon(*args):
    app.gui.window.dialog_fade_label("Saving exclude polygons to exclude.geojson ...")
    app.toolbox["modelmaker_hurrywave"].write_exclude_polygon()
    app.toolbox["modelmaker_hurrywave"].exclude_polygon_changed = False

def select_exclude_polygon(*args):
    index = args[0]
    feature_id = app.toolbox["modelmaker_hurrywave"].exclude_polygon.loc[index, "id"]
    app.map.layer["modelmaker_hurrywave"].layer["mask_exclude"].activate_feature(feature_id)

def exclude_polygon_created(gdf, index, id):
    app.toolbox["modelmaker_hurrywave"].exclude_polygon = gdf
    nrp = len(app.toolbox["modelmaker_hurrywave"].exclude_polygon)
    app.gui.setvar("modelmaker_hurrywave", "exclude_polygon_index", nrp - 1)
    app.toolbox["modelmaker_hurrywave"].exclude_polygon_changed = True
    update()

def exclude_polygon_modified(gdf, index, id):
    app.toolbox["modelmaker_hurrywave"].exclude_polygon = gdf
    app.toolbox["modelmaker_hurrywave"].exclude_polygon_changed = True

def exclude_polygon_selected(index):
    app.gui.setvar("modelmaker_hurrywave", "exclude_polygon_index", index)
    update()

def update():
    # app.toolbox["modelmaker_hurrywave"].update_polygons()

    nrp = len(app.toolbox["modelmaker_hurrywave"].include_polygon)
    incnames = []
    for ip in range(nrp):
        incnames.append(str(ip + 1))
    app.gui.setvar("modelmaker_hurrywave", "nr_include_polygons", nrp)
    app.gui.setvar("modelmaker_hurrywave", "include_polygon_names", incnames)

    nrp = len(app.toolbox["modelmaker_hurrywave"].exclude_polygon)
    excnames = []
    for ip in range(nrp):
        excnames.append(str(ip + 1))
    app.gui.setvar("modelmaker_hurrywave", "nr_exclude_polygons", nrp)
    app.gui.setvar("modelmaker_hurrywave", "exclude_polygon_names", excnames)

    # nrp = len(app.toolbox["modelmaker_hurrywave"].boundary_polygon)
    # bndnames = []
    # for ip in range(nrp):
    #     bndnames.append(str(ip + 1))
    # app.gui.setvar("modelmaker_hurrywave", "nr_boundary_polygons", nrp)
    # app.gui.setvar("modelmaker_hurrywave", "boundary_polygon_names", bndnames)

    app.gui.window.update()

def update_mask(*args):
    app.toolbox["modelmaker_hurrywave"].update_mask()

def cut_inactive_cells(*args):
    app.toolbox["modelmaker_hurrywave"].cut_inactive_cells()

