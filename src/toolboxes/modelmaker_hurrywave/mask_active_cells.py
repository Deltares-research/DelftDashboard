# -*- coding: utf-8 -*-
"""
GUI methods for modelmaker_hurrywave -> mask_active_cells

Created on Mon May 10 12:18:09 2021

@author: Maarten van Ormondt
"""

from ddb import ddb

def select(*args):
    # De-activate existing layers
    ddb.update_map()
    # Show the mask include and exclude layer
    ddb.map.layer["modelmaker_hurrywave"].layer["mask_include"].set_mode("active")
    ddb.map.layer["modelmaker_hurrywave"].layer["mask_exclude"].set_mode("active")

def select_include_polygon(*args):
    pass

def draw_include_polygon(*args):
    ddb.map.layer["modelmaker_hurrywave"].layer["mask_include"].draw_polygon()

def delete_include_polygon(*args):
    pass

def load_include_polygon(*args):
    pass

def save_include_polygon(*args):
    pass

def include_polygon_created(gdf, feature_shape, feature_id):
    ddb.toolbox["modelmaker_hurrywave"].include_polygon = gdf
    nrp = len(ddb.toolbox["modelmaker_hurrywave"].include_polygon)
    ddb.gui.setvar("modelmaker_hurrywave", "include_polygon_index", nrp - 1)
    update()

def include_polygon_modified(gdf, feature_shape, feature_id):
    pass

def include_polygon_selected(gdf, feature_shape, feature_id):
    pass

def select_exclude_polygon(*args):
    pass

def draw_exclude_polygon(*args):
    ddb.toolbox["modelmaker_hurrywave"].draw_exclude_polygon()

def delete_exclude_polygon(*args):
    pass

def load_exclude_polygon(*args):
    pass

def save_exclude_polygon(*args):
    pass

def exclude_polygon_created(gdf, feature_shape, feature_id):
    ddb.toolbox["modelmaker_hurrywave"].exclude_polygon = gdf
    nrp = len(ddb.toolbox["modelmaker_hurrywave"].exclude_polygon)
    ddb.gui.setvar("modelmaker_hurrywave", "nr_exclude_polygon_index", nrp - 1)
    update()

def exclude_polygon_modified(gdf, feature_shape, feature_id):
    pass

def exclude_polygon_selected(gdf, feature_shape, feature_id):
    pass

def update():

    nrp = len(ddb.toolbox["modelmaker_hurrywave"].include_polygon)
    incnames = []
    for ip in range(nrp):
        incnames.append(str(ip + 1))
    ddb.gui.setvar("modelmaker_hurrywave", "nr_include_polygons", nrp)
    ddb.gui.setvar("modelmaker_hurrywave", "include_polygon_names", incnames)

    nrp = len(ddb.toolbox["modelmaker_hurrywave"].exclude_polygon)
    excnames = []
    for ip in range(nrp):
        excnames.append(str(ip + 1))
    ddb.gui.setvar("modelmaker_hurrywave", "nr_exclude_polygons", nrp)
    ddb.gui.setvar("modelmaker_hurrywave", "exclude_polygon_names", excnames)

    ddb.gui.update()


    # group = "modelmaker_hurrywave"
    # include_names = []
    # nrp = len(ddb.toolbox["modelmaker_hurrywave"].selected_bathymetry_datasets)
    # if nrd>0:
    #     for dataset in ddb.toolbox["modelmaker_hurrywave"].selected_bathymetry_datasets:
    #         selected_names.append(dataset["dataset"].name)
    #     ddb.gui.setvar(group, "selected_bathymetry_dataset_names", selected_names)
    #     index = ddb.gui.getvar(group, "selected_bathymetry_dataset_index")
    #     if index > nrd - 1:
    #         index = nrd - 1
    #     dataset = ddb.toolbox["modelmaker_hurrywave"].selected_bathymetry_datasets[index]
    #     ddb.gui.setvar(group, "selected_bathymetry_dataset_zmin", dataset["zmin"])
    #     ddb.gui.setvar(group, "selected_bathymetry_dataset_zmax", dataset["zmax"])

    pass


def update_mask(*args):
    ddb.toolbox["modelmaker_hurrywave"].update_mask()
