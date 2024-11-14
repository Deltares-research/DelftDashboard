# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

import os
import yaml
# from matplotlib.colors import ListedColormap
import importlib
from pyproj import CRS

from guitares.gui import GUI
from guitares.colormap import read_color_maps
from cht_bathymetry import BathymetryDatabase
from cht_tide import TideModelDatabase
from .gui import build_gui_config

from delftdashboard.app import app

def initialize():

    app.server_path = os.path.join(app.main_path, "server")
    app.config_path = os.path.join(app.main_path, "config")

    # Set default config
    app.config                  = {}
    app.config["gui_framework"] = "pyqt5"
    app.config["server_port"]   = 3000
    app.config["server_nodejs"] = False
    app.config["stylesheet"]    = ""
    app.config["title"]         = "Delft Dashboard"
    app.config["width"]         = 800
    app.config["height"]        = 600
    app.config["model"]         = []
    app.config["toolbox"]       = []
    app.config["window_icon"]   = os.path.join(app.config_path, "images", "deltares_icon.png")
    app.config["splash_file"]   = os.path.join(app.config_path, "images", "DelftDashBoard_python.jpg")
    app.config["bathymetry_database"] = ""
    app.config["sfincs_exe_path"] = ""
    app.config["hurrywave_exe_path"] = ""
    app.config["auto_update_bathymetry"] = True
    app.config["auto_update_tide_models"] = True

    # Read cfg file and override stuff in default config dict
    # cfg file contains gui config stuff, but not properties that need to be edited by the user ! It always sits in the config folder.
    cfg_file_name = os.path.join(app.config_path, "delftdashboard.cfg")
    cfgfile = open(cfg_file_name, "r")
    config = yaml.load(cfgfile, Loader=yaml.FullLoader)
    for key in config:
        app.config[key] = config[key]
    cfgfile.close()

    # Read ini file and override stuff in default config dict
    # ini file contains properties that need to be edited by the user !
    ini_file_name = os.path.join(app.main_path, "delftdashboard.ini")
    # Check if there is also a local ini file
    if os.path.exists(os.path.join(os.getcwd(), "delftdashboard.ini")):
        ini_file_name = os.path.join(os.getcwd(), "delftdashboard.ini")
    inifile = open(ini_file_name, "r")
    config = yaml.load(inifile, Loader=yaml.FullLoader)
    for key in config:
        app.config[key] = config[key]
    inifile.close()

    # Initialize GUI object
    app.gui = GUI(app,
                  framework=app.config["gui_framework"],
                  config_path=app.config_path,
                  server_path=app.server_path,
                  server_nodejs=app.config["server_nodejs"],
                  server_port=app.config["server_port"],
                  stylesheet=app.config["stylesheet"],
                  icon=app.config["window_icon"],
                  splash_file=app.config["splash_file"],
                  copy_mapbox_server_folder=False,
                  copy_maplibre_server_folder=True
                  )

    # Bathymetry database (initialize local database)
    if "bathymetry_database_path" not in app.config:
        app.config["bathymetry_database_path"] = os.path.join(app.config["data_path"], "bathymetry")
    s3_bucket = "deltares-ddb"
    s3_key = f"data/bathymetry"
    app.bathymetry_database = BathymetryDatabase(path=app.config["bathymetry_database_path"],
                                                 s3_bucket=s3_bucket,
                                                 s3_key=s3_key)

    # Check for changes in online database and download if necessary
    if app.config["auto_update_bathymetry"]:
        app.bathymetry_database.check_online_database()

    # Define some other variables
    app.crs = CRS(4326)
    if "default_bathymetry_dataset" in app.config:
        app.background_topography = app.config["default_bathymetry_dataset"]
    else:
        app.background_topography  = app.bathymetry_database.dataset_names()[0][0]

    # Tide model database
    if "tide_model_database_path" not in app.config:
        app.config["tide_model_database_path"] = os.path.join(app.config["data_path"], "tide_models")
    s3_bucket = "deltares-ddb"
    s3_key = f"data/tide_models"
    app.tide_model_database = TideModelDatabase(path=app.config["tide_model_database_path"],
                                                s3_bucket=s3_bucket,
                                                s3_key=s3_key)
    if app.config["auto_update_tide_models"]:
        app.tide_model_database.check_online_database()
    short_names, long_names = app.tide_model_database.dataset_names()
    app.gui.setvar("tide_models", "long_names", long_names)
    app.gui.setvar("tide_models", "names", short_names)

    # Use GUI variables to set the view settings    

    # Layer style
    app.gui.setvar("view_settings", "layer_style", "streets-v12")
    # Projection
    app.gui.setvar("view_settings", "projection", "mercator")
    # Topography
    app.gui.setvar("view_settings", "topography_dataset", app.background_topography)
    app.gui.setvar("view_settings", "topography_auto_update", "True")
    app.gui.setvar("view_settings", "topography_visible", True)
    app.gui.setvar("view_settings", "topography_colormap", "earth")
    app.gui.setvar("view_settings", "topography_autoscaling", True)
    app.gui.setvar("view_settings", "topography_opacity", 0.7)
    app.gui.setvar("view_settings", "topography_quality", "medium")
    app.gui.setvar("view_settings", "topography_hillshading", True)
    app.gui.setvar("view_settings", "topography_interp_method", "linear")
    # app.gui.setvar("view_settings", "topography_interp_method", "nearest")
    app.gui.setvar("view_settings", "topography_zmin", -10.0)
    app.gui.setvar("view_settings", "topography_zmax", 10.0)
    app.gui.setvar("view_settings", "layer_style", "streets-v12")
    app.gui.setvar("view_settings", "terrain_exaggeration", 1.5)
    app.gui.setvar("view_settings", "terrain_visible", False)
    # Read color maps (should be done in guitares)
    cmps = read_color_maps(os.path.join(app.config_path, "colormaps"))
    app.gui.setvar("view_settings", "colormaps", cmps)

    # Initialize toolboxes
    initialize_toolboxes()

    # Initialize models
    initialize_models()

    # Set active toolbox and model
    app.active_model   = app.model[list(app.model)[0]]
    app.active_toolbox = app.toolbox[list(app.toolbox)[0]]

    # GUI variables
    app.gui.setvar("menu", "active_model_name", "")
    app.gui.setvar("menu", "active_toolbox_name", "")
    app.gui.setvar("menu", "active_topography_name", app.background_topography)

    # # Layers tab
    # app.gui.setvar("layers", "contour_elevation", 0.0)
    # app.gui.setvar("layers", "buffer_land", 5000.0)
    # app.gui.setvar("layers", "buffer_sea", 2000.0)
    # app.gui.setvar("layers", "buffer_single", True)

    # Now build up GUI config
    build_gui_config()

def initialize_toolboxes():

    # Initialize toolboxes
    app.toolbox = {}
    for tlb in app.config["toolbox"]:
        toolbox_name = tlb["name"]
        # And initialize this toolbox
        print("Adding toolbox : " + toolbox_name)
        module = importlib.import_module("delftdashboard.toolboxes." + toolbox_name + "." + toolbox_name)
        # Initialize the toolbox
        app.toolbox[toolbox_name] = module.Toolbox(toolbox_name)
        # Set the callback module. This is the module that contains the callback functions,
        # and does not have to be the same as the toolbox module.
        # This is useful as some toolboxes do not have tabs for which modules are defined,
        # and the main module can become very busy with all the callbacks and the toolbox object.
        if app.toolbox[toolbox_name].callback_module_name is None:
            # Callback module is same as toolbox module            
            app.toolbox[toolbox_name].callback_module = module
        else:
            # Callback module is different from toolbox module
            app.toolbox[toolbox_name].callback_module = importlib.import_module(f"delftdashboard.toolboxes.{toolbox_name}.{app.toolbox[toolbox_name].callback_module_name}")
        app.toolbox[toolbox_name].initialize()

def initialize_models():

    # Initialize models
    app.model = {}
    for mdl in app.config["model"]:
        model_name = mdl["name"]
        # And initialize the domain for this model
        print("Adding model   : " + model_name)
        module = importlib.import_module("delftdashboard.models." + model_name + "." + model_name)
        app.model[model_name] = module.Model(model_name)
        if "exe_path" in mdl:
            app.model[model_name].exe_path = mdl["exe_path"]
        else:
            app.model[model_name].exe_path = ""    
        # Loop through toolboxes to see which ones should be activated for which model
        app.model[model_name].toolbox = []
        for tlb in app.config["toolbox"]:
            okay = True
            if "for_model" in tlb:
                if model_name not in tlb["for_model"]:
                    okay = False
            if okay:
                app.model[model_name].toolbox.append(tlb["name"])
        app.model[model_name].initialize()
                
