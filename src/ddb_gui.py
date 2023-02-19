# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

import os
import importlib

from ddb import ddb
from guitares.gui import set_missing_element_values, read_gui_elements
from cht.bathymetry.bathymetry_database import bathymetry_database


def build_gui_config():
    # Read GUI elements

    # Toolboxes
    for toolbox_name in ddb.toolbox:
        # Read the GUI elements for this toolbox
        path = os.path.join(ddb.main_path, "toolboxes", toolbox_name, "config")
        file_name = toolbox_name + ".yml"
#        ddb.toolbox[toolbox_name].element = ddb.gui.read_gui_elements(path, file_name)
        ddb.toolbox[toolbox_name].element = read_gui_elements(path, file_name)
        variable_group = toolbox_name
        module = importlib.import_module("toolboxes." + toolbox_name + "." + toolbox_name)
        set_missing_element_values(ddb.toolbox[toolbox_name].element,
                                   variable_group,
                                   module,
                                   ddb.gui)

    # Models
    for model_name in ddb.model:
        # Add the GUI elements (tab panel) for this model
        path = os.path.join(ddb.main_path, "models", model_name, "config")
        file_name = model_name + ".yml"
        ddb.model[model_name].element = read_gui_elements(path, file_name)[0]

    # The Delft Dashboard GUI is built up programmatically
    ddb.gui.config["window"] = {}
    ddb.gui.config["window"]["title"] = ddb.config["title"]
    ddb.gui.config["window"]["width"] = ddb.config["width"]
    ddb.gui.config["window"]["height"] = ddb.config["height"]
    ddb.gui.config["window"]["icon"]  = ddb.config["window_icon"]
    ddb.gui.config["menu"] = []
    ddb.gui.config["toolbar"] = []
    ddb.gui.config["element"] = []

    # Add tab panels for models
    for model_name in ddb.model:
        ddb.gui.config["element"].append(ddb.model[model_name].element)

    # Now add MapBox element
    mpbox = {}
    mpbox["style"] = "mapbox"
    mpbox["id"] = "map"
    mpbox["position"] = {}
    mpbox["position"]["x"] = 20
    mpbox["position"]["y"] = 195
    mpbox["position"]["width"] = -20
    mpbox["position"]["height"] = -40
    mpbox["module"] = "ddb_map"
    ddb.gui.config["element"].append(mpbox)

    # Menu

    # File
    menu = {}
    menu["text"] = "File"
    menu["module"] = "ddb_menu"
    menu["menu"] = []
    menu["menu"].append({"text": "New", "method": "new", "separator": True})
    menu["menu"].append({"text": "Open", "method": "open"})
    menu["menu"].append({"text": "Save", "method": "save", "separator": True})
    menu["menu"].append({"text": "Exit", "method": "exit"})
    ddb.gui.config["menu"].append(menu)

    # Model
    menu = {}
    menu["text"] = "Model"
    menu["module"] = "ddb_model"
    menu["menu"] = []
    for model_name in ddb.model:
        menu["menu"].append({"text": ddb.model[model_name].long_name,
                             "method": "select_model",
                             "id": model_name,
                             "option": model_name,
                             "checkable": True})
    ddb.gui.config["menu"].append(menu)

    # Toolbox
    menu = {}
    menu["text"] = "Toolbox"
    menu["module"] = "ddb_toolbox"
    menu["menu"] = []
    # for toolbox_name in ddb.toolbox:
    #     menu["menu"].append({"text": ddb.toolbox[toolbox_name].long_name,
    #                          "method": "select_toolbox",
    #                          "id": toolbox_name,
    #                          "option": toolbox_name,
    #                          "checkable": True})
    ddb.gui.config["menu"].append(menu)


    # Topography
    source_names, sources = bathymetry_database.sources()
#    dataset_names, dataset_long_names, dataset_source_names = bathymetry_database.dataset_names()
    menu = {}
    menu["text"] = "Topography"
    menu["module"] = "menu_topography"
    menu["menu"] = []
    for source in sources:
        source_menu = {}
        source_menu["text"] = source.name
        source_menu["menu"] = []
        for dataset in source.dataset:
            source_menu["menu"].append({"id": "topography." + dataset.name, "text": dataset.name, "separator": False,  "checkable": True, "option": dataset.name, "method": "select_dataset"})
        menu["menu"].append(source_menu)
    ddb.gui.config["menu"].append(menu)

    # View
    menu = {}
    menu["text"] = "View"
    menu["module"] = "menu_view"
    menu["menu"] = []
    menu["menu"].append({"id": "view.mercator",    "text": "Mercator",   "method": "mercator",   "separator": False, "checkable": True})
    menu["menu"].append({"id": "view.globe",       "text": "Globe",      "method": "globe",      "separator": True,  "checkable": True})
    menu["menu"].append({"id": "view.topography",  "text": "Topography", "method": "topography", "separator": True,  "checkable": True})

    # layer_style_menu = {}
    # layer_style_menu["text"] = "Layer Style"
    # layer_style_menu["menu"] = []
    # layer_style_menu["menu"].append({"id": "view.layer_style.streets", "text": "Streets", "separator": False,  "checkable": True, "option": "streets-v12", "method": "layer_style"})
    # layer_style_menu["menu"].append({"id": "view.layer_style.satellite", "text": "Satellite", "separator": False,  "checkable": True, "option": "satellite-v9", "method": "layer_style"})
    # layer_style_menu["menu"].append({"id": "view.layer_style.satellite_streets", "text": "Satellite Streets", "separator": False,  "checkable": True, "option": "satellite-streets-v12", "method": "layer_style"})
    # layer_style_menu["menu"].append({"id": "view.layer_style.dark", "text": "Dark", "separator": False,  "checkable": True, "option": "dark-v11", "method": "layer_style"})
    # layer_style_menu["menu"].append({"id": "view.layer_style.light", "text": "Light", "separator": False,  "checkable": True, "option": "light-v11", "method": "layer_style"})
    # menu["menu"].append(layer_style_menu)

    menu["menu"].append({"id": "view.terrain",  "text": "3D Terrain", "method": "terrain", "separator": True,  "checkable": True})

    ddb.gui.config["menu"].append(menu)

    # Coordinate system
    menu = {}
    menu["text"] = "Coordinate System"
    menu["module"] = "ddb_coordinate_system"
    menu["menu"] = []
    menu["menu"].append({"text": "WGS 84", "method": "wgs84", "separator": False})
    menu["menu"].append({"text": "Select Other Geographic ...", "method": "other_geographic", "separator": True})
    menu["menu"].append({"text": "Select UTM Zone ...", "method": "utm_zone", "separator": False})
    menu["menu"].append({"text": "Select Other Projected ...", "method": "other_projected", "separator": False})
    ddb.gui.config["menu"].append(menu)


    # Help
    menu = {}
    menu["text"] = "Help"
    menu["module"] = "menu_help"
    menu["menu"] = []
    ddb.gui.config["menu"].append(menu)


#    ddb.gui.config["element"].pop(1)
#    ddb.gui.config["element"] = []
