# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
import os
#from PyQt5.QtWidgets import QFileDialog

from delftdashboard.app import app
from delftdashboard.operations.model import GenericModel
from cht_hurrywave.hurrywave import HurryWave

class Model(GenericModel):
    def __init__(self, name):
        super().__init__()

        self.name = name
        self.long_name = "HurryWave"

    def initialize(self):
        self.active_domain = 0
        self.domain = HurryWave()
        self.set_gui_variables()

    def add_layers(self):
        # Add main DDB layer
        layer = app.map.add_layer("hurrywave")

        layer.add_layer("grid", type="image")

        layer.add_layer("mask_include",
                        type="circle",
                        file_name="hurrywave_mask_include.geojson",
                        circle_radius=3,
                        fill_color="yellow",
                        line_color="transparent",
                        fill_opacity=1.0)

        layer.add_layer("mask_boundary",
                        type="circle",
                        file_name="hurrywave_mask_boundary.geojson",
                        circle_radius=3,
                        fill_color="red",
                        line_color="transparent",
                        fill_opacity=1.0)

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
                        hover_property="name",
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
                        hover_property="name",
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
            # Grid is always made visible
            app.map.layer["hurrywave"].layer["grid"].show()
            # Mask is made invisible
            app.map.layer["hurrywave"].layer["mask_include"].hide()
            app.map.layer["hurrywave"].layer["mask_boundary"].hide()
            # Boundary points are made grey
            app.map.layer["hurrywave"].layer["boundary_points"].deactivate()
            # Observation points are made grey
            app.map.layer["hurrywave"].layer["observation_points_regular"].deactivate()
            app.map.layer["hurrywave"].layer["observation_points_spectra"].deactivate()
        elif mode == "invisible":
            # Everything set to invisible
            app.map.layer["hurrywave"].hide()

    def new(self):
        self.initialize_domain()
        self.set_gui_variables()
        app.map.layer["modelmaker_hurrywave"].clear()

    def clear_spatial_attributes(self):
        # This happens when a new grid is created, but we want to keep time, physical and numerical attributes
        # Clear the map
        app.map.layer["hurrywave"].clear()
        # And remove them from the model domain
        self.domain.clear_spatial_attributes()
        self.set_gui_variables()

    def set_gui_variables(self):

        group = "hurrywave"

        # Input variables
        for var_name in vars(self.domain.input.variables):
            app.gui.setvar(group, var_name, getattr(self.domain.input.variables, var_name))

        # Boundary points
        app.gui.setvar(group, "boundary_dx", 50000.0)

        # View settings
        app.gui.setvar(group, "view_grid", True)

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
            self.domain = HurryWave()
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
            # Zoom to model extent
            bounds = self.domain.grid.bounds(crs=4326, buffer=0.1)
            app.map.fit_bounds(bounds[0], bounds[1], bounds[2], bounds[3])

    def save(self):
        # Write hurrywave.inp and run.bat
        self.domain.path = os.getcwd()        
        self.domain.input.variables.epsg = app.crs.to_epsg()
        self.domain.exe_path = app.config["hurrywave_exe_path"]
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

    def get_view_menu(self):
        model_view_menu = {}
        model_view_menu["text"] = self.long_name
        model_view_menu["menu"] = []
        model_view_menu["menu"].append({"variable_group": self.name,
                                        "id": f"view.{self.name}.grid",
                                        "text": "Grid",
                                        "variable": "view_grid",
                                        "separator": True,
                                        "checkable": True,
                                        "method": self.set_view_menu,
                                        "option": "grid",
                                        "dependency": [{"action": "check", "checkfor": "all", "check": [{"variable": "view_grid", "operator": "eq", "value": True}]}]})
        return model_view_menu

    def set_view_menu(self, option, checked):
        if option == "grid":
            print(f"Checked: {checked}")
            if app.gui.getvar(self.name, "view_grid"):
                print("Grid is made visible")
            else:
                print("Grid is made invisible")
