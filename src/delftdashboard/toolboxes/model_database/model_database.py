# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

This module defines the Toolbox class for handling watersheds in Delft Dashboard.
It provides methods to initialize the toolbox, select datasets, and update boundaries on the map.

Classes:
    Toolbox: A class for handling watersheds in Delft Dashboard.

Usage:
    from delftdashboard.toolboxes.watersheds import Toolbox
"""

import os
import geopandas as gpd
import fiona
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.ops import transform
import pyproj
from typing import List, Dict, Any, Union

from delftdashboard.operations.toolbox import GenericToolbox
from delftdashboard.app import app
from delftdashboard.operations import map

# For now, we do need make a separate cht package for the watersheds. Rather, we keep it in Delft Dashboard.
from .cht_modeldatabase.model_database import ModelDatabase

class Toolbox(GenericToolbox):
    def __init__(self, name: str):
        """
        Initialize the Toolbox class.

        Parameters:
        name (str): The name of the toolbox.
        """
        super().__init__()
        self.name: str = name
        self.long_name: str = "Model Database"
        self.gdf: gpd.GeoDataFrame = gpd.GeoDataFrame()

    def initialize(self) -> None:
        """
        Initialize the model toolbox.
        """
        if "model_database_path" not in app.config:
            app.config["model_database_path"] = os.path.join(app.config["data_path"], "model_database")

        app.model_database = ModelDatabase(path=app.config["model_database_path"],
                                          )
        short_names, long_names = app.model_database.dataset_names()

        # GUI variables
        group = "collections"
        if len(short_names) == 0:
            raise Exception("No datasets found in the watersheds database")
        else:
            app.gui.setvar(group, "collection_names", short_names)
            app.gui.setvar(group, "colleection_long_names", long_names)
            app.gui.setvar(group, "collection", short_names[0])
            app.gui.setvar(group, "buffer", 100.0)
            app.gui.setvar(group, "nr_selected_models", 0)
            # app.gui.setvar(group, "level_names", app.watersheds_database.dataset[short_names[0]].level_names)
            # app.gui.setvar(group, "level_long_names", app.watersheds_database.dataset[short_names[0]].level_long_names)
            # app.gui.setvar(group, "level", app.watersheds_database.dataset[short_names[0]].level_names[0])

# #     def select_tab(self) -> None:
# #         """
# #         Select the watersheds tab and update the map.
# #         """
# #         map.update()
# #         app.map.layer["watersheds"].show()
# #         app.map.layer["watersheds"].layer["boundaries"].activate()

    def set_layer_mode(self, mode: str) -> None:
        """
        Set the layer mode for the collections 
        Parameters:
        mode (str): The mode to set the layer to ("inactive" or "invisible").
        """
        if mode == "inactive":
            # Make all layers invisible
            app.map.layer["collections"].hide()
        if mode == "invisible":
            # Make all layers invisible
            app.map.layer["collections"].hide()

#     def add_layers(self) -> None:
#         """
#         Add layers to the map for the watersheds.
#         """
#         layer = app.map.add_layer("watersheds")
#         layer.add_layer("boundaries",
#                          type="polygon_selector",
#                          hover_property="name",
#                          line_color="white",
#                          line_opacity=0.5,
#                          line_color_selected="dodgerblue",
#                          line_opacity_selected=1.0,
#                          fill_color="dodgerblue",
#                          fill_opacity=0.0,
#                          fill_color_selected="dodgerblue",
#                          fill_opacity_selected=0.6,
#                          fill_color_hover="green",
#                          fill_opacity_hover=0.35,
#                          selection_type="multiple",
#                          select=self.select_watershed_from_map
#                         )

#     def select_watershed_from_map(self, features: List[Dict[str, Any]], layer: Any) -> None:
#         """
#         Select watersheds from the map.

#         Parameters:
#         features (List[Dict[str, Any]]): List of selected features.
#         layer (Any): The layer from which the features were selected.
#         """
#         indices = []
#         ids = []
#         for feature in features:
#             indices.append(feature["properties"]["index"])
#             ids.append(feature["properties"]["id"])
#         app.gui.setvar("watersheds", "selected_indices", indices)
#         app.gui.setvar("watersheds", "selected_ids", ids)    
#         app.gui.setvar("watersheds", "nr_selected_watersheds", len(indices))
#         app.gui.window.update()

#     def update_boundaries_on_map(self) -> None:
#         """
#         Update the boundaries of the watersheds on the map.
#         """
#         dataset_name = app.gui.getvar("watersheds", "dataset")
#         dataset = app.watersheds_database.dataset[dataset_name]
#         extent = app.map.map_extent
#         xmin = extent[0][0]
#         ymin = extent[0][1]
#         xmax = extent[1][0]
#         ymax = extent[1][1]
#         level = app.gui.getvar("watersheds", "level")

#         # First check if dataset files need to be downloaded
#         if not dataset.check_files():
#             rsp = app.gui.window.dialog_yes_no(f"Dataset {dataset_name} is not locally available. Do you want to try to download it? This may take several minutes.",
#                                                "Download dataset?")
#             if rsp:
#                 wb = app.gui.window.dialog_wait("Downloading watersheds ...")
#                 dataset.download()
#                 wb.close()
#             else:
#                 return
#         # Waitbox
#         wb = app.gui.window.dialog_wait("Loading watersheds ...")
#         self.gdf = dataset.get_watersheds_in_bbox(xmin, ymin, xmax, ymax, level)
#         app.map.layer["watersheds"].layer["boundaries"].set_data(self.gdf)
#         wb.close()

    # def select_collection(self) -> None:
    #     """
    #     Select a collections for the model database.
    #     """
    #     dataset_name = app.gui.getvar("models", "collection")
    #     dataset = app.watersheds_database.dataset[dataset_name]
    #     app.gui.setvar("collections", "nr_selected_models", 0)
    #     app.gui.window.update()

#     def select_level(self) -> None:
#         """
#         Select a level for the watersheds.
#         """
#         pass

#     def save(self) -> None:
#         """
#         Save the selected watersheds to a file.
#         """
#         if len(self.gdf) == 0:
#             return

#         dataset_name = app.gui.getvar("watersheds", "dataset")

#         if app.map.crs.to_epsg() != 4326:
#             crs_string = "_epsg" + str(app.map.crs.to_epsg())
#         else:
#             crs_string = ""

#         # Loop through gdf
#         names = []
#         ids = []
#         polys = []
#         for index, row in self.gdf.iterrows():
#             if row["id"] in app.gui.getvar("watersheds", "selected_ids"):
#                 ids.append(row["id"])
#                 names.append(row["name"])
#                 if row["geometry"].geom_type == "Polygon":
#                     p = Polygon(row["geometry"].exterior.coords)
#                     polys.append(p)
#                 else:
#                     # Loop through polygons in MultiPolygon
#                     for pol in row["geometry"].geoms:
#                         p = Polygon(pol.exterior.coords)
#                         polys.append(p)

#         if len(names) == 0:
#             return

#         if len(names) > 1:
#             filename = f"{dataset_name}_merged{crs_string}.geojson"
#         else:
#             filename = f"{dataset_name}_{ids[0]}{crs_string}.geojson"

#         rsp = app.gui.window.dialog_save_file("Save watersheds as ...",
#                                               file_name=filename,
#                                               filter="*.geojson",
#                                               allow_directory_change=False)
#         if rsp[0]:
#             filename = rsp[2]
#         else:
#             # User pressed cancel
#             return

#         # Merge polygons
#         merged = unary_union(polys)

#         if len(names) > 1:
#             filename_txt = os.path.splitext(filename)[0] + ".txt"
#             # Write text file with watershed names
#             with open(filename_txt, "w") as f:
#                 for index, name in enumerate(names):
#                     f.write(ids[index] + " " + name + '\n')

#         # Apply buffer
#         self.dbuf = app.gui.getvar("watersheds", "buffer") / 100000.0
#         if self.dbuf > 0.0:
#             merged = merged.buffer(self.dbuf, resolution=16)
#             merged = merged.simplify(self.dbuf)

#         # Original merged geometry is in WGS84 (because that's what the original data is in)
#         # Convert to map crs
#         gdf = gpd.GeoDataFrame(geometry=[merged]).set_crs(4326).to_crs(app.map.crs)
#         gdf.to_file(filename, driver="GeoJSON")

#     def edit_buffer(self) -> None:
#         """
#         Edit the buffer for the watersheds.
#         """
#         pass

# def select(*args) -> None:
#     app.toolbox["watersheds"].select_tab()

def select_collection(*args) -> None:
    app.toolbox["model_database"].select_dataset()

# def select_level(*args) -> None:
#     app.toolbox["watersheds"].select_level()

# def update(*args) -> None:
#     app.toolbox["watersheds"].update_boundaries_on_map()

# def save(*args) -> None:
#     app.toolbox["watersheds"].save()

# def edit_buffer(*args) -> None:
#     app.toolbox["watersheds"].edit_buffer()
