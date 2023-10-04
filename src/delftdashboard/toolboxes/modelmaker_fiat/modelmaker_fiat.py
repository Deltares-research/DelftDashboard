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

        # Set variables

        # Grid outline
        self.grid_outline = gpd.GeoDataFrame()

        # Include polygons
        self.include_polygon = gpd.GeoDataFrame()
        self.include_file_name = "include.geojson"

        # Exclude polygons
        self.exclude_polygon = gpd.GeoDataFrame()
        self.exclude_file_name = "exclude.geojson"

        # Boundary polygons
        self.boundary_polygon = gpd.GeoDataFrame()
        self.boundary_file_name = "boundary.geojson"

        self.setup_dict = {}

        # Set GUI variable
        group = "modelmaker_fiat"

        # Domain
        app.gui.setvar(group, "x0", 0.0)
        app.gui.setvar(group, "y0", 0.0)
        app.gui.setvar(group, "nmax", 0)
        app.gui.setvar(group, "mmax", 0)
        app.gui.setvar(group, "dx", 0.1)
        app.gui.setvar(group, "dy", 0.1)
        app.gui.setvar(group, "rotation", 0.0)

    def set_layer_mode(self, mode):
        if mode == "inactive":
            # Make all layers invisible
            app.map.layer["modelmaker_fiat"].set_visibility(False)
        if mode == "invisible":
            app.map.layer["modelmaker_fiat"].set_visibility(False)

    def add_layers(self):
        # Add Mapbox layers
        layer = app.map.add_layer("modelmaker_fiat")

        # Grid outline
        from .domain import grid_outline_created
        from .domain import grid_outline_modified

        layer.add_layer(
            "grid_outline",
            type="draw",
            shape="rectangle",
            create=grid_outline_created,
            modify=grid_outline_modified,
            polygon_line_color="mediumblue",
            polygon_fill_opacity=0.3,
            rotate=True,
        )

    def generate_grid(self):
        dlg = app.gui.window.dialog_wait("Generating grid ...")

        model = app.model["fiat"].domain

        group = "modelmaker_fiat"
        model.input.variables.x0 = app.gui.getvar(group, "x0")
        model.input.variables.y0 = app.gui.getvar(group, "y0")
        model.input.variables.dx = app.gui.getvar(group, "dx")
        model.input.variables.dy = app.gui.getvar(group, "dy")
        model.input.variables.nmax = app.gui.getvar(group, "nmax")
        model.input.variables.mmax = app.gui.getvar(group, "mmax")
        model.input.variables.rotation = app.gui.getvar(group, "rotation")

        group = "fiat"
        app.gui.setvar(group, "x0", model.input.variables.x0)
        app.gui.setvar(group, "y0", model.input.variables.y0)
        app.gui.setvar(group, "dx", model.input.variables.dx)
        app.gui.setvar(group, "dy", model.input.variables.dy)
        app.gui.setvar(group, "nmax", model.input.variables.nmax)
        app.gui.setvar(group, "mmax", model.input.variables.mmax)
        app.gui.setvar(group, "rotation", model.input.variables.rotation)

        model.grid.build()

        app.map.layer["fiat"].layer["grid"].set_data(
            model.grid,
            xlim=[app.gui.getvar(group, "x0"), app.gui.getvar(group, "x0")],
            ylim=[app.gui.getvar(group, "y0"), app.gui.getvar(group, "y0")],
        )

        dlg.close()

    def update_mask(self):
        dlg = app.gui.window.dialog_wait("Updating mask ...")

        grid = app.model["fiat"].domain.grid
        grid.build_mask(
            zmin=app.gui.getvar("modelmaker_fiat", "global_zmin"),
            zmax=app.gui.getvar("modelmaker_fiat", "global_zmax"),
            include_polygon=app.toolbox["modelmaker_fiat"].include_polygon,
            include_zmin=app.gui.getvar("modelmaker_fiat", "include_zmin"),
            include_zmax=app.gui.getvar("modelmaker_fiat", "include_zmax"),
            exclude_polygon=app.toolbox["modelmaker_fiat"].exclude_polygon,
            exclude_zmin=app.gui.getvar("modelmaker_fiat", "exclude_zmin"),
            exclude_zmax=app.gui.getvar("modelmaker_fiat", "exclude_zmax"),
            boundary_polygon=app.toolbox["modelmaker_fiat"].boundary_polygon,
            boundary_zmin=app.gui.getvar("modelmaker_fiat", "boundary_zmin"),
            boundary_zmax=app.gui.getvar("modelmaker_fiat", "boundary_zmax"),
        )
        app.map.layer["fiat"].layer["mask_include"].set_data(
            grid.mask_to_gdf(option="include")
        )
        app.map.layer["fiat"].layer["mask_boundary"].set_data(
            grid.mask_to_gdf(option="boundary")
        )
        if not app.model["fiat"].domain.input.variables.mskfile:
            app.model["fiat"].domain.input.variables.mskfile = "fiat.msk"
        grid.write_msk_file()
        # GUI variables
        app.gui.setvar(
            "fiat", "mskfile", app.model["fiat"].domain.input.variables.mskfile
        )

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

        # app.toolbox["modelmaker_fiat"].write_include_polygon()
        # app.toolbox["modelmaker_fiat"].write_exclude_polygon()
        # app.toolbox["modelmaker_fiat"].write_boundary_polygon()

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
        dct = yaml2dict(file_name)
        self.setup_dict = dct

        group = "modelmaker_fiat"
        # Coordinates
        app.gui.setvar(group, "x0", dct["coordinates"]["x0"])
        app.gui.setvar(group, "y0", dct["coordinates"]["y0"])
        app.gui.setvar(group, "dx", dct["coordinates"]["dx"])
        app.gui.setvar(group, "dy", dct["coordinates"]["dy"])
        app.gui.setvar(group, "nmax", dct["coordinates"]["nmax"])
        app.gui.setvar(group, "mmax", dct["coordinates"]["mmax"])
        app.gui.setvar(group, "rotation", dct["coordinates"]["rotation"])
        app.model["fiat"].domain.crs = CRS(dct["coordinates"]["crs"])
        # Mask
        app.gui.setvar(group, "global_zmin", dct["mask"]["zmin"])
        app.gui.setvar(group, "global_zmax", dct["mask"]["zmax"])

        if len(dct["mask"]["include_polygon"]) > 0:
            self.include_file_name = dct["mask"]["include_polygon"][0]["file_name"]
            app.gui.setvar(
                group, "include_zmin", dct["mask"]["include_polygon"][0]["zmin"]
            )
            app.gui.setvar(
                group, "include_zmax", dct["mask"]["include_polygon"][0]["zmax"]
            )
            # Now read in polygons from geojson file (or other file)
            self.read_include_polygon()
            self.plot_include_polygon()
        else:
            self.include_polygon = gpd.GeoDataFrame()

        if len(dct["mask"]["exclude_polygon"]) > 0:
            self.exclude_file_name = dct["mask"]["exclude_polygon"][0]["file_name"]
            app.gui.setvar(
                group, "exclude_zmin", dct["mask"]["exclude_polygon"][0]["zmin"]
            )
            app.gui.setvar(
                group, "exclude_zmax", dct["mask"]["exclude_polygon"][0]["zmax"]
            )
            # Now read in polygons from geojson file (or other file)
            self.read_exclude_polygon()
            self.plot_exclude_polygon()
        else:
            self.exclude_polygon = gpd.GeoDataFrame()

        if len(dct["mask"]["open_boundary_polygon"]) > 0:
            self.boundary_file_name = dct["mask"]["open_boundary_polygon"][0][
                "file_name"
            ]
            app.gui.setvar(
                group, "boundary_zmin", dct["mask"]["open_boundary_polygon"][0]["zmin"]
            )
            app.gui.setvar(
                group, "boundary_zmax", dct["mask"]["open_boundary_polygon"][0]["zmax"]
            )
            # Now read in polygons from geojson file (or other file)
            self.read_boundary_polygon()
            self.plot_boundary_polygon()
        else:
            self.boundary_polygon = gpd.GeoDataFrame()

        self.update_polygons()

        layer = app.map.layer["modelmaker_fiat"].layer["grid_outline"]
        lenx = dct["coordinates"]["mmax"] * dct["coordinates"]["dx"]
        leny = dct["coordinates"]["nmax"] * dct["coordinates"]["dy"]
        layer.add_rectangle(
            dct["coordinates"]["x0"],
            dct["coordinates"]["y0"],
            lenx,
            leny,
            dct["coordinates"]["rotation"],
        )

    def write_setup_yaml(self):
        group = "modelmaker_fiat"
        dct = {}
        # Coordinates
        dct["coordinates"] = {}
        dct["coordinates"]["x0"] = float(app.gui.getvar(group, "x0"))
        dct["coordinates"]["y0"] = float(app.gui.getvar(group, "y0"))
        dct["coordinates"]["dx"] = float(app.gui.getvar(group, "dx"))
        dct["coordinates"]["dy"] = float(app.gui.getvar(group, "dy"))
        dct["coordinates"]["nmax"] = int(app.gui.getvar(group, "nmax"))
        dct["coordinates"]["mmax"] = int(app.gui.getvar(group, "mmax"))
        dct["coordinates"]["rotation"] = float(app.gui.getvar(group, "rotation"))
        dct["coordinates"]["crs"] = app.model["fiat"].domain.crs.name
        # Mask
        dct["mask"] = {}
        dct["mask"]["zmin"] = app.gui.getvar(group, "global_zmin")
        dct["mask"]["zmax"] = app.gui.getvar(group, "global_zmax")
        dct["mask"]["include_polygon"] = []
        if len(app.toolbox["modelmaker_fiat"].include_polygon) > 0:
            pol = {}
            pol["file_name"] = self.include_file_name
            pol["zmin"] = app.gui.getvar("modelmaker_fiat", "include_zmin")
            pol["zmax"] = app.gui.getvar("modelmaker_fiat", "include_zmax")
            dct["mask"]["include_polygon"].append(pol)
        dct["mask"]["exclude_polygon"] = []
        if len(app.toolbox["modelmaker_fiat"].exclude_polygon) > 0:
            pol = {}
            pol["file_name"] = self.exclude_file_name
            pol["zmin"] = app.gui.getvar("modelmaker_fiat", "exclude_zmin")
            pol["zmax"] = app.gui.getvar("modelmaker_fiat", "exclude_zmax")
            dct["mask"]["exclude_polygon"].append(pol)
        dct["mask"]["open_boundary_polygon"] = []
        if len(app.toolbox["modelmaker_fiat"].boundary_polygon) > 0:
            pol = {}
            pol["file_name"] = self.boundary_file_name
            pol["zmin"] = app.gui.getvar("modelmaker_fiat", "boundary_zmin")
            pol["zmax"] = app.gui.getvar("modelmaker_fiat", "boundary_zmax")
            dct["mask"]["open_boundary_polygon"].append(pol)

        self.setup_dict = dct

        dict2yaml("model_setup.yml", dct)
