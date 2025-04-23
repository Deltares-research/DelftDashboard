# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
import os

from delftdashboard.app import app
from delftdashboard.operations import map

from cht_sfincs import SFINCS
# from delft3dfm import Delft3DFM
from cht_hurrywave import HurryWave
from cht_nesting import nest1

def select(*args):
    # Select the nesting toolbox
    map.update()
    # Set detail model loaded to False to avoid confusion
    app.gui.setvar("nesting", "detail_model_type", "")
    app.gui.setvar("nesting", "detail_model_loaded", False)
    update()

def update(*args):
    # Update the nesting toolbox
    # Set the detail model names
    if app.active_model.name == "sfincs_cht":
        detail_model_types = ["sfincs_cht"]
    elif app.active_model.name == "delft3dfm":
        detail_model_types = ["sfincs_cht", "delft3dfm"]
    elif app.active_model.name == "hurrywave":
        detail_model_types = ["sfincs_cht", "hurrywave"]
    else:
        detail_model_types = []
    app.gui.setvar("nesting", "detail_model_types", detail_model_types)    

    # Check if the current model name is in the detail model names
    # If not set the detail model name to the first in the list
    detail_model_type = app.gui.getvar("nesting", "detail_model_type")
    if detail_model_type not in detail_model_types:
        app.gui.setvar("nesting", "detail_model_type", app.gui.getvar("nesting", "detail_model_types")[0])   
   
    # Set the detail model long names
    long_names = []
    for model_name in app.gui.getvar("nesting", "detail_model_types"):
        long_names.append(app.model[model_name].long_name)    

    app.gui.setvar("nesting", "detail_model_type_long_names", long_names)        

    app.gui.window.update()

def load_detail_model(*args):    # Load the nesting toolbox

    detail_model_type = app.gui.getvar("nesting", "detail_model_type")

    if detail_model_type == "sfincs_cht":
        rsp = app.gui.window.dialog_open_file("Select file ...",
                                            file_name="sfincs.inp",
                                            filter="sfincs.inp",
                                            allow_directory_change=True)
    elif detail_model_type == "hurrywave":
        rsp = app.gui.window.dialog_open_file("Select file ...",
                                            file_name="hurrywave.inp",
                                            filter="hurrywave.inp",
                                            allow_directory_change=True)
    else:
        # This should never happen
        print("Unknown detail model name: ", detail_model_type)
        return    

    if rsp[0]:
        app.gui.setvar("nesting", "detail_model_file", rsp[0])
        app.gui.setvar("nesting", "detail_model_loaded", True) 
    else:
        app.gui.setvar("nesting", "detail_model_file", "")
        app.gui.setvar("nesting", "detail_model_loaded", False)
        return

def select_detail_model_type(*args):
    app.gui.setvar("nesting", "detail_model_loaded", False)

def edit_obs_point_prefix(*args):
    pass

def perform_nesting_step_1(*args):

    detail_model_type = app.gui.getvar("nesting", "detail_model_type")
    detail_model_file = app.gui.getvar("nesting", "detail_model_file")

    if app.active_model.name == "sfincs_cht":
        # Points were only added to the sfincs_cht model. Need to know new file name.
        file_name = app.model["sfincs_cht"].domain.input.variables.obsfile
        if not file_name:
            file_name = "sfincs.obs"
        rsp = app.gui.window.dialog_save_file("Select file ...",
                                            file_name=file_name,
                                            filter="*.obs",
                                            allow_directory_change=False)
        if rsp[0]:
            obsfile = rsp[2] # file name without path
        else:
            return

    elif app.active_model.name == "hurrywave":
        if detail_model_type == "sfincs_cht":
            # Getting time series for SnapWave
            spectra = False
        else:
            # Getting spectra for other wave model
            spectra = True
        # Points were only added to the sfincs_cht model. Need to know new file name, but also it we need osp and obs files.
        if spectra:
            file_name = app.model["hurrywave"].domain.input.variables.ospfile
            if not file_name:
                file_name = "hurrywave.osp"
            rsp = app.gui.window.dialog_save_file("Select file ...",
                                                file_name=file_name,
                                                filter="*.osp",
                                                allow_directory_change=False)
            if rsp[0]:
                ospfile = rsp[2] # file name without path
            else:
                return
        else:
            file_name = app.model["hurrywave"].domain.input.variables.obsfile
            if not file_name:
                file_name = "hurrywave.obs"
            rsp = app.gui.window.dialog_save_file("Select file ...",
                                                file_name=file_name,
                                                filter="*.obs",
                                                allow_directory_change=False)
            if rsp[0]:
                obsfile = rsp[2] # file name without path
            else:
                return

    # Add waitbox
    wb = app.gui.window.dialog_wait("Performing nesting step 1 ...")

    # Get the folder name of the selected file
    path = os.path.dirname(detail_model_file)

    print("Reading detail model ...")
    if detail_model_type == "sfincs_cht":
        detail_model = SFINCS()
        detail_model.path = path
        detail_model.read()
    elif detail_model_type == "hurrywave":
        detail_model = HurryWave()
        detail_model.path = path
        detail_model.read()

    # Do some checks here
    if detail_model_type == "sfincs_cht" and app.active_model.name == "hurrywave":
        # Make sure that SnapWave is activated in the sfincs_cht model
        if not detail_model.input.variables.snapwave:
            wb.close()
            app.gui.window.dialog_warning("SnapWave is not activated in the SFINCS model. It can not be nested in HurryWave.")
            return
        # Make sure that there is a bwv file in the sfincs_cht model
        if not detail_model.input.variables.snapwave_bndfile:
            wb.close()
            app.gui.window.dialog_warning("No snapwave bnd file found in the SFINCS model. It can not be nested in HurryWave.")
            return

    obs_point_prefix = app.gui.getvar("nesting", "obs_point_prefix") 

    okay = nest1(app.active_model.domain, detail_model, obs_point_prefix=obs_point_prefix)

    wb.close()

    if okay:
        print("Nesting step 1 completed successfully")
        # Update observations layer and save the observation points
        if app.active_model.name == "sfincs_cht":
            app.active_model.domain.input.variables.obsfile = obsfile # file name without path
            app.active_model.domain.observation_points.write()
            gdf = app.active_model.domain.observation_points.gdf
            app.map.layer["sfincs_cht"].layer["observation_points"].set_data(gdf, 0)
            app.gui.setvar("sfincs_cht", "active_observation_point", 0)
            app.gui.setvar("sfincs_cht", "nr_observation_points", len(gdf))
        elif app.active_model.name == "hurrywave":
            if spectra:
                app.active_model.domain.input.variables.ospfile = ospfile # file name without path
                app.active_model.domain.observation_points_sp2.write()
                gdf = app.active_model.domain.observation_points_sp2.gdf
                app.map.layer["hurrywave"].layer["observation_points_spectra"].set_data(gdf, 0)
                app.gui.setvar("hurrywave", "active_observation_point_spectra", 0)
                app.gui.setvar("hurrywave", "nr_observation_points_spectra", len(gdf))
            else:
                app.active_model.domain.input.variables.obsfile = obsfile # file name without path
                app.active_model.domain.observation_points_regular.write()
                gdf = app.active_model.domain.observation_points_regular.gdf
                app.map.layer["hurrywave"].layer["observation_points_regular"].set_data(gdf, 0)
                app.gui.setvar("hurrywave", "active_observation_point_regular", 0)
                app.gui.setvar("hurrywave", "nr_observation_points_regular", len(gdf))
