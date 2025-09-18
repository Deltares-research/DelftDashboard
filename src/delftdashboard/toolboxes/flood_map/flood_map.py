# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
import os
import geopandas as gpd
import xarray as xr

# import datetime
from delftdashboard.app import app
from delftdashboard.operations.toolbox import GenericToolbox

# from cht_sfincs import SFINCS
from cht_tiling import FloodMap
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
        app.gui.setvar(group, "topo_file_string", "File : ")
        app.gui.setvar(group, "index_file_string", "File : ")
        app.gui.setvar(group, "map_file_string", "File : ")
        app.gui.setvar(group, "instantaneous_or_maximum", "maximum")
        app.gui.setvar(group, "available_time_strings", [""])
        app.gui.setvar(group, "time_index", 0)
        app.gui.setvar(group, "flood_map_opacity", 0.7)
        app.gui.setvar(group, "continuous_or_discrete_colors", "discrete")
        app.gui.setvar(group, "cmap", "jet")
        app.gui.setvar(group, "cmin", 0.0)
        app.gui.setvar(group, "cmax", 2.0)
        app.gui.setvar(group, "colormaps", app.gui.getvar("view_settings", "colormaps"))
        

        self.flood_map = FloodMap()
        # Set some default values
        self.flood_map.cmap = app.gui.getvar(group, "cmap")
        self.flood_map.cmin = app.gui.getvar(group, "cmin")
        self.flood_map.cmax = app.gui.getvar(group, "cmax")
        self.flood_map.color_values = "default" # Using green, yellow, orange, red
        self.flood_map.discrete_colors = True

        # Exclude polygons SnapWave
        self.polygon = gpd.GeoDataFrame()

        self.instantaneous_time_strings = [""]
        self.maximum_time_strings = [""]
        self.nr_of_instantaneous_times = 0
        self.nr_of_maximum_times = 0

    def set_layer_mode(self, mode):
        if mode == "active":
            # Make container layer visible
            app.map.layer["flood_map"].show()
            # Always show track layer
            app.map.layer["flood_map"].layer["flood_map"].show()
            app.map.layer["flood_map"].layer["polygon"].hide()

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
                        type="raster_image",
                        opacity=0.7,
                        legend_position="bottom-right")
        # Open boundary
        from .topobathy import polygon_created
        layer.add_layer("polygon", type="draw",
                             shape="polygon",
                             create=polygon_created,
                             polygon_line_color="deepskyblue",
                             polygon_fill_color="deepskyblue",
                             polygon_fill_opacity=0.1)

    def load_topobathy_geotiff(self):
        """Select topo/bathy geotiff file"""
        full_name, path, name, ext, fltr = app.gui.window.dialog_open_file("Select topo/bathy geotiff file", filter="*.tif")
        if not full_name:
            return
        self.topobathy_geotiff = full_name
        self.flood_map.set_topobathy_file(full_name)

    def generate_topobathy_geotiff(self):

        if self.polygon.empty:
            # If there is no polygon, use the bounding box of the model

            if app.active_model.name == "sfincs_cht":
                bounds = app.active_model.domain.grid.bounds()            
            else:
                # Get the bounding box of the model
                print("Not supported")            
                return
        else:
            # Use the bounding box of the polygon
            bounds = self.polygon.total_bounds
                
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
            full_name, path, name, ext, fltr = app.gui.window.dialog_save_file("Save index geotiff file", filter="*.tif")
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
            self.map_file_name = file_name[0]

            self.dsa = xr.open_dataset(self.map_file_name)

            # Read the output file lazily

            # Get the time strings
            
            # Instantaneous
            times = self.dsa.time.values
            dt_list = times.astype('datetime64[s]').astype(object)
            self.instantaneous_time_strings = [dt.strftime("%Y-%m-%d %H:%M:%S") for dt in dt_list]
            self.nr_of_instantaneous_times = len(self.instantaneous_time_strings)

            # Maximum
            max_times = self.dsa.timemax.values
            dt_list = max_times.astype('datetime64[s]').astype(object)
            self.maximum_time_strings = [dt.strftime("%Y-%m-%d %H:%M:%S") for dt in dt_list]
            self.nr_of_maximum_times = len(self.maximum_time_strings)

            app.gui.setvar("flood_map", "time_index", 0)
        # return
        # Read file

        # Create XR DataArray

        # Set data
        # app.map.layer[self.name].layer["flood_map_from_tiles"].index_path = os.path.join(pth, "tiles", "indices")
        # app.map.layer[self.name].layer["flood_map_from_tiles"].topobathy_path = os.path.join(pth, "tiles", "topobathy")
        # app.map.layer[self.name].layer["flood_map_from_tiles"].set_data(da)

        # zs = da.values[:]
        # self.flood_map.set_water_level(zs)
        # app.map.layer[self.name].layer["flood_map"].set_data(self.flood_map)

    def update_flood_map(self):

        instantaneous_or_maximum = app.gui.getvar("flood_map", "instantaneous_or_maximum")

        if instantaneous_or_maximum == "instantaneous":
            if self.nr_of_instantaneous_times == 0:
                # Clear flood map layer
                app.map.layer["flood_map"].layer["flood_map"].clear()
                return
        else:
            if self.nr_of_maximum_times == 0:
                # Clear flood map layer
                app.map.layer["flood_map"].layer["flood_map"].clear()
                return

        itime = app.gui.getvar("flood_map", "time_index")

        if instantaneous_or_maximum == "instantaneous":
            zs = self.dsa.zs.isel(time=itime).values[:]
        else:
            zs = self.dsa.zsmax.isel(timemax=itime).values[:]
        
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
