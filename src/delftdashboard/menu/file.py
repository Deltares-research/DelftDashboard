# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""
import os
from delftdashboard.app import app
from delftdashboard.operations.initialize import initialize_toolboxes, initialize_models


def new(option):
    # Reset everything
    # Remove layers
    ok = app.gui.window.dialog_yes_no("This will clear all existing data! Continue?")
    if not ok:
        return
    for toolbox in app.toolbox.keys():
        if toolbox in app.map.layer:
            app.map.layer[toolbox].delete()

    if app.active_model.name in app.model.keys():
        app.map.layer["buildings"].delete()
        app.map.layer["roads"].delete()
        app.map.layer["aggregation"].delete()                

    # Initialize toolboxes
    initialize_toolboxes()

    # Initialize SFINCS models
    if app.active_model.name != 'fiat':
        initialize_models()

    # Add layers
    for toolbox in app.toolbox:
        app.toolbox[toolbox].add_layers()
        
    if app.active_model.name in app.model.keys():
        app.active_model.add_layers()

    app.gui.window.dialog_info(
    "Please select a new working directory",
    "Select working directory",
    )
    select_working_directory(option)       
    ## FREDERIQUE: commented out below because it changes the active model
    # app.active_model = app.model[list(app.model)[0]]
    # app.active_toolbox = app.toolbox[list(app.toolbox)[0]]


def open(option):
    app.active_model.open()


def save(option):
    app.active_model.save()


def select_working_directory(option):
    path = app.gui.window.dialog_select_path(
        "Select working directory", path=os.getcwd()
    )
    if path:
        os.chdir(path)
        app.gui.config["working_directory"] = path

        try:
            app.model[app.active_model.name].select_working_directory()
        except:
            print("No method select_working_directory for model: ", app.active_model.name)
            pass

def exit(option):
    app.gui.quit()
