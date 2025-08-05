# -*- coding: utf-8 -*-
"""
Callback functions for bathy/topo selection
"""

from delftdashboard.app import app

def select_bathymetry_source(*args):
    source = args[0]
    dataset_names, dataset_long_names, dataset_source_names = app.bathymetry_database.dataset_names(source=source)
    group = "bathy_topo_selector"
    app.gui.setvar(group, "bathymetry_dataset_names", dataset_names)
    app.gui.setvar(group, "bathymetry_dataset_index", 0)


def select_bathymetry_dataset(*args):
    pass

def use_dataset(*args):
    group = "bathy_topo_selector"
    names = app.gui.getvar(group, "bathymetry_dataset_names")
    index = app.gui.getvar(group, "bathymetry_dataset_index")
    name  = names[index]
    if name not in app.gui.getvar(group, "selected_bathymetry_dataset_names"):
        # d = bathymetry_database.get_dataset(name)
        dataset = {"name": name, "zmin": -99999.0, "zmax": 99999.0}
        app.selected_bathymetry_datasets.append(dataset)
        app.gui.setvar(group, "selected_bathymetry_dataset_index", len(app.selected_bathymetry_datasets) - 1)
        update()


def select_selected_bathymetry_dataset(*args):
    update()


def remove_selected_bathymetry_dataset(*args):
    if len(app.selected_bathymetry_datasets) == 0:
        return
    group = "bathy_topo_selector"
    index = app.gui.getvar(group, "selected_bathymetry_dataset_index")
    app.selected_bathymetry_datasets.pop(index)
    update()


def move_up_selected_bathymetry_dataset(*args):
    if len(app.selected_bathymetry_datasets) < 2:
        return
    group = "bathy_topo_selector"
    index = app.gui.getvar(group, "selected_bathymetry_dataset_index")
    if index == 0:
        return
    i0 = index
    i1 = index - 1
    app.selected_bathymetry_datasets[i0],\
    app.selected_bathymetry_datasets[i1] = \
    app.selected_bathymetry_datasets[i1], \
    app.selected_bathymetry_datasets[i0]
    app.gui.setvar(group, "selected_bathymetry_dataset_index", index - 1)
    update()


def move_down_selected_bathymetry_dataset(*args):
    if len(app.selected_bathymetry_datasets) < 2:
        return
    group = "bathy_topo_selector"
    index = app.gui.getvar(group, "selected_bathymetry_dataset_index")
    if index == len(app.selected_bathymetry_datasets) - 1:
        return
    i0 = index
    i1 = index + 1
    app.selected_bathymetry_datasets[i0],\
    app.selected_bathymetry_datasets[i1] = \
    app.selected_bathymetry_datasets[i1], \
    app.selected_bathymetry_datasets[i0]
    app.gui.setvar(group, "selected_bathymetry_dataset_index", index + 1)
    update()


def edit_zmax_bathymetry_dataset(*args):
    group = "bathy_topo_selector"
    index = app.gui.getvar(group, "selected_bathymetry_dataset_index")
    app.selected_bathymetry_datasets[index]["zmax"] = args[0]


def edit_zmin_bathymetry_dataset(*args):
    group = "bathy_topo_selector"
    index = app.gui.getvar(group, "selected_bathymetry_dataset_index")
    app.selected_bathymetry_datasets[index]["zmin"] = args[0]

def load_polygon(*args):
    """Load a polygon from a file"""
    group = "bathy_topo_selector"
    full_name, path, name, ext, fltr = app.gui.window.dialog_open_file("Select polygon file", filter="*.geojson")
    if not full_name:
        return
    index = app.gui.getvar(group, "selected_bathymetry_dataset_index")
    app.selected_bathymetry_datasets[index]["polygon_file"] = full_name

def edit(*args):
    pass

def update():
    group = "bathy_topo_selector"
    selected_names = []
    nrd = len(app.selected_bathymetry_datasets)
    if nrd>0:
        for dataset in app.selected_bathymetry_datasets:
            # selected_names.append(dataset["dataset"].name)
            selected_names.append(dataset["name"])
        app.gui.setvar(group, "selected_bathymetry_dataset_names", selected_names)
        index = app.gui.getvar(group, "selected_bathymetry_dataset_index")
        if index > nrd - 1:
            index = nrd - 1
        dataset = app.selected_bathymetry_datasets[index]
        app.gui.setvar(group, "selected_bathymetry_dataset_zmin", dataset["zmin"])
        app.gui.setvar(group, "selected_bathymetry_dataset_zmax", dataset["zmax"])
    else:
        app.gui.setvar(group, "selected_bathymetry_dataset_names", [])
        app.gui.setvar(group, "selected_bathymetry_dataset_index", 0)
        app.gui.setvar(group, "selected_bathymetry_dataset_zmin", -99999.0)
        app.gui.setvar(group, "selected_bathymetry_dataset_zmax", 99999.0)
    app.gui.setvar(group, "nr_selected_bathymetry_datasets", nrd)

def info(*args):
    pass
