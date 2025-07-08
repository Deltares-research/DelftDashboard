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

from .model import Deltares_Model

class ModelDatabase:
    """
    The main model Database class

    :param path: Path name where model_database.toml is stored.
    :type path: string
    """

    def __init__(self,
                 path=None):
        self.model = []
        self.path   = path
        self.read()
        self.initialized = True
       
    def read(self):
        """
        Reads meta-data of all models in the database. 
        """

        if self.path is None:
            print("Path to bathymetry database not set !")
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

            if "path" in d:
                path = d["path"]
            else:
                path = os.path.join(self.path, name)

            # Read the meta data for this collection
            fname = os.path.join(path, "collection" + ".tml") # add type?

            if os.path.exists(fname):
                collection_metadata = toml.load(fname)

                for m in collection_metadata["model"]:

                    name = m["name"]
                    type = m["type"]

                    model_path = os.path.join(path, type, name)
                    model_metadata_path = os.path.join(model_path, "model.toml")
                    if os.path.exists(model_metadata_path):     
                        model_metadata = toml.load(model_metadata_path)
                        if "path" in model_metadata:
                            model_path = model_metadata["path"]
                            
                    else:
                        print("Could not find model path for " + name + " ! Skipping domain.")
                        continue

                    model = Deltares_Model(name = f"{type}_{name}", path = model_path, type = type, collection = d["name"])
                    #model.database = self    
            
                    self.model.append(model)

            else:
                print("Could not find collection file for " + name + " ! Skipping collection.")
                continue



    # def load_dataset(self, name):
    #     path = os.path.join(self.path, name)
    #     metadata = toml.load(os.path.join(path, "metadata.tml"))
    #     dataset_format = metadata["format"]
    #     if dataset_format == "netcdf_tiles_v1":
    #         dataset = BathymetryDatasetNetCDFTilesV1(name, path)
    #     elif dataset_format == "netcdf_tiles_v2":
    #         dataset = BathymetryDatasetNetCDFTilesV2(name, path)
    #     elif dataset_format == "tiled_web_map":
    #         dataset = BathymetryDatasetTiledWebMap(name, path)
    #     elif dataset_format == "cog":
    #         dataset = BathymetryDatasetCOG(name, path)
    #     dataset.database = self
    #     # Check if dataset already exists in database
    #     for d in self.dataset:
    #         if d.name == name:
    #             # Replace existing dataset
    #             d = dataset
    #             return
    #     self.dataset.append(dataset)


    def get_model(self, name):
            for model in self.model:
                if model.name == name:
                    return model
            return None

    def model_names(self, collection=None):
        short_name_list = []
        long_name_list = []
        collection_name_list = []
        for model in self.model:
            ok = False
            if collection:
                if model.collection == collection:
                    ok = True
            else:
                ok = True
            if ok:
                short_name_list.append(model.name)
                long_name_list.append(model.long_name)
                collection_name_list.append(model.collection)
        return short_name_list, long_name_list, collection_name_list

    def collections(self):

        collections = []
        collection_names = []

        for model in self.model:
            collection= model.collection
            if collection in collection_names:
                # Existing source
                for clt in collections:
                    if clt.name == collection:
                        clt.model.append(model)
            else:
                # New source
                clt = ModelCollection(collection)
                clt.model.append(model)
                collections.append(clt)
                collection_names.append(collection)

                print("No collection found, adding collection: " + collection)

        return collection_names, collections

class ModelCollection:  
    def __init__(self, name):        
        self.name    = name
        self.model = []

# def dict2yaml(file_name, dct, sort_keys=False):
#     yaml_string = yaml.dump(dct, sort_keys=sort_keys)    
#     file = open(file_name, "w")  
#     file.write(yaml_string)
#     file.close()

# def yaml2dict(file_name):
#     file = open(file_name,"r")
#     dct = yaml.load(file, Loader=yaml.FullLoader)
#     return dct
