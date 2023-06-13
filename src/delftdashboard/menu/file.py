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
    for model in app.model.keys():
        if model in app.map.layer:
            app.map.layer[model].delete()

    # Initialize toolboxes
    initialize_toolboxes()

    # Initialize models
    initialize_models()

    # Add layers
    for toolbox in app.toolbox:
        app.toolbox[toolbox].add_layers()
    for model in app.model:
        app.model[model].add_layers()
    app.active_model   = app.model[list(app.model)[0]]
    app.active_toolbox = app.toolbox[list(app.toolbox)[0]]

def open(option):
    app.active_model.open()

def save(option):
    app.active_model.save()

def select_working_directory(option):
    path = app.gui.window.dialog_select_path("Select working directory", path=os.getcwd())
    if path:
        os.chdir(path)

def exit(option):
    app.gui.quit()
