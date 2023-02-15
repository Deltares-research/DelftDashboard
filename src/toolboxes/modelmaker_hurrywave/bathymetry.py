# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

from ddb import ddb
from cht.bathymetry.bathymetry_database import bathymetry_database

def select(*args):
    # De-activate existing layers
    ddb.update_map()

def select_bathymetry_source(*args):
    source = args[0]
    dataset_names, dataset_long_names, dataset_source_names = bathymetry_database.dataset_names(source=source)
    ddb.gui.setvar("modelmaker_hurrywave", "bathymetry_dataset_names", dataset_names)
    ddb.gui.setvar("modelmaker_hurrywave", "bathymetry_dataset_index", 0)


def select_bathymetry_dataset(*args):
    pass


def use_dataset(*args):
    group = "modelmaker_hurrywave"
    names = ddb.gui.getvar(group, "bathymetry_dataset_names")
    index = ddb.gui.getvar(group, "bathymetry_dataset_index")
    name  = names[index]
    if name not in ddb.gui.getvar(group, "selected_bathymetry_dataset_names"):
        d = bathymetry_database.get_dataset(name)
        dataset = {"dataset": d, "zmin": -99999.0, "zmax": 99999.0}
        ddb.toolbox["modelmaker_hurrywave"].selected_bathymetry_datasets.append(dataset)
        ddb.gui.setvar(group, "selected_bathymetry_dataset_index", len(ddb.toolbox["modelmaker_hurrywave"].selected_bathymetry_datasets) - 1)
        update()


def select_selected_bathymetry_dataset(*args):
    update()


def remove_selected_bathymetry_dataset(*args):
    if len(ddb.toolbox["modelmaker_hurrywave"].selected_bathymetry_datasets) == 0:
        return
    group = "modelmaker_hurrywave"
    index = ddb.gui.getvar(group, "selected_bathymetry_dataset_index")
    ddb.toolbox["modelmaker_hurrywave"].selected_bathymetry_datasets.pop(index)
    update()


def  move_up_selected_bathymetry_dataset(*args):
    if len(ddb.toolbox["modelmaker_hurrywave"].selected_bathymetry_datasets) < 2:
        return
    group = "modelmaker_hurrywave"
    index = ddb.gui.getvar(group, "selected_bathymetry_dataset_index")
    if index == 0:
        return
    i0 = index
    i1 = index - 1
    ddb.toolbox["modelmaker_hurrywave"].selected_bathymetry_datasets[i0],\
    ddb.toolbox["modelmaker_hurrywave"].selected_bathymetry_datasets[i1] = \
    ddb.toolbox["modelmaker_hurrywave"].selected_bathymetry_datasets[i1], \
    ddb.toolbox["modelmaker_hurrywave"].selected_bathymetry_datasets[i0]
    ddb.gui.setvar(group, "selected_bathymetry_dataset_index", index - 1)
    update()


def move_down_selected_bathymetry_dataset(*args):
    if len(ddb.toolbox["modelmaker_hurrywave"].selected_bathymetry_datasets) < 2:
        return
    group = "modelmaker_hurrywave"
    index = ddb.gui.getvar(group, "selected_bathymetry_dataset_index")
    if index == len(ddb.toolbox["modelmaker_hurrywave"].selected_bathymetry_datasets) - 1:
        return
    i0 = index
    i1 = index + 1
    ddb.toolbox["modelmaker_hurrywave"].selected_bathymetry_datasets[i0],\
    ddb.toolbox["modelmaker_hurrywave"].selected_bathymetry_datasets[i1] = \
    ddb.toolbox["modelmaker_hurrywave"].selected_bathymetry_datasets[i1], \
    ddb.toolbox["modelmaker_hurrywave"].selected_bathymetry_datasets[i0]
    ddb.gui.setvar(group, "selected_bathymetry_dataset_index", index + 1)
    update()


def edit_zmax_bathymetry_dataset(*args):
    group = "modelmaker_hurrywave"
    index = ddb.gui.getvar(group, "selected_bathymetry_dataset_index")
    ddb.toolbox["modelmaker_hurrywave"].selected_bathymetry_datasets[index]["zmax"] = args[0]


def edit_zmin_bathymetry_dataset(*args):
    group = "modelmaker_hurrywave"
    index = ddb.gui.getvar(group, "selected_bathymetry_dataset_index")
    ddb.toolbox["modelmaker_hurrywave"].selected_bathymetry_datasets[index]["zmin"] = args[0]


def update():
    group = "modelmaker_hurrywave"
    selected_names = []
    nrd = len(ddb.toolbox["modelmaker_hurrywave"].selected_bathymetry_datasets)
    if nrd>0:
        for dataset in ddb.toolbox["modelmaker_hurrywave"].selected_bathymetry_datasets:
            selected_names.append(dataset["dataset"].name)
        ddb.gui.setvar(group, "selected_bathymetry_dataset_names", selected_names)
        index = ddb.gui.getvar(group, "selected_bathymetry_dataset_index")
        if index > nrd - 1:
            index = nrd - 1
        dataset = ddb.toolbox["modelmaker_hurrywave"].selected_bathymetry_datasets[index]
        ddb.gui.setvar(group, "selected_bathymetry_dataset_zmin", dataset["zmin"])
        ddb.gui.setvar(group, "selected_bathymetry_dataset_zmax", dataset["zmax"])
    else:
        ddb.gui.setvar(group, "selected_bathymetry_dataset_names", [])
        ddb.gui.setvar(group, "selected_bathymetry_dataset_index", 0)
        ddb.gui.setvar(group, "selected_bathymetry_dataset_zmin", -99999.0)
        ddb.gui.setvar(group, "selected_bathymetry_dataset_zmax", 99999.0)
    ddb.gui.setvar(group, "nr_selected_bathymetry_datasets", nrd)


def generate_bathymetry(*args):
    grid = ddb.model["hurrywave"].domain.grid
    bathymetry_list = ddb.toolbox["modelmaker_hurrywave"].selected_bathymetry_datasets
    ddb.model["hurrywave"].domain.bathymetry.build(grid, bathymetry_list)
    ddb.model["hurrywave"].domain.bathymetry.write()
