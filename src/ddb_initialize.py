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
from colormap import read_colormap

from ddb import ddb
from ddb_gui import build_gui_config

def initialize():

    ddb.main_path = os.path.dirname(os.path.abspath(__file__))
    ddb.server_path = os.path.join(ddb.main_path, "server")

    # Set default config
    ddb.config                  = {}
    ddb.config["gui_framework"] = "pyqt5"
    ddb.config["server_port"]   = 3000
#    ddb.config["stylesheet"]    = "Combinear.qss"
    ddb.config["stylesheet"]    = ""
    ddb.config["title"]         = "Delft Dashboard"
    ddb.config["width"]         = 800
    ddb.config["height"]        = 600
    ddb.config["model"]         = []
    ddb.config["toolbox"]       = []
    ddb.config["window_icon"]   = os.path.join(ddb.main_path, "settings", "images", "deltares_icon.png")
#    ddb.config["splash_file"]   = os.path.join(ddb.main_path, "settings", "images", "DelftDashBoard.jpg")
    ddb.config["splash_file"]   = None

    # Read ini file and override stuff in default config dict
    inifile = open("delftdashboard.ini", "r")
    config = yaml.load(inifile, Loader=yaml.FullLoader)
    for key in config:
        ddb.config[key] = config[key]
    inifile.close()

    # Initialize GUI object
    ddb.gui = GUI(ddb,
                  framework=ddb.config["gui_framework"],
                  config_path=ddb.main_path,
                  server_path=ddb.server_path,
                  server_port=ddb.config["server_port"],
                  stylesheet=ddb.config["stylesheet"],
                  splash_file=ddb.config["splash_file"],
                  copy_mapbox_server_folder=True)

    ddb.gui.show_splash()


    # Define some other variables
    ddb.crs = CRS(4326)
    ddb.auto_update_topography = True
    ddb.background_topography  = "gebco22"
    ddb.bathymetry_database_path = "c:\\work\\delftdashboard\\data\\bathymetry"
    bathymetry_database.initialize(ddb.bathymetry_database_path)


    # View
    ddb.view = {}
    ddb.view["projection"] = "mercator"
    ddb.view["topography"] = {}
    ddb.view["topography"]["visible"]  = True
    ddb.view["topography"]["opacity"]  = 0.5
    ddb.view["topography"]["quality"]  = "medium"
    ddb.view["topography"]["colormap"] = "earth"
    ddb.view["topography"]["interp_method"] = "nearest"
    ddb.view["topography"]["interp_method"] = "linear"
    ddb.view["layer_style"] = "streets"
    ddb.view["terrain"] = {}
    ddb.view["terrain"]["visible"] = False
    ddb.view["terrain"]["exaggeration"] = 1.5
    ddb.view["interp_method"] = "nearest"

    # Initialize toolboxes
    ddb.toolbox = {}
    for tlb in ddb.config["toolbox"]:
        toolbox_name = tlb["name"]
        # And initialize this toolbox
        module = importlib.import_module("toolboxes." + toolbox_name + "." + toolbox_name)
        ddb.toolbox[toolbox_name] = module.Toolbox(toolbox_name)

    # Initialize models
    ddb.model = {}
    for mdl in ddb.config["model"]:
        model_name = mdl["name"]
        # And initialize the domain for this model
        module = importlib.import_module("models." + model_name + "." + "ddb_" + model_name)
        ddb.model[model_name] = module.Model(model_name)
        if "exe_path" in mdl:
            ddb.model[model_name].domain.exe_path = mdl["exe_path"]
        # Loop through toolboxes to see which ones should be activated for which model
        ddb.model[model_name].toolbox = []
        for tlb in ddb.config["toolbox"]:
            okay = True
            if "for_model" in tlb:
                if model_name not in tlb["for_model"]:
                    okay = False
            if okay:
                ddb.model[model_name].toolbox.append(tlb["name"])

    # Set active toolbox and model
    ddb.active_model   = ddb.model[list(ddb.model)[0]]
    ddb.active_toolbox = ddb.toolbox[list(ddb.toolbox)[0]]


    # Read bathymetry database

    # Read tide database

    # Read color maps
    rgb = read_colormap('c:/work/checkouts/svn/OET/matlab/applications/DelftDashBoard/settings/colormaps/earth.txt')
    ddb.color_map_earth = ListedColormap(rgb)

    # GUI variables
    ddb.gui.setvar("menu", "active_model_name", "")
    ddb.gui.setvar("menu", "active_toolbox_name", "")
    ddb.gui.setvar("menu", "active_topography_name", ddb.background_topography)


    # Now build up GUI config
    build_gui_config()
