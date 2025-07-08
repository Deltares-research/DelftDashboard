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
    app.map.layer["modelmaker_delft3dfm"].layer["polygon_refinement"].activate()
    app.map.layer["delft3dfm"].layer["grid"].activate()
    app.map.layer["modelmaker_delft3dfm"].layer["grid_outline"].activate()
    update()

def draw_refinement_polygon(*args):
    app.map.layer["modelmaker_delft3dfm"].layer["polygon_refinement"].crs = app.crs
    app.map.layer["modelmaker_delft3dfm"].layer["polygon_refinement"].draw()
    update()
    
def delete_refinement_polygon(*args):
    if len(app.toolbox["modelmaker_delft3dfm"].refinement_polygon) == 0:
        return
    index = app.gui.getvar("modelmaker_delft3dfm", "refinement_polygon_index")
    app.toolbox["modelmaker_delft3dfm"].refinement_polygon_names.pop(index)
    feature_id = app.map.layer["modelmaker_delft3dfm"].layer["polygon_refinement"].get_feature_id(index)
    # Delete from map
    app.map.layer["modelmaker_delft3dfm"].layer["polygon_refinement"].delete_feature(feature_id)
    # Delete from app
    app.toolbox["modelmaker_delft3dfm"].refinement_polygon = app.toolbox["modelmaker_delft3dfm"].refinement_polygon.drop(index)
    if len(app.toolbox["modelmaker_delft3dfm"].refinement_polygon) > 0:
        app.toolbox["modelmaker_delft3dfm"].refinement_polygon = app.toolbox["modelmaker_delft3dfm"].refinement_polygon.reset_index(drop=True)

    # If the last polygon was deleted, set index to last available polygon
    if index > len(app.toolbox["modelmaker_delft3dfm"].refinement_polygon) - 1:
        index = max(len(app.toolbox["modelmaker_delft3dfm"].refinement_polygon) - 1, 0)
        app.gui.setvar("modelmaker_delft3dfm", "refinement_polygon_index", index)
    update()

def load_refinement_polygon(*args):
    full_name, path, name, ext, fltr = app.gui.window.dialog_open_file("Select refinement polygon file ...", filter="*.geojson")
    if not full_name:
        return
    app.gui.setvar("modelmaker_delft3dfm", "refinement_polygon_file", full_name)
    app.toolbox["modelmaker_delft3dfm"].read_refinement_polygon()
    app.toolbox["modelmaker_delft3dfm"].plot_refinement_polygon()
    update()

def save_refinement_polygon(*args):
    file_name = app.gui.getvar("modelmaker_delft3dfm", "refinement_polygon_file")
    rsp = app.gui.window.dialog_save_file("Select file ...",
                                    file_name=file_name,
                                    filter="*.geojson",
                                    allow_directory_change=False)
    app.gui.setvar("modelmaker_delft3dfm", "refinement_polygon_file", rsp[2])
    app.toolbox["modelmaker_delft3dfm"].write_refinement_polygon()

def select_refinement_polygon(*args):
    index = args[0]
#    feature_id = app.map.layer["modelmaker_delft3dfm"].layer["polygon_refinement"].get_feature_id(index)
#    feature_id = app.toolbox["modelmaker_delft3dfm"].refinement_polygon.loc[index, "id"]
    app.map.layer["modelmaker_delft3dfm"].layer["polygon_refinement"].activate_feature(index)
     
# def select_refinement_level(*args):
#     level_index = args[0]
#     # Get index of selected polygon 
#     index = app.gui.getvar("modelmaker_delft3dfm", "refinement_polygon_index")
#     app.toolbox["modelmaker_delft3dfm"].refinement_levels[index] = level_index + 1
#     update()

def edit_settings(*args):
    # Get index of selected polygon 
    index = app.gui.getvar("modelmaker_delft3dfm", "refinement_polygon_index")
    app.toolbox["modelmaker_delft3dfm"].refinement_polygon.at[index, "min_edge_size"] = app.gui.getvar("modelmaker_delft3dfm", "ref_min_edge_size")
    update()

def refinement_polygon_created(gdf, index, id):
    app.toolbox["modelmaker_delft3dfm"].refinement_polygon = gdf
    nrp = len(app.toolbox["modelmaker_delft3dfm"].refinement_polygon)
    app.gui.setvar("modelmaker_delft3dfm", "refinement_polygon_index", nrp - 1)
    name, okay = app.gui.window.dialog_string("Edit name for new refinement polygon")
    if not okay:
        return            # Cancel was clicked
    if name in app.gui.getvar("modelmaker_delft3dfm", "refinement_polygon_names"):
        app.gui.window.dialog_info("A refinement polygon with this name already exists !")
        return
    # # Add refinement polygon name
    app.toolbox["modelmaker_delft3dfm"].refinement_polygon_names.append(name)
    update()

def refinement_polygon_modified(gdf, index, id):
    app.toolbox["modelmaker_delft3dfm"].refinement_polygon = gdf

def refinement_polygon_selected(index):
    app.gui.setvar("modelmaker_delft3dfm", "refinement_polygon_index", index)
    update()

def update():
    index = app.gui.getvar("modelmaker_delft3dfm", "refinement_polygon_index")
    # levels = app.toolbox["modelmaker_delft3dfm"].refinement_levels
    # if len(levels) > 0:
    #     app.gui.setvar("modelmaker_delft3dfm", "refinement_polygon_level", levels[index] - 1)
    # else:
    #     app.gui.setvar("modelmaker_delft3dfm", "refinement_polygon_level", 0)
    nrp = len(app.toolbox["modelmaker_delft3dfm"].refinement_polygon)
    if nrp > 0:
        min_edge_size = app.toolbox["modelmaker_delft3dfm"].refinement_polygon.loc[index, "min_edge_size"]
        app.gui.setvar("modelmaker_delft3dfm", "ref_min_edge_size", min_edge_size)
    else:
        app.gui.setvar("modelmaker_delft3dfm", "ref_min_edge_size", 0)
    # refnames = []
    # levstr = app.gui.getvar("modelmaker_delft3dfm", "refinement_polygon_levels")
    # if nrp>0:
    #     for ip in range(nrp):
    #         refnames.append(str(ip + 1) + " (" + levstr[levels[ip] - 1] + ")")
    # else:        
    #     pass
    refnames = app.toolbox["modelmaker_delft3dfm"].refinement_polygon_names
    app.gui.setvar("modelmaker_delft3dfm", "nr_refinement_polygons", nrp)
    app.gui.setvar("modelmaker_delft3dfm", "refinement_polygon_names", refnames)
    app.gui.window.update()

def build_depthrefined_grid(*args):
    app.toolbox["modelmaker_delft3dfm"].generate_depth_refinement()

def build_polygonrefined_grid(*args):
    app.toolbox["modelmaker_delft3dfm"].generate_polygon_refinement()

def build_polygondepthrefined_grid(*args):
    app.toolbox["modelmaker_delft3dfm"].generate_polygon_depth_refinement()

def connect_nodes(*args):
    app.toolbox["modelmaker_delft3dfm"].connect_nodes()

def refine_size(*args):
    # app.model["delft3dfm"].domain.grid.refinement_polygon= app.toolbox["modelmaker_delft3dfm", "refinement_polygon")
    # app.model["delft3dfm"].domain.refinement_depth= app.gui.getvar("modelmaker_delft3dfm", "refinement_depth")
    app.model["delft3dfm"].domain.grid.min_edge_size= app.gui.getvar("modelmaker_delft3dfm", "depth_min_edge_size")
