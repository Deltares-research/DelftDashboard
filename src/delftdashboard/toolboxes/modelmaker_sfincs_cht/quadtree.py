# -*- coding: utf-8 -*-
"""
GUI methods for modelmaker_sfincs -> quadtree

Created on Mon May 10 12:18:09 2021

@author: Maarten van Ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations import map

def select(*args):
    # De-activate() existing layers
    map.update()
    # Show the refinement layer
    app.map.layer["modelmaker_sfincs_cht"].layer["quadtree_refinement"].activate()
    app.map.layer["sfincs_cht"].layer["grid"].activate()
    app.map.layer["modelmaker_sfincs_cht"].layer["grid_outline"].activate()
    # Strings for refinement levels
    levstr = []
    for i in range(10):
        dx = app.gui.getvar("modelmaker_sfincs_cht", "dx")
        if app.map.crs.is_geographic:
            sfx = str(dx/(2**(i + 1))) + "°  ~" + str(int(dx*111000/(2**(i + 1)))) + " m"
        else:
            sfx = str(dx/(2**(i + 1))) + " m"

        levstr.append("x" + str(2**(i + 1)) + " (" + sfx + ")") 
    app.gui.setvar("modelmaker_sfincs_cht", "refinement_polygon_levels", levstr)
    app.gui.window.statusbar.show_message("Select refinement polygon(s) and set refinement levels.", 5000)
    update()

def draw_refinement_polygon(*args):
    app.map.layer["modelmaker_sfincs_cht"].layer["quadtree_refinement"].crs = app.crs
    app.map.layer["modelmaker_sfincs_cht"].layer["quadtree_refinement"].draw()

def delete_refinement_polygon(*args):
    if len(app.toolbox["modelmaker_sfincs_cht"].refinement_polygon) == 0:
        return
    index = app.gui.getvar("modelmaker_sfincs_cht", "refinement_polygon_index")
    app.toolbox["modelmaker_sfincs_cht"].refinement_levels.pop(index)
    feature_id = app.map.layer["modelmaker_sfincs_cht"].layer["quadtree_refinement"].get_feature_id(index)
    # Delete from map
    app.map.layer["modelmaker_sfincs_cht"].layer["quadtree_refinement"].delete_feature(feature_id)
    # Delete from app
    app.toolbox["modelmaker_sfincs_cht"].refinement_polygon = app.toolbox["modelmaker_sfincs_cht"].refinement_polygon.drop(index)
    if len(app.toolbox["modelmaker_sfincs_cht"].refinement_polygon) > 0:
        app.toolbox["modelmaker_sfincs_cht"].refinement_polygon = app.toolbox["modelmaker_sfincs_cht"].refinement_polygon.reset_index(drop=True)

    # If the last polygon was deleted, set index to last available polygon
    if index > len(app.toolbox["modelmaker_sfincs_cht"].refinement_polygon) - 1:
        index = max(len(app.toolbox["modelmaker_sfincs_cht"].refinement_polygon) - 1, 0)
        app.gui.setvar("modelmaker_sfincs_cht", "refinement_polygon_index", index)
    update()

def load_refinement_polygon(*args):
    full_name, path, name, ext, fltr = app.gui.window.dialog_open_file("Select refinement polygon file ...", filter="*.geojson")
    if not full_name:
        return
    app.gui.setvar("modelmaker_sfincs_cht", "refinement_polygon_file", full_name)
    app.toolbox["modelmaker_sfincs_cht"].read_refinement_polygon()
    app.toolbox["modelmaker_sfincs_cht"].plot_refinement_polygon()
    update()

def save_refinement_polygon(*args):
    app.toolbox["modelmaker_sfincs_cht"].write_refinement_polygon()

def select_refinement_polygon(*args):
    index = args[0]
#    feature_id = app.map.layer["modelmaker_sfincs_cht"].layer["quadtree_refinement"].get_feature_id(index)
#    feature_id = app.toolbox["modelmaker_sfincs_cht"].refinement_polygon.loc[index, "id"]
    app.map.layer["modelmaker_sfincs_cht"].layer["quadtree_refinement"].activate_feature(index)

def select_refinement_level(*args):
    level_index = args[0]
    # Get index of selected polygon 
    index = app.gui.getvar("modelmaker_sfincs_cht", "refinement_polygon_index")
    app.toolbox["modelmaker_sfincs_cht"].refinement_levels[index] = level_index + 1
    update()

def edit_zmin_zmax(*args):
    # Get index of selected polygon 
    index = app.gui.getvar("modelmaker_sfincs_cht", "refinement_polygon_index")
    app.toolbox["modelmaker_sfincs_cht"].refinement_zmin[index] = app.gui.getvar("modelmaker_sfincs_cht", "refinement_polygon_zmin")
    app.toolbox["modelmaker_sfincs_cht"].refinement_zmax[index] = app.gui.getvar("modelmaker_sfincs_cht", "refinement_polygon_zmax")
    update()

def refinement_polygon_created(gdf, index, id):
    app.toolbox["modelmaker_sfincs_cht"].refinement_polygon = gdf
    nrp = len(app.toolbox["modelmaker_sfincs_cht"].refinement_polygon)
    app.gui.setvar("modelmaker_sfincs_cht", "refinement_polygon_index", nrp - 1)
    # Add refinement level
    app.toolbox["modelmaker_sfincs_cht"].refinement_levels.append(1)
    app.toolbox["modelmaker_sfincs_cht"].refinement_zmin.append(-1000000.0)
    app.toolbox["modelmaker_sfincs_cht"].refinement_zmax.append(1000000.0)
    update()

def refinement_polygon_modified(gdf, index, id):
    app.toolbox["modelmaker_sfincs_cht"].refinement_polygon = gdf

def refinement_polygon_selected(index):
    app.gui.setvar("modelmaker_sfincs_cht", "refinement_polygon_index", index)
    update()

def update():
    index = app.gui.getvar("modelmaker_sfincs_cht", "refinement_polygon_index")
    levels = app.toolbox["modelmaker_sfincs_cht"].refinement_levels
    if len(levels) > 0:
        app.gui.setvar("modelmaker_sfincs_cht", "refinement_polygon_level", levels[index] - 1)
        app.gui.setvar("modelmaker_sfincs_cht", "refinement_polygon_zmin", app.toolbox["modelmaker_sfincs_cht"].refinement_zmin[index])
        app.gui.setvar("modelmaker_sfincs_cht", "refinement_polygon_zmax", app.toolbox["modelmaker_sfincs_cht"].refinement_zmax[index])
    else:
        app.gui.setvar("modelmaker_sfincs_cht", "refinement_polygon_level", 0)
        app.gui.setvar("modelmaker_sfincs_cht", "refinement_polygon_zmin", -1000000.0)
        app.gui.setvar("modelmaker_sfincs_cht", "refinement_polygon_zmax", 1000000.0)
    nrp = len(app.toolbox["modelmaker_sfincs_cht"].refinement_polygon)
    refnames = []
    levstr = app.gui.getvar("modelmaker_sfincs_cht", "refinement_polygon_levels")
    if nrp>0:
        for ip in range(nrp):
            refnames.append(str(ip + 1) + " (" + levstr[levels[ip] - 1] + ")")
    else:        
        pass
    app.gui.setvar("modelmaker_sfincs_cht", "nr_refinement_polygons", nrp)
    app.gui.setvar("modelmaker_sfincs_cht", "refinement_polygon_names", refnames)
    app.gui.window.update()

def build_quadtree_grid(*args):
    # First check if zmin and zmax are set for any of the polygons. If so, check that bathy sets have been defined. If not, give a warning.
    # Loop though polygons
    zminzmax = False
    for i in range(len(app.toolbox["modelmaker_sfincs_cht"].refinement_polygon)):
        if app.toolbox["modelmaker_sfincs_cht"].refinement_zmin[i] > -20000.0 or app.toolbox["modelmaker_sfincs_cht"].refinement_zmax[i] < 20000.0:
            zminzmax = True
    if zminzmax:
        if len(app.toolbox["modelmaker_sfincs_cht"].selected_bathymetry_datasets) == 0:
            app.gui.window.dialog_warning("Please select at least one bathymetry dataset (see next tab).")
            return
    nmax = app.gui.getvar("modelmaker_sfincs_cht", "nmax")
    mmax = app.gui.getvar("modelmaker_sfincs_cht", "mmax")
    if nmax == 0 or mmax == 0:
        app.gui.window.dialog_warning("Please first draw bounding box for grid.")
        return

    app.toolbox["modelmaker_sfincs_cht"].generate_grid()
