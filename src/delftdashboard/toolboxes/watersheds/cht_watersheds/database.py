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

from .hydrobasins import HydroBASINSDataset
from .wbd import WBDDataset

class WatershedsDatabase:
    """
    The main Watersheds Database class

    :param pth: Path name where bathymetry tiles will be cached.
    :type pth: string
    """

    def __init__(self, path=None, s3_bucket=None, s3_key=None, s3_region=None):
        self.path = path
        self.dataset = {}
        self.s3_client = None
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key
        self.s3_region = s3_region
        self.read()

    def read(self):
        """
        Reads meta-data of all datasets in the database.
        """
        if self.path is None:
            print("Path to watersheds database not set !")
            return

        # Check if the path exists. If not, create it.
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        # Read in database
        tml_file = os.path.join(self.path, "watersheds.tml")
        if not os.path.exists(tml_file):
            print("Warning! Watersheds database file not found: " + tml_file)
            return

        datasets = toml.load(tml_file)

        for d in datasets["dataset"]:

            name = d["name"]

            if "path" in d:
                path = d["path"]
            else:
                path = os.path.join(self.path, name)

            # Read the metadata file
            metadata_file = os.path.join(path, "metadata.tml")
            if not os.path.exists(metadata_file):
                print(f"Warning! Metadata file not found: {metadata_file}")
                continue
            metadata = toml.load(metadata_file)
            
            if metadata["format"] == "hydrosheds":
                self.dataset[name] = HydroBASINSDataset(name, path)
            elif metadata["format"] == "wbd":
                self.dataset[name] = WBDDataset(name, path)

    def check_online_database(self):
        if self.s3_client is None:
            self.s3_client = boto3.client(
                "s3", config=Config(signature_version=UNSIGNED)
            )
        if self.s3_bucket is None:
            return
        # First download a copy of bathymetry.tml and call it bathymetry_s3.tml
        key = f"{self.s3_key}/watersheds.tml"
        filename = os.path.join(self.path, "watersheds_s3.tml")
        print("Updating watersheds database ...")
        try:
            self.s3_client.download_file(
                Bucket=self.s3_bucket,  # assign bucket name
                Key=key,  # key is the file name
                Filename=filename,
            )  # storage file path
        except Exception:
            # Download failed
            print(
                f"Failed to download {key} from {self.s3_bucket}. Database will not be updated."
            )
            return

        # Read watersheds_s3.tml
        short_name_list, long_name_list = self.dataset_names()
        datasets_s3 = toml.load(filename)
        watersheds_added = False
        added_names = []
        # Loop through s3 datasets, and check whether they exist in the local database.
        # If so, check if the metadata also exists. If not, make local folder and download the metadata.
        # Additionally, check if available_tiles.nc in s3 and not in local database, download it.
        for d in datasets_s3["dataset"]:
            # Get list of existing datasets
            s3_name = d["name"]
            if s3_name not in short_name_list:
                # Dataset not in local database
                print(f"Adding watersheds {s3_name} to local database ...")
                # Create folder and download metadata
                path = os.path.join(self.path, s3_name)
                os.makedirs(path, exist_ok=True)
                key = f"{self.s3_key}/{s3_name}/metadata.tml"
                filename = os.path.join(path, "metadata.tml")
                # Download metadata
                try:
                    self.s3_client.download_file(
                        Bucket=self.s3_bucket,  # assign bucket name
                        Key=key,  # key is the file name
                        Filename=filename,
                    )  # storage file path
                except Exception as e:
                    print(e)
                    print(f"Failed to download {key}. Skipping watersheds dataset.")
                    continue
                # Necessary data has been downloaded
                watersheds_added = True
                added_names.append(s3_name)
        # Write new local bathymetry.tml
        if watersheds_added:
            d = {}
            d["dataset"] = []
            for name in short_name_list:
                d["dataset"].append({"name": name})
            for name in added_names:
                d["dataset"].append({"name": name})
            # Now write the new bathymetry.tml
            with open(os.path.join(self.path, "watersheds.tml"), "w") as tml:
                toml.dump(d, tml)
            # Read the database again
            self.dataset = {}
            self.read()

    def dataset_names(self):
        short_name_list = []
        long_name_list = []
        # Loop through the keys of the dictionary
        for key in self.dataset.keys():
            short_name_list.append(key)
            long_name_list.append(self.dataset[key].long_name)
        return short_name_list, long_name_list
