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
    app.map.layer["modelmaker_sfincs_hmt"].layer["quadtree_refinement"].activate()
    app.map.layer["sfincs_hmt"].layer["grid"].activate()
    app.map.layer["modelmaker_sfincs_hmt"].layer["grid_outline"].activate()
    # Strings for refinement levels
    levstr = []
    for i in range(10):
        dx = app.gui.getvar("modelmaker_sfincs_hmt", "dx")
        if app.map.crs.is_geographic:
            sfx = str(dx/(2**(i + 1))) + "°  ~" + str(int(dx*111000/(2**(i + 1)))) + " m"
        else:
            sfx = str(dx/(2**(i + 1))) + " m"

        levstr.append("x" + str(2**(i + 1)) + " (" + sfx + ")") 
    app.gui.setvar("modelmaker_sfincs_hmt", "refinement_polygon_levels", levstr)
    app.gui.window.statusbar.show_message("Select refinement polygon(s) and set refinement levels.", 5000)
    update()

def draw_refinement_polygon(*args):
    app.map.layer["modelmaker_sfincs_hmt"].layer["quadtree_refinement"].crs = app.crs
    app.map.layer["modelmaker_sfincs_hmt"].layer["quadtree_refinement"].draw()

def delete_refinement_polygon(*args):
    if len(app.toolbox["modelmaker_sfincs_hmt"].refinement_polygon) == 0:
        return
    index = app.gui.getvar("modelmaker_sfincs_hmt", "refinement_polygon_index")
    # Delete from app
    app.toolbox["modelmaker_sfincs_hmt"].refinement_polygon = app.toolbox["modelmaker_sfincs_hmt"].refinement_polygon.drop(index)
    if len(app.toolbox["modelmaker_sfincs_hmt"].refinement_polygon) > 0:
        app.toolbox["modelmaker_sfincs_hmt"].refinement_polygon = app.toolbox["modelmaker_sfincs_hmt"].refinement_polygon.reset_index(drop=True)
    app.toolbox["modelmaker_sfincs_hmt"].plot_refinement_polygon()

    # If the last polygon was deleted, set index to last available polygon
    if index > len(app.toolbox["modelmaker_sfincs_hmt"].refinement_polygon) - 1:
        index = max(len(app.toolbox["modelmaker_sfincs_hmt"].refinement_polygon) - 1, 0)
        app.gui.setvar("modelmaker_sfincs_hmt", "refinement_polygon_index", index)
    update()

def load_refinement_polygon(*args):
    full_name, path, name, ext, fltr = app.gui.window.dialog_open_file("Select refinement polygon file ...", filter="*.geojson")
    if not full_name:
        return
    append = False
    if app.gui.getvar("modelmaker_sfincs_hmt", "nr_refinement_polygons") > 0:
        append = app.gui.window.dialog_yes_no("Add to existing refinement polygons?", " ")    
    app.toolbox["modelmaker_sfincs_hmt"].read_refinement_polygon(full_name, append)
    app.toolbox["modelmaker_sfincs_hmt"].plot_refinement_polygon()
    update()

def save_refinement_polygon(*args):
    app.toolbox["modelmaker_sfincs_hmt"].write_refinement_polygon()

def select_refinement_polygon(*args):
    index = args[0]
    app.map.layer["modelmaker_sfincs_hmt"].layer["quadtree_refinement"].activate_feature(index)

def select_refinement_level(*args):
    level_index = args[0]
    # Get index of selected polygon 
    index = app.gui.getvar("modelmaker_sfincs_hmt", "refinement_polygon_index")
    app.toolbox["modelmaker_sfincs_hmt"].refinement_polygon.at[index, "refinement_level"] = level_index + 1
    update()

def edit_zmin_zmax(*args):
    # Get index of selected polygon 
    index = app.gui.getvar("modelmaker_sfincs_hmt", "refinement_polygon_index")
    app.toolbox["modelmaker_sfincs_hmt"].refinement_polygon.at[index, "zmin"] = app.gui.getvar("modelmaker_sfincs_hmt", "refinement_polygon_zmin")
    app.toolbox["modelmaker_sfincs_hmt"].refinement_polygon.at[index, "zmax"] = app.gui.getvar("modelmaker_sfincs_hmt", "refinement_polygon_zmax")
    update()

def refinement_polygon_created(gdf, index, feature_id):
    app.toolbox["modelmaker_sfincs_hmt"].refinement_polygon = gdf
    nrp = len(app.toolbox["modelmaker_sfincs_hmt"].refinement_polygon)
    app.gui.setvar("modelmaker_sfincs_hmt", "refinement_polygon_index", nrp - 1)
    update()

def refinement_polygon_modified(gdf, index, id):
    app.toolbox["modelmaker_sfincs_hmt"].refinement_polygon = gdf

def refinement_polygon_selected(index):
    app.gui.setvar("modelmaker_sfincs_hmt", "refinement_polygon_index", index)
    update()

def update():
    index = app.gui.getvar("modelmaker_sfincs_hmt", "refinement_polygon_index")
    nrp = len(app.toolbox["modelmaker_sfincs_hmt"].refinement_polygon)
    if nrp > 0:
        zmin = app.toolbox["modelmaker_sfincs_hmt"].refinement_polygon.loc[index, "zmin"]
        zmax = app.toolbox["modelmaker_sfincs_hmt"].refinement_polygon.loc[index, "zmax"]
        app.gui.setvar("modelmaker_sfincs_hmt", "refinement_polygon_zmin", zmin)
        app.gui.setvar("modelmaker_sfincs_hmt", "refinement_polygon_zmax", zmax)
    else:
        app.gui.setvar("modelmaker_sfincs_hmt", "refinement_polygon_zmin", -1000000.0)
        app.gui.setvar("modelmaker_sfincs_hmt", "refinement_polygon_zmax", 1000000.0)
    refnames = []
    levstr = app.gui.getvar("modelmaker_sfincs_hmt", "refinement_polygon_levels")
    if nrp>0:
        for ip in range(nrp):
            ilev = int(app.toolbox["modelmaker_sfincs_hmt"].refinement_polygon.loc[ip, "refinement_level"])
            refnames.append(str(ip + 1) + " (" + levstr[ilev - 1] + ")")
    else:        
        pass
    app.gui.setvar("modelmaker_sfincs_hmt", "nr_refinement_polygons", nrp)
    app.gui.setvar("modelmaker_sfincs_hmt", "refinement_polygon_names", refnames)
    app.gui.window.update()

def build_quadtree_grid(*args):
    # First check if zmin and zmax are set for any of the polygons. If so, check that bathy sets have been defined. If not, give a warning.
    # Loop though polygons
    zminzmax = False
    for i, row in app.toolbox["modelmaker_sfincs_hmt"].refinement_polygon.iterrows():
        if row["zmin"] > -20000.0 or row["zmax"] < 20000.0:
            zminzmax = True
    if zminzmax:
        if len(app.toolbox["modelmaker_sfincs_hmt"].selected_bathymetry_datasets) == 0:
            app.gui.window.dialog_warning("Please select at least one bathymetry dataset (see next tab).")
            return
    nmax = app.gui.getvar("modelmaker_sfincs_hmt", "nmax")
    mmax = app.gui.getvar("modelmaker_sfincs_hmt", "mmax")
    if nmax == 0 or mmax == 0:
        app.gui.window.dialog_warning("Please first draw bounding box for grid.")
        return

    app.toolbox["modelmaker_sfincs_hmt"].generate_grid()
