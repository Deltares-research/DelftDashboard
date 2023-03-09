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

        self.set_gui_variables()

    def set_layer_mode(self, mode):
        if mode == "inactive":
            ddb.map.layer["modelmaker_sfincs"].set_mode("invisible")
        elif mode == "invisible":
            ddb.map.layer["modelmaker_sfincs"].set_mode("invisible")

    # def update_map(self, option):
    #     # Get layer
    #     layer = ddb.map.layer["modelmaker_sfincs"]
    #     if option == "deactivate":
    #         # Make the layers invisible
    #         layer.set_mode("inactive")


    def set_gui_variables(self):
        # Set GUI variables
        group = "modelmaker_sfincs"
        ddb.gui.setvar(group, "x0", self.x0)
        ddb.gui.setvar(group, "y0", self.y0)
        ddb.gui.setvar(group, "nmax", self.nmax)
        ddb.gui.setvar(group, "mmax", self.mmax)
        ddb.gui.setvar(group, "dx", self.dx)
        ddb.gui.setvar(group, "dy", self.dy)
        ddb.gui.setvar(group, "rotation", self.rotation)

    def get_gui_variables(self):
        # Set GUI variables
        group = "modelmaker_sfincs"
        self.dx = ddb.gui.setvar(group, "x0")
        self.dy = ddb.gui.setvar(group, "y0")
        self.nmax = ddb.gui.setvar(group, "nmax")
        self.mmax = ddb.gui.setvar(group, "mmax")
        self.rotation = ddb.gui.setvar(group, "rotation")

    def add_layers(self):
        # Add Mapbox layers
        layer = ddb.map.add_layer("modelmaker_sfincs")
        # Grid outline
        layer.add_layer("grid_outline", type="draw",
                             shape="rectangle",
                             create=self.grid_outline_created,
                             modify=self.grid_outline_modified,
                             polygon_line_color="mediumblue",
                             polygon_fill_opacity=0.3)

        # Quadtree refinement polygons
        layer.add_layer("quadtree_refinement", type="draw",
                             shape="polygon",
                             create=self.refinement_polygon_created,
                             modify=self.refinement_polygon_modified,
                             polygon_line_color="gold",
                             polygon_fill_color="gold",
                             polygon_fill_opacity=0.3)

        # Mask active cells
        layer.add_layer("mask_include", type="draw",
                             shape="polygon",
                             create=self.include_polygon_created,
                             modify=self.include_polygon_modified,
                             polygon_line_color="limegreen",
                             polygon_fill_color="limegreen",
                             polygon_fill_opacity=0.3)
        layer.add_layer("mask_exclude", type="draw",
                             shape="polygon",
                             create=self.exclude_polygon_created,
                             modify=self.exclude_polygon_modified,
                             polygon_line_color="orangered",
                             polygon_fill_color="orangered",
                             polygon_fill_opacity=0.3)
        # Mask boundary cells
        layer.add_layer("mask_boundary", type="draw",
                             shape="polygon",
                             create=self.boundary_polygon_created,
                             modify=self.boundary_polygon_modified,
                             polygon_line_color="deepskyblue",
                             polygon_fill_color="deepskyblue",
                             polygon_fill_opacity=0.3)

#        layer.add_deck_geojson_layer("sfincs_grid", data="./_deck.geojson")
#        layer.add_deck_geojson_layer("sfincs_grid")

    def draw_grid_outline(self):
        ddb.map.layer["modelmaker_sfincs"].layer["grid_outline"].draw()

    def grid_outline_created(self, gdf, feature_shape, feature_id):
        # Remove the old grid outline
        layer = ddb.map.layer["modelmaker_sfincs"].layer["grid_outline"]
        layer.delete_feature(self.grid_outline_id)
        self.grid_outline_id = feature_id
        self.x0       = round(gdf["x0"][0], 3)
        self.y0       = round(gdf["y0"][0], 3)
        self.lenx     = gdf["dx"][0]
        self.leny     = gdf["dy"][0]
        self.rotation = gdf["rotation"][0]*180/math.pi
        self.get_outline_geometry() # Compute nmax and mmax
        self.set_gui_variables()

    def grid_outline_modified(self, gdf, feature_shape, feature_id):
        self.x0       = round(gdf["x0"][0], 3)
        self.y0       = round(gdf["y0"][0], 3)
        self.lenx     = gdf["dx"][0]
        self.leny     = gdf["dy"][0]
        self.rotation = round(gdf["rotation"][0] * 180 / math.pi, 1)
        self.get_outline_geometry()  # Compute nmax and mmax
        self.set_gui_variables()

    def get_outline_geometry(self):
        self.nmax = np.floor(self.leny/self.dy).astype(int)
        self.mmax = np.floor(self.lenx/self.dx).astype(int)

    def generate_grid(self):
        model = ddb.model["sfincs"].domain
        model.setup_grid(self.x0,
                         self.y0,
                         self.dx,
                         self.dy,
                         self.nmax,
                         self.mmax,
                         self.rotation,
                         4326)
        gdf = grid2gdf(self.x0, self.y0, self.nmax, self.mmax, self.dx, self.dy, self.rotation)
        layer = ddb.gui.map_widget["map"].layer["modelmaker_sfincs"]
        grid_layer = layer.get("sfincs_grid")
        if grid_layer:
            grid_layer.delete()
        layer.add_deck_geojson_layer("sfincs_grid", data=gdf, file_name="sfincs_grid.geojson")

    def draw_refinement_polygon(self):
        ddb.map.layer["modelmaker_sfincs"].layer["quadtree_refinement"].draw_polygon()

    def refinement_polygon_created(self, gdf, feature_shape, feature_id):
        pass
    def refinement_polygon_modified(self, gdf, feature_shape, feature_id):
        pass
    def draw_include_polygon(self):
        ddb.map.layer["modelmaker_sfincs"].layer["mask_include"].draw_polygon()
    def include_polygon_created(self, gdf, feature_shape, feature_id):
        pass
    def include_polygon_modified(self, gdf, feature_shape, feature_id):
        pass

    def draw_exclude_polygon(self):
        ddb.map.layer["modelmaker_sfincs"].layer["mask_exclude"].draw_polygon()
    def exclude_polygon_created(self, gdf, feature_shape, feature_id):
        pass
    def exclude_polygon_modified(self, gdf, feature_shape, feature_id):
        pass

    def draw_boundary_polygon(self):
        ddb.map.layer["modelmaker_sfincs"].layer["mask_boundary"].draw_polygon()
    def boundary_polygon_created(self, gdf, feature_shape, feature_id):
        pass
    def boundary_polygon_modified(self, gdf, feature_shape, feature_id):
        pass


def grid2gdf(x0, y0, nmax, mmax, dx, dy, rotation):
    lines = []
    print("making lines")
    cosrot = math.cos(rotation*math.pi/180)
    sinrot = math.sin(rotation*math.pi/180)
    for n in range(nmax):
        for m in range(mmax):
            xa = x0 + m*dx*cosrot - n*dy*sinrot
            ya = y0 + m*dx*sinrot + n*dy*cosrot
            xb = x0 + (m + 1)*dx*cosrot - n*dy*sinrot
            yb = y0 + (m + 1)*dx*sinrot + n*dy*cosrot
            line = shapely.geometry.LineString([[xa, ya], [xb, yb]])
            lines.append(line)
            xb = x0 + m*dx*cosrot - (n + 1)*dy*sinrot
            yb = y0 + m*dx*sinrot + (n + 1)*dy*cosrot
            line = shapely.geometry.LineString([[xa, ya], [xb, yb]])
            lines.append(line)
    print("making multi line string")
    geom = shapely.geometry.MultiLineString(lines)
    print("making gdf")
    gdf = gpd.GeoDataFrame(crs='epsg:4326', geometry=[geom])
    print("done")
    return gdf
