# -*- coding: utf-8 -*-
"""
Created on Sun Apr 25 10:58:08 2021

@author: Maarten van Ormondt
"""

import os

import geopandas as gpd
import toml
import boto3
from botocore import UNSIGNED
from botocore.client import Config

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
        self.s3_bucket = None
        self.s3_key = None
        self.s3_region = None
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
        if "s3_bucket" in metadata:
            self.s3_bucket = metadata["s3_bucket"]
        if "s3_key" in metadata:
            self.s3_key = metadata["s3_key"]
        if "s3_region" in metadata:
            self.s3_region = metadata["s3_region"]    

    def get_watersheds_in_bbox(self, xmin, ymin, xmax, ymax, level):
        # Method overruled in inherited classes
        return gpd.GeoDataFrame()

    def check_files(self):
        okay = True
        for file in self.files:
            if not os.path.exists(os.path.join(self.path, file)):
                okay = False
                break
        return okay    

    def download(self):
        if self.s3_bucket is None:
            return
        # Check if download is needed
        for file in self.files:
            if not os.path.exists(os.path.join(self.path, file)):
                s3_client = boto3.client(
                    "s3", config=Config(signature_version=UNSIGNED)
                )
                break
        # Get all files defined in the toml file
        for file in self.files:
            if not os.path.exists(os.path.join(self.path, file)):
                print(f"Downloading {file} from tide model {self.name} ...")
                s3_client.download_file(
                    self.s3_bucket,
                    f"{self.s3_key}/{file}",
                    os.path.join(self.path, file),
                )
