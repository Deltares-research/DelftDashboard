# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
import os
import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog

from ddb_model import GenericModel
from ddb import ddb

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

    def add_layers(self):
        # Add main DDB layer
        layer = ddb.map.add_layer("hurrywave")


    def open(self):
        fname = QFileDialog.getOpenFileName(None, "Open file", "",
                                            "HurryWave input file (hurrywave.inp)")
        fname = fname[0]
        if fname:
            path = os.path.dirname(fname)
            self.domain.path = path
            self.domain.read()
            # Change working directory
#            os.chdir(path)
            # Change CRS
            ddb.crs = self.domain.crs

            self.plot()

    def save(self):
        # Write hurrywave.inp
        self.domain.input.write()

    def load(self):
        self.domain.read()

    def plot(self):
#        gdf = self.domain.grid.to_gdf()

        layer = ddb.map.layer["hurrywave"]

        # grid_layer = layer.get("grid")
        # if grid_layer:
        #     grid_layer.delete()
        # layer.add_deck_geojson_layer("grid", data=gdf, file_name="hurrywave_grid.geojson")

        if self.domain.mask.array:
            layer.add_geojson_layer("mask",
                                    data=self.domain.mask.to_gdf(self.domain.grid),
                                    file_name="hurrywave_mask.geojson",
                                    type="circle",
                                    circle_radius=3,
                                    fill_color="yellow",
                                    line_color="transparent")

        if self.domain.input.variables.bndfile:
            layer.add_geojson_layer("boundary_points",
                                    data=self.domain.boundary_conditions.gdf,
                                    file_name="hurrywave_boundary_points.geojson",
                                    type="marker_selector",
                                    circle_radius=5,
                                    fill_color="royalblue")

        if self.domain.input.variables.obsfile:
            layer.add_geojson_layer("observation_points_regular",
                                    data=self.domain.observation_points_regular.gdf,
                                    file_name="hurrywave_observation_points.geojson",
                                    type="marker_selector",
                                    circle_radius=5,
                                    fill_color="orange")

    def set_gui_variables(self):
        group = "hurrywave"

        # Input variables
        for var_name in vars(self.domain.input.variables):
            ddb.gui.setvar(group, var_name, getattr(self.domain.input.variables, var_name))

        ddb.gui.setvar(group, "output_options_text", ["NetCDF", "Binary", "ASCII"])
        ddb.gui.setvar(group, "output_options_values", ["net", "bin", "asc"])

    def set_model_variables(self):
        # Update all model input variables
        for var_name in vars(self.domain.input.variables):
            setattr(self.domain.input.variables, var_name, ddb.gui.getvar("hurrywave", var_name))

    def initialize_domain(self):
        self.domain = HurryWave()

    def set_input_variable(self, gui_variable, value):
        pass

