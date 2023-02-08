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
        ddb.gui.setvar(group, "rectangle_names", [])
        ddb.gui.setvar(group, "active_rectangle", 0)

        self.polygon = []
        self.rectangle = []
        self.polyline = []

    def plot(self):
        pass

    def update_map(self, option):
        if option == "deactivate":
            pass

    def draw_polygon(self):
        mp = ddb.gui.map_widget["map"]
        layer = mp.add_layer("drawing")
        draw_layer = layer.add_draw_layer("polygon",
                                          create=self.polygon_created,
                                          modify=self.polygon_modified,
                                          select=self.polygon_selected)
        draw_layer.draw_polygon()


    def polygon_created(self, gdf, feature_shape, feature_id):
        # Polygon was added on map
        npol = len(self.polygon) + 1
        name = "polygon_" + str(npol)
        self.polygon.append(Polygon(name, gdf))
        ddb.gui.setvar("drawing", "active_polygon", npol - 1)
        #        geom = gdf.to_crs(3857).buffer(5000.0).to_crs(4326)
        #        ddb.gui.map_widget["map"].layer["drawing"].add_deck_geojson_layer("buffer01", data=geom)
        self.update()

    def polygon_modified(self, gdf, feature_shape, feature_id):
        # Find out which polygon this was modified
        polygon, index = self.find_item_by_id(self.polygon, gdf["id"][0])
        polygon.gdf = gdf
        ddb.gui.setvar("drawing", "active_polygon", index)
        self.update()

    def polygon_selected(self, feature_id):
        # Find out which polygon this was
        polygon, index = self.find_item_by_id(self.polygon, feature_id)
        if index:
            ddb.gui.setvar("drawing", "active_polygon", index)
            self.update()

    def select_polygon(self):
        # Polygon selected from list
        iac = ddb.gui.getvar("drawing", "active_polygon")
        # Activate on map
        feature_id = self.polygon[iac].gdf["id"][0]
        ddb.gui.map_widget["map"].layer["drawing"].layer["polygon"].activate_feature(feature_id)

    def delete_polygon(self):
        if self.polygon:
            iac = ddb.gui.getvar("drawing", "active_polygon")
            feature_id = self.polygon[iac].gdf["id"][0]
            ddb.gui.map_widget["map"].layer["drawing"].layer["polygon"].delete_feature(feature_id)
            self.polygon.pop(iac)
            self.update()

    def draw_rectangle(self):
        mp = ddb.gui.map_widget["map"]
        layer = mp.add_layer("drawing")
        draw_layer = layer.add_draw_layer("rectangle",
                                          create=self.rectangle_created,
                                          modify=self.rectangle_modified,
                                          select=self.rectangle_selected)
        draw_layer.draw_rectangle()

    def rectangle_created(self, gdf, feature_shape, feature_id):
        # rectangle was added on map
        nrect = len(self.rectangle) + 1
        name = "rectangle_" + str(nrect)
        self.rectangle.append(Polygon(name, gdf))
        ddb.gui.setvar("drawing", "active_rectangle", nrect - 1)
        self.update()

    def rectangle_modified(self, gdf, feature_shape, feature_id):
        # Find out which rectangle this was modified
        rectangle, index = self.find_item_by_id(self.rectangle, gdf["id"][0])
        rectangle.gdf = gdf
        ddb.gui.setvar("drawing", "active_rectangle", index)
        self.update()

    def rectangle_selected(self, feature_id):
        # # Find out which rectangle this was
        rectangle, index = self.find_item_by_id(self.rectangle, feature_id)
        if index:
            ddb.gui.setvar("drawing", "active_rectangle", index)
            self.update()


    def select_rectangle(self):
        # Polygon selected from list
        iac = ddb.gui.getvar("drawing", "active_rectangle")
        # Activate on map
        feature_id = self.rectangle[iac].gdf["id"][0]
        ddb.gui.map_widget["map"].layer["drawing"].layer["rectangle"].activate_feature(feature_id)

    def delete_rectangle(self):
        if self.rectangle:
            iac = ddb.gui.getvar("drawing", "active_rectangle")
            feature_id = self.rectangle[iac].gdf["id"][0]
            ddb.gui.map_widget["map"].layer["drawing"].layer["rectangle"].delete_feature(feature_id)
            self.rectangle.pop(iac)
            self.update()

    def draw_polyline(self):
        mp = ddb.gui.map_widget["map"]
        layer = mp.add_layer("drawing")
        draw_layer = layer.add_draw_layer("polyline",
                                          create=self.polyline_created,
                                          modify=self.polyline_modified,
                                          select=self.polyline_selected,
                                          polyline_line_width=5)
        draw_layer.draw_polyline()

    def polyline_created(self, gdf, feature_shape, feature_id):
        # polyline was added on map
        nrect = len(self.polyline) + 1
        name = "polyline_" + str(nrect)
        self.polyline.append(Polygon(name, gdf))
        ddb.gui.setvar("drawing", "active_polyline", nrect - 1)
        self.update()

    def polyline_modified(self, gdf, feature_shape, feature_id):
        # Find out which polyline this was modified
        polyline, index = self.find_item_by_id(self.polyline, gdf["id"][0])
        polyline.gdf = gdf
        ddb.gui.setvar("drawing", "active_polyline", index)
        self.update()

    def polyline_selected(self, feature_id):
        # # Find out which polyline this was
        polyline, index = self.find_item_by_id(self.polyline, feature_id)
        if index:
            ddb.gui.setvar("drawing", "active_polyline", index)
            self.update()

    def select_polyline(self):
        # Polygon selected from list
        iac = ddb.gui.getvar("drawing", "active_polyline")
        # Activate on map
        feature_id = self.polyline[iac].gdf["id"][0]
        ddb.gui.map_widget["map"].layer["drawing"].layer["polyline"].activate_feature(feature_id)

    def delete_polyline(self):
        if self.polyline:
            iac = ddb.gui.getvar("drawing", "active_polyline")
            feature_id = self.polyline[iac].gdf["id"][0]
            ddb.gui.map_widget["map"].layer["drawing"].layer["polyline"].delete_feature(feature_id)
            self.polyline.pop(iac)
            self.update()

    def update(self):
        # Update polygon names
        self.update_polygon_names()
        self.update_rectangle_names()
        self.update_polyline_names()

        iac = ddb.gui.getvar("drawing", "active_polygon")
        iac = min(iac, len(self.polygon) - 1)
        ddb.gui.setvar("drawing", "active_polygon", iac)

        iac = ddb.gui.getvar("drawing", "active_rectangle")
        iac = min(iac, len(self.rectangle) - 1)
        ddb.gui.setvar("drawing", "active_rectangle", iac)

        iac = ddb.gui.getvar("drawing", "active_polyline")
        iac = min(iac, len(self.polyline) - 1)
        ddb.gui.setvar("drawing", "active_polyline", iac)

        ddb.gui.update_tab()

    def update_polygon_names(self):
        names = []
        for polygon in self.polygon:
            names.append(polygon.name)
        ddb.gui.setvar("drawing", "polygon_names", names)

    def update_polyline_names(self):
        names = []
        for polyline in self.polyline:
            names.append(polyline.name)
        ddb.gui.setvar("drawing", "polyline_names", names)

    def update_rectangle_names(self):
        names = []
        for rectangle in self.rectangle:
            names.append(rectangle.name)
        ddb.gui.setvar("drawing", "rectangle_names", names)

    def find_item_by_id(self, items, feature_id):
        for index, item in enumerate(items):
            if item.gdf["id"][0] == feature_id:
                return item, index
        return None, None

# Methods that are called from the GUI

def draw_polygon():
    ddb.toolbox["drawing"].draw_polygon()


def select_polygon():
    ddb.toolbox["drawing"].select_polygon()


def delete_polygon():
    ddb.toolbox["drawing"].delete_polygon()


def draw_rectangle():
    ddb.toolbox["drawing"].draw_rectangle()


def select_rectangle():
    ddb.toolbox["drawing"].select_rectangle()


def delete_rectangle():
    ddb.toolbox["drawing"].delete_rectangle()

def draw_polyline():
    ddb.toolbox["drawing"].draw_polyline()


def select_polyline():
    ddb.toolbox["drawing"].select_polyline()


def delete_polyline():
    ddb.toolbox["drawing"].delete_polyline()
