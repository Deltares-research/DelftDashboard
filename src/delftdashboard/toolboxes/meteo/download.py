# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
from delftdashboard.app import app
from delftdashboard.operations import map

# Callbacks
def select(*args):
    # De-activate() existing layers
    map.update()
    # Tab selected
    app.toolbox["meteo"].set_layer_mode("active")

def select_dataset(*args):
    pass

def edit_time(*args):
    pass

def download(*args):
    dataset_name = app.gui.getvar("meteo", "selected_dataset")
    tstart = app.gui.getvar("meteo", "tstart")
    tend = app.gui.getvar("meteo", "tstop")
    dataset = app.meteo_database.dataset[dataset_name]
    # Add waitbox
    wb = app.gui.window.dialog_wait("Downloading meteo data ...")
    dataset.download([tstart, tend])
    wb.close()
 