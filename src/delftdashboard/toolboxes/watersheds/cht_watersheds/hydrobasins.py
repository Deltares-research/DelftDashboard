# -*- coding: utf-8 -*-
"""
Created on Sun Apr 25 10:58:08 2021

@author: Maarten van Ormondt
"""

import os

import geopandas as gpd
from shapely.geometry import box

from .dataset import WatershedsDataset

class HydroBASINSDataset(WatershedsDataset):
    def __init__(self, name, path):
        super().__init__(name, path)
        self.level_names = ["lev01", "lev02", "lev03", "lev04", "lev05", "lev06", "lev07", "lev08", "lev09", "lev10", "lev11", "lev12"]
        self.level_long_names = ["Level 1", "Level 2", "Level 3", "Level 4", "Level 5", "Level 6", "Level 7", "Level 8", "Level 9", "Level 10", "Level 11", "Level 12"]

    def get_watersheds_in_bbox(self, xmin, ymin, xmax, ymax, level):

        # Read the specific layer from the geodatabase
        filename = os.path.join(self.path, f"{self.prefix}_{level}_v1c.shp")

        # Read the shapefile but only get the data within the bounding box
        gdf = gpd.read_file(filename, bbox=box(xmin, ymin, xmax, ymax)).to_crs(4326)

        # Copy column "HYBAS_ID" to "id"
        gdf["id"] = gdf["HYBAS_ID"]
        # Copy column "HYBAS_ID" to "name"
        gdf["name"] = gdf["HYBAS_ID"]
        # Convert "id" and "name" to string
        gdf["id"] = gdf["id"].astype(str)
        gdf["name"] = gdf["name"].astype(str)

        return gdf
