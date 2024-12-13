# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
import os
# import math
# import numpy as np
# import geopandas as gpd
# import shapely
# import json
# import os
from delftdashboard.app import app
from delftdashboard.operations.toolbox import GenericToolbox

from cht_cyclones import CycloneTrackDatabase

class Toolbox(GenericToolbox):
    def __init__(self, name):
        super().__init__()

        self.name = name
        self.long_name = "Tropical Cyclone"

    def initialize(self):

        # Set variables
        self.tc = None
        self.track_dataset = None

        # Set GUI variables
        group = "tropical_cyclone"
        app.gui.setvar(group, "name", "")
        app.gui.setvar(group, "ensemble_start_time", None)
        app.gui.setvar(group, "ensemble_start_time_index", 0)
        app.gui.setvar(group, "ensemble_number_of_realizations", 100)
        app.gui.setvar(group, "ensemble_duration", 72)
        app.gui.setvar(group, "ensemble_cone_buffer", 300000.0)
        app.gui.setvar(group, "ensemble_cone_only_forecast", True)
        app.gui.setvar(group, "track_time_strings", [])

        # Read track database
        s3_bucket = "deltares-ddb"
        s3_key = f"data/tropical_cyclones"
        path = os.path.join(app.config["data_path"], "tropical_cyclones")
        self.cyclone_track_database = CycloneTrackDatabase(path,
                                                           s3_bucket=s3_bucket,
                                                           s3_key=s3_key)
        self.cyclone_track_database.check_online_database()
        short_names, long_names = self.cyclone_track_database.dataset_names()
        app.gui.setvar("tropical_cyclone", "track_dataset_long_names", long_names)
        app.gui.setvar("tropical_cyclone", "track_dataset_names", short_names)
        app.gui.setvar("tropical_cyclone", "selected_track_dataset", short_names[0])

    def set_layer_mode(self, mode):
        if mode == "active":
            # Make container layer visible
            app.map.layer[self.name].show()
            # Always show track layer
            app.map.layer[self.name].layer["cyclone_track"].show()
            # But hide ensemble layers
            app.map.layer[self.name].layer["cyclone_track_ensemble"].hide()
            app.map.layer[self.name].layer["cyclone_track_ensemble_cone"].hide()
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
            "cyclone_track_ensemble",
            type="line",
            line_color="white",
            line_width=1,
            line_opacity=0.5
        )
        layer.add_layer(
            "cyclone_track_ensemble_cone",
            type="line",
            line_color="white",
            line_width=2,
            line_opacity=1.0
        )
        layer.add_layer(
            "cyclone_track",
            type="cyclone_track",
            # file_name="tracks.geojson",
            line_color="dodgerblue",
            line_width=2,
            line_color_selected="red",
            line_width_selected=3,
            hover_param="description",
        )

    def track_added(self):
        app.gui.setvar("tropical_cyclone", "ensemble_start_time", None)
        app.gui.setvar("tropical_cyclone", "ensemble_start_time_index", 0)
        self.plot_track()

    def plot_track(self):
        app.map.layer[self.name].layer["cyclone_track"].set_data(self.tc.track.gdf)

    def build_spiderweb(self):
        # Write the track
        self.tc.write_track(self.tc.name + ".cyc")
        # Build and save the spw file
        spw_file = self.tc.name + ".spw"
        p = app.gui.window.dialog_progress("               Generating wind fields ...                ", len(self.tc.track.gdf))
        self.tc.compute_wind_field(filename=spw_file, progress_bar=p, format="ascii", error_stats=False)
        p.close()

        # Get the active model
        model = app.active_model
        if model.name == "sfincs_cht":
            # Add the spw file to the model
            model.domain.input.variables.spwfile = spw_file
            # And update the GUI variable
            app.gui.setvar("sfincs_cht", "spwfile", spw_file)
        elif model.name == "hurrywave":
            # Add the spw file to the model
            model.domain.input.variables.spwfile = spw_file
            # And update the GUI variable
            app.gui.setvar("hurrywave", "spwfile", spw_file)    
