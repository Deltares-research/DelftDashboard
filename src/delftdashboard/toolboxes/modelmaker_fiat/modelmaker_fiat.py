# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

import geopandas as gpd
from pyproj import CRS

from hydromt_fiat.api.hydromt_fiat_vm import HydroMtViewModel
from delftdashboard.operations.toolbox import GenericToolbox
from delftdashboard.app import app


class Toolbox(GenericToolbox):
    def __init__(self, name):
        super().__init__()

        self.name = name
        self.long_name = "Model boundary"

        # Set GUI variable
        group = "modelmaker_fiat"

        app.gui.setvar(group, "selected_aoi_method", "polygon")
        app.gui.setvar(
            group,
            "setup_aoi_method_string",
            ["Draw Polygon", "Draw box", "Select SFINCS model domain", "Upload file"],
        )
        app.gui.setvar(
            group,
            "setup_aoi_method_value",
            ["polygon", "box", "sfincs", "file"],
        )
        app.gui.setvar(group, "active_area_of_interest", "")
        app.gui.setvar(group, "area_of_interest", 0)
        app.gui.setvar(group, "selected_crs", "EPSG:4326")
        app.gui.setvar(group, "selected_scenario", "MyScenario")

        # Area of Interest
        self.area_of_interest = gpd.GeoDataFrame()
        self.area_of_interest_file_name = "area_of_interest.geojson"

        self.setup_dict = {}

    def set_layer_mode(self, mode):
        if mode == "inactive":
            # Make all layers invisible
            app.map.layer["modelmaker_fiat"].set_mode("invisible")
        if mode == "invisible":
            app.map.layer["modelmaker_fiat"].set_mode("invisible")

    def add_layers(self):
        # Add Mapbox layers
        layer = app.map.add_layer("modelmaker_fiat")

        layer.add_layer(
            "area_of_interest_bbox",
            type="draw",
            shape="rectangle",
            polygon_line_color="orange",
            polygon_fill_color="#fcc203",
            polygon_fill_opacity=0.3,
            rotate=True,
        )

        layer.add_layer(
            "area_of_interest_polygon",
            type="draw",
            shape="polygon",
            polygon_line_color="orange",
            polygon_fill_color="#fcc203",
            polygon_fill_opacity=0.3,
            rotate=True,
        )

        layer.add_layer(
            "area_of_interest_from_file",
            type="draw",
            shape="polygon",
            polygon_line_color="orange",
            polygon_fill_color="#fcc203",
            polygon_fill_opacity=0.3,
            rotate=True,
        )

        layer.add_layer(
            "area_of_interest_from_sfincs",
            type="draw",
            shape="rectangle",
            polygon_line_color="orange",
            polygon_fill_color="#fcc203",
            polygon_fill_opacity=0.3,
            rotate=True,
        )

    def set_scenario(self):
        selected_scenario = app.gui.getvar("modelmaker_fiat", "selected_scenario")
        scenario_folder = app.config["working_directory"] + "\\" + selected_scenario
        app.gui.setvar("fiat", "selected_scenario", selected_scenario)
        app.gui.setvar("fiat", "scenario_folder", scenario_folder)
        hydromt_vm = HydroMtViewModel(
            app.config["working_directory"],
            app.config["data_libs"],
            scenario_folder,
        )
        return hydromt_vm

    def set_crs(self):
        selected_crs = app.gui.getvar("modelmaker_fiat", "selected_crs")
        app.gui.setvar("fiat", "selected_crs", selected_crs)

    def generate_grid(self):
        dlg = app.gui.window.dialog_wait("Generating grid ...")

        # model = app.model["fiat"].domain

        # group = "modelmaker_fiat"
        # model.input.variables.x0 = app.gui.getvar(group, "x0")

        # group = "fiat"
        # app.gui.setvar(group, "x0", model.input.variables.x0)

        # model.grid.build()

        # app.map.layer["fiat"].layer["grid"].set_data(
        #     model.grid,
        #     xlim=[app.gui.getvar(group, "x0"), app.gui.getvar(group, "x0")],
        #     ylim=[app.gui.getvar(group, "y0"), app.gui.getvar(group, "y0")],
        # )

        dlg.close()

    def build_model(self):
        self.generate_grid()
        self.update_mask()

    def update_polygons(self):
        nrp = len(self.include_polygon)
        incnames = []
        for ip in range(nrp):
            incnames.append(str(ip + 1))
        app.gui.setvar("modelmaker_fiat", "nr_include_polygons", nrp)
        app.gui.setvar("modelmaker_fiat", "include_polygon_names", incnames)

        nrp = len(self.exclude_polygon)
        excnames = []
        for ip in range(nrp):
            excnames.append(str(ip + 1))
        app.gui.setvar("modelmaker_fiat", "nr_exclude_polygons", nrp)
        app.gui.setvar("modelmaker_fiat", "exclude_polygon_names", excnames)

        nrp = len(self.boundary_polygon)
        bndnames = []
        for ip in range(nrp):
            bndnames.append(str(ip + 1))
        app.gui.setvar("modelmaker_fiat", "nr_boundary_polygons", nrp)
        app.gui.setvar("modelmaker_fiat", "boundary_polygon_names", bndnames)

        app.toolbox["modelmaker_fiat"].write_boundary_polygon()

    def plot_include_polygon(self):
        layer = app.map.layer["modelmaker_fiat"].layer["mask_include"]
        layer.clear()
        layer.add_feature(self.include_polygon)

    def read_setup_yaml(self, file_name):
        pass

    def write_setup_yaml(self):
        pass

    def generate_aoi(self):
        pass
