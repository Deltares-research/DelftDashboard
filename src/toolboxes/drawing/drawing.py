# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

from ddb_toolbox import GenericToolbox
from ddb import ddb


class Polygon:
    def __init__(self, name, gdf):
        self.name = name
        self.gdf = gdf


class Toolbox(GenericToolbox):
    def __init__(self, name):
        super().__init__()

        self.name = name
        self.long_name = "Drawing"

        # Set GUI variables
        group = "drawing"
        ddb.gui.setvar(group, "polygon_names", [])
        ddb.gui.setvar(group, "active_polygon", 0)
        ddb.gui.setvar(group, "polyline_names", [])
        ddb.gui.setvar(group, "active_polyline", 0)

        self.polygon = []
        self.polyline = []

    def plot(self):
        pass

    def draw_polygon(self):
        mp = ddb.gui.map_widget["map"]
        layer = mp.add_layer("drawing")
        draw_layer = layer.add_draw_layer("polygon",
                                          create=self.polygon_created,
                                          modify=self.polygon_modified,
                                          select=self.polygon_selected)
        draw_layer.draw_polygon()

    def polygon_created(self, gdf):
        # Polygon was added on map
        npol = len(self.polygon) + 1
        name = "polygon_" + str(npol)
        self.polygon.append(Polygon(name, gdf))
        ddb.gui.setvar("drawing", "active_polygon", npol - 1)
        geom = gdf.to_crs(3857).buffer(5000.0).to_crs(4326)
        ddb.gui.map_widget["map"].layer["drawing"].add_deck_geojson_layer("buffer01", data=geom)
        self.update()

    def polygon_modified(self, gdf):
        # Find out which polygon this was modified
        polygon, index = self.find_item_by_id(self.polygon, gdf["id"][0])
        polygon.gdf = gdf
        ddb.gui.setvar("drawing", "active_polygon", index)
        self.update()

    def polygon_selected(self, feature_id):
        # Find out which polygon this was
        polygon, index = self.find_item_by_id(self.polygon, feature_id)
        ddb.gui.setvar("drawing", "active_polygon", index)
        self.update()

    def select_polygon(self):
        # Polygon selected from list
        iac = ddb.gui.getvar("drawing", "active_polygon")
        print("Polygon selected: " + self.polygon[iac].name)
        # Activate on map
        feature_id = self.polygon[iac].gdf["id"][0]
        ddb.gui.map_widget["map"].layer["drawing"].layer["polygon"].activate_feature(feature_id)


    def delete_polygon(self):
        # npol = len(self.polygon) + 1
        # name = "polygon_" + str(npol)
        # self.polygon.append(Polygon(name, feature.id, feature.geometry))
        # ddb.gui.setvar("drawing", "active_polygon", npol)
        iac = ddb.gui.getvar("drawing", "active_polygon")
        feature_id = self.polygon[iac].gdf["id"][0]
        ddb.gui.map_widget["map"].layer["drawing"].layer["polygon"].delete_feature(feature_id)
        self.polygon.pop(iac)
        self.update()

    def update(self):
        # Update polygon names
        self.update_polygon_names()
        iac = ddb.gui.getvar("drawing", "active_polygon")
        iac = min(iac, len(self.polygon) - 1)
        ddb.gui.setvar("drawing", "active_polygon", iac)
        ddb.gui.update()

    def update_polygon_names(self):
        names = []
        for polygon in self.polygon:
            names.append(polygon.name)
        ddb.gui.setvar("drawing", "polygon_names", names)

    def find_item_by_id(self, items, id):
        for index, item in enumerate(items):
            if item.gdf["id"][0] == id:
                return item, index

# Methods that are called from the GUI

def draw_polygon():
    ddb.toolbox["drawing"].draw_polygon()


def select_polygon():
    ddb.toolbox["drawing"].select_polygon()


def delete_polygon():
    ddb.toolbox["drawing"].delete_polygon()
