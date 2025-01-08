# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

import os
import geopandas as gpd
import pandas as pd
import datetime
import matplotlib.pyplot as plt

from delftdashboard.operations.toolbox import GenericToolbox
from delftdashboard.app import app
from delftdashboard.operations import map

from cht_tide import TideStationsDatabase

class Toolbox(GenericToolbox):
    def __init__(self, name):
        super().__init__()

        self.name = name
        self.long_name = "Tide Stations"

    def initialize(self):

        # Set variables
        self.gdf = gpd.GeoDataFrame()
        
        # Read the database
        if "tide_stations_database_path" not in app.config:
            app.config["tide_stations_database_path"] = os.path.join(app.config["data_path"], "tide_stations")
        s3_bucket = "deltares-ddb"
        s3_key = f"data/tide_stations"
        app.tide_stations_database = TideStationsDatabase(path=app.config["tide_stations_database_path"],
                                                          s3_bucket=s3_bucket,
                                                          s3_key=s3_key)
        # if app.config["auto_update_tide_stations"]:
        #     app.tide_stations_database.check_online_database()
        short_names, long_names = app.tide_stations_database.dataset_names()
        app.gui.setvar("tide_stations", "dataset_long_names", long_names)
        app.gui.setvar("tide_stations", "dataset_names", short_names)
        app.gui.setvar("tide_stations", "dataset_name", short_names[0])
        app.gui.setvar("tide_stations", "active_station_index", 0)
        app.gui.setvar("tide_stations", "naming_option", "name")
        app.gui.setvar("tide_stations", "station_names", [])
        app.gui.setvar("tide_stations", "main_components", False)
        # get today's date (rounded down to 00h00)
        tnow = datetime.datetime.now()
        tstart = datetime.datetime(tnow.year, tnow.month, tnow.day)
        tend   = tstart + datetime.timedelta(days=30)
        app.gui.setvar("tide_stations", "tstart", tstart)
        app.gui.setvar("tide_stations", "tend", tend)
        app.gui.setvar("tide_stations", "dt", 600.0)
        app.gui.setvar("tide_stations", "offset", 0.0)
        app.gui.setvar("tide_stations", "format", "tek")
        # app.gui.setvar("tide_stations", "format_text", ["*.tek","*.csv","*.nc"])
        # app.gui.setvar("tide_stations", "format_value", ["tek","csv","nc"])
        app.gui.setvar("tide_stations", "format_text", ["*.tek","*.csv"])
        app.gui.setvar("tide_stations", "format_value", ["tek","csv"])
        app.gui.setvar("tide_stations", "format", "tek")
        app.gui.setvar("tide_stations", "constituent_table", pd.DataFrame())
        app.toolbox["tide_stations"].polygon = None

    def select_tab(self):
        map.update()
        app.map.layer["tide_stations"].show()
        app.map.layer["tide_stations"].layer["stations"].activate()
        app.map.layer["tide_stations"].layer["polygon"].activate()
        dataset_name = app.gui.getvar("tide_stations", "dataset_name")
        dataset = app.tide_stations_database.dataset[dataset_name]
        if not dataset.is_read:
            # First time this tab is opened
            self.select_dataset()
        self.update_constituent_table()

    def set_layer_mode(self, mode):
        if mode == "inactive":
            # Make all layers invisible
            app.map.layer["tide_stations"].hide()
        if mode == "invisible":
            # Make all layers invisible
            app.map.layer["tide_stations"].hide()

    def add_layers(self):
        # Add Mapbox layers
        layer = app.map.add_layer("tide_stations")
        layer.add_layer("stations",
                         type="circle_selector",
                         hover_property="name",
                         line_color="white",
                         line_color_selected="white",
                         select=self.select_station_from_map
                        )        
        layer.add_layer("polygon",
                        type="draw",
                        shape="polygon",
                        create=self.polygon_created)

    def polygon_created(self, gdf, index, id):
        app.toolbox["tide_stations"].polygon = gdf

    def select_dataset(self):
        dataset_name = app.gui.getvar("tide_stations", "dataset_name")
        dataset = app.tide_stations_database.dataset[dataset_name]
        # add wait message
        dlg = app.gui.window.dialog_wait("Reading tide stations dataset ...")
        dataset.get_gdf()
        self.gdf = dataset.gdf
        dlg.close()
        names, ids = dataset.station_names()
        app.gui.setvar("tide_stations", "active_station_index", 0)
        app.gui.setvar("tide_stations", "naming_option", "name")
        app.gui.setvar("tide_stations", "station_names", names)
        app.map.layer["tide_stations"].layer["stations"].set_data(self.gdf, 0)
        self.update() # update list of stations
        self.update_constituent_table()

    def add_stations_to_model(self):
        app.active_model.add_stations(self.gdf, naming_option=app.gui.getvar("tide_stations", "naming_option"))

    def select_naming_option(self):
        self.update()
        opt = app.gui.getvar("tide_stations", "naming_option")
        index = app.gui.getvar("tide_stations", "active_station_index")
        app.map.layer["tide_stations"].layer["stations"].hover_property = opt
        app.map.layer["tide_stations"].layer["stations"].set_data(self.gdf,
                                                                         index)
    def select_station_from_map(self, *args):
        index = args[0]["properties"]["index"]
        app.gui.setvar("tide_stations", "active_station_index", index)
        self.update_constituent_table()
        app.gui.window.update()

    def select_station_from_list(self):
        index = app.gui.getvar("tide_stations", "active_station_index")
        app.map.layer["tide_stations"].layer["stations"].select_by_index(index)
        self.update_constituent_table()

    def view_tide_signal(self):
        station_name = app.gui.getvar("tide_stations", "station_names")[app.gui.getvar("tide_stations", "active_station_index")]
        dataset_name = app.gui.getvar("tide_stations", "dataset_name")
        dataset = app.tide_stations_database.dataset[dataset_name]
        tstart = app.gui.getvar("tide_stations", "tstart")
        tend = app.gui.getvar("tide_stations", "tend")
        offset = app.gui.getvar("tide_stations", "offset")

        if app.gui.getvar("tide_stations", "naming_option") == "name":
            prd = dataset.predict(name=station_name, start=tstart, end=tend, offset=offset)
        else:
            prd = dataset.predict(id=station_name, start=tstart, end=tend, offset=offset)
        # If there is already a plot, add the new one to the same plot
        # Otherwise, create a new plot
        # plt.figure()
        # Check if there is a plot open
        if len(plt.get_fignums()) > 0:
            # Add prd to the existing plot
            # Get the axis handle
            prd.plot(ax=plt.gca())
        else:
            # Create a new plot
            self.legend_list = []
            prd.plot()
        # Set the title to station name
        # plt.title(station_name)
        # Remove the legend
        self.legend_list.append(station_name)
        plt.legend(self.legend_list)
        # Get the active figure
        fig = plt.gcf()
        fig.canvas.draw() 
        fig.canvas.flush_events()         
        plt.show()

    def export_tide_signal(self):

        dataset_name = app.gui.getvar("tide_stations", "dataset_name")
        dataset = app.tide_stations_database.dataset[dataset_name]
        opt = app.gui.getvar("tide_stations", "naming_option")
        tstart = app.gui.getvar("tide_stations", "tstart")
        tend = app.gui.getvar("tide_stations", "tend")
        dt = app.gui.getvar("tide_stations", "dt")
        offset = app.gui.getvar("tide_stations", "offset")
        fmt = app.gui.getvar("tide_stations", "format")

        # Add wait message
        dlg = app.gui.window.dialog_wait("Exporting tide signal(s) ...")

        if app.toolbox["tide_stations"].polygon is None:
            # No polygon defined, so just pick active station
            station_list = [app.gui.getvar("tide_stations", "station_names")[app.gui.getvar("tide_stations", "active_station_index")]]
        else:
            # Get all stations within polygon
            station_list = []
            for index, row in self.gdf.iterrows():
                if app.toolbox["tide_stations"].polygon.contains(row.geometry)[0]:
                    station_list.append(row[opt])

        for station_name in station_list:
            stname = station_name
            stname = stname.replace(" ", "_")
            # Replace all special characters by _
            stname = ''.join(e if e.isalnum() else "" for e in stname)
            filename = f"{stname}.{fmt}"
            if opt == "name":
                prd = dataset.predict(name=station_name, start=tstart, end=tend, dt=dt, filename=filename, format=fmt, offset=offset)
            else:
                prd = dataset.predict(id=station_name, start=tstart, end=tend, dt=dt, filename=filename, format=fmt, offset=offset)

        dlg.close()        

    def update(self):
        stnames = []
        opt = app.gui.getvar("tide_stations", "naming_option")
        for index, row in self.gdf.iterrows():
            stnames.append(row[opt])
        app.gui.setvar("tide_stations", "station_names", stnames)

    def update_constituent_table(self):
        dataset_name = app.gui.getvar("tide_stations", "dataset_name")
        opt = app.gui.getvar("tide_stations", "naming_option")
        dataset = app.tide_stations_database.dataset[dataset_name]
        station_name = app.gui.getvar("tide_stations", "station_names")[app.gui.getvar("tide_stations", "active_station_index")]
        if opt == "name":
            tbl = dataset.get_components(name=station_name)
        else:
            tbl = dataset.get_components(id=station_name)
        app.gui.setvar("tide_stations", "constituent_table", tbl)

def select(*args):
    app.toolbox["tide_stations"].select_tab()

def select_dataset(*args):
    app.toolbox["tide_stations"].select_dataset()

def select_station(*args):
    app.toolbox["tide_stations"].select_station_from_list()

def select_naming_option(*args):
    app.toolbox["tide_stations"].select_naming_option()

def add_stations_to_model(*args):
    app.toolbox["tide_stations"].add_stations_to_model()

def view_tide_signal(*args):
    app.toolbox["tide_stations"].view_tide_signal()

def export_tide_signal(*args):
    app.toolbox["tide_stations"].export_tide_signal()

def export_tidal_components(*args):
    app.toolbox["tide_stations"].export_tidal_components()

def draw_polygon(*args):
    app.map.layer["tide_stations"].layer["polygon"].draw()

def delete_polygon(*args):
    app.map.layer["tide_stations"].layer["polygon"].clear()
    app.toolbox["tide_stations"].polygon = None
