# -*- coding: utf-8 -*-
"""
Created on Sun Apr 25 10:58:08 2021

@author: Maarten van Ormondt
"""

import os
import shutil
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

        # Create a default model.tml file if it does not exist. Why do we actually need this file?
        # model_tml_path = os.path.join(self.path, "model_database.tml")

        # Check if collections are present in the model_database_path
        collections = []
        for entry in os.listdir(self.path):
            entry_path = os.path.join(self.path, entry)
            if os.path.isdir(entry_path):
                # Try to get long_name from a metadata file, else use entry as long_name
                long_name = entry.replace("_", " ").title()
                collections.append({"name": entry, "long_name": long_name})
            
        # If collection list is empty, print warning
        if not collections:
            print("Warning! No collections found in model database.")
            return

        else:
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

                        full_model_name = f"{model_name}"

                        # For now only HW and SFINCS models are supported
                        if type_name not in ["sfincs", "hurrywave"]:
                            continue

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
            collection = model.collection
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

                # print("No collection found, adding collection: " + collection)

        return collection_names, collections

    def add_collection(self, name, long_name=None):
        """
        Add a new collection to the model database.
        """
        if long_name is None:
            long_name = name.replace("_", " ").title()

        collection_path = os.path.join(self.path, name)
        if not os.path.exists(collection_path):
            os.makedirs(collection_path)

        # # Add to model_database.tml
        # tml_file = os.path.join(self.path, "model_database.tml")
        # with open(tml_file, "a") as f:
        #     f.write(f'\n[[collection]]\nname = "{name}"\nlong_name = "{long_name}"\npath = "{collection_path}"\n')

        print(f"Collection '{name}' added to model database.")

    def copy_model_input_files(self, domain_name, to_path):
        """
        Copy input files from the domain's input folder to the current working directory or a specified path.
        """

        # Ensure the destination path exists
        if not os.path.exists(to_path):
            os.makedirs(to_path)

        # Get the domain from the model database
        domain = self.get_model(name=domain_name)

        # Get domain path robustly
        domain_path = getattr(domain, 'path', None)
        if not domain_path or not isinstance(domain_path, str):
            print(f"Invalid or missing domain path for domain: {domain_name}")
            return
        domain_input_folder = os.path.join(domain_path, "input")
        
        # Copy all input files from the domain input folder to the current working directory
        # We do not want to overwrite existing files in the model database!
        for item in os.listdir(domain_input_folder):
            src = os.path.join(domain_input_folder, item)
            dst = os.path.join(os.getcwd(), item)
            if os.path.isfile(src):
                shutil.copy2(src, dst)
            elif os.path.isdir(src):
                # If it's a directory, copy recursively
                if not os.path.exists(dst):
                    os.makedirs(dst)
                for sub_item in os.listdir(src):
                    sub_src = os.path.join(src, sub_item)
                    sub_dst = os.path.join(dst, sub_item)
                    if os.path.isfile(sub_src):
                        shutil.copy2(sub_src, sub_dst)

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
