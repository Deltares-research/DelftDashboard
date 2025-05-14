# -*- coding: utf-8 -*-
"""
GUI methods for modelmaker_delft3dfm -> mask_active_cells

Created on Mon May 10 12:18:09 2021

@author: Maarten van Ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations import map

def select(*args):
    # De-activate() existing layers
    map.update()
    # Show the mask include and exclude polygons
    # app.map.layer["modelmaker_delft3dfm"].layer["include_polygon"].activate()
    app.map.layer["modelmaker_delft3dfm"].layer["exclude_polygon"].activate()
    # Show the grid and mask
    app.map.layer["sfincs_cht"].layer["grid"].activate()
    # app.map.layer["sfincs_cht"].layer["mask_include"].activate()
    # app.map.layer["sfincs_cht"].layer["mask_open_boundary"].activate()
    # app.map.layer["sfincs_cht"].layer["mask_outflow_boundary"].activate()
    update()

# def draw_include_polygon(*args):
#     app.map.layer["modelmaker_delft3dfm"].layer["include_polygon"].crs = app.crs
#     app.map.layer["modelmaker_delft3dfm"].layer["include_polygon"].draw()

# def delete_include_polygon(*args):
#     if len(app.toolbox["modelmaker_delft3dfm"].include_polygon) == 0:
#         return
#     index = app.gui.getvar("modelmaker_delft3dfm", "include_polygon_index")
#     gdf = app.map.layer["modelmaker_delft3dfm"].layer["include_polygon"].delete_feature(index)
#     app.toolbox["modelmaker_delft3dfm"].include_polygon = gdf
#     update()

# def load_include_polygon(*args):
#     full_name, path, name, ext, fltr = app.gui.window.dialog_open_file("Select include polygon file ...", filter="*.geojson")
#     okay = True
#     if not okay:
#         return
#     app.gui.setvar("modelmaker_delft3dfm", "include_polygon_file", name)
#     app.toolbox["modelmaker_delft3dfm"].read_include_polygon()
#     app.toolbox["modelmaker_delft3dfm"].plot_include_polygon()
#     update()

# def save_include_polygon(*args):
#     app.toolbox["modelmaker_delft3dfm"].write_include_polygon()

# def select_include_polygon(*args):
#     index = args[0]
#     app.map.layer["modelmaker_delft3dfm"].layer["include_polygon"].activate_feature(index)

# def include_polygon_created(gdf, index, id):
#     app.toolbox["modelmaker_delft3dfm"].include_polygon = gdf
#     nrp = len(app.toolbox["modelmaker_delft3dfm"].include_polygon)
#     app.gui.setvar("modelmaker_delft3dfm", "include_polygon_index", nrp - 1)
#     update()

# def include_polygon_modified(gdf, index, id):
#     app.toolbox["modelmaker_delft3dfm"].include_polygon = gdf

# def include_polygon_selected(index):
#     # Selected from map
#     app.gui.setvar("modelmaker_delft3dfm", "include_polygon_index", index)
#     update()

def draw_exclude_polygon(*args):
    app.map.layer["modelmaker_delft3dfm"].layer["exclude_polygon"].crs = app.crs
    app.map.layer["modelmaker_delft3dfm"].layer["exclude_polygon"].draw()
    update()

def delete_exclude_polygon(*args):
    if len(app.toolbox["modelmaker_delft3dfm"].exclude_polygon) == 0:
        return
    index = app.gui.getvar("modelmaker_delft3dfm", "exclude_polygon_index")
    # Delete from map
    gdf = app.map.layer["modelmaker_delft3dfm"].layer["exclude_polygon"].delete_feature(index)
    app.toolbox["modelmaker_delft3dfm"].exclude_polygon = gdf
    update()

def load_exclude_polygon(*args):
    fname = app.gui.window.dialog_open_file("Select file ...",
                                        # file_name="coastlines.shp",
                                        filter= None, #"*.obs",
                                        allow_directory_change=True,
                                        multiple=True)
    app.gui.setvar("modelmaker_delft3dfm", "exclude_polygon_file", fname[2])
    app.toolbox["modelmaker_delft3dfm"].read_exclude_polygon()
    app.toolbox["modelmaker_delft3dfm"].plot_exclude_polygon()
    update()

def save_exclude_polygon(*args):
    file_name = app.gui.getvar("modelmaker_delft3dfm", "exclude_polygon")
    rsp = app.gui.window.dialog_save_file("Select file ...",
                                    file_name=file_name,
                                    filter="*.geojson",
                                    allow_directory_change=False)
    app.gui.setvar("modelmaker_delft3dfm", "exclude_polygon_file", rsp[2])
    app.toolbox["modelmaker_delft3dfm"].write_exclude_polygon()

def select_exclude_polygon(*args):
    index = args[0]
    app.map.layer["modelmaker_delft3dfm"].layer["exclude_polygon"].activate_feature(index)

def exclude_polygon_created(gdf, index, id):
    app.toolbox["modelmaker_delft3dfm"].exclude_polygon = gdf
    nrp = len(app.toolbox["modelmaker_delft3dfm"].exclude_polygon)
    app.gui.setvar("modelmaker_delft3dfm", "exclude_polygon_index", nrp - 1)
    update()

def exclude_polygon_modified(gdf, index, id):
    app.toolbox["modelmaker_delft3dfm"].exclude_polygon = gdf

def exclude_polygon_selected(index):
    app.gui.setvar("modelmaker_delft3dfm", "exclude_polygon_index", index)
    update()

def update():
    # Include
    # nrp = len(app.toolbox["modelmaker_delft3dfm"].include_polygon)
    # incnames = []
    # for ip in range(nrp):
    #     incnames.append(str(ip + 1))
    # app.gui.setvar("modelmaker_delft3dfm", "nr_include_polygons", nrp)
    # app.gui.setvar("modelmaker_delft3dfm", "include_polygon_names", incnames)
    # index = app.gui.getvar("modelmaker_delft3dfm", "include_polygon_index")
    # if index > nrp - 1:
    #     index = max(nrp - 1, 0)
    # app.gui.setvar("modelmaker_delft3dfm", "include_polygon_index", index)

    # Exclude
    nrp = len(app.toolbox["modelmaker_delft3dfm"].exclude_polygon)
    excnames = []
    for ip in range(nrp):
        excnames.append(str(ip + 1))
    app.gui.setvar("modelmaker_delft3dfm", "nr_exclude_polygons", nrp)
    app.gui.setvar("modelmaker_delft3dfm", "exclude_polygon_names", excnames)
    index = app.gui.getvar("modelmaker_delft3dfm", "exclude_polygon_index")
    if index > nrp - 1:
        index = max(nrp - 1, 0)
    app.gui.setvar("modelmaker_delft3dfm", "exclude_polygon_index", index)
    # Update GUI
    app.gui.window.update()

def update_mask(*args):
    app.toolbox["modelmaker_delft3dfm"].update_mask()

def cut_polygon(*args):
    app.toolbox["modelmaker_delft3dfm"].cut_polygon()

def cut_coastline(*args):
    app.toolbox["modelmaker_delft3dfm"].cut_coastline()

