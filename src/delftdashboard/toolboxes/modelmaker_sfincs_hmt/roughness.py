# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations import map

def select(*args):
    # De-activate existing layers
    map.update()
    app.map.layer["sfincs_hmt"].layer["grid"].set_mode("active")


def select_manning_dataset(*args):
    landuse_names = app.gui.getvar("modelmaker_sfincs_hmt", "roughness_dataset_names")
    app.gui.setvar("modelmaker_sfincs_hmt", "selected_manning_dataset_index", args[0])
    app.gui.setvar("modelmaker_sfincs_hmt", "selected_manning_dataset_names", [landuse_names[args[0]]])

    if landuse_names[args[0]] != "Use constants":
        dataset = {"lulc_fn": landuse_names[args[0]]}
        # for now we only support 1 dataset from the GUI
        app.toolbox["modelmaker_sfincs_hmt"].selected_manning_datasets = [dataset]  
        app.gui.setvar("modelmaker_sfincs_hmt", "roughness_mapping_name", f"{landuse_names[args[0]]}_mapping.csv")

def select_mapping_file(*args):
    fname = app.gui.open_file_name(
        "Select mapping file to convert landuse to mannings' n", ".csv",
    )
    if fname:
        app.gui.setvar("modelmaker_sfincs_hmt", "roughness_mapping_name", fname)  

def generate_manning(*args):
    app.toolbox["modelmaker_sfincs_hmt"].generate_manning()