# -*- coding: utf-8 -*-
"""
GUI methods for modelmaker_hurrywave -> mask_boundary_cells

Created on Mon May 10 12:18:09 2021

@author: Maarten van Ormondt
"""

from ddb import ddb

def select(*args):
    # De-activate existing layers
    ddb.update_map()
    # Show the mask boundary layer
    ddb.map.layer["modelmaker_hurrywave"].layer["mask_boundary"].set_mode("active")

def select_boundary_polygon(*args):
    pass

def draw_boundary_polygon(*args):
    ddb.map.layer["modelmaker_hurrywave"].layer["mask_boundary"].draw_polygon()

def delete_boundary_polygon(*args):
    pass

def load_boundary_polygon(*args):
    pass

def save_boundary_polygon(*args):
    pass

def boundary_polygon_created(gdf, feature_shape, feature_id):
    ddb.toolbox["modelmaker_hurrywave"].boundary_polygon = gdf
    nrp = len(ddb.toolbox["modelmaker_hurrywave"].boundary_polygon)
    ddb.gui.setvar("modelmaker_hurrywave", "nr_boundary_polygon_index", nrp - 1)
    update()

def boundary_polygon_modified(gdf, feature_shape, feature_id):
    pass

def boundary_polygon_selected(gdf, feature_shape, feature_id):
    pass


def update():

    nrp = len(ddb.toolbox["modelmaker_hurrywave"].boundary_polygon)
    names = []
    for ip in range(nrp):
        names.append(str(ip + 1))
    ddb.gui.setvar("modelmaker_hurrywave", "nr_boundary_polygons", nrp)
    ddb.gui.setvar("modelmaker_hurrywave", "nr_boundary_polygon_names", names)


    # group = "modelmaker_hurrywave"
    # boundary_names = []
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
