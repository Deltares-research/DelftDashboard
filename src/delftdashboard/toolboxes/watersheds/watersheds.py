"""Watersheds toolbox for selecting and exporting watershed boundaries."""

import os
from typing import Any, Dict, List

import geopandas as gpd
from shapely.geometry import Polygon
from shapely.ops import unary_union

from delftdashboard.app import app
from delftdashboard.operations import map
from delftdashboard.operations.toolbox import GenericToolbox

from .cht_watersheds import WatershedsDatabase


class Toolbox(GenericToolbox):
    """Toolbox for browsing, selecting, and exporting watershed boundaries.

    Parameters
    ----------
    name : str
        Short name used to register the toolbox in the application.
    """

    def __init__(self, name: str) -> None:
        super().__init__()
        self.name: str = name
        self.long_name: str = "Watersheds"
        self.gdf: gpd.GeoDataFrame = gpd.GeoDataFrame()

    def initialize(self) -> None:
        """Set up the watershed database, load datasets, and configure GUI variables."""
        if "watersheds_database_path" not in app.config:
            app.config["watersheds_database_path"] = os.path.join(
                app.config["data_path"], "watersheds"
            )
        s3_bucket = app.config["s3_bucket"]
        s3_key = "data/watersheds"
        app.watersheds_database = WatershedsDatabase(
            path=app.config["watersheds_database_path"],
            s3_bucket=s3_bucket,
            s3_key=s3_key,
            check_online=app.online,
        )

        short_names, long_names = app.watersheds_database.dataset_names()

        # GUI variables
        group = "watersheds"
        if len(short_names) == 0:
            raise Exception("No datasets found in the watersheds database")
        else:
            app.gui.setvar(group, "dataset_names", short_names)
            app.gui.setvar(group, "dataset_long_names", long_names)
            app.gui.setvar(group, "dataset", short_names[0])
            app.gui.setvar(group, "buffer", 100.0)
            app.gui.setvar(group, "nr_selected_watersheds", 0)
            app.gui.setvar(
                group,
                "level_names",
                app.watersheds_database.dataset[short_names[0]].level_names,
            )
            app.gui.setvar(
                group,
                "level_long_names",
                app.watersheds_database.dataset[short_names[0]].level_long_names,
            )
            app.gui.setvar(
                group,
                "level",
                app.watersheds_database.dataset[short_names[0]].level_names[0],
            )

    def select_tab(self) -> None:
        """Activate the watersheds tab and show boundary layers."""
        map.update()
        app.map.layer["watersheds"].show()
        app.map.layer["watersheds"].layer["boundaries"].activate()

    def set_layer_mode(self, mode: str) -> None:
        """Control visibility of watershed map layers.

        Parameters
        ----------
        mode : str
            One of "inactive" or "invisible".
        """
        if mode == "inactive":
            # Make all layers invisible
            app.map.layer["watersheds"].hide()
        if mode == "invisible":
            # Make all layers invisible
            app.map.layer["watersheds"].hide()

    def add_layers(self) -> None:
        """Register polygon selector layers on the map for watershed boundaries."""
        layer = app.map.add_layer("watersheds")
        layer.add_layer(
            "boundaries",
            type="polygon_selector",
            hover_property="name",
            line_color="white",
            line_opacity=0.5,
            line_color_selected="dodgerblue",
            line_opacity_selected=1.0,
            fill_color="dodgerblue",
            fill_opacity=0.0,
            fill_color_selected="dodgerblue",
            fill_opacity_selected=0.6,
            fill_color_hover="green",
            fill_opacity_hover=0.35,
            selection_type="multiple",
            select=self.select_watershed_from_map,
        )

    def select_watershed_from_map(
        self, features: List[Dict[str, Any]], layer: Any
    ) -> None:
        """Store selected watershed features from the map.

        Parameters
        ----------
        features : List[Dict[str, Any]]
            List of selected features with properties.
        layer : Any
            Map layer that triggered the selection.
        """
        indices = []
        ids = []
        for feature in features:
            indices.append(feature["properties"]["index"])
            ids.append(feature["properties"]["id"])
        app.gui.setvar("watersheds", "selected_indices", indices)
        app.gui.setvar("watersheds", "selected_ids", ids)
        app.gui.setvar("watersheds", "nr_selected_watersheds", len(indices))
        app.gui.window.update()

    def update_boundaries_on_map(self) -> None:
        """Load and display watershed boundaries for the current map extent."""
        dataset_name = app.gui.getvar("watersheds", "dataset")
        dataset = app.watersheds_database.dataset[dataset_name]
        extent = app.map.map_extent
        xmin = extent[0][0]
        ymin = extent[0][1]
        xmax = extent[1][0]
        ymax = extent[1][1]
        level = app.gui.getvar("watersheds", "level")

        # First check if dataset files need to be downloaded
        if not dataset.check_files():
            rsp = app.gui.window.dialog_yes_no(
                f"Dataset {dataset_name} is not locally available. Do you want to try to download it? This may take several minutes.",
                "Download dataset?",
            )
            if rsp:
                wb = app.gui.window.dialog_wait("Downloading watersheds ...")
                dataset.download()
                wb.close()
            else:
                return
        # Waitbox
        wb = app.gui.window.dialog_wait("Loading watersheds ...")
        self.gdf = dataset.get_watersheds_in_bbox(xmin, ymin, xmax, ymax, level)
        app.map.layer["watersheds"].layer["boundaries"].set_data(self.gdf)
        wb.close()

    def select_dataset(self) -> None:
        """Update available levels when the user selects a different dataset."""
        dataset_name = app.gui.getvar("watersheds", "dataset")
        dataset = app.watersheds_database.dataset[dataset_name]
        app.gui.setvar("watersheds", "level_names", dataset.level_names)
        app.gui.setvar("watersheds", "level_long_names", dataset.level_long_names)
        app.gui.setvar("watersheds", "level", dataset.level_names[0])
        app.gui.setvar("watersheds", "nr_selected_watersheds", 0)
        app.gui.window.update()

    def select_level(self) -> None:
        """Handle watershed level selection events (placeholder)."""
        pass

    def save(self) -> None:
        """Export the selected watersheds to a GeoJSON file."""
        if len(self.gdf) == 0:
            return

        dataset_name = app.gui.getvar("watersheds", "dataset")

        if app.map.crs.to_epsg() != 4326:
            crs_string = f"_epsg{app.map.crs.to_epsg()}"
        else:
            crs_string = ""

        # Loop through gdf
        names = []
        ids = []
        polys = []
        for index, row in self.gdf.iterrows():
            if row["id"] in app.gui.getvar("watersheds", "selected_ids"):
                ids.append(row["id"])
                names.append(row["name"])
                if row["geometry"].geom_type == "Polygon":
                    p = Polygon(row["geometry"].exterior.coords)
                    polys.append(p)
                else:
                    # Loop through polygons in MultiPolygon
                    for pol in row["geometry"].geoms:
                        p = Polygon(pol.exterior.coords)
                        polys.append(p)

        if len(names) == 0:
            return

        if len(names) > 1:
            filename = f"{dataset_name}_merged{crs_string}.geojson"
        else:
            filename = f"{dataset_name}_{ids[0]}{crs_string}.geojson"

        rsp = app.gui.window.dialog_save_file(
            "Save watersheds as ...",
            file_name=filename,
            filter="*.geojson",
            allow_directory_change=False,
        )
        if rsp[0]:
            filename = rsp[2]
        else:
            # User pressed cancel
            return

        # Merge polygons
        merged = unary_union(polys)

        if len(names) > 1:
            filename_txt = os.path.splitext(filename)[0] + ".txt"
            # Write text file with watershed names
            with open(filename_txt, "w") as f:
                for index, name in enumerate(names):
                    f.write(ids[index] + " " + name + "\n")

        # Apply buffer
        self.dbuf = app.gui.getvar("watersheds", "buffer") / 100000.0
        if self.dbuf > 0.0:
            merged = merged.buffer(self.dbuf, resolution=16)
            merged = merged.simplify(self.dbuf)

        # Original merged geometry is in WGS84 (because that's what the original data is in)
        # Convert to map crs
        gdf = gpd.GeoDataFrame(geometry=[merged]).set_crs(4326).to_crs(app.map.crs)
        gdf.to_file(filename, driver="GeoJSON")

    def edit_buffer(self) -> None:
        """Handle buffer distance edit events (placeholder)."""
        pass


def select(*args: Any) -> None:
    """Activate the watersheds tab."""
    app.toolbox["watersheds"].select_tab()


def select_dataset(*args: Any) -> None:
    """Handle dataset selection change."""
    app.toolbox["watersheds"].select_dataset()


def select_level(*args: Any) -> None:
    """Handle level selection change."""
    app.toolbox["watersheds"].select_level()


def update(*args: Any) -> None:
    """Update watershed boundaries on the map."""
    app.toolbox["watersheds"].update_boundaries_on_map()


def save(*args: Any) -> None:
    """Save selected watersheds to file."""
    app.toolbox["watersheds"].save()


def edit_buffer(*args: Any) -> None:
    """Handle buffer distance edit."""
    app.toolbox["watersheds"].edit_buffer()
