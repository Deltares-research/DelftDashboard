# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

import os
import yaml
from matplotlib.colors import ListedColormap
import importlib
from pyproj import CRS

from guitares.gui import GUI
from cht.bathymetry.bathymetry_database import bathymetry_database
from .colormap import read_colormap
from .gui import build_gui_config

from delftdashboard.app import app
from hydromt import DataCatalog


def initialize():
    app.server_path = os.path.join(app.main_path, "server")
    app.config_path = os.path.join(app.main_path, "config")

    # Set default config
    app.config = {}
    app.config["gui_framework"] = "pyqt5"
    app.config["server_port"] = 3000
    app.config["server_nodejs"] = False
    app.config["stylesheet"] = ""
    app.config["title"] = "Delft Dashboard"
    app.config["width"] = 800
    app.config["height"] = 600
    app.config["model"] = []
    app.config["toolbox"] = []
    app.config["window_icon"] = os.path.join(app.config_path, "images", "deltares.ico")
    app.config["splash_file"] = os.path.join(
        app.config_path, "images", "DelftDashBoard.jpg"
    )
    app.config["bathymetry_database"] = None
    app.config["data_libs"] = None
    app.config["working_directory"] = os.getcwd()

    # Read ini file and override stuff in default config dict
    inifile = open(os.path.join(app.config_path, "delftdashboard.ini"), "r")
    config = yaml.load(inifile, Loader=yaml.FullLoader)
    for key in config:
        app.config[key] = config[key]
    inifile.close()

    assert (
        app.config["bathymetry_database"] is not None
        or app.config["data_libs"] is not None
    ), "Bathymetry database or data_libs not defined in delftdashboard.ini"

    # Initialize GUI object
    app.gui = GUI(
        app,
        framework=app.config["gui_framework"],
        config_path=app.config_path,
        server_path=app.server_path,
        server_nodejs=app.config["server_nodejs"],
        server_port=app.config["server_port"],
        stylesheet=app.config["stylesheet"],
        icon=app.config["window_icon"],
        splash_file=app.config["splash_file"],
        copy_mapbox_server_folder=True,
    )

    # # Show splash screen
    # self.show_splash()

    # Define some other variables
    app.crs = CRS(4326)
    app.auto_update_topography = True
    app.background_topography = "gebco22"
    if app.config["bathymetry_database"] is not None:
        app.bathymetry_database_path = app.config["bathymetry_database"]
        bathymetry_database.initialize(app.bathymetry_database_path)
    # NOTE initialize HydroMT data catalog
    if app.config["data_libs"] is not None:
        app.data_catalog = DataCatalog(data_libs=app.config["data_libs"])

    # View
    app.view = {}
    app.view["projection"] = "mercator"
    app.view["topography"] = {}
    app.view["topography"]["visible"] = True
    app.view["topography"]["opacity"] = 0.5
    app.view["topography"]["quality"] = "medium"
    app.view["topography"]["colormap"] = "earth"
    app.view["topography"]["interp_method"] = "nearest"
    app.view["topography"]["interp_method"] = "linear"
    app.view["layer_style"] = "streets-v12"
    app.view["terrain"] = {}
    app.view["terrain"]["visible"] = False
    app.view["terrain"]["exaggeration"] = 1.5
    app.view["interp_method"] = "nearest"

    # Initialize toolboxes
    initialize_toolboxes()

    # Initialize models
    initialize_models()

    # Set active toolbox and model
    app.active_model = app.model[list(app.model)[0]]
    app.active_toolbox = app.toolbox[list(app.toolbox)[0]]

    # Read color maps
    rgb = read_colormap(os.path.join(app.config_path, "colormaps", "earth.txt"))
    app.color_map_earth = ListedColormap(rgb)

    # GUI variables
    app.gui.setvar("menu", "active_model_name", "")
    app.gui.setvar("menu", "active_toolbox_name", "")
    app.gui.setvar("menu", "active_topography_name", app.background_topography)
    app.gui.setvar("menu", "projection", "mercator")
    app.gui.setvar("menu", "show_topography", True)
    app.gui.setvar("menu", "show_terrain", False)
    app.gui.setvar("menu", "layer_style", app.view["layer_style"])

    # Now build up GUI config
    build_gui_config()


def initialize_toolboxes():
    # Initialize toolboxes
    app.toolbox = {}
    for tlb in app.config["toolbox"]:
        toolbox_name = tlb["name"]
        # And initialize this toolbox
        print("Adding toolbox : " + toolbox_name)
        module = importlib.import_module(
            "delftdashboard.toolboxes." + toolbox_name + "." + toolbox_name
        )
        app.toolbox[toolbox_name] = module.Toolbox(toolbox_name)
        app.toolbox[toolbox_name].module = module


def initialize_models():
    # Initialize models
    app.model = {}
    for mdl in app.config["model"]:
        model_name = mdl["name"]
        # And initialize the domain for this model
        print("Adding model   : " + model_name)
        module = importlib.import_module(
            "delftdashboard.models." + model_name + "." + model_name
        )
        app.model[model_name] = module.Model(model_name)
        if "exe_path" in mdl:
            app.model[model_name].domain.exe_path = mdl["exe_path"]
        # Loop through toolboxes to see which ones should be activated for which model
        app.model[model_name].toolbox = []
        for tlb in app.config["toolbox"]:
            okay = True
            if "for_model" in tlb:
                if model_name not in tlb["for_model"]:
                    okay = False
            if okay:
                app.model[model_name].toolbox.append(tlb["name"])
