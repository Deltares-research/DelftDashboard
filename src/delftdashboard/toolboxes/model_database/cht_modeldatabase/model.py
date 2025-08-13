# -*- coding: utf-8 -*-
"""
Created on Sun Apr 25 10:58:08 2021

@author: Maarten van Ormondt
"""

import os

import geopandas as gpd
from pyproj import CRS
import toml
import boto3
from botocore import UNSIGNED
from botocore.client import Config

import xarray as xr
import numpy as np
import geopandas as gpd
from rasterio.features import shapes
from shapely.geometry import shape

from shapely.geometry import Polygon

from affine import Affine


from shapely.geometry import box

from cht_sfincs.sfincs import SFINCS
from cht_hurrywave.hurrywave import HurryWave

class Model:
    """
    Bathymetry dataset class
    """

    def __init__(self):
        """
        Initialize the BathymetryDataset class.
        """
        self.database: Any = None
        self.name: str = ""
        self.long_name: str = ""
        self.collection: str = ""
        self.data_format: str = ""  # netcdftiles, geotiff, etc
        self.nr_zoom_levels: int = 0
        self.zoom_level: List[int] = []
        self.coordinate_system: List[str] = []
        self.use_cache: bool = True
        self.remote_path: str = ""
        self.path: str = ""
        self.local_path: str = ""
        self.vertical_units: str = "m"
        self.vertical_reference_level_name: str = "MSL"
        self.vertical_reference_level_difference_with_MSL: float = 0.0
        self.crs: Optional[CRS] = None

    def read_metadata(self) -> None:
        """
        Read metadata file and set attributes.

        Raises:
        FileNotFoundError: If the metadata file does not exist.
        """
        tml_file = os.path.join(self.local_path, self.name + ".tml")
        if not os.path.exists(tml_file):
            tml_file = os.path.join(self.local_path, "model.toml")
        tml = toml.load(tml_file)
        for key in tml:
            setattr(self, key, tml[key])
        # Long name for backwards compatibility
        if "long_name" in tml:
            self.long_name = tml["long_name"]
        # Make sure there is always a long_name
        if self.long_name == "":
            self.long_name = self.name

        if "coord_ref_sys_name" in tml:
            self.crs = CRS(tml["coord_ref_sys_name"])

    def get_data(self) -> None:
        """
        Placeholder method to get data from the dataset.
        """
        pass

    def get_bbox(self, **kwargs) -> None:
        """
        Placeholder method to get the bounding box of the dataset.
        """
        pass

class Deltares_Model(Model):
    """
    Bathymetry dataset class 

    :ivar name: initial value: ''
    :ivar nr_zoom_levels: initial value: 0
    """

    def __init__(self, name, path, type= None, collection=None):
        super().__init__()        
        self.name              = name
        self.path              = path
        self.collection        = collection
        self.type              = type
        self.local_path        = path
        self.use_cache         = True
        self.read_metadata()


    def get_model_gdf(self):

        # Check is geojson exists, if so copy and save in same folder with misc.geojson
    
        filename = os.path.join(self.path, "misc", f"{self.name}.geojson")
        if os.path.exists(filename):
            pass
        else:
            # Fallback to a default filename if the name is not set
            filename = os.path.join(self.path, "misc", "exterior.geojson")

        if not os.path.exists(filename):

            print(f"File {filename} does not exist, creating file...")

            # Create a dummy GeoDataFrame
            if self.type == "sfincs":

                # try:
                sfincs_model = SFINCS(os.path.join(self.path, "input"))

                # Reads sfincs.inp and attribute files
                sfincs_model.read()

                # Ideally we want to read the geojson directly and not all the gridded input for this model
                gdf = sfincs_model.grid.exterior.to_crs(4326)
                gdf.to_file(filename, driver="GeoJSON")
                gdf["name"] = self.name
                return gdf
                
                # except Exception as e:
                #     print(f"Error reading SFINCS model: {e}")
                #     gdf = gpd.GeoDataFrame(geometry=[], crs=4326)
                #     return gdf
            
            elif self.type == "hurrywave":
                try:
                    hw_model = HurryWave(path=os.path.join(self.path, "input"))
                    hw_model.read()  # Ideally we want to read the geojson directly and not all the gridded input for this model
                    # Convert to GeoDataFrame
                    gdf = hw_model.grid.data.exterior.to_crs(4326)
                    gdf.to_file(filename, driver="GeoJSON")
                    gdf["name"] = self.name
                    return gdf
                except Exception as e:
                    print(f"Error reading HurryWave model: {e}")
                    gdf = gpd.GeoDataFrame(geometry=[], crs=4326)
                    return gdf
                
        else:
            gdf = gpd.read_file(filename).to_crs(4326)
            gdf["name"] = self.name
            return gdf