# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
import os
from PyQt5.QtWidgets import QFileDialog

from ddb import ddb
from operations.model import GenericModel
from cht.hurrywave.hurrywave import HurryWave

class Model(GenericModel):
    def __init__(self, name):
        super().__init__()

        self.name = name
        self.long_name = "HurryWave"

        print("Model " + self.name + " added!")
        self.active_domain = 0

        self.initialize_domain()

        self.set_gui_variables()

    def initialize_domain(self):
        self.domain = HurryWave()

    def add_layers(self):
        # Add main DDB layer
        layer = ddb.map.add_layer("hurrywave")

        layer.add_layer("grid", type="deck_geojson",
                        file_name="hurrywave_grid.geojson",
                        line_color="black")

        layer.add_layer("mask_include",
                        type="circle",
                        file_name="hurrywave_mask_include.geojson",
                        circle_radius=3,
                        fill_color="yellow",
                        line_color="transparent")

        layer.add_layer("mask_boundary",
                        type="circle",
                        file_name="hurrywave_mask_boundary.geojson",
                        circle_radius=3,
                        fill_color="red",
                        line_color="transparent")

        # Move this to hurrywave.py
        from .boundary_conditions import select_boundary_point_from_map
        layer.add_layer("boundary_points",
                        type="circle_selector",
                        select=select_boundary_point_from_map,
                        line_color="white",
                        line_opacity=1.0,
                        fill_color="blue",
                        fill_opacity=1.0,
                        circle_radius=3,
                        circle_radius_selected=4,
                        line_color_selected="white",
                        fill_color_selected="red")

        layer.add_layer("observation_points",
                        type="circle_selector",
                        line_color="white",
                        line_opacity=1.0,
                        fill_color="blue",
                        fill_opacity=1.0,
                        circle_radius=3,
                        circle_radius_selected=4,
                        line_color_selected="white",
                        fill_color_selected="red")

    def set_layer_mode(self, mode):
        if mode == "inactive":
            # Mask is made invisible
            ddb.map.layer["hurrywave"].layer["grid"].set_mode("invisible")
            ddb.map.layer["hurrywave"].layer["mask_include"].set_mode("invisible")
            ddb.map.layer["hurrywave"].layer["mask_boundary"].set_mode("invisible")
            # Boundary points are made grey
            ddb.map.layer["hurrywave"].layer["boundary_points"].set_mode("inactive")
            # Observation points are made grey
            ddb.map.layer["hurrywave"].layer["observation_points"].set_mode("inactive")
        if mode == "invisible":
            ddb.map.layer["hurrywave"].set_mode("invisible")

    def set_gui_variables(self):
        group = "hurrywave"
        # Input variables
        for var_name in vars(self.domain.input.variables):
            ddb.gui.setvar(group, var_name, getattr(self.domain.input.variables, var_name))
        ddb.gui.setvar(group, "output_options_text", ["NetCDF", "Binary", "ASCII"])
        ddb.gui.setvar(group, "output_options_values", ["net", "bin", "asc"])
        ddb.gui.setvar(group, "wind_type", "uniform")
        ddb.gui.setvar(group, "boundary_point_names", [])
        ddb.gui.setvar(group, "nr_boundary_points", 0)
        ddb.gui.setvar(group, "active_boundary_point", 0)

    def set_input_variables(self):
        # Update all model input variables
        for var_name in vars(self.domain.input.variables):
            setattr(self.domain.input.variables, var_name, ddb.gui.getvar("hurrywave", var_name))

    def open(self):
        # Open input file, and change working directory
        fname = ddb.gui.open_file_name("Open file", "HurryWave input file (hurrywave.inp)")
        if fname:
            path = os.path.dirname(fname)
            self.domain.path = path
            self.domain.read()
            # Change working directory
            os.chdir(path)
            # Change CRS
            ddb.crs = self.domain.crs

#            self.plot()

    def save(self):
        # Write hurrywave.inp
        self.domain.path = os.getcwd()
        self.domain.input.write()
        self.domain.write_batch_file()


    def load(self):
        self.domain.read()

    def set_crs(self, crs):
        self.domain.crs = crs

#     def plot(self):

#         # Called when a model has been loaded
# #        gdf = self.domain.grid.to_gdf()

#         layer = ddb.map.layer["hurrywave"]

#         # grid_layer = layer.get("grid")
#         # if grid_layer:
#         #     grid_layer.delete()
#         # layer.add_deck_geojson_layer("grid", data=gdf, file_name="hurrywave_grid.geojson")

#         if self.domain.mask.array:
#             layer.add_geojson_layer("mask",
#                                     data=self.domain.mask.to_gdf(self.domain.grid),
#                                     file_name="hurrywave_mask.geojson",
#                                     type="circle",
#                                     circle_radius=3,
#                                     fill_color="yellow",
#                                     line_color="transparent")

#         # if self.domain.input.variables.bndfile:
#         #     layer.add_geojson_layer("boundary_points",
#         #                             data=self.domain.boundary_conditions.gdf,
#         #                             file_name="hurrywave_boundary_points.geojson",
#         #                             type="marker_selector",
#         #                             circle_radius=5,
#         #                             fill_color="royalblue")

#         if self.domain.input.variables.obsfile:
#             layer.add_geojson_layer("observation_points_regular",
#                                     data=self.domain.observation_points_regular.gdf,
#                                     file_name="hurrywave_observation_points.geojson",
#                                     type="marker_selector",
#                                     circle_radius=5,
#                                     fill_color="orange")


    # def set_input_variable(self, gui_variable, value):
    #     pass

