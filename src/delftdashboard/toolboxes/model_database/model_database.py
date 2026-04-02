"""Domain database toolbox for managing collections of pre-built model domains."""

import os

import geopandas as gpd
import pandas as pd

from delftdashboard.app import app
from delftdashboard.operations.toolbox import GenericToolbox

from .cht_modeldatabase.model_database import ModelDatabase


class Toolbox(GenericToolbox):
    """Toolbox for browsing and configuring model domains from a database.

    Parameters
    ----------
    name : str
        Short name used to register the toolbox in the application.
    """

    def __init__(self, name: str) -> None:
        super().__init__()
        self.name: str = name
        self.long_name: str = "Domain Database"
        self.gdf: gpd.GeoDataFrame = gpd.GeoDataFrame()

    def initialize(self) -> None:
        """Set up the model database, load collections, and configure GUI variables."""
        if "model_database_path" not in app.config:
            app.config["model_database_path"] = os.path.join(
                app.config["data_path"], "model_database"
            )

        app.model_database = ModelDatabase(path=app.config["model_database_path"])

        collection_names, collections_long_names = app.model_database.collections()

        if len(collection_names) == 0:
            model_names = []
            model_long_names = []
            model_source_names = []
            collection_names = [""]
            collections_long_names = [""]
        else:
            model_names, model_long_names, model_source_names = (
                app.model_database.model_names(collection=collection_names[0])
            )

        # GUI variables
        group = "model_database"
        app.gui.setvar(group, "available_collection_names", collection_names)
        if len(collections_long_names) > 0:
            app.gui.setvar(
                group, "active_available_collection_name", collection_names[0]
            )
        else:
            app.gui.setvar(group, "active_available_collection_name", "")

        app.gui.setvar(group, "selected_collection_names", [])
        app.gui.setvar(group, "active_selected_collection_name", "")

        app.gui.setvar(group, "domain_names", [])
        app.gui.setvar(group, "active_domain_name", "")

        app.gui.setvar(group, "show_sfincs", True)
        app.gui.setvar(group, "show_hurrywave", True)

        app.gui.setvar(group, "active_model_type", [])
        app.gui.setvar(group, "active_model_crs", [])

        app.gui.setvar(group, "selected_collection_toml", collection_names[0])
        app.gui.setvar(group, "flow_nested", None)
        app.gui.setvar(group, "flow_spinup_time", 24.0)
        app.gui.setvar(group, "station", None)

        app.gui.setvar(group, "make_flood_map", True)
        app.gui.setvar(group, "make_water_level_map", True)
        app.gui.setvar(group, "make_precipitation_map", True)

        model_settings = {
            "model_name": "No model selected yet",
            "long_name": None,
            "type": None,
            "crs": None,
            "flow_nested": None,
            "flow_spinup_time": None,
            "wave_spinup_time": None,
            "vertical_reference_level_name": None,
            "vertical_reference_level_difference_with_msl": None,
            "boundary_water_level_correction": None,
            "station": None,
            "make_flood_map": False,
            "make_water_level_map": False,
            "make_precipitation_map": False,
            "make_wave_map": False,
        }

        df = pd.DataFrame(list(model_settings.items()), columns=["Setting", "Value"])
        df.set_index("Setting", inplace=True)

        app.gui.setvar(group, "model_settings", df)

    def add_layers(self) -> None:
        """Register polygon-selector map layers for SFINCS and HurryWave domains."""
        from .generate_database import select_model_from_map

        layer = app.map.add_layer("model_database")

        layer.add_layer(
            "boundaries_sfincs",
            type="polygon_selector",
            hover_property="name",
            line_color="green",
            line_opacity=1.0,
            line_color_selected="red",
            line_opacity_selected=1.0,
            fill_color="green",
            fill_opacity=0.2,
            fill_color_selected="orange",
            fill_opacity_selected=0.6,
            fill_color_hover="green",
            fill_opacity_hover=0.35,
            selection_type="single",
            select=select_model_from_map,
        )

        layer.add_layer(
            "boundaries_hurrywave",
            type="polygon_selector",
            hover_property="name",
            line_color="blue",
            line_opacity=1.0,
            line_color_selected="red",
            line_opacity_selected=1.0,
            fill_color="blue",
            fill_opacity=0.2,
            fill_color_selected="orange",
            fill_opacity_selected=0.6,
            fill_color_hover="blue",
            fill_opacity_hover=0.35,
            selection_type="single",
            select=select_model_from_map,
        )

    def set_layer_mode(self, mode: str) -> None:
        """Control visibility of model database map layers.

        Parameters
        ----------
        mode : str
            One of "inactive" or "invisible".
        """
        if mode == "inactive":
            # Make all layers invisible
            app.map.layer["model_database"].hide()
        if mode == "invisible":
            # Make all layers invisible
            app.map.layer["model_database"].hide()
