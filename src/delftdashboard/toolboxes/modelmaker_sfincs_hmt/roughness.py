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
    group = "modelmaker_sfincs_hmt"
    landuse_names = app.gui.getvar(group, "roughness_dataset_names")
    index = app.gui.getvar(group, "roughness_dataset_index")
    name = landuse_names[index]

    if name != "Use constants":
        dataset = {"lulc": landuse_names[index]}
        # for now we only support 1 dataset from the GUI
        app.toolbox["modelmaker_sfincs_hmt"].selected_manning_datasets = [dataset] 
        app.gui.setvar("modelmaker_sfincs_hmt", "roughness_reclass_table", f"{landuse_names[index]}_mapping.csv")

def select_reclass_table(*args):
    fname = app.gui.open_file_name(
        "Select mapping file to convert landuse/ladncover to Mannings' n", ".csv",
    )
    if fname:
        app.gui.setvar("modelmaker_sfincs_hmt", "roughness_reclass_table", fname)  
        app.toolbox["modelmaker_sfincs_hmt"].selected_manning_datasets[0].update({"reclass_table": fname})

def generate_manning(*args):
    app.toolbox["modelmaker_sfincs_hmt"].generate_manning()