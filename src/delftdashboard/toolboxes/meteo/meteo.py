# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
import datetime
from delftdashboard.app import app
from delftdashboard.operations.toolbox import GenericToolbox

class Toolbox(GenericToolbox):
    def __init__(self, name):
        super().__init__()

        self.name = name
        self.long_name = "Meteo"

    def initialize(self):

        # Set GUI variables

        sources = app.meteo_database.list_sources()
        datasets = app.meteo_database.list_dataset_names()

        group = "meteo"

        app.gui.setvar(group, "dataset_names", datasets)
        app.gui.setvar(group, "dataset_long_names", datasets)
        if len(datasets) > 0:
            app.gui.setvar(group, "selected_dataset", datasets[0])
        else:   
            app.gui.setvar(group, "selected_dataset", "")

        app.gui.setvar(group, "source_names", sources)
        app.gui.setvar(group, "source_long_names", sources)
        if len(sources) > 0:
            app.gui.setvar(group, "selected_source", sources[0])
        else:            
            app.gui.setvar(group, "selected_source", "")

        app.gui.setvar(group, "lon_min", 0.0)
        app.gui.setvar(group, "lon_max", 0.0)
        app.gui.setvar(group, "lat_min", 0.0)
        app.gui.setvar(group, "lat_max", 0.0)

        app.gui.setvar(group, "edit_bbox", False)

        # Set tstart and tstop
        tstart = datetime.datetime(2020, 1, 1, 0, 0, 0)
        tstop = datetime.datetime(2020, 1, 2, 0, 0, 0)
        app.gui.setvar(group, "tstart", tstart)
        app.gui.setvar(group, "tstop", tstop)

    def set_layer_mode(self, mode):
        pass

    def add_layers(self):
        # # Add Mapbox layers
        # layer = app.map.add_layer(self.name)
        # layer.add_layer("flood_map",
        #                 type="image")
        pass
