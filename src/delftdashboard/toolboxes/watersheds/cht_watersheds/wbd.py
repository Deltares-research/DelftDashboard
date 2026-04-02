"""USGS Watershed Boundary Dataset (WBD) implementation.

Provide the WBDDataset class for reading WBD shapefiles
at various Hydrologic Unit Code (HUC) levels.
"""

import os

import geopandas as gpd
from shapely.geometry import box

from .dataset import WatershedsDataset


class WBDDataset(WatershedsDataset):
    """Watershed dataset backed by USGS WBD shapefiles."""

    def __init__(self, name: str, path: str) -> None:
        """Initialize the WBD dataset.

        Parameters
        ----------
        name : str
            Short name of the dataset.
        path : str
            Local directory path for the shapefiles.
        """
        super().__init__(name, path)
        self.level_names = [
            "WBDHU2",
            "WBDHU4",
            "WBDHU6",
            "WBDHU8",
            "WBDHU10",
            "WBDHU12",
            "WBDHU14",
            "WBDHU16",
        ]
        self.level_long_names = [
            "WBDHU2",
            "WBDHU4",
            "WBDHU6",
            "WBDHU8",
            "WBDHU10",
            "WBDHU12",
            "WBDHU14",
            "WBDHU16",
        ]

    def get_watersheds_in_bbox(
        self, xmin: float, ymin: float, xmax: float, ymax: float, layer: str
    ) -> gpd.GeoDataFrame:
        """Return WBD watersheds within the given bounding box.

        Parameters
        ----------
        xmin : float
            Minimum longitude.
        ymin : float
            Minimum latitude.
        xmax : float
            Maximum longitude.
        ymax : float
            Maximum latitude.
        layer : str
            WBD layer name (e.g. "WBDHU8").

        Returns
        -------
        gpd.GeoDataFrame
            Watersheds intersecting the bounding box.
        """
        if layer == "WBDHU2":
            hucstr = "huc2"
        elif layer == "WBDHU4":
            hucstr = "huc4"
        elif layer == "WBDHU6":
            hucstr = "huc6"
        elif layer == "WBDHU8":
            hucstr = "huc8"
        elif layer == "WBDHU10":
            hucstr = "huc10"
        elif layer == "WBDHU12":
            hucstr = "huc12"
        elif layer == "WBDHU14":
            hucstr = "huc14"
        elif layer == "WBDHU16":
            hucstr = "huc16"

        # Read the specific layer from the geodatabase
        filename = os.path.join(self.path, layer + ".shp")

        gdf = (
            gpd.read_file(filename, bbox=box(xmin, ymin, xmax, ymax))
            .rename(columns={hucstr: "id"})
            .to_crs(4326)
        )

        return gdf
