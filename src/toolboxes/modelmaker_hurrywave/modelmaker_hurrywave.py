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

from operations.toolbox import GenericToolbox
from ddb import ddb
from cht.bathymetry.bathymetry_database import bathymetry_database

class Toolbox(GenericToolbox):
    def __init__(self, name):
        super().__init__()

        self.name = name
        self.long_name = "Model Maker"

        # Set variables

        # Grid outline
        self.grid_outline = gpd.GeoDataFrame()

        # Bathymetry
        self.selected_bathymetry_datasets = []

        # Include polygons
        self.include_polygon = gpd.GeoDataFrame()
        # Exclude polygons
        self.exclude_polygon = gpd.GeoDataFrame()
        # Boundary polygons
        self.boundary_polygon = gpd.GeoDataFrame()

        # Set GUI variable
        group = "modelmaker_hurrywave"
        # Domain
        ddb.gui.setvar(group, "x0", 0.0)
        ddb.gui.setvar(group, "y0", 0.0)
        ddb.gui.setvar(group, "nmax", 0)
        ddb.gui.setvar(group, "mmax", 0)
        ddb.gui.setvar(group, "dx", 0.1)
        ddb.gui.setvar(group, "dy", 0.1)
        ddb.gui.setvar(group, "rotation", 0.0)

        # Bathymetry
        source_names, sources = bathymetry_database.sources()
        ddb.gui.setvar(group, "bathymetry_source_names", source_names)
        ddb.gui.setvar(group, "active_bathymetry_source", source_names[0])
        dataset_names, dataset_long_names, dataset_source_names = bathymetry_database.dataset_names(source=source_names[0])
        ddb.gui.setvar(group, "bathymetry_dataset_names", dataset_names)
        ddb.gui.setvar(group, "bathymetry_dataset_index", 0)
        ddb.gui.setvar(group, "selected_bathymetry_dataset_names", [])
        ddb.gui.setvar(group, "selected_bathymetry_dataset_index", 0)
        ddb.gui.setvar(group, "selected_bathymetry_dataset_zmin", -99999.0)
        ddb.gui.setvar(group, "selected_bathymetry_dataset_zmax", 99999.0)
        ddb.gui.setvar(group, "nr_selected_bathymetry_datasets", 0)

        # Mask
        ddb.gui.setvar(group, "global_zmax",     -2.0)
        ddb.gui.setvar(group, "global_zmin", -99999.0)
        ddb.gui.setvar(group, "include_polygon_names", [])
        ddb.gui.setvar(group, "include_polygon_index", 0)
        ddb.gui.setvar(group, "nr_include_polygons", 0)
        ddb.gui.setvar(group, "include_zmax",  99999.0)
        ddb.gui.setvar(group, "include_zmin", -99999.0)
        ddb.gui.setvar(group, "exclude_polygon_names", [])
        ddb.gui.setvar(group, "exclude_polygon_index", 0)
        ddb.gui.setvar(group, "nr_exclude_polygons", 0)
        ddb.gui.setvar(group, "exclude_zmax",  99999.0)
        ddb.gui.setvar(group, "exclude_zmin", -99999.0)
        ddb.gui.setvar(group, "boundary_polygon_names", [])
        ddb.gui.setvar(group, "boundary_polygon_index", 0)
        ddb.gui.setvar(group, "nr_boundary_polygons", 0)
        ddb.gui.setvar(group, "boundary_zmax",  99999.0)
        ddb.gui.setvar(group, "boundary_zmin", -99999.0)

    def set_layer_mode(self, mode):
        if mode == "inactive":
            # Make all layers invisible
            ddb.map.layer["modelmaker_hurrywave"].set_mode("invisible")
        if mode == "invisible":
            ddb.map.layer["modelmaker_hurrywave"].set_mode("invisible")


    # def set_gui_variables(self):
    #     # Set GUI variables
    #     group = "modelmaker_hurrywave"
    #     pass
    #     # ddb.gui.setvar(group, "x0", self.x0)
    #     # ddb.gui.setvar(group, "y0", self.y0)
    #     # ddb.gui.setvar(group, "nmax", self.nmax)
    #     # ddb.gui.setvar(group, "mmax", self.mmax)
    #     # ddb.gui.setvar(group, "dx", self.dx)
    #     # ddb.gui.setvar(group, "dy", self.dy)
    #     # ddb.gui.setvar(group, "rotation", self.rotation)
    #
    # def get_gui_variables(self):
    #     # Set GUI variables
    #     group = "modelmaker_hurrywave"
    #     pass
    #     # self.dx = ddb.gui.getvar(group, "x0")
    #     # self.dy = ddb.gui.getvar(group, "y0")
    #     # self.nmax = ddb.gui.getvar(group, "nmax")
    #     # self.mmax = ddb.gui.getvar(group, "mmax")
    #     # self.rotation = ddb.gui.getvar(group, "rotation")

    def add_layers(self):
        # Add Mapbox layers
        layer = ddb.map.add_layer("modelmaker_hurrywave")

        # Grid outline
        from .domain import grid_outline_created
        from .domain import grid_outline_modified
        layer.add_layer("grid_outline", type="draw",
                             shape="rectangle",
                             create=grid_outline_created,
                             modify=grid_outline_modified,
                             polygon_line_color="mediumblue",
                             polygon_fill_opacity=0.3)

        ### Mask
        # Include
        from .mask_active_cells import include_polygon_created
        from .mask_active_cells import include_polygon_modified
        from .mask_active_cells import include_polygon_selected
        layer.add_layer("mask_include", type="draw",
                             shape="polygon",
                             create=include_polygon_created,
                             modify=include_polygon_modified,
                             select=include_polygon_selected,
                             polygon_line_color="limegreen",
                             polygon_fill_color="limegreen",
                             polygon_fill_opacity=0.3)
        # Exclude
        from .mask_active_cells import exclude_polygon_created
        from .mask_active_cells import exclude_polygon_modified
        from .mask_active_cells import exclude_polygon_selected
        layer.add_layer("mask_exclude", type="draw",
                             shape="polygon",
                             create=exclude_polygon_created,
                             modify=exclude_polygon_modified,
                             select=exclude_polygon_selected,
                             polygon_line_color="orangered",
                             polygon_fill_color="orangered",
                             polygon_fill_opacity=0.3)
        # Boundary
        from .mask_boundary_cells import boundary_polygon_created
        from .mask_boundary_cells import boundary_polygon_modified
        from .mask_boundary_cells import boundary_polygon_selected
        layer.add_layer("mask_boundary", type="draw",
                             shape="polygon",
                             create=boundary_polygon_created,
                             modify=boundary_polygon_modified,
                             select=boundary_polygon_selected,
                             polygon_line_color="deepskyblue",
                             polygon_fill_color="deepskyblue",
                             polygon_fill_opacity=0.3)
    def generate_grid(self):
        model = ddb.model["hurrywave"].domain

        group = "modelmaker_hurrywave"
        model.input.variables.x0       = ddb.gui.getvar(group, "x0")
        model.input.variables.y0       = ddb.gui.getvar(group, "y0")
        model.input.variables.dx       = ddb.gui.getvar(group, "dx")
        model.input.variables.dy       = ddb.gui.getvar(group, "dy")
        model.input.variables.nmax     = ddb.gui.getvar(group, "nmax")
        model.input.variables.mmax     = ddb.gui.getvar(group, "mmax")
        model.input.variables.rotation = ddb.gui.getvar(group, "rotation")

        group = "hurrywave"
        ddb.gui.setvar(group, "x0", model.input.variables.x0)
        ddb.gui.setvar(group, "y0", model.input.variables.y0)
        ddb.gui.setvar(group, "dx", model.input.variables.dx)
        ddb.gui.setvar(group, "dy", model.input.variables.dy)
        ddb.gui.setvar(group, "nmax", model.input.variables.nmax)
        ddb.gui.setvar(group, "mmax", model.input.variables.mmax)
        ddb.gui.setvar(group, "rotation", model.input.variables.rotation)

        model.grid.build()

        gdf = model.grid.to_gdf()
        layer = ddb.map.layer["hurrywave"].layer["grid"]
        layer.set_data(gdf)
        # grid_layer = layer.get("grid")
        # if grid_layer:
        #     grid_layer.delete()
#        layer.add_deck_geojson_layer("hurrywave_grid", data=gdf, file_name="hurrywave_grid.geojson")

    def generate_bathymetry(self):
        bathymetry_list = ddb.toolbox["modelmaker_hurrywave"].selected_bathymetry_datasets
        ddb.model["hurrywave"].domain.bathymetry.build(bathymetry_list)
        ddb.model["hurrywave"].domain.bathymetry.write()

    def update_mask(self):
        mask = ddb.model["hurrywave"].domain.mask
        mask.build(zmin=ddb.gui.getvar("modelmaker_hurrywave", "global_zmin"),
                   zmax=ddb.gui.getvar("modelmaker_hurrywave", "global_zmax"),
                   include_polygon=ddb.toolbox["modelmaker_hurrywave"].include_polygon,
                   include_zmin=ddb.gui.getvar("modelmaker_hurrywave", "include_zmin"),
                   include_zmax=ddb.gui.getvar("modelmaker_hurrywave", "include_zmax"),
                   exclude_polygon=ddb.toolbox["modelmaker_hurrywave"].exclude_polygon,
                   exclude_zmin=ddb.gui.getvar("modelmaker_hurrywave", "exclude_zmin"),
                   exclude_zmax=ddb.gui.getvar("modelmaker_hurrywave", "exclude_zmax"),
                   boundary_polygon=ddb.toolbox["modelmaker_hurrywave"].boundary_polygon,
                   boundary_zmin=ddb.gui.getvar("modelmaker_hurrywave", "boundary_zmin"),
                   boundary_zmax=ddb.gui.getvar("modelmaker_hurrywave", "boundary_zmax")
                   )
        gdf_include = mask.to_gdf(option="include")
        layer = ddb.map.layer["hurrywave"].layer["mask_include"]
        layer.set_data(gdf_include)
        gdf_boundary = mask.to_gdf(option="boundary")
        layer = ddb.map.layer["hurrywave"].layer["mask_boundary"]
        layer.set_data(gdf_boundary)
        ddb.model["hurrywave"].domain.mask.write()
