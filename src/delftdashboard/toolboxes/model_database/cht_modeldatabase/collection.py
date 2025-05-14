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

class ModelCollection:
    def __init__(self, name, long_name, path):
        self.name = name
        self.long_name = long_name
        self.path = path
    

    def check_files(self):
        okay = True
        for file in self.files:
            if not os.path.exists(os.path.join(self.path, file)):
                okay = False
                break
        return okay    

    