# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
import math
import numpy as np
import geopandas as gpd
import shapely
import json
import os

from delftdashboard.operations.toolbox import GenericToolbox
from delftdashboard.app import app
from cht.tropical_cyclone.cyclone_track_database import CycloneTrackDatabase

# Callbacks

def select(*args):
    # De-activate existing layers
    app.update_map()
    # Tab selected
    app.toolbox["tropical_cyclone"].set_layer_mode("active")


def select_track(*args):
    app.toolbox["tropical_cyclone"].select_track()


def build_spiderweb(*args):
    app.toolbox["tropical_cyclone"].build_spiderweb()



class Toolbox(GenericToolbox):
    def __init__(self, name):
        super().__init__()

        self.name = name
        self.long_name = "Tropical Cyclone"

        # Set variables
        self.track_gdf = gpd.GeoDataFrame()
        self.track_database = None

        # Set GUI variables
        group = "tropical_cyclone"
        app.gui.setvar(group, "name", "")

    def set_layer_mode(self, mode):
        if mode == "active":
            app.map.layer[self.name].layer["cyclone_track"].set_mode("active")
        elif mode == "inactive":
            # Make all layers invisible
            app.map.layer[self.name].set_mode("invisible")
        if mode == "invisible":
            # Make all layers invisible
            app.map.layer[self.name].set_mode("invisible")

    def add_layers(self):
        # Add Mapbox layers
        layer = app.map.add_layer(self.name)
        layer.add_layer(
            "cyclone_track",
            type="circle",
            file_name="tracks.geojson",
            line_color="dodgerblue",
            line_width=2,
            line_color_selected="red",
            line_width_selected=3,
            hover_param="description",
        )

    def select_track(self):
        if self.track_database is None:
            # Read database
            self.track_database = CycloneTrackDatabase(
                "ibtracs",
                file_name=r"d:\old_d\delftdashboard\data\toolboxes\TropicalCyclone\IBTrACS.ALL.v04r00.nc",
            )

        # Open track selector
        tc, okay = self.track_database.track_selector(
            app, lon=-80.0, lat=30.0, distance=300.0, year_min=2000, year_max=2023
        )

        if okay:
            self.tc = tc
            self.plot_track()

    def plot_track(self):
        layer = app.map.layer[self.name].layer["cyclone_track"]
        layer.set_data(self.tc.track)
        layer.set_mode("active")

    def build_spiderweb(self):
        self.tc.spiderweb_radius = 500.0
        self.tc.nr_radial_bins = 125
        self.tc.wind_conversion_factor = 0.9
        # Save the track file
        self.tc.write_track(self.tc.name + ".cyc", "ddb_cyc")
        # Build and save the spw file
        spw_file = self.tc.name + ".spw"
        p = app.gui.window.dialog_progress("               Generating wind fields ...                ", len(self.tc.track))
        self.tc.to_spiderweb(spw_file, progress_bar=p)
        if app.active_model.name== "hurrywave":
            app.active_model.domain.input.variables.spwfile = spw_file
            app.active_model.domain.input.write()
            app.gui.setvar("hurrywave", "wind_type", "spiderweb")
            app.gui.setvar("hurrywave", "spwfile", spw_file)
        elif app.active_model.name== "sfincs":
            app.active_model.domain.input.variables.spwfile = spw_file

    # def update_progress(self, it):
    #     self.progress_dialog.set_value(it + 1)
    #     pass        

