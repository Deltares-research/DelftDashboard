# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
import os

from delftdashboard.app import app

from cht_sfincs import SFINCS
# from delft3dfm import Delft3DFM
from cht_hurrywave import HurryWave
from cht_nesting import nest2

def select(*args):
    # Select the nesting toolbox
    app.map.update()
    # Set detail model loaded to False to avoid confusion
    app.gui.setvar("nesting", "overall_model_type", "")
    app.gui.setvar("nesting", "overall_model_loaded", False)
    update()

def update(*args):
    # Update the nesting toolbox
    # Set the detail model names
    if app.active_model.name == "sfincs_cht":
        # Check if waves are turned on
        if app.active_model.domain.input.variables.snapwave:
            overall_model_types = ["sfincs_cht", "delft3dfm", "hurrywave"]
        else:
            overall_model_types = ["sfincs_cht", "delft3dfm"]
    elif app.active_model.name == "delft3dfm":
        overall_model_types = ["sfincs_cht", "delft3dfm"]
    elif app.active_model.name == "hurrywave":
        overall_model_types = ["hurrywave"]
    else:
        overall_model_types = []

    # Check if all overall model types are available
    for model_name in overall_model_types:
        if model_name not in app.model:
            overall_model_types.remove(model_name)

    app.gui.setvar("nesting", "overall_model_types", overall_model_types)

    # Check if the current model name is in the detail model names
    # If not set the detail model name to the first in the list
    overall_model_type = app.gui.getvar("nesting", "overall_model_type")
    if overall_model_type not in overall_model_types:
        app.gui.setvar("nesting", "overall_model_type", app.gui.getvar("nesting", "overall_model_types")[0])   
   
    # Set the detail model long names
    long_names = []
    for model_name in app.gui.getvar("nesting", "overall_model_types"):
        long_names.append(app.model[model_name].long_name)    

    app.gui.setvar("nesting", "overall_model_type_long_names", long_names)        

    app.gui.window.update()

def load_overall_model(*args):    # Load the nesting toolbox

    overall_model_type = app.gui.getvar("nesting", "overall_model_type")

    if overall_model_type == "sfincs_cht":
        rsp = app.gui.window.dialog_open_file("Select file ...",
                                            file_name="sfincs.inp",
                                            filter="sfincs.inp",
                                            allow_directory_change=True)
    elif overall_model_type == "hurrywave":
        rsp = app.gui.window.dialog_open_file("Select file ...",
                                            file_name="hurrywave.inp",
                                            filter="hurrywave.inp",
                                            allow_directory_change=True)
    else:
        # This should never happen
        print("Unknown overall model name: ", overall_model_type)
        return    

    if rsp[0]:
        app.gui.setvar("nesting", "overall_model_file", rsp[0])
        app.gui.setvar("nesting", "overall_model_loaded", True) 
    else:
        app.gui.setvar("nesting", "overall_model_file", "")
        app.gui.setvar("nesting", "overall_model_loaded", False)
        return

def select_overall_model_type(*args):
    app.gui.setvar("nesting", "overall_model_loaded", False)

def edit_obs_point_prefix(*args):
    pass

def edit_water_level_correction(*args):
    pass

def perform_nesting_step_2(*args):

    if app.active_model.name == "sfincs_cht":
        # Points were only added to the sfincs_cht model. Need to know new file name.
        file_name = app.model["sfincs_cht"].domain.input.variables.bzsfile
        if not file_name:
            file_name = "sfincs.bzs"
        rsp = app.gui.window.dialog_save_file("Select file ...",
                                            file_name=file_name,
                                            filter="*.bzs",
                                            allow_directory_change=False)
        if rsp[0]:
            bzsfile = rsp[2] # file name without path
        else:
            return
    elif app.active_model.name == "hurrywave":
        # Points were only added to the sfincs_cht model. Need to know new file name.
        file_name = app.model["hurrywave"].domain.input.variables.bspfile
        if not file_name:
            file_name = "hurrywave.bsp"
        rsp = app.gui.window.dialog_save_file("Select file ...",
                                            file_name=file_name,
                                            filter="*.bsp",
                                            allow_directory_change=False)
        if rsp[0]:
            bspfile = rsp[2] # file name without path
        else:
            return

    # Add waitbox
    wb = app.gui.window.dialog_wait("Performing nesting step 2 ...")

    overall_model_type = app.gui.getvar("nesting", "overall_model_type")
    overall_model_file = app.gui.getvar("nesting", "overall_model_file")

    # Get the folder name of the selected file
    path = os.path.dirname(overall_model_file)

    if overall_model_type == "sfincs_cht":
        overall_model = SFINCS()
        overall_model.path = path
    elif overall_model_type == "hurrywave":
        overall_model = HurryWave()
        overall_model.path = path

    obs_point_prefix = app.gui.getvar("nesting", "obs_point_prefix")    

    okay = nest2(overall_model,
                 app.active_model.domain,
                 obs_point_prefix=obs_point_prefix,
                 boundary_water_level_correction=0.0)

    wb.close()

    if okay:
        print("Nesting step 2 completed successfully")
        # Update observations layer and save the observation points
        if app.active_model.name == "sfincs_cht":
            app.active_model.domain.input.variables.bzsfile = bzsfile # file name without path
            app.active_model.domain.boundary_conditions.write_boundary_conditions_timeseries()
        elif app.active_model.name == "hurrywave":
            app.active_model.domain.input.variables.bspfile = bspfile # file name without path
            app.active_model.domain.boundary_conditions.write_boundary_conditions_spectra()
