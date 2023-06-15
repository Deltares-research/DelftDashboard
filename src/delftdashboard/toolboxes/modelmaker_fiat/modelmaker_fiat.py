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

from cht.misc.misc_tools import dict2yaml
from cht.misc.misc_tools import yaml2dict


class Toolbox(GenericToolbox):
    def __init__(self, name):
        super().__init__()

        self.name = name
        self.long_name = "Model Maker"

        # Set GUI variable
        group = "modelmaker_fiat"

        app.gui.setvar(group, "selected_aoi_method", "Draw Polygon")
        app.gui.setvar(
            group,
            "setup_aoi_method_string",
            ["Draw Polygon", "Draw Bounding Box", "Use SFINCS Domain", "Load File"],
        )
        app.gui.setvar(
            group,
            "setup_aoi_method_value",
            ["Draw Polygon", "Draw Bounding Box", "Use SFINCS Domain", "Load File"],
        )
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
            "area_of_interest",
            type="draw",
            shape="rectangle",
            # create=grid_outline_created,
            # modify=grid_outline_modified,
            polygon_line_color="mediumblue",
            polygon_fill_opacity=0.3,
            rotate=True,
        )

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

    def read_include_polygon(self):
        self.include_polygon = gpd.read_file(self.include_file_name)
        self.update_polygons()

    def read_exclude_polygon(self):
        self.exclude_polygon = gpd.read_file(self.exclude_file_name)
        self.update_polygons()

    def read_boundary_polygon(self):
        self.boundary_polygon = gpd.read_file(self.boundary_file_name)
        self.update_polygons()

    def write_include_polygon(self):
        if len(self.include_polygon) == 0:
            return
        gdf = gpd.GeoDataFrame(geometry=self.include_polygon["geometry"])
        gdf.to_file(self.include_file_name, driver="GeoJSON")

    def write_exclude_polygon(self):
        if len(self.exclude_polygon) == 0:
            return
        gdf = gpd.GeoDataFrame(geometry=self.exclude_polygon["geometry"])
        gdf.to_file(self.exclude_file_name, driver="GeoJSON")

    def write_boundary_polygon(self):
        if len(self.boundary_polygon) == 0:
            return
        gdf = gpd.GeoDataFrame(geometry=self.boundary_polygon["geometry"])
        gdf.to_file(self.boundary_file_name, driver="GeoJSON")

    def plot_include_polygon(self):
        layer = app.map.layer["modelmaker_fiat"].layer["mask_include"]
        layer.clear()
        layer.add_feature(self.include_polygon)

    def plot_exclude_polygon(self):
        layer = app.map.layer["modelmaker_fiat"].layer["mask_exclude"]
        layer.clear()
        layer.add_feature(self.exclude_polygon)

    def plot_boundary_polygon(self):
        layer = app.map.layer["modelmaker_fiat"].layer["mask_boundary"]
        layer.clear()
        layer.add_feature(self.boundary_polygon)

    def read_setup_yaml(self, file_name):
        pass

    def write_setup_yaml(self):
        pass

    def generate_aoi(self):
        pass
