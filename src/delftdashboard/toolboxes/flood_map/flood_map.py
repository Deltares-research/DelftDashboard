# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
import os
import datetime
# import math
# import numpy as np
# import geopandas as gpd
# import shapely
# import json
# import os
from delftdashboard.app import app
from delftdashboard.operations.toolbox import GenericToolbox

from cht_cyclones import CycloneTrackDatabase, TropicalCyclone

class Toolbox(GenericToolbox):
    def __init__(self, name):
        super().__init__()

        self.name = name
        self.long_name = "Flood Map"

    def initialize(self):

        # Set variables

        group = "flood_map"

        app.gui.setvar(group, "name", "")
        app.gui.setvar(group, "track_loaded", False)


        app.gui.setvar(group, "ensemble_start_time", None)
        app.gui.setvar(group, "ensemble_start_time_index", 0)
        app.gui.setvar(group, "ensemble_number_of_realizations", 100)
        app.gui.setvar(group, "ensemble_duration", 72)
        app.gui.setvar(group, "ensemble_cone_buffer", 300000.0)
        app.gui.setvar(group, "ensemble_cone_only_forecast", True)
        app.gui.setvar(group, "ensemble_start_time", None)

        app.gui.setvar(group, "track_time_strings", [])

        app.gui.setvar(group, "include_rainfall", False)
        app.gui.setvar(group, "wind_profile_options", ["holland2010"])
        app.gui.setvar(group, "wind_profile_option_strings", ["Holland (2010)"])
        app.gui.setvar(group, "vmax_pc_options", ["holland2008"])
        app.gui.setvar(group, "vmax_pc_option_strings", ["Holland (2008)"])
        app.gui.setvar(group, "rmax_options", ["nederhoff2019"])
        app.gui.setvar(group, "rmax_option_strings", ["Nederhoff et al. (2019)"])
        app.gui.setvar(group, "rainfall_options", ["ipet"])
        app.gui.setvar(group, "rainfall_option_strings", ["IPET"])


    def set_layer_mode(self, mode):
        if mode == "active":
            # Make container layer visible
            app.map.layer[self.name].show()
            # Always show track layer
            app.map.layer[self.name].layer["flood_map"].show()
        elif mode == "inactive":
            # Make all layers invisible
            app.map.layer[self.name].hide()
        if mode == "invisible":
            # Make all layers invisible
            app.map.layer[self.name].hide()

    def add_layers(self):
        # Add Mapbox layers
        layer = app.map.add_layer(self.name)
        layer.add_layer(
            "flood_map",
            type="image"
        )

    def load_map_output(self):
        # Load the map output
        file_name = app.gui.window.dialog_open_file("Open map output file", "*.nc")
        if file_name[0]:
            # Read the map output
            self.read_output(file_name[0])

    def read_output(self, file_name):
        # Read the map output
        pass        

    def load_his_output(self):
        # Load the map output
        file_name = app.gui.window.dialog_open_file("Open map output file", "*.nc")
        if file_name[0]:
            self.tc.read_track(file_name[0])
            self.tc.name = os.path.basename(file_name[0]).split(".")[0]
            app.gui.setvar("tropical_cyclone", "ensemble_start_time", None)
            app.gui.setvar("tropical_cyclone", "ensemble_start_time_index", 0)
            app.gui.setvar("tropical_cyclone", "track_loaded", True)
            self.plot_track()
