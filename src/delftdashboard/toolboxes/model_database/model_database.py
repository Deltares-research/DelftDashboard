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
import fiona
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.ops import transform
import pyproj
from typing import List, Dict, Any, Union
import matplotlib.colors as colors
import matplotlib.cm as cm

from delftdashboard.operations.toolbox import GenericToolbox
from delftdashboard.app import app
from delftdashboard.operations import map

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
        Initialize the model toolbox.
        """
        if "model_database_path" not in app.config:
            app.config["model_database_path"] = os.path.join(app.config["data_path"], "model_database")

        app.model_database = ModelDatabase(path=app.config["model_database_path"])
        app.selected_collections = []
        app.selected_domains = []
        app.domains = []

        collection_names, collections_long_names = app.model_database.collections()
        model_names, model_long_names, model_source_names = app.model_database.model_names(collection=collection_names[0])
        
        # GUI variables
        group = "model_database"
        if len(model_names) == 0:
            raise Exception("No models found in model database")
        else:
            app.gui.setvar(group, "collection_names", collection_names)
            app.gui.setvar(group, "collection_long_names", collections_long_names)
            app.gui.setvar(group, "collection", collection_names[0])
            app.gui.setvar(group, "collection_index", 0)
            
            app.gui.setvar(group, "selected_collection_index", 0)
            app.gui.setvar(group, "selected_collection_names", [])
            app.gui.setvar(group, "selected_domain_index", 0)
            app.gui.setvar(group, "selected_domain_names", [])
            app.gui.setvar(group, "domain_index", 0)
            app.gui.setvar(group, "domain_names", [])
            app.gui.setvar(group, "domain_index_all", 0)
            app.gui.setvar(group, "domain_names_all", [])
            app.gui.setvar(group, "select_sfincs", True)
            app.gui.setvar(group, "select_hurrywave", True)

            app.gui.setvar(group, "active_model_name", [])
            app.gui.setvar(group, "active_model_long_name", [])
            app.gui.setvar(group, "active_model_type", [])  
            app.gui.setvar(group, "active_model_crs", [])

            app.gui.setvar(group, "selected_collection_toml", [])
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


            
            # app.gui.setvar(group, "level_names", app.watersheds_database.dataset[short_names[0]].level_names)
            # app.gui.setvar(group, "level_long_names", app.watersheds_database.dataset[short_names[0]].level_long_names)
            # app.gui.setvar(group, "level", app.watersheds_database.dataset[short_names[0]].level_names[0])

    def select_tab(self) -> None:
        """
        Select the domain database tab and update the map.
        """
        app.active_model.set_layer_mode("invisible")
        map.update()


    def add_layers(self) -> None:
        """
        Add layers to the map for the models.
        """
        layer = app.map.add_layer("model_database")
        layer.add_layer("boundaries",
                        type="polygon_selector",
                        hover_property="name",
                        line_color= "line_color",
                        line_opacity=1.0,
                        line_color_selected="dodgerblue",
                        line_opacity_selected=1.0,
                        fill_color="line_color",
                        fill_opacity=0.2,
                        fill_color_selected="dodgerblue",
                        fill_opacity_selected=0.6,
                        fill_color_hover="line_color",
                        fill_opacity_hover=0.35,
                        selection_type="single",
                        select=self.select_model_from_map
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



    def select_model_from_map(self, feature: Dict[str, Any], layer: Any) -> None:
        """
        Select models from the map.

        Parameters:
        features (List[Dict[str, Any]]): List of selected features.
        layer (Any): The layer from which the features were selected.
        """

        app.selected_domains = []

        domain = {"name", feature["properties"]["name"]}
        app.selected_domains.append(feature["properties"]["name"])
        app.gui.setvar("model_database", "selected_domain_names", feature["properties"]["name"])  
        app.gui.setvar("model_database", "selected_domain_index", feature["properties"]["index"])

        app.gui.window.update()

    
    def update_boundaries_on_map(self) -> None:
        """
        Update the boundaries of the models on the map.
        """

        select_sfincs = app.gui.getvar("model_database", "select_sfincs")
        select_hurrywave = app.gui.getvar("model_database", "select_hurrywave")
        selected_collection_names = app.gui.getvar("model_database", "selected_collection_names")

        all_model_names = []
        for collection in selected_collection_names:
            model_names, _, _ = app.model_database.model_names(collection=collection)
            all_model_names.extend(model_names)

        all_models = []

        for model_name in all_model_names:
            model = app.model_database.get_model(name=model_name)

            if not select_sfincs:
                # Check if the model is a SFINCS model
                if model.type == "sfincs":
                    # If it is, remove it from the list of models to be displayed
                    continue

            if not select_hurrywave:
                # Check if the model is a SFINCS model
                if model.type == "hurrywave":
                    # If it is, remove it from the list of models to be displayed
                    continue

            all_models.append(model)

        # app.gui.setvar("model_database", "selected_model_names", all_model_names)
        # app.gui.setvar("model_database", "selected_models", all_models)

        gdf_all = gpd.GeoDataFrame()
        # Waitbox
        wb = app.gui.window.dialog_wait("Loading domains...")
        for m in all_models:
            gdf = m.get_model_gdf()
            gdf["type"] = m.type  # Tag with model type
            gdf_all = pd.concat([gdf_all, gdf])

        if gdf_all.empty:
            app.map.layer["model_database"].layer["boundaries"].clear()
            wb.close()
            return
        
        else:
            gdf_all.reset_index(drop=True, inplace=True)

            # Generate unique colors by model type
            unique_types = gdf_all["type"].unique()
            cmap = cm.get_cmap('Set2', len(unique_types))
            type_to_color = {t: colors.to_hex(cmap(i)) for i, t in enumerate(unique_types)}

            # Map colors to each row
            gdf_all["line_color"] = gdf_all["type"].map(type_to_color)

            app.map.layer["model_database"].layer["boundaries"].set_data(gdf_all)
            wb.close()



def select(*args) -> None:
    app.toolbox["model_database"].select_tab()

def select_model(*args) -> None:
    app.toolbox["model_database"].select_model()

def select_selected_models(*args):
    update()

def update(*args) -> None:
    app.toolbox["model_database"].update_boundaries_on_map()