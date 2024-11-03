# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""
import os
from delftdashboard.app import app

def new(option):
    # Reset everything

    ok = app.gui.window.dialog_yes_no("This will clear all existing data! Continue?")
    if not ok:
        return

    # Initialize toolboxes
    for toolbox in app.toolbox.values():
        toolbox.initialize()
        toolbox.clear_layers()

    # Initialize models    
    for model in app.model.values():
        model.initialize()
        model.clear_layers()

    app.active_model   = app.model[list(app.model)[0]]
    app.active_toolbox = app.toolbox[list(app.toolbox)[0]]
    app.active_toolbox.select()

def open(option):
    app.active_model.open()

def save(option):
    app.active_model.save()

def select_working_directory(option):
    path = app.gui.window.dialog_select_path("Select working directory ...", path=os.getcwd())
    if path:
        os.chdir(path)
        # Set path for all models to new working directory
        for model in app.model:
            try:
                app.model[model].domain.path = path   
            except Exception as e:
                print("Could not set path for model : ", model)
                pass


def exit(option):
    app.gui.quit()
