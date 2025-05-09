# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

import os
# import importlib

from delftdashboard.app import app

def build_gui_config():
    # Read GUI elements

    # Toolboxes
    for toolbox_name in app.toolbox:
        # Read the GUI elements for this toolbox
        path = os.path.join(app.main_path, "toolboxes", toolbox_name, "config")
        file_name = toolbox_name + ".yml"
        app.toolbox[toolbox_name].element = app.gui.read_gui_elements(path, file_name)
        for element in app.toolbox[toolbox_name].element:
            # Set the callback module. This is the module that contains the callback functions, and does not have to be the same as the toolbox module.
            # This is useful as some toolboxes do not have tabs for which modules are defined, and the main module can become very busy with all the callbacks and the toolbox object.
            if app.toolbox[toolbox_name].callback_module_name is None:
                element["module"]         = "delftdashboard.toolboxes." + toolbox_name + "." + toolbox_name
            else:
                element["module"]         = "delftdashboard.toolboxes." + toolbox_name + "." + app.toolbox[toolbox_name].callback_module_name
            element["variable_group"] = toolbox_name

    # Models
    for model_name in app.model:
        # Add the GUI elements (tab panel) for this model
        path = os.path.join(app.main_path, "models", model_name, "config")
        file_name = model_name + ".yml"
        app.model[model_name].element = app.gui.read_gui_elements(path, file_name)[0]
        app.model[model_name].element["variable_group"] = model_name
        app.model[model_name].element["module"] = "delftdashboard.models." + model_name + "." + model_name

    # The Delft Dashboard GUI is built up programmatically
    app.gui.config["window"] = {}
    app.gui.config["window"]["title"]  = app.config["title"]
    app.gui.config["window"]["width"]  = app.config["width"]
    app.gui.config["window"]["height"] = app.config["height"]
    app.gui.config["window"]["icon"]   = app.config["window_icon"]
    app.gui.config["menu"] = []
    app.gui.config["toolbar"] = []
    app.gui.config["element"] = []
    app.gui.config["statusbar"] = {}
    app.gui.config["statusbar"]["field"] = []
    app.gui.config["statusbar"]["field"].append({"id": "crs_name", "text": "WGS 84 (geographic) - EPSG:4326", "width": 12})
    app.gui.config["statusbar"]["field"].append({"id": "lon", "text": "Lon :", "width": 4})
    app.gui.config["statusbar"]["field"].append({"id": "lat", "text": "Lat :", "width": 4})
    app.gui.config["statusbar"]["field"].append({"id": "x", "text": "X :", "width": 4})
    app.gui.config["statusbar"]["field"].append({"id": "y", "text": "Y :", "width": 4})
    app.gui.config["statusbar"]["field"].append({"id": "distance", "text": "", "width": 4})

    # # Layer tab
    # # Read elements
    # path = os.path.join(app.main_path, "layers", "config")
    # file_name = "layers.yml"
    # layer_tab_element = app.gui.read_gui_elements(path, file_name)

    # Add tab panels for models
    for model_name in app.model:
        # First insert tabs for Layers and Toolbox
        tab_panel = app.model[model_name].element
        tab_panel["tab"].insert(0, {'string': 'Toolbox', 'element': [], "module": ""})
        app.gui.config["element"].append(app.model[model_name].element)

    # Now add map element
    mp = {}
    mp["style"] = "map"
    mp["id"] = "map"
    mp["position"] = {}
    mp["position"]["x"] = 20
    mp["position"]["y"] = 180
    mp["position"]["width"] = -20
    mp["position"]["height"] = -40
    mp["module"] = "delftdashboard.operations.map"
    app.gui.config["element"].append(mp)

    # Menu

    # File
    menu = {}
    menu["text"] = "File"
    menu["module"] = "delftdashboard.menu.file"
    menu["menu"] = []
    menu["menu"].append({"text": "New", "method": "new", "separator": True})
    menu["menu"].append({"text": "Open", "method": "open"})
    menu["menu"].append({"text": "Save", "method": "save", "separator": True})
    menu["menu"].append({"text": "Select Working Directory", "method": "select_working_directory", "separator": True})
    menu["menu"].append({"text": "Exit", "method": "exit"})
    app.gui.config["menu"].append(menu)

    # Model
    menu = {}
    menu["text"] = "Model"
    menu["module"] = "delftdashboard.menu.model"
    menu["menu"] = []
    for model_name in app.model:
        dependency = [{"action": "check",
                       "checkfor": "all",
                       "check": [{"variable": "active_model_name",
                                  "operator": "eq",
                                  "value": model_name}]
                     }]
        menu["menu"].append({"text": app.model[model_name].long_name,
                             "variable_group": "menu",
                             "method": "select",
                             "id": model_name,
                             "option": model_name,
                             "checkable": True,
                             "dependency": dependency})
    app.gui.config["menu"].append(menu)

    # Toolbox
    menu = {}
    menu["text"] = "Toolbox"
    menu["module"] = "delftdashboard.menu.toolbox"
    menu["menu"] = []
    menu["menu"].append({"text": "toolbox"})
    app.gui.config["menu"].append(menu)

    # Topography
    source_names, sources = app.bathymetry_database.sources()
    menu = {}
    menu["text"] = "Topography"
    menu["id"] = "topography"
    menu["module"] = "delftdashboard.menu.topography"
    menu["menu"] = []
    for source in sources:
        source_menu = {}
        source_menu["text"] = source.name
        source_menu["id"] = "topography." + source.name
        source_menu["menu"] = []
        for dataset in source.dataset:
            dependency = [{"action": "check",
                           "checkfor": "all",
                           "check": [{"variable": "topography_dataset",
                                      "operator": "eq",
                                      "value": dataset.name}]
                           }]
                
            source_menu["menu"].append({"id": "topography." + dataset.name,
                                        "variable_group": "view_settings",
                                        "text": dataset.long_name,
                                        "separator": False,
                                        "checkable": True,
                                        "option": dataset.name,
                                        "method": "select_dataset",
                                        "dependency": dependency})
        menu["menu"].append(source_menu)
    app.gui.config["menu"].append(menu)

    # dependency = [{"action": "check", "checkfor": "all", "check": [{"variable": "projection", "operator": "eq", "value": "mercator"}]}]

    # View
    menu = {}
    menu["text"] = "View"
    menu["module"] = "delftdashboard.menu.view"
    menu["menu"] = []
    menu["menu"].append({"variable_group": "view_settings", "id": "view.topography",  "text": "Topography", "method": "topography", "separator": True,  "checkable": True, "dependency": [{"action": "check", "checkfor": "all", "check": [{"variable": "topography_visible", "operator": "eq", "value": True}]}]})

    # View settings
    menu["menu"].append({"variable_group": "menu", "id": "view.settings",  "text": "Settings ...", "method": "edit_settings", "separator": True,  "checkable": False})

    # Add menu items for models
    # Loop over all models in model dict
    for model in app.model.values():
        model_view_menu = model.get_view_menu()
        # Check it's not an empty dictionary
        if model_view_menu:
            menu["menu"].append(model_view_menu)

    app.gui.config["menu"].append(menu)

    # Coordinate system
    menu = {}
    menu["text"] = "Coordinate System"
    menu["module"] = "delftdashboard.menu.coordinate_system"
    menu["menu"] = []
    menu["menu"].append({"text": "WGS 84", "method": "wgs84", "separator": False})
    menu["menu"].append({"text": "Select Other Geographic ...", "method": "other_geographic", "separator": True})
    menu["menu"].append({"text": "Select UTM Zone ...", "method": "utm_zone", "separator": False})
    menu["menu"].append({"text": "Select Other Projected ...", "method": "other_projected", "separator": False})
    app.gui.config["menu"].append(menu)

    # Help
    menu = {}
    menu["text"] = "Help"
    menu["module"] = "delftdashboard.menu.help"
    menu["menu"] = []
    app.gui.config["menu"].append(menu)
