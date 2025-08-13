# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

This module defines the Toolbox class for handling watersheds in Delft Dashboard.
It provides methods to initialize the toolbox, select datasets, and update boundaries on the map.

Classes:
    Toolbox: A class for handling watersheds in Delft Dashboard.

Usage:
    from delftdashboard.toolboxes.watersheds import Toolbox
"""

import os
import geopandas as gpd
import pandas as pd

from delftdashboard.operations.toolbox import GenericToolbox
from delftdashboard.app import app

# For now, we do need make a separate cht package for the watersheds. Rather, we keep it in Delft Dashboard.
from .cht_modeldatabase.model_database import ModelDatabase

class Toolbox(GenericToolbox):
    def __init__(self, name: str):
        """
        Initialize the Toolbox class.

        Parameters:
        name (str): The name of the toolbox.
        """
        super().__init__()
        self.name: str = name
        self.long_name: str = "Domain Database"
        self.gdf: gpd.GeoDataFrame = gpd.GeoDataFrame()

    def initialize(self) -> None:
        """
        Initialize the domain database toolbox.
        """
        if "model_database_path" not in app.config:
            app.config["model_database_path"] = os.path.join(app.config["data_path"], "model_database")

        # Do we plan to use model_database anywhere else? Otherwise, make it an attribute of the Toolbox class (i.e. self).
        app.model_database = ModelDatabase(path=app.config["model_database_path"])

        collection_names, collections_long_names = app.model_database.collections()

        if len(collection_names) == 0:
            # If no collections are found, set default values
            collection_names = [""]
            collections_long_names = [""]
    
        
        # GUI variables
        group = "model_database"
        app.gui.setvar(group, "available_collection_names", collection_names)
        if len(collections_long_names) > 0:
            app.gui.setvar(group, "active_available_collection_name", collection_names[0])
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
        """
        Add layers to the map for the models.
        """
        # Import select callback from .generate_database
        from .generate_database import select_model_from_map
        layer = app.map.add_layer("model_database")

        layer.add_layer("boundaries_sfincs",
                        type="polygon_selector",
                        hover_property="name",
                        line_color= "green",
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
                        select=select_model_from_map
                        )

        layer.add_layer("boundaries_hurrywave",
                        type="polygon_selector",
                        hover_property="name",
                        line_color= "blue",
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
                        select=select_model_from_map
                        )


    def set_layer_mode(self, mode: str) -> None:
        """
        Set the layer mode for the model collections 
        Parameters:
        mode (str): The mode to set the layer to ("inactive" or "invisible").
        """
        if mode == "inactive":
            # Make all layers invisible
            app.map.layer["model_database"].hide()
        if mode == "invisible":
            # Make all layers invisible
            app.map.layer["model_database"].hide()
