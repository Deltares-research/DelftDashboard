# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

from delftdashboard.app import app
from cht_bathymetry.bathymetry_database import bathymetry_database
from delftdashboard.operations import map

def select(*args):
    # De-activate() existing layers
    map.update()
    app.map.layer["sfincs_cht"].layer["grid"].activate()

def select_bathymetry_source(*args):
    source = args[0]
    dataset_names, dataset_long_names, dataset_source_names = bathymetry_database.dataset_names(source=source)
    app.gui.setvar("modelmaker_sfincs_cht", "bathymetry_dataset_names", dataset_names)
    app.gui.setvar("modelmaker_sfincs_cht", "bathymetry_dataset_index", 0)


def select_bathymetry_dataset(*args):
    pass


def use_dataset(*args):
    group = "modelmaker_sfincs_cht"
    names = app.gui.getvar(group, "bathymetry_dataset_names")
    index = app.gui.getvar(group, "bathymetry_dataset_index")
    name  = names[index]
    if name not in app.gui.getvar(group, "selected_bathymetry_dataset_names"):
        d = bathymetry_database.get_dataset(name)
        dataset = {"dataset": d, "zmin": -99999.0, "zmax": 99999.0}
        app.toolbox["modelmaker_sfincs_cht"].selected_bathymetry_datasets.append(dataset)
        app.gui.setvar(group, "selected_bathymetry_dataset_index", len(app.toolbox["modelmaker_sfincs_cht"].selected_bathymetry_datasets) - 1)
        update()


def select_selected_bathymetry_dataset(*args):
    update()


def remove_selected_bathymetry_dataset(*args):
    if len(app.toolbox["modelmaker_sfincs_cht"].selected_bathymetry_datasets) == 0:
        return
    group = "modelmaker_sfincs_cht"
    index = app.gui.getvar(group, "selected_bathymetry_dataset_index")
    app.toolbox["modelmaker_sfincs_cht"].selected_bathymetry_datasets.pop(index)
    update()


def  move_up_selected_bathymetry_dataset(*args):
    if len(app.toolbox["modelmaker_sfincs_cht"].selected_bathymetry_datasets) < 2:
        return
    group = "modelmaker_sfincs_cht"
    index = app.gui.getvar(group, "selected_bathymetry_dataset_index")
    if index == 0:
        return
    i0 = index
    i1 = index - 1
    app.toolbox["modelmaker_sfincs_cht"].selected_bathymetry_datasets[i0],\
    app.toolbox["modelmaker_sfincs_cht"].selected_bathymetry_datasets[i1] = \
    app.toolbox["modelmaker_sfincs_cht"].selected_bathymetry_datasets[i1], \
    app.toolbox["modelmaker_sfincs_cht"].selected_bathymetry_datasets[i0]
    app.gui.setvar(group, "selected_bathymetry_dataset_index", index - 1)
    update()


def move_down_selected_bathymetry_dataset(*args):
    if len(app.toolbox["modelmaker_sfincs_cht"].selected_bathymetry_datasets) < 2:
        return
    group = "modelmaker_sfincs_cht"
    index = app.gui.getvar(group, "selected_bathymetry_dataset_index")
    if index == len(app.toolbox["modelmaker_sfincs_cht"].selected_bathymetry_datasets) - 1:
        return
    i0 = index
    i1 = index + 1
    app.toolbox["modelmaker_sfincs_cht"].selected_bathymetry_datasets[i0],\
    app.toolbox["modelmaker_sfincs_cht"].selected_bathymetry_datasets[i1] = \
    app.toolbox["modelmaker_sfincs_cht"].selected_bathymetry_datasets[i1], \
    app.toolbox["modelmaker_sfincs_cht"].selected_bathymetry_datasets[i0]
    app.gui.setvar(group, "selected_bathymetry_dataset_index", index + 1)
    update()


def edit_zmax_bathymetry_dataset(*args):
    group = "modelmaker_sfincs_cht"
    index = app.gui.getvar(group, "selected_bathymetry_dataset_index")
    app.toolbox["modelmaker_sfincs_cht"].selected_bathymetry_datasets[index]["zmax"] = args[0]


def edit_zmin_bathymetry_dataset(*args):
    group = "modelmaker_sfincs_cht"
    index = app.gui.getvar(group, "selected_bathymetry_dataset_index")
    app.toolbox["modelmaker_sfincs_cht"].selected_bathymetry_datasets[index]["zmin"] = args[0]


def update():
    group = "modelmaker_sfincs_cht"
    selected_names = []
    nrd = len(app.toolbox["modelmaker_sfincs_cht"].selected_bathymetry_datasets)
    if nrd>0:
        for dataset in app.toolbox["modelmaker_sfincs_cht"].selected_bathymetry_datasets:
            selected_names.append(dataset["dataset"].name)
        app.gui.setvar(group, "selected_bathymetry_dataset_names", selected_names)
        index = app.gui.getvar(group, "selected_bathymetry_dataset_index")
        if index > nrd - 1:
            index = nrd - 1
        dataset = app.toolbox["modelmaker_sfincs_cht"].selected_bathymetry_datasets[index]
        app.gui.setvar(group, "selected_bathymetry_dataset_zmin", dataset["zmin"])
        app.gui.setvar(group, "selected_bathymetry_dataset_zmax", dataset["zmax"])
    else:
        app.gui.setvar(group, "selected_bathymetry_dataset_names", [])
        app.gui.setvar(group, "selected_bathymetry_dataset_index", 0)
        app.gui.setvar(group, "selected_bathymetry_dataset_zmin", -99999.0)
        app.gui.setvar(group, "selected_bathymetry_dataset_zmax", 99999.0)
    app.gui.setvar(group, "nr_selected_bathymetry_datasets", nrd)


def generate_bathymetry(*args):
    app.toolbox["modelmaker_sfincs_cht"].generate_bathymetry()

def info(*args):
    pass
