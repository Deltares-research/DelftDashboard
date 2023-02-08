# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

import os
import yaml
from matplotlib.colors import ListedColormap
import importlib

from guitools.gui import GUI
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
                  stylesheet=ddb.config["stylesheet"])

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

    # Define some other variables
    ddb.auto_update_topography = True
    ddb.background_topography  = "gebco22"
    ddb.bathymetry_database_path = "c:\\work\\delftdashboard\\data\\bathymetry"
    bathymetry_database.initialize(ddb.bathymetry_database_path)

    # Read bathymetry database

    # Read tide database

    # Read color maps
    rgb = read_colormap('c:/work/checkouts/svn/OET/matlab/applications/DelftDashBoard/settings/colormaps/earth.txt')
    ddb.color_map_earth = ListedColormap(rgb)


    # Now build up GUI config
    build_gui_config()
