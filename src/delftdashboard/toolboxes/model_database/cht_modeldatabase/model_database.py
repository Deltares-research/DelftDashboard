# -*- coding: utf-8 -*-
"""
Created on Sun Apr 25 10:58:08 2021

@author: Maarten van Ormondt
"""

import os

import boto3
import toml
from botocore import UNSIGNED
from botocore.client import Config

class ModelDatabase:
    """
    The main model Database class

    :param path: Path name where model_database.toml is stored.
    :type path: string
    """

    def __init__(self, path=None):
        self.path = path
        self.dataset = {}
        self.read()

    def read(self):
        """
        Reads meta-data of all datasets in the database.
        """
        if self.path is None:
            print("Path to model database not set !")
            return

        # Check if the path exists. If not, create it.
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        # Read in database
        tml_file = os.path.join(self.path, "model_database.tml")
        if not os.path.exists(tml_file):
            print("Warning! Model database file not found: " + tml_file)
            return

        collections = toml.load(tml_file)

        for d in collections["collection"]:

            name = d["name"]
            self.dataset[name] = name

            if "path" in d:
                path = d["path"]
            else:
                path = os.path.join(self.path, name)

        
            # # Read the metadata file
            # metadata_file = os.path.join(path, "metadata.tml")
            # if not os.path.exists(metadata_file):
            #     print(f"Warning! Metadata file not found: {metadata_file}")
            #     continue
            # metadata = toml.load(metadata_file)


        


    def dataset_names(self):
        short_name_list = []
        long_name_list = []
        # Loop through the keys of the dictionary
        for key in self.dataset.keys():
            short_name_list.append(key)
            long_name_list.append(self.dataset[key].long_name)
        return short_name_list, long_name_list
