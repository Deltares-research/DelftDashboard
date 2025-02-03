# -*- coding: utf-8 -*-
"""
Created on Sun Apr 25 10:58:08 2021

@author: Maarten van Ormondt
"""

import os

import geopandas as gpd
import toml

class WatershedsDataset:
    def __init__(self, name, path):
        self.name = name
        self.long_name = name
        self.path = path
        self.gdf = gpd.GeoDataFrame()
        self.is_read = False
        self.level_names = []
        self.level_long_names = []
        self.files = []
        self.prefix = ""
        self.read_metadata()

    def read_metadata(self):
        if not os.path.exists(os.path.join(self.path, "metadata.tml")):
            print(
                "Warning! Watersheds metadata file not found: "
                + os.path.join(self.path, "metadata.tml")
            )
            return
        metadata = toml.load(os.path.join(self.path, "metadata.tml"))
        if "longname" in metadata:
            self.long_name = metadata["longname"]
        elif "long_name" in metadata:
            self.long_name = metadata["long_name"]
        if "files" in metadata:
            self.files = metadata["files"]
        if "prefix" in metadata:
            self.prefix = metadata["prefix"]    

    def get_watersheds_in_bbox(self, xmin, ymin, xmax, ymax, level):
        # Method overruled in inherited classes
        return gpd.GeoDataFrame()

