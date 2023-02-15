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

from ddb_toolbox import GenericToolbox
from ddb import ddb
from cht.bathymetry.bathymetry_database import bathymetry_database

class Toolbox(GenericToolbox):
    def __init__(self, name):
        super().__init__()

        self.name = name
        self.long_name = "Model Maker"
        print("Toolbox " + self.name + " added!")

        # Set variables
        self.x0 = 0.0
        self.y0 = 0.0
        self.dx = 0.1
        self.dy = 0.1
        self.nmax = 0
        self.mmax = 0
        self.lenx = 0.0
        self.leny = 0.0
        self.rotation = 0.0
        self.grid_outline_id = None

        # Bathymetry
        self.selected_bathymetry_datasets = []

        # Include polygons
        self.include_polygon = gpd.GeoDataFrame()
        self.include_zmin    = -99999.0
        self.include_zmax    = 99999.0

        # Exclude polygons
        self.exclude_polygon = gpd.GeoDataFrame()
        self.include_zmin    = -99999.0
        self.include_zmax    = 99999.0

        # Boundary polygons
        self.boundary_polygon = gpd.GeoDataFrame()
        self.boundary_zmin    = -99999.0
        self.boundary_zmax    = 99999.0


        # Set GUI variable
        group = "modelmaker_hurrywave"

        # Domain
        ddb.gui.setvar(group, "x0", self.x0)
        ddb.gui.setvar(group, "y0", self.y0)
        ddb.gui.setvar(group, "nmax", self.nmax)
        ddb.gui.setvar(group, "mmax", self.mmax)
        ddb.gui.setvar(group, "dx", self.dx)
        ddb.gui.setvar(group, "dy", self.dy)
        ddb.gui.setvar(group, "rotation", self.rotation)

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
        ddb.gui.setvar(group, "global_zmax",  99999.0)
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

    def update_map(self, option):
        # Get layer
        layer = ddb.map.layer["modelmaker_hurrywave"]
        if option == "deactivate":
            # Make the layers invisible
            layer.set_mode("inactive")


    def set_gui_variables(self):
        # Set GUI variables
        group = "modelmaker_hurrywave"
        ddb.gui.setvar(group, "x0", self.x0)
        ddb.gui.setvar(group, "y0", self.y0)
        ddb.gui.setvar(group, "nmax", self.nmax)
        ddb.gui.setvar(group, "mmax", self.mmax)
        ddb.gui.setvar(group, "dx", self.dx)
        ddb.gui.setvar(group, "dy", self.dy)
        ddb.gui.setvar(group, "rotation", self.rotation)

    def get_gui_variables(self):
        # Set GUI variables
        group = "modelmaker_hurrywave"
        self.dx = ddb.gui.getvar(group, "x0")
        self.dy = ddb.gui.getvar(group, "y0")
        self.nmax = ddb.gui.getvar(group, "nmax")
        self.mmax = ddb.gui.getvar(group, "mmax")
        self.rotation = ddb.gui.getvar(group, "rotation")

    def add_layers(self):
        # Add Mapbox layers
        layer = ddb.map.add_layer("modelmaker_hurrywave")

        # Grid outline
        layer.add_draw_layer("grid_outline",
                             create=self.grid_outline_created,
                             modify=self.grid_outline_modified,
                             polygon_line_color="mediumblue",
                             polygon_fill_opacity=0.3)


        ### Mask

        # Include
        from .mask_active_cells import include_polygon_created
        from .mask_active_cells import include_polygon_modified
        from .mask_active_cells import include_polygon_selected
        layer.add_draw_layer("mask_include",
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
        layer.add_draw_layer("mask_exclude",
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
        layer.add_draw_layer("mask_boundary",
                             create=boundary_polygon_created,
                             modify=boundary_polygon_modified,
                             select=boundary_polygon_selected,
                             polygon_line_color="deepskyblue",
                             polygon_fill_color="deepskyblue",
                             polygon_fill_opacity=0.3)

    def draw_grid_outline(self):
        ddb.map.layer["modelmaker_hurrywave"].layer["grid_outline"].draw_rectangle()

    def grid_outline_created(self, gdf, feature_shape, feature_id):
        # Remove the old grid outline
        layer = ddb.map.layer["modelmaker_hurrywave"].layer["grid_outline"]
        layer.delete_feature(self.grid_outline_id)
        self.grid_outline_id = feature_id
        self.x0       = round(gdf["x0"][0], 3)
        self.y0       = round(gdf["y0"][0], 3)
        self.lenx     = gdf["dx"][0]
        self.leny     = gdf["dy"][0]
        self.rotation = gdf["rotation"][0]*180/math.pi
        self.get_outline_geometry() # Compute nmax and mmax
        self.set_gui_variables()
        ddb.gui.update()

    def grid_outline_modified(self, gdf, feature_shape, feature_id):
        self.x0       = round(gdf["x0"][0], 3)
        self.y0       = round(gdf["y0"][0], 3)
        self.lenx     = gdf["dx"][0]
        self.leny     = gdf["dy"][0]
        self.rotation = round(gdf["rotation"][0] * 180 / math.pi, 1)
        self.get_outline_geometry()  # Compute nmax and mmax
        self.set_gui_variables()
        ddb.gui.update()

    def get_outline_geometry(self):
        self.nmax = np.floor(self.leny/self.dy).astype(int)
        self.mmax = np.floor(self.lenx/self.dx).astype(int)

    def generate_grid(self):
        model = ddb.model["hurrywave"].domain
        model.grid.build(self.x0,
                         self.y0,
                         self.dx,
                         self.dy,
                         self.mmax,
                         self.nmax,
                         self.rotation,
                         ddb.crs)

        model.input.variables.x0 = self.x0
        model.input.variables.y0 = self.y0
        model.input.variables.dx = self.dx
        model.input.variables.dy = self.dy
        model.input.variables.nmax = self.nmax
        model.input.variables.mmax = self.mmax
        model.input.variables.rotation = self.rotation

        gdf = model.grid.to_gdf()
        layer = ddb.map.layer["hurrywave"]
        grid_layer = layer.get("grid")
        if grid_layer:
            grid_layer.delete()
        layer.add_deck_geojson_layer("hurrywave_grid", data=gdf, file_name="hurrywave_grid.geojson")

    # def draw_include_polygon(self):
    #     ddb.map.layer["modelmaker_hurrywave"].layer["mask_include"].draw_polygon()
    # def include_polygon_created(self, gdf, feature_shape, feature_id):
    #     pass
    # def include_polygon_modified(self, gdf, feature_shape, feature_id):
    #     pass

    # def draw_exclude_polygon(self):
    #     ddb.map.layer["modelmaker_hurrywave"].layer["mask_exclude"].draw_polygon()
    # def exclude_polygon_created(self, gdf, feature_shape, feature_id):
    #     pass
    # def exclude_polygon_modified(self, gdf, feature_shape, feature_id):
    #     pass
    #
    # def draw_boundary_polygon(self):
    #     ddb.map.layer["modelmaker_hurrywave"].layer["mask_boundary"].draw_polygon()
    # def boundary_polygon_created(self, gdf, feature_shape, feature_id):
    #     pass
    # def boundary_polygon_modified(self, gdf, feature_shape, feature_id):
    #     pass

    # def select_bathymetry_source(self):
    #     dataset_names, dataset_long_names, dataset_source_names = bathymetry_database.dataset_names(source=ddb.gui.getvar("modelmaker_hurrywave", "active_bathymetry_source"))
    #     ddb.gui.setvar("modelmaker_hurrywave", "bathymetry_dataset_names", dataset_names)
    #     ddb.gui.setvar("modelmaker_hurrywave", "active_bathymetry_dataset", dataset_names[0])
    def update_mask(self):
        pass
