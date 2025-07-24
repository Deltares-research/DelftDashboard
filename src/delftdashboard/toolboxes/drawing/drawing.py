# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
import geopandas as gpd

from delftdashboard.operations.toolbox import GenericToolbox
from delftdashboard.app import app

class Toolbox(GenericToolbox):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.long_name = "Drawing"

    def initialize(self):

        # Set GUI variables
        group = "drawing"
        app.gui.setvar(group, "nr_polygons", 0)
        app.gui.setvar(group, "polygon_names", [])
        app.gui.setvar(group, "active_polygon", 0)
        app.gui.setvar(group, "polygon_buffer_distance", 0.0)
        app.gui.setvar(group, "polygon_simplify_distance", 0.0)

        app.gui.setvar(group, "nr_polylines", 0)
        app.gui.setvar(group, "polyline_names", [])
        app.gui.setvar(group, "active_polyline", 0)
        app.gui.setvar(group, "polyline_buffer_distance", 0.0)
        app.gui.setvar(group, "polyline_simplify_distance", 0.0)

        self.polygon = gpd.GeoDataFrame()
        self.polyline = gpd.GeoDataFrame()

        self.polygon_file_name = "polygon.geojson"
        self.polyline_file_name = "polyline.geojson"

    def add_layers(self):
        # Add Mapbox layers
        layer = app.map.add_layer("drawing")
        from .polygon import polygon_created
        from .polygon import polygon_modified
        from .polygon import polygon_selected
        layer.add_layer("polygon",
                        type="draw",
                        shape="polygon",
                        create=polygon_created,
                        modify=polygon_modified,
                        select=polygon_selected)
        layer.add_layer("polygon_tmp",
                        type="polygon",
                        line_color="white",
                        line_style="--")
        from .polyline import polyline_created
        from .polyline import polyline_modified
        from .polyline import polyline_selected
        layer.add_layer("polyline",
                        type="draw",
                        shape="polyline",
                        create=polyline_created,
                        modify=polyline_modified,
                        select=polyline_selected)
        layer.add_layer("polyline_tmp",
                        type="polygon",
                        line_color="white",
                        line_style="--")

    def plot(self):
        pass

    def set_layer_mode(self, mode):
        if mode == "inactive":
            app.map.layer["drawing"].hide()
            app.map.layer["drawing"].layer["polygon"].hide()
            app.map.layer["drawing"].layer["polygon_tmp"].hide()
            app.map.layer["drawing"].layer["polyline"].hide()
            app.map.layer["drawing"].layer["polyline_tmp"].hide()
        elif mode == "invisible":
            app.map.layer["drawing"].hide()
            app.map.layer["drawing"].layer["polygon"].hide()
            app.map.layer["drawing"].layer["polygon_tmp"].hide()
            app.map.layer["drawing"].layer["polyline"].hide()
            app.map.layer["drawing"].layer["polyline_tmp"].hide()
        else:
            app.map.layer["drawing"].show()
