# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
import os
from PyQt5.QtWidgets import QFileDialog

from delftdashboard.app import app
from delftdashboard.operations.model import GenericModel
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
        layer = app.map.add_layer("hurrywave")

        # layer.add_layer("grid", type="deck_geojson",
        #                 file_name="hurrywave_grid.geojson",
        #                 line_color="black")
        layer.add_layer("grid", type="image")

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
                        hover_property="name",
                        line_color="white",
                        line_opacity=1.0,
                        fill_color="blue",
                        fill_opacity=1.0,
                        circle_radius=4,
                        circle_radius_selected=5,
                        line_color_selected="white",
                        fill_color_selected="red",
                        circle_radius_inactive=4,
                        line_color_inactive="white",
                        fill_color_inactive="lightgrey"
                       )

        from .observation_points_regular import select_observation_point_from_map_regular
        layer.add_layer("observation_points_regular",
                        type="circle_selector",
                        select=select_observation_point_from_map_regular,
                        line_color="white",
                        line_opacity=1.0,
                        fill_color="blue",
                        fill_opacity=1.0,
                        circle_radius=3,
                        circle_radius_selected=4,
                        line_color_selected="white",
                        fill_color_selected="red")

        from .observation_points_spectra import select_observation_point_from_map_spectra
        layer.add_layer("observation_points_spectra",
                        type="circle_selector",
                        select=select_observation_point_from_map_spectra,
                        line_color="white",
                        line_opacity=1.0,
                        fill_color="orange",
                        fill_opacity=1.0,
                        circle_radius=3,
                        circle_radius_selected=4,
                        line_color_selected="white",
                        fill_color_selected="red")

    def set_layer_mode(self, mode):
        if mode == "inactive":
            # Grid is made visible
            app.map.layer["hurrywave"].layer["grid"].set_activity(False)
            # Mask is made invisible
            app.map.layer["hurrywave"].layer["mask_include"].set_visibility(False)
            app.map.layer["hurrywave"].layer["mask_boundary"].set_visibility(False)
            # Boundary points are made grey
            app.map.layer["hurrywave"].layer["boundary_points"].set_activity(False)
            # Observation points are made grey
            app.map.layer["hurrywave"].layer["observation_points_regular"].set_activity(False)
            app.map.layer["hurrywave"].layer["observation_points_spectra"].set_activity(False)
        elif mode == "invisible":
            # Everything set to invisible
            app.map.layer["hurrywave"].set_visibility(False)

    def set_gui_variables(self):
        group = "hurrywave"
        # Input variables
        for var_name in vars(self.domain.input.variables):
            app.gui.setvar(group, var_name, getattr(self.domain.input.variables, var_name))
        app.gui.setvar(group, "output_options_text", ["NetCDF", "Binary", "ASCII"])
        app.gui.setvar(group, "output_options_values", ["net", "bin", "asc"])
        app.gui.setvar(group, "wind_type", "uniform")
        app.gui.setvar(group, "boundary_point_names", [])
        app.gui.setvar(group, "nr_boundary_points", 0)
        app.gui.setvar(group, "active_boundary_point", 0)
        app.gui.setvar(group, "boundary_forcing", self.domain.boundary_conditions.forcing)
        app.gui.setvar(group, "boundary_hm0", 1.0)
        app.gui.setvar(group, "boundary_tp", 6.0)
        app.gui.setvar(group, "boundary_wd", 0.0)
        app.gui.setvar(group, "boundary_ds", 30.0)

        app.gui.setvar(group, "observation_point_names_regular", [])
        app.gui.setvar(group, "nr_observation_points_regular", 0)
        app.gui.setvar(group, "active_observation_point_regular", 0)

        app.gui.setvar(group, "observation_point_names_spectra", [])
        app.gui.setvar(group, "nr_observation_points_spectra", 0)
        app.gui.setvar(group, "active_observation_point_spectra", 0)

    def set_input_variables(self):
        # Update all model input variables
        for var_name in vars(self.domain.input.variables):
            setattr(self.domain.input.variables, var_name, app.gui.getvar("hurrywave", var_name))

    def open(self):
        # Open input file, and change working directory
        fname = app.gui.window.dialog_open_file("Open file", filter="HurryWave input file (hurrywave.inp)")
        fname = fname[0]
        if fname:
            dlg = app.gui.window.dialog_wait("Loading HurryWave model ...")
            path = os.path.dirname(fname)
            self.domain.path = path
            self.domain.read()
            self.set_gui_variables()
            # Change working directory
            os.chdir(path)
            # Change CRS
            app.crs = self.domain.crs
            self.plot()
            dlg.close()

    def save(self):
        # Write hurrywave.inp
        self.domain.path = os.getcwd()
        self.domain.input.write()
        self.domain.write_batch_file()


    def load(self):
        self.domain.read()

    def set_crs(self):
        self.domain.crs = app.crs
        self.domain.clear_spatial_attributes()
        self.plot()

    def plot(self):
        # Grid
        app.map.layer["hurrywave"].layer["grid"].set_data(self.domain.grid)
        # Mask
        app.map.layer["hurrywave"].layer["mask_include"].set_data(self.domain.grid.mask_to_gdf(option="include"))
        app.map.layer["hurrywave"].layer["mask_boundary"].set_data(self.domain.grid.mask_to_gdf(option="boundary"))
        # Boundary points
        gdf = self.domain.boundary_conditions.gdf
        app.map.layer["hurrywave"].layer["boundary_points"].set_data(gdf, 0)
        # Observation points
        gdf = self.domain.observation_points_regular.gdf
        app.map.layer["hurrywave"].layer["observation_points_regular"].set_data(gdf, 0)
        gdf = self.domain.observation_points_sp2.gdf
        app.map.layer["hurrywave"].layer["observation_points_spectra"].set_data(gdf, 0)

    def add_stations(self, gdf_stations_to_add, naming_option="id"):
        self.domain.observation_points_regular.add_points(gdf_stations_to_add, name=naming_option)
        gdf = self.domain.observation_points_regular.gdf
        app.map.layer["hurrywave"].layer["observation_points_regular"].set_data(gdf, 0)
        if not self.domain.input.variables.obsfile:
            self.domain.input.variables.obsfile = "hurrywave.obs"
        self.domain.observation_points_regular.write()
