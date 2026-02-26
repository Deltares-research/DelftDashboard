# -*- coding: utf-8 -*-
"""
GUI methods for modelmaker_hurrywave -> mask_boundary_cells

Created on Mon May 10 12:18:09 2021

@author: Maarten van Ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations import map

def select(*args):
    # De-activate() existing layers
    map.update()
    # Show the boundary polygons
    app.map.layer["modelmaker_hurrywave"].layer["mask_boundary"].activate()
    # Show the grid and mask
    app.map.layer["hurrywave"].layer["grid"].activate()
    app.map.layer["hurrywave"].layer["mask"].activate()

def deselect(*args):
    changed = False
    if app.toolbox["modelmaker_hurrywave"].boundary_polygon_changed and len(app.toolbox["modelmaker_hurrywave"].boundary_polygon) > 0:
        changed = True
    if changed:    
        ok = app.gui.window.dialog_yes_no("Your polygons have changed. Would you like to save the changes?")
        if ok:
            if app.toolbox["modelmaker_hurrywave"].boundary_polygon_changed and len(app.toolbox["modelmaker_hurrywave"].boundary_polygon) > 0:
                save_boundary_polygon()

def draw_boundary_polygon(*args):
    app.map.layer["modelmaker_hurrywave"].layer["mask_boundary"].crs = app.crs
    app.map.layer["modelmaker_hurrywave"].layer["mask_boundary"].draw()

def delete_boundary_polygon(*args):
    if len(app.toolbox["modelmaker_hurrywave"].boundary_polygon) == 0:
        return
    index = app.gui.getvar("modelmaker_hurrywave", "boundary_polygon_index")
    gdf = app.map.layer["modelmaker_hurrywave"].layer["mask_boundary"].delete_feature(index)
    app.toolbox["modelmaker_hurrywave"].boundary_polygon = gdf
    app.toolbox["modelmaker_hurrywave"].boundary_polygon_changed = True
    # If the last polygon was deleted, set index to last available polygon
    if index > len(app.toolbox["modelmaker_hurrywave"].boundary_polygon) - 1:
        app.gui.setvar("modelmaker_hurrywave", "boundary_polygon_index", len(app.toolbox["modelmaker_hurrywave"].boundary_polygon) - 1)
    update()

def load_boundary_polygon(*args):
    full_name, path, name, ext, fltr = app.gui.window.dialog_open_file("Select boundary polygon file ...", filter="*.geojson")
    if not full_name:
        return
    append = False
    if app.gui.getvar("modelmaker_hurrywave", "nr_boundary_polygons"):
        append = app.gui.window.dialog_yes_no("Add to existing boundary polygons?", " ")
    app.toolbox["modelmaker_hurrywave"].read_boundary_polygon(full_name, append)
    app.toolbox["modelmaker_hurrywave"].plot_boundary_polygon()
    if append:
        app.toolbox["modelmaker_hurrywave"].boundary_polygon_changed = True
    else:
        save_boundary_polygon()    
    update()

def save_boundary_polygon(*args):
    app.gui.window.dialog_fade_label("Saving boundary polygons to boundary.geojson ...")
    app.toolbox["modelmaker_hurrywave"].write_boundary_polygon()
    app.toolbox["modelmaker_hurrywave"].boundary_polygon_changed = False

def select_boundary_polygon(*args):
    index = args[0]
    feature_id = app.toolbox["modelmaker_hurrywave"].boundary_polygon.loc[index, "id"]
    app.map.layer["modelmaker_hurrywave"].layer["mask_boundary"].activate_feature(feature_id)

def boundary_polygon_created(gdf, index, id):
    app.toolbox["modelmaker_hurrywave"].boundary_polygon = gdf
    app.toolbox["modelmaker_hurrywave"].boundary_polygon_changed = True
    nrp = len(app.toolbox["modelmaker_hurrywave"].boundary_polygon)
    app.gui.setvar("modelmaker_hurrywave", "boundary_polygon_index", nrp - 1)
    update()

def boundary_polygon_modified(gdf, index, id):
    app.toolbox["modelmaker_hurrywave"].boundary_polygon = gdf
    app.toolbox["modelmaker_hurrywave"].boundary_polygon_changed = True

def boundary_polygon_selected(index):
    app.gui.setvar("modelmaker_hurrywave", "boundary_polygon_index", index)
    update()

def update():
    # app.toolbox["modelmaker_hurrywave"].update_polygons()
    nrp = len(app.toolbox["modelmaker_hurrywave"].boundary_polygon)
    bndnames = []
    for ip in range(nrp):
        bndnames.append(str(ip + 1))
    app.gui.setvar("modelmaker_hurrywave", "nr_boundary_polygons", nrp)
    app.gui.setvar("modelmaker_hurrywave", "boundary_polygon_names", bndnames)
    # app.toolbox["modelmaker_hurrywave"].write_include_polygon()
    # app.toolbox["modelmaker_hurrywave"].write_exclude_polygon()
    # app.toolbox["modelmaker_hurrywave"].write_boundary_polygon()

    app.gui.window.update()

def update_mask(*args):
    app.toolbox["modelmaker_hurrywave"].update_mask()

def cut_inactive_cells(*args):
    app.toolbox["modelmaker_hurrywave"].cut_inactive_cells()
