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
from cht_sfincs import FloodMap
from .utils import make_topobathy_cog

class Toolbox(GenericToolbox):
    def __init__(self, name):
        super().__init__()

        self.name = name
        self.long_name = "Flood Map"

    def initialize(self):

        # Set variables

        group = "flood_map"

        app.gui.setvar(group, "dx_geotiff", 10.0)
        app.gui.setvar(group, "map_file_name", "")

        self.flood_map = FloodMap()


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
        layer.add_layer("flood_map",
                        type="image")

    def load_topobathy_geotiff(self):
        """Select topo/bathy geotiff file"""
        full_name, path, name, ext, fltr = app.gui.window.dialog_open_file("Select topo/bathy geotiff file", filter="*.tif")
        if not full_name:
            return
        self.topobathy_geotiff = full_name
        self.flood_map.set_topobathy_file(full_name)

    def generate_topobathy_geotiff(self):
        # Need to get the bounding box of the model
        # Check what type of model this is
        if app.active_model.name == "sfincs_cht":
            bounds = app.active_model.domain.grid.bounds()            
        else:
            # Get the bounding box of the model
            print("Not supported")            
            return
                
        dx = app.gui.getvar("flood_map", "dx_geotiff")
        full_name, path, name, ext, fltr = app.gui.window.dialog_save_file("Save topo/bathy geotiff file", filter="*.tif")
        if not full_name:
            return
        filename = full_name
        wb = app.gui.window.dialog_wait("Generating topobathy geotiff ...")
        make_topobathy_cog(filename,
                           app.selected_bathymetry_datasets,
                           bounds,
                           app.map.crs,
                           bathymetry_database=app.bathymetry_database,
                           dx=dx)
        self.topobathy_geotiff = filename
        self.flood_map.set_topobathy_file(filename)
        wb.close()

    def load_index_geotiff(self):
        """Select index geotiff file"""
        full_name, path, name, ext, fltr = app.gui.window.dialog_open_file("Select index geotiff file", filter="*.tif")
        if not full_name:
            return
        self.index_geotiff = full_name
        self.flood_map.set_index_file(full_name)

    def generate_index_geotiff(self):
        if app.active_model.name == "sfincs_cht":
            full_name, path, name, ext, fltr = app.gui.window.dialog_save_file("Save topo/bathy geotiff file", filter="*.tif")
            if not full_name:
                return
            filename = full_name
            wb = app.gui.window.dialog_wait("Generating index geotiff ...")
            app.active_model.domain.grid.make_index_cog(filename,
                                                        app.toolbox["flood_map"].topobathy_geotiff)
            wb.close()
            self.flood_map.set_index_file(filename)
            self.index_geotiff = filename
        else:
            print("Not supported")
            return

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
        # app.map.layer[self.name].layer["flood_map_from_tiles"].index_path = os.path.join(pth, "tiles", "indices")
        # app.map.layer[self.name].layer["flood_map_from_tiles"].topobathy_path = os.path.join(pth, "tiles", "topobathy")
        # app.map.layer[self.name].layer["flood_map_from_tiles"].set_data(da)

        zs = da.values[:]
        self.flood_map.set_water_level(zs)
        app.map.layer[self.name].layer["flood_map"].set_data(self.flood_map)

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

    def export_flood_map(self):
        # Export flood map
        file_name = app.gui.window.dialog_save_file("Export flood map", "*.tif")
        if file_name[0]:
            wb = app.gui.window.dialog_wait("Exporting flood map ...")
            self.flood_map.make()
            self.flood_map.write(file_name[0])
            wb.close()
