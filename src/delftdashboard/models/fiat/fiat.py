# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
import os
from PyQt5.QtWidgets import QFileDialog
from pathlib import Path

from delftdashboard.app import app
from delftdashboard.operations.model import GenericModel
from cht.hurrywave.hurrywave import HurryWave


class Model(GenericModel):
    def __init__(self, name):
        super().__init__()

        self.name = name
        self.long_name = "fiat"

        print("Model " + self.name + " added!")
        self.active_domain = 0

        self.initialize_domain()

        self.set_gui_variables()

    def initialize_domain(self):
        self.domain = HurryWave()

    def add_layers(self):
        # Add main DDB layer
        layer = app.map.add_layer("fiat")

        # layer.add_layer("grid", type="deck_geojson",
        #                 file_name="fiat_grid.geojson",
        #                 line_color="black")
        layer.add_layer("grid", type="image")

        layer.add_layer(
            "mask_include",
            type="circle",
            file_name="fiat_mask_include.geojson",
            circle_radius=3,
            fill_color="yellow",
            line_color="transparent",
        )

        layer.add_layer(
            "mask_boundary",
            type="circle",
            file_name="fiat_mask_boundary.geojson",
            circle_radius=3,
            fill_color="red",
            line_color="transparent",
        )

    def set_layer_mode(self, mode):
        if mode == "inactive":
            # Grid is made visible
            app.map.layer["fiat"].layer["grid"].set_mode("inactive")
            # Mask is made invisible
            app.map.layer["fiat"].layer["mask_include"].set_mode("invisible")
            app.map.layer["fiat"].layer["mask_boundary"].set_mode("invisible")
            # Boundary points are made grey
            app.map.layer["fiat"].layer["boundary_points"].set_mode("inactive")
            # Observation points are made grey
            app.map.layer["fiat"].layer["observation_points_regular"].set_mode(
                "inactive"
            )
            app.map.layer["fiat"].layer["observation_points_spectra"].set_mode(
                "inactive"
            )
        elif mode == "invisible":
            # Everything set to invisible
            app.map.layer["fiat"].set_mode("invisible")

    def set_gui_variables(self):
        group = "fiat"
        # Input variables
        for var_name in vars(self.domain.input.variables):
            app.gui.setvar(
                group, var_name, getattr(self.domain.input.variables, var_name)
            )
        app.gui.setvar(group, "output_options_text", ["NetCDF", "GeoPackage", "CSV"])
        app.gui.setvar(group, "output_options_values", ["NetCDF", "GeoPackage", "CSV"])
        app.gui.setvar(group, "show_area_geometry", False)
        app.gui.setvar(group, "asset_locations_string", ["National Structure Inventory (NSI)", "Upload data"])
        app.gui.setvar(group, "asset_locations_value", ["nsi", "file"])
        app.gui.setvar(group, "asset_locations", None)
        app.gui.setvar(group, "damages_source_string", ["Hazus", "Create"])
        app.gui.setvar(group, "damages_source_value", ["hazus", "create"])
        app.gui.setvar(group, "damages_source", None)
        app.gui.setvar(group, "show_asset_locations", False)
        app.gui.setvar(group, "show_extraction_method", False)
        app.gui.setvar(group, "extraction_method", "Centroid")
        app.gui.setvar(group, "show_secondary_classification", False)

    def set_input_variables(self):
        # Update all model input variables
        for var_name in vars(self.domain.input.variables):
            setattr(
                self.domain.input.variables, var_name, app.gui.getvar("fiat", var_name)
            )

    def open(self):
        # Open input file, and change working directory
        fname = app.gui.window.dialog_open_file(
            "Open file", filter="fiat input file;;ini files (*.ini)"
        )
        fname = fname[0]
        if fname:
            dlg = app.gui.window.dialog_wait("Loading fiat model ...")
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
        # Write fiat.inp
        self.domain.path = os.getcwd()
        self.domain.input.write()
        self.domain.write_batch_file()

    def load(self):
        self.domain.read()

    def set_crs(self, crs):
        self.domain.crs = crs

    def plot(self):
        # Grid
        gdf = self.domain.grid.to_gdf()
        app.map.layer["fiat"].layer["grid"].set_data(gdf)

    def set_classification_field(self):
        # get window config yaml path
        pop_win_config_path = str(
            Path(
                app.gui.config_path
            ).parent  # TODO: replace with a variables config_path for the fiat model
            / "models"
            / self.name
            / "config"
            / "exposure_classification_fields.yml"
        )

        # Create pop-up and only continue if user presses ok
        okay, data = app.gui.popup(pop_win_config_path, None)
        if not okay:
            return
