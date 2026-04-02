"""Base class for watershed datasets.

Provide the WatershedsDataset base class with metadata reading,
file checking, and S3 download support.
"""

import os

import boto3
import geopandas as gpd
import toml
from botocore import UNSIGNED
from botocore.client import Config


class WatershedsDataset:
    """Base class for a single watershed dataset."""

    def __init__(self, name: str, path: str) -> None:
        """Initialize the dataset and read its metadata.

        Parameters
        ----------
        name : str
            Short name of the dataset.
        path : str
            Local directory path for the dataset.
        """
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

    def read_metadata(self) -> None:
        """Read dataset metadata from the local metadata.tml file."""
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

    def get_watersheds_in_bbox(
        self, xmin: float, ymin: float, xmax: float, ymax: float, level: str
    ) -> gpd.GeoDataFrame:
        """Return watersheds within the given bounding box.

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
        level : str
            Watershed level identifier.

        Returns
        -------
        gpd.GeoDataFrame
            Watersheds intersecting the bounding box.
        """
        return gpd.GeoDataFrame()

    def check_files(self) -> bool:
        """Check whether all required dataset files exist locally.

        Returns
        -------
        bool
            True if all files are present.
        """
        okay = True
        for file in self.files:
            if not os.path.exists(os.path.join(self.path, file)):
                okay = False
                break
        return okay

    def download(self) -> None:
        """Download missing dataset files from S3."""
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
