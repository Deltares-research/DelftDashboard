# -*- coding: utf-8 -*-
"""
GUI methods for modelmaker_delft3dfm -> mask_boundary_cells

Created on Mon May 10 12:18:09 2021

@author: Maarten van Ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations import map

def select(*args):
    # De-activate() existing layers
    map.update()
    # Show the boundary polygons
    app.map.layer["modelmaker_delft3dfm"].layer["open_boundary_polygon"].activate()
    # app.map.layer["modelmaker_delft3dfm"].layer["outflow_boundary_polygon"].activate()
    # Show the grid and mask
    app.map.layer["delft3dfm"].layer["grid"].activate()
    # app.map.layer["delft3dfm"].layer["mask"].activate()
    update()

def draw_open_boundary_polygon(*args):
    app.map.layer["modelmaker_delft3dfm"].layer["open_boundary_polygon"].crs = app.crs
    app.map.layer["modelmaker_delft3dfm"].layer["open_boundary_polygon"].draw()
    update()

def delete_open_boundary_polygon(*args):
    if len(app.toolbox["modelmaker_delft3dfm"].open_boundary_polygon) == 0:
        return
    index = app.gui.getvar("modelmaker_delft3dfm", "open_boundary_polygon_index")
    app.toolbox["modelmaker_delft3dfm"].open_boundary_polygon_names.pop(index)
    feature_id = app.map.layer["modelmaker_delft3dfm"].layer["open_boundary_polygon"].get_feature_id(index)
    # Delete from map
    gdf = app.map.layer["modelmaker_delft3dfm"].layer["open_boundary_polygon"].delete_feature(feature_id)
    # Delete from app
    app.toolbox["modelmaker_delft3dfm"].open_boundary_polygon = app.toolbox["modelmaker_delft3dfm"].open_boundary_polygon.drop(index)
    if len(app.toolbox["modelmaker_delft3dfm"].open_boundary_polygon) > 0:
        app.toolbox["modelmaker_delft3dfm"].open_boundary_polygon = app.toolbox["modelmaker_delft3dfm"].open_boundary_polygon.reset_index(drop=True)
    # If the last polygon was deleted, set index to last available polygon
    if index > len(app.toolbox["modelmaker_delft3dfm"].open_boundary_polygon) - 1:
        index = max(len(app.toolbox["modelmaker_delft3dfm"].open_boundary_polygon) - 1, 0)
        app.gui.setvar("modelmaker_delft3dfm", "open_boundary_polygon_index", index)
    # app.toolbox["modelmaker_delft3dfm"].open_boundary_polygon = gdf
    update()

def load_open_boundary_polygon(*args):
    fname = app.gui.window.dialog_open_file("Select file ...",
                                        # file_name="coastlines.shp",
                                        filter= None, #"*.obs",
                                        allow_directory_change=True,
                                        multiple=True)
    app.gui.setvar("modelmaker_delft3dfm", "open_boundary_polygon_file", fname[2])
    app.toolbox["modelmaker_delft3dfm"].read_open_boundary_polygon()
    app.toolbox["modelmaker_delft3dfm"].plot_open_boundary_polygon()
    update()

def save_open_boundary_polygon(*args):
    file_name = app.gui.getvar("modelmaker_delft3dfm", "open_boundary_polygon")
    rsp = app.gui.window.dialog_save_file("Select file ...",
                                    file_name=file_name,
                                    filter="*.geojson",
                                    allow_directory_change=False)
    app.gui.setvar("modelmaker_delft3dfm", "open_boundary_polygon_file", rsp[2])
    app.toolbox["modelmaker_delft3dfm"].write_open_boundary_polygon()

def select_open_boundary_polygon(*args):
    index = args[0]
    app.map.layer["modelmaker_delft3dfm"].layer["open_boundary_polygon"].activate_feature(index)

def open_boundary_polygon_created(gdf, index, id):
    while True:
        name, okay = app.gui.window.dialog_string("Edit name for new open boundary polygon")
        if not okay:
            app.map.layer["modelmaker_delft3dfm"].layer["open_boundary_polygon"].delete_feature(index)
            return            # Cancel was clicked
        if name in app.gui.getvar("modelmaker_delft3dfm", "open_boundary_polygon_names"):
            app.gui.window.dialog_info("An open boundary polygon with this name already exists !")
        else:
            break
    gdf.at[index, "name"] = name
    app.toolbox["modelmaker_delft3dfm"].open_boundary_polygon = gdf
    nrp = len(app.toolbox["modelmaker_delft3dfm"].open_boundary_polygon)
    app.gui.setvar("modelmaker_delft3dfm", "open_boundary_polygon_index", nrp - 1)
    app.toolbox["modelmaker_delft3dfm"].open_boundary_polygon_names.append(name)

    update()

def open_boundary_polygon_modified(gdf, index, id):
    app.toolbox["modelmaker_delft3dfm"].open_boundary_polygon = gdf

def open_boundary_polygon_selected(index):
    app.gui.setvar("modelmaker_delft3dfm", "open_boundary_polygon_index", index)
    update()

# def edit_resolution(*args):
#     # Get index of selected polygon 
#     index = app.gui.getvar("modelmaker_delft3dfm", "refinement_polygon_index")
#     app.toolbox["modelmaker_delft3dfm"].refinement_polygon.at[index, "min_edge_size"] = app.gui.getvar("modelmaker_delft3dfm", "ref_min_edge_size")
#     update()

# def draw_outflow_boundary_polygon(*args):
#     app.map.layer["modelmaker_delft3dfm"].layer["outflow_boundary_polygon"].crs = app.crs
#     app.map.layer["modelmaker_delft3dfm"].layer["outflow_boundary_polygon"].draw()

# def delete_outflow_boundary_polygon(*args):
#     if len(app.toolbox["modelmaker_delft3dfm"].outflow_boundary_polygon) == 0:
#         return
#     index = app.gui.getvar("modelmaker_delft3dfm", "outflow_boundary_polygon_index")
#     # Delete from map
#     gdf = app.map.layer["modelmaker_delft3dfm"].layer["outflow_boundary_polygon"].delete_feature(index)
#     app.toolbox["modelmaker_delft3dfm"].outflow_boundary_polygon = gdf
#     update()

# def load_outflow_boundary_polygon(*args):
#     fname, okay = app.gui.window.dialog_open_file("Select outflow boundary polygon file ...", filter="*.geojson")
#     if not okay:
#         return
#     app.gui.setvar("modelmaker_delft3dfm", "outflow_boundary_polygon_file", fname[2])
#     app.toolbox["modelmaker_delft3dfm"].read_outflow_boundary_polygon()
#     app.toolbox["modelmaker_delft3dfm"].plot_outflow_boundary_polygon()

# def save_outflow_boundary_polygon(*args):
#     app.toolbox["modelmaker_delft3dfm"].write_outflow_boundary_polygon()

# def select_outflow_boundary_polygon(*args):
#     index = args[0]
#     app.map.layer["modelmaker_delft3dfm"].layer["outflow_boundary_polygon"].activate_feature(index)

# def outflow_boundary_polygon_created(gdf, index, id):
#     app.toolbox["modelmaker_delft3dfm"].outflow_boundary_polygon = gdf
#     nrp = len(app.toolbox["modelmaker_delft3dfm"].outflow_boundary_polygon)
#     app.gui.setvar("modelmaker_delft3dfm", "outflow_boundary_polygon_index", nrp - 1)
#     update()

# def outflow_boundary_polygon_modified(gdf, index, id):
#     app.toolbox["modelmaker_delft3dfm"].outflow_boundary_polygon = gdf

# def outflow_boundary_polygon_selected(index):
#     app.gui.setvar("modelmaker_delft3dfm", "outflow_boundary_polygon_index", index)
#     update()



def update():
    # Open
    index = app.gui.getvar("modelmaker_delft3dfm", "open_boundary_polygon_index")
    nrp = len(app.toolbox["modelmaker_delft3dfm"].open_boundary_polygon)
    polnames = app.toolbox["modelmaker_delft3dfm"].open_boundary_polygon_names
    app.gui.setvar("modelmaker_delft3dfm", "nr_open_boundary_polygons", nrp)
    app.gui.setvar("modelmaker_delft3dfm", "open_boundary_polygon_names", polnames)
    if index > nrp - 1:
        index = max(nrp - 1, 0)
    app.gui.setvar("modelmaker_delft3dfm", "open_boundary_polygon_index", index)

    # # Outflow
    # nrp = len(app.toolbox["modelmaker_delft3dfm"].outflow_boundary_polygon)
    # names = []
    # for ip in range(nrp):
    #     names.append(str(ip + 1))
    # app.gui.setvar("modelmaker_delft3dfm", "nr_outflow_boundary_polygons", nrp)
    # app.gui.setvar("modelmaker_delft3dfm", "outflow_boundary_polygon_names", names)
    # index = app.gui.getvar("modelmaker_delft3dfm", "outflow_boundary_polygon_index")
    # if index > nrp - 1:
    #     index = max(nrp - 1, 0)
    # app.gui.setvar("modelmaker_delft3dfm", "outflow_boundary_polygon_index", index)

    # Update GUI
    app.gui.window.update()

def generate_bnd_coastline(*args):
    app.toolbox["modelmaker_delft3dfm"].generate_bnd_coastline()

def generate_bnd_polygon(*args):
    app.toolbox["modelmaker_delft3dfm"].generate_bnd_polygon()
    
def load_bnd(*args):
    fname = app.gui.window.dialog_open_file("Select file ...",
                                    file_name="bnd.pli",
                                    filter= "*.pli",
                                    allow_directory_change=True)
    app.toolbox["modelmaker_delft3dfm"].load_bnd(fname[0])
    
def set_resolution(*args):
    update()
# def update_mask(*args):
#     app.toolbox["modelmaker_delft3dfm"].update_mask()

# def cut_inactive_cells(*args):
#     app.toolbox["modelmaker_delft3dfm"].cut_inactive_cells()
