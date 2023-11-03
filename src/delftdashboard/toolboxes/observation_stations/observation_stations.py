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
from pyproj import CRS

from delftdashboard.operations.toolbox import GenericToolbox
from delftdashboard.app import app
from delftdashboard.operations import map

import cht_observations.observation_stations as obs

class Toolbox(GenericToolbox):
    def __init__(self, name):
        super().__init__()

        self.name = name
        self.long_name = "Observation Stations"

        # Set variables
        self.gdf = gpd.GeoDataFrame()

        # add sources
        self.sources = {"ndbc": "National Data Buoy Center (NDBC)",
                   "noaa_coops": "NOAA Tides and Currents (CO-OPS)"}

        # Set GUI variables
        group = "observation_stations"
        app.gui.setvar(group, "source_names", list(self.sources.values()))
        app.gui.setvar(group, "active_source_index", 0)

        stnames, self.gdf = get_station_names(list(self.sources.keys())[0])

        app.gui.setvar(group, "station_names", stnames)
        app.gui.setvar(group, "active_station_index", 0)
        app.gui.setvar(group, "naming_option", "name")

        # Specify how to add to the model
        options = [ "Observation Point", "Water level boundary"]
        app.gui.setvar(group, "model_options", options)
        app.gui.setvar(group, "model_option_index", 0)

    def select_tab(self):
        map.update()
        app.map.layer["observation_stations"].layer["stations"].activate()
        app.map.layer["observation_stations"].layer["stations"].show()
        opt = app.gui.getvar("observation_stations", "naming_option")
        app.map.layer["observation_stations"].layer["stations"].hover_property = opt
        index = app.gui.getvar("observation_stations", "active_station_index")
        app.map.layer["observation_stations"].layer["stations"].set_data(self.gdf, index)
        self.update()

    def select_source(self, index):
        group = "observation_stations"
        stnames, self.gdf = get_station_names(list(self.sources.keys())[index])
    
        app.gui.setvar(group, "station_names", stnames)
        app.gui.setvar(group, "active_station_index", 0)
        app.map.layer["observation_stations"].layer["stations"].set_data(self.gdf, 0)
        self.update()

    def set_layer_mode(self, mode):
        if mode == "inactive":
            # Make all layers invisible
            app.map.layer["observation_stations"].deactivate()
        if mode == "invisible":
            # Make all layers invisible
            app.map.layer["observation_stations"].hide()

    def add_layers(self):
        # Add Mapbox layers
        layer = app.map.add_layer("observation_stations")
        layer.add_layer("stations",
                         type="circle_selector",
                         line_color="white",
                         line_color_selected="white",
                         select=self.select_station_from_map
                        )        

    def add_stations_to_model(self):
        index = app.gui.getvar("observation_stations", "active_station_index")
        gdf = self.gdf.iloc[[index]]
        app.active_model.add_stations(gdf, 
                                      naming_option=app.gui.getvar("observation_stations", "naming_option"),
                                      model_option=app.gui.getvar("observation_stations", "model_option_index"))

    def add_all_stations_to_model(self):
        gdf = self.gdf

        # get model extent
        try:
            gdf = app.active_model.domain.region
        except:
            print("Warning: No model extent found")
            return

        app.active_model.add_stations(gdf, 
                                      naming_option=app.gui.getvar("observation_stations", "naming_option"),
                                      model_option=app.gui.getvar("observation_stations", "model_option_index"))
    def select_naming_option(self):
        self.update()
        opt = app.gui.getvar("observation_stations", "naming_option")
        index = app.gui.getvar("observation_stations", "active_station_index")
        app.map.layer["observation_stations"].layer["stations"].hover_property = opt
        app.map.layer["observation_stations"].layer["stations"].set_data(self.gdf,
                                                                         index)


    def select_station_from_map(self, *args):
        index = args[0]["properties"]["index"]
        app.gui.setvar("observation_stations", "active_station_index", index)
        app.gui.window.update()

    def select_station_from_list(self):
        index = app.gui.getvar("observation_stations", "active_station_index")
        app.map.layer["observation_stations"].layer["stations"].select_by_index(index)

    def update(self):
        stnames = []
        opt = app.gui.getvar("observation_stations", "naming_option")
        for index, row in self.gdf.iterrows():
            stnames.append(row[opt])
        app.gui.setvar("observation_stations", "station_names", stnames)

# 
def select(*args):
    app.toolbox["observation_stations"].select_tab()

def select_source(*args):
    index= app.gui.getvar("observation_stations", "active_source_index")
    app.toolbox["observation_stations"].select_source(index=index)

def select_station(*args):
    app.toolbox["observation_stations"].select_station_from_list()

def select_naming_option(*args):
    app.toolbox["observation_stations"].select_naming_option()

def add_stations_to_model(*args):
    app.toolbox["observation_stations"].add_stations_to_model()

##
def get_station_names(source):

    obs_data = obs.source(source)
    obs_data.get_active_stations()
    gdf = obs_data.gdf()

    stnames = []
    for station in obs_data.active_stations:
        stnames.append(station["name"])

    return stnames, gdf