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
from cht_sfincs import SFINCS

class Toolbox(GenericToolbox):
    def __init__(self, name):
        super().__init__()

        self.name = name
        self.long_name = "Flood Map"

    def initialize(self):

        # Set variables

        group = "flood_map"

        app.gui.setvar(group, "map_file_name", "")



    def set_layer_mode(self, mode):
        if mode == "active":
            # Make container layer visible
            app.map.layer[self.name].show()
            # Always show track layer
            app.map.layer[self.name].layer["flood_map_from_tiles"].show()
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
            "flood_map_from_tiles",
            type="raster_from_tiles",
            option="flood_map",
        )

    def load_map_output(self):
        # Load the map output
        file_name = app.gui.window.dialog_open_file("Open map output file", "*.nc")
        # Use full path
        if file_name[0]:
            # Read the map output
            app.gui.setvar("flood_map", "map_file_name", file_name[0])
            self.read_output()

    def read_output(self):
        # Read the map output
        file_name = app.gui.getvar("flood_map", "map_file_name")
        pth = os.path.dirname(file_name)
        sf = SFINCS(root=pth)
        da = sf.output.read_zsmax(fmt="xarray")

        # return
        # Read file

        # Create XR DataArray

        # Set data
        app.map.layer[self.name].layer["flood_map_from_tiles"].index_path = os.path.join(pth, "tiles", "indices")
        app.map.layer[self.name].layer["flood_map_from_tiles"].topobathy_path = os.path.join(pth, "tiles", "topobathy")
        app.map.layer[self.name].layer["flood_map_from_tiles"].set_data(da)

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
