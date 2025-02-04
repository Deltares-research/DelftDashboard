# -*- coding: utf-8 -*-
"""
Created on Sun Apr 25 10:58:08 2021

@author: Maarten van Ormondt
"""

import os

import geopandas as gpd
from shapely.geometry import box

from .dataset import WatershedsDataset

class WBDDataset(WatershedsDataset):
    def __init__(self, name, path):
        super().__init__(name, path)
        self.level_names = ["WBDHU2", "WBDHU4", "WBDHU6", "WBDHU8", "WBDHU10", "WBDHU12", "WBDHU14", "WBDHU16"]
        self.level_long_names = ["WBDHU2", "WBDHU4", "WBDHU6", "WBDHU8", "WBDHU10", "WBDHU12", "WBDHU14", "WBDHU16"]

    def get_watersheds_in_bbox(self, xmin, ymin, xmax, ymax, layer):

        if layer=="WBDHU2":
            hucstr = "huc2"
        elif layer=="WBDHU4":
            hucstr = "huc4"
        elif layer=="WBDHU6":
            hucstr = "huc6"
        elif layer=="WBDHU8":
            hucstr = "huc8"
        elif layer=="WBDHU10":
            hucstr = "huc10"
        elif layer=="WBDHU12":
            hucstr = "huc12"
        elif layer=="WBDHU14":
            hucstr = "huc14"
        elif layer=="WBDHU16":
            hucstr = "huc16"

        # Read the specific layer from the geodatabase
        filename = os.path.join(self.path, layer + ".shp")

        gdf = gpd.read_file(filename, bbox=box(xmin, ymin, xmax, ymax)).rename(columns={hucstr: "id"}).to_crs(4326)

        return gdf
