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

    :param path: Path name where model_database is stored.
    :type path: string
    """

    def __init__(self,
                 path=None):
        self.model = []
        self.path   = path
        self.read()
        self.initialized = True
       
    def read(self):
        if self.path is None:
            print("Path to model database not set!")
            return

        if not os.path.exists(self.path):
            os.makedirs(self.path)

        # Always expect this file
        tml_file = os.path.join(self.path, "model_database.tml")
        if not os.path.exists(tml_file):
            print("Error! Required model database file not found: " + tml_file)
            return

        # Load collections
        try:
            collections = toml.load(tml_file)["collection"]
        except Exception as e:
            print(f"Failed to load model_database.tml: {e}")
            return

        for d in collections:
            collection_name = d["name"]
            collection_path = d.get("path", os.path.join(self.path, collection_name))

            if not os.path.exists(collection_path):
                print(f"Collection path does not exist: {collection_path}")
                continue

            # Traverse: collection/type/model/
            for type_name in os.listdir(collection_path):
                type_path = os.path.join(collection_path, type_name)
                if not os.path.isdir(type_path):
                    continue

                for model_name in os.listdir(type_path):
                    model_path = os.path.join(type_path, model_name)
                    if not os.path.isdir(model_path):
                        continue

                    model_metadata_path = os.path.join(model_path, "model.toml")
                    if os.path.exists(model_metadata_path):
                        model_metadata = toml.load(model_metadata_path)
                        actual_model_path = model_metadata.get("path", model_path)
                    else:
                        print(f"Missing model.toml for model '{model_name}' in type '{type_name}' — skipping.")
                        continue

                    full_model_name = f"{type_name}_{model_name}"
                    model = Deltares_Model(
                        name=full_model_name,
                        path=actual_model_path,
                        type=type_name,
                        collection=collection_name
                    )
                    self.model.append(model)


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
