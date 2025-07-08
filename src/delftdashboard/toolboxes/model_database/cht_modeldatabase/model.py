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

        # Read the specific layer from the geodatabase
        
        filename = os.path.join(self.path, "misc", f"{self.name}.geojson")
        if not os.path.exists(filename):
            print(f"File {filename} does not exist, creating file...")
            # Create a dummy GeoDataFrame
            if self.type == "sfincs":
                sfincs_model = SFINCS(os.path.join(self.path, "input"), crs = 4326)
                sfincs_model.read()
                gdf = sfincs_model.grid.exterior.to_crs(4326)
                gdf.to_file(filename, driver="GeoJSON")
                gdf["name"] = self.name
                return gdf
            
            elif self.type == "hurrywave": 
                hw_model = HurryWave(path = os.path.join(self.path, "input"), crs = 4326)
                hw_model.read()

            # 1. Load your DataArray
            mask = hw_model.grid.ds.mask
            assert 'x' in mask.coords and 'y' in mask.coords

            # 2. Convert mask to binary numpy array
            mask_array = (mask.values > 0).astype(np.uint8)

            # 3. Use a dummy transform (pixel grid space)
            transform = Affine.translation(0, 0) * Affine.scale(1, 1)

            # 4. Vectorize the binary mask in index space
            shapes_gen = shapes(mask_array, mask=mask_array, transform=transform)

            # 5. Map index-space polygons to real coordinates
            x_coords = mask.x.values
            y_coords = mask.y.values

            def pixel_to_coords(poly):
                new_coords = []
                for x, y in poly.exterior.coords:
                    i = int(np.clip(y, 0, x_coords.shape[0] - 1))
                    j = int(np.clip(x, 0, x_coords.shape[1] - 1))
                    new_coords.append((x_coords[i, j], y_coords[i, j]))
                return Polygon(new_coords)

            # 6. Generate real-world polygons
            polygons = []
            for geom, val in shapes_gen:
                if val == 1:
                    poly = shape(geom)
                    real_poly = pixel_to_coords(poly)
                    if real_poly.is_valid:
                        polygons.append(real_poly)

            # 7. Create GeoDataFrame
            region = gpd.GeoDataFrame(geometry=polygons, crs=hw_model.crs)

            # 8. Dissolve into single geometry
            gdf = region.dissolve()
            gdf["name"] = self.name

            # 9. Export to GeoJSON
            gdf.to_file(filename, driver="GeoJSON")
            
        else:
            gdf = gpd.read_file(filename).to_crs(4326)
            gdf["name"] = self.name
            return gdf
