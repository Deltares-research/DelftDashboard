"""Observation stations toolbox class and GUI callbacks for browsing and adding stations."""

from __future__ import annotations

from typing import Any

import geopandas as gpd

from delftdashboard.app import app
from delftdashboard.operations import map
from delftdashboard.operations.toolbox import GenericToolbox


class Toolbox(GenericToolbox):
    """Toolbox for viewing observation stations and adding them to the active model."""

    def __init__(self, name: str) -> None:
        """Initialize the observation stations toolbox.

        Parameters
        ----------
        name : str
            Short name for this toolbox instance.
        """
        super().__init__()

        self.name = name
        self.long_name = "Observation Stations"

    def initialize(self) -> None:
        """Set up initial state and GUI variables."""
        # Set variables
        self.gdf = gpd.GeoDataFrame()

    def select_tab(self) -> None:
        """Activate the observation stations tab and refresh the map layer."""
        map.update()
        app.map.layer["observation_stations"].layer["stations"].activate()
        opt = app.gui.getvar("observation_stations", "naming_option")
        index = app.gui.getvar("observation_stations", "active_station_index")
        app.map.layer["observation_stations"].layer["stations"].set_data(
            self.gdf, index
        )
        self.update()

    def set_layer_mode(self, mode: str) -> None:
        """Set the visibility mode for observation station map layers.

        Parameters
        ----------
        mode : str
            The layer mode to apply (e.g. "inactive", "invisible").
        """
        if mode == "inactive":
            # Make all layers invisible
            app.map.layer["observation_stations"].hide()
        if mode == "invisible":
            # Make all layers invisible
            app.map.layer["observation_stations"].hide()

    def add_layers(self) -> None:
        """Add observation station map layers."""
        # Add Mapbox layers
        layer = app.map.add_layer("observation_stations")
        layer.add_layer(
            "stations",
            type="circle_selector",
            line_color="white",
            line_color_selected="white",
            select=self.select_station_from_map,
        )

    def add_stations_to_model(self) -> None:
        """Add the current stations to the active model."""
        app.active_model.add_stations(
            self.gdf,
            naming_option=app.gui.getvar("observation_stations", "naming_option"),
        )

    def select_naming_option(self) -> None:
        """Update the station list and hover property when the naming option changes."""
        self.update()
        opt = app.gui.getvar("observation_stations", "naming_option")
        index = app.gui.getvar("observation_stations", "active_station_index")
        app.map.layer["observation_stations"].layer["stations"].hover_property = opt
        app.map.layer["observation_stations"].layer["stations"].set_data(
            self.gdf, index
        )

    def select_station_from_map(self, *args: Any) -> None:
        """Handle station selection from the map.

        Parameters
        ----------
        *args : Any
            Map callback arguments; first element contains feature properties.
        """
        index = args[0]["properties"]["index"]
        app.gui.setvar("observation_stations", "active_station_index", index)
        app.gui.window.update()

    def select_station_from_list(self) -> None:
        """Handle station selection from the GUI list."""
        index = app.gui.getvar("observation_stations", "active_station_index")
        app.map.layer["observation_stations"].layer["stations"].select_by_index(index)

    def update(self) -> None:
        """Refresh the station name list in the GUI."""
        stnames = []
        opt = app.gui.getvar("observation_stations", "naming_option")
        for index, row in self.gdf.iterrows():
            stnames.append(row[opt])
        app.gui.setvar("observation_stations", "station_names", stnames)


#
def select(*args: Any) -> None:
    """GUI callback to select the observation stations tab.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    app.toolbox["observation_stations"].select_tab()


def select_station(*args: Any) -> None:
    """GUI callback to select a station from the list.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    app.toolbox["observation_stations"].select_station_from_list()


def select_naming_option(*args: Any) -> None:
    """GUI callback to change the naming option.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    app.toolbox["observation_stations"].select_naming_option()


def add_stations_to_model(*args: Any) -> None:
    """GUI callback to add stations to the active model.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    app.toolbox["observation_stations"].add_stations_to_model()
