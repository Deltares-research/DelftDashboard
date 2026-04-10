"""Tide stations toolbox class and GUI callbacks for browsing, predicting, and exporting tidal data."""

from __future__ import annotations

import datetime
import os
from typing import Any

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from cht_tide import TideStationsDatabase

from delftdashboard.app import app
from delftdashboard.operations import map
from delftdashboard.operations.toolbox import GenericToolbox


class Toolbox(GenericToolbox):
    """Toolbox for viewing tide stations and exporting tidal predictions."""

    def __init__(self, name: str) -> None:
        """Initialize the tide stations toolbox.

        Parameters
        ----------
        name : str
            Short name for this toolbox instance.
        """
        super().__init__()

        self.name = name
        self.long_name = "Tide Stations"

    def initialize(self) -> None:
        """Set up initial state, read the tide stations database, and register GUI variables."""
        # Set variables
        self.gdf = gpd.GeoDataFrame()

        # Read the database
        if "tide_stations_database_path" not in app.config:
            app.config["tide_stations_database_path"] = os.path.join(
                app.config["data_path"], "tide_stations"
            )
        s3_bucket = app.config["s3_bucket"]
        s3_key = "data/tide_stations"
        app.tide_stations_database = TideStationsDatabase(
            path=app.config["tide_stations_database_path"],
            s3_bucket=s3_bucket,
            s3_key=s3_key,
            check_online=app.online,
        )

        short_names, long_names = app.tide_stations_database.dataset_names()
        if len(short_names) == 0:
            short_names = [" "]
            long_names = [" "]

        app.gui.setvar("tide_stations", "dataset_long_names", long_names)
        app.gui.setvar("tide_stations", "dataset_names", short_names)
        app.gui.setvar("tide_stations", "dataset_name", short_names[0])
        app.gui.setvar("tide_stations", "active_station_index", 0)
        app.gui.setvar("tide_stations", "naming_option", "name")
        app.gui.setvar("tide_stations", "station_names", [])
        app.gui.setvar("tide_stations", "main_components", False)
        # get today's date (rounded down to 00h00)
        tnow = datetime.datetime.now()
        tstart = datetime.datetime(tnow.year, tnow.month, tnow.day)
        tend = tstart + datetime.timedelta(days=30)
        app.gui.setvar("tide_stations", "tstart", tstart)
        app.gui.setvar("tide_stations", "tend", tend)
        app.gui.setvar("tide_stations", "dt", 600.0)
        app.gui.setvar("tide_stations", "offset", 0.0)
        app.gui.setvar("tide_stations", "format", "tek")
        app.gui.setvar("tide_stations", "format_text", ["*.tek", "*.csv"])
        app.gui.setvar("tide_stations", "format_value", ["tek", "csv"])
        app.gui.setvar("tide_stations", "format", "tek")
        app.gui.setvar("tide_stations", "constituent_table", pd.DataFrame())
        app.toolbox["tide_stations"].polygon = None

    def select_tab(self) -> None:
        """Activate the tide stations tab and load dataset if needed."""
        map.update()
        app.map.layer["tide_stations"].show()
        app.map.layer["tide_stations"].layer["stations"].activate()
        app.map.layer["tide_stations"].layer["polygon"].activate()
        dataset_name = app.gui.getvar("tide_stations", "dataset_name")
        dataset = app.tide_stations_database.dataset[dataset_name]
        if not dataset.is_read:
            # First time this tab is opened
            self.select_dataset()
        self.update_constituent_table()

    def set_layer_mode(self, mode: str) -> None:
        """Set the visibility mode for tide station map layers.

        Parameters
        ----------
        mode : str
            The layer mode to apply (e.g. "inactive", "invisible").
        """
        if mode == "inactive":
            # Make all layers invisible
            app.map.layer["tide_stations"].hide()
        if mode == "invisible":
            # Make all layers invisible
            app.map.layer["tide_stations"].hide()

    def add_layers(self) -> None:
        """Add tide station and polygon map layers."""
        # Add Mapbox layers
        layer = app.map.add_layer("tide_stations")
        layer.add_layer(
            "stations",
            type="circle_selector",
            hover_property="name",
            line_color="white",
            line_color_selected="white",
            select=self.select_station_from_map,
        )
        layer.add_layer(
            "polygon", type="draw", shape="polygon", create=self.polygon_created
        )

    def polygon_created(self, gdf: gpd.GeoDataFrame, index: int, id: Any) -> None:
        """Store the drawn polygon for filtering stations.

        Parameters
        ----------
        gdf : gpd.GeoDataFrame
            GeoDataFrame containing the drawn polygon.
        index : int
            Feature index of the created polygon.
        id : Any
            Feature identifier.
        """
        app.toolbox["tide_stations"].polygon = gdf

    def select_dataset(self) -> None:
        """Load and display the selected tide station dataset."""
        dataset_name = app.gui.getvar("tide_stations", "dataset_name")
        dataset = app.tide_stations_database.dataset[dataset_name]
        # add wait message
        dlg = app.gui.window.dialog_wait("Reading tide stations dataset ...")
        dataset.get_gdf()
        self.gdf = dataset.gdf
        dlg.close()
        names, ids = dataset.station_names()
        app.gui.setvar("tide_stations", "active_station_index", 0)
        app.gui.setvar("tide_stations", "naming_option", "name")
        app.gui.setvar("tide_stations", "station_names", names)
        app.map.layer["tide_stations"].layer["stations"].set_data(self.gdf, 0)
        self.update()  # update list of stations
        self.update_constituent_table()

    def add_stations_to_model(self) -> None:
        """Add the current stations to the active model."""
        app.active_model.add_stations(
            self.gdf, naming_option=app.gui.getvar("tide_stations", "naming_option")
        )

    def select_naming_option(self) -> None:
        """Update the station list and hover property when the naming option changes."""
        self.update()
        opt = app.gui.getvar("tide_stations", "naming_option")
        index = app.gui.getvar("tide_stations", "active_station_index")
        app.map.layer["tide_stations"].layer["stations"].hover_property = opt
        app.map.layer["tide_stations"].layer["stations"].set_data(self.gdf, index)

    def select_station_from_map(self, *args: Any) -> None:
        """Handle station selection from the map.

        Parameters
        ----------
        *args : Any
            Map callback arguments; first element contains feature properties.
        """
        index = args[0]["properties"]["index"]
        app.gui.setvar("tide_stations", "active_station_index", index)
        self.update_constituent_table()
        app.gui.window.update()

    def select_station_from_list(self) -> None:
        """Handle station selection from the GUI list."""
        index = app.gui.getvar("tide_stations", "active_station_index")
        app.map.layer["tide_stations"].layer["stations"].select_by_index(index)
        self.update_constituent_table()

    def view_tide_signal(self) -> None:
        """Plot the tidal prediction for the active station."""
        station_name = app.gui.getvar("tide_stations", "station_names")[
            app.gui.getvar("tide_stations", "active_station_index")
        ]
        dataset_name = app.gui.getvar("tide_stations", "dataset_name")
        dataset = app.tide_stations_database.dataset[dataset_name]
        tstart = app.gui.getvar("tide_stations", "tstart")
        tend = app.gui.getvar("tide_stations", "tend")
        offset = app.gui.getvar("tide_stations", "offset")

        if app.gui.getvar("tide_stations", "naming_option") == "name":
            prd = dataset.predict(
                name=station_name, start=tstart, end=tend, offset=offset
            )
        else:
            prd = dataset.predict(
                id=station_name, start=tstart, end=tend, offset=offset
            )
        # If there is already a plot, add the new one to the same plot
        # Otherwise, create a new plot
        if len(plt.get_fignums()) > 0:
            # Add prd to the existing plot
            prd.plot(ax=plt.gca())
        else:
            # Create a new plot
            self.legend_list = []
            prd.plot()
        self.legend_list.append(station_name)
        plt.legend(self.legend_list)
        # Get the active figure
        fig = plt.gcf()
        fig.canvas.draw()
        fig.canvas.flush_events()
        plt.show()

    def export_tide_signal(self) -> None:
        """Export tidal predictions for active station or all stations within the polygon."""
        dataset_name = app.gui.getvar("tide_stations", "dataset_name")
        dataset = app.tide_stations_database.dataset[dataset_name]
        opt = app.gui.getvar("tide_stations", "naming_option")
        tstart = app.gui.getvar("tide_stations", "tstart")
        tend = app.gui.getvar("tide_stations", "tend")
        dt = app.gui.getvar("tide_stations", "dt")
        offset = app.gui.getvar("tide_stations", "offset")
        fmt = app.gui.getvar("tide_stations", "format")

        # Add wait message
        dlg = app.gui.window.dialog_wait("Exporting tide signal(s) ...")

        if app.toolbox["tide_stations"].polygon is None:
            # No polygon defined, so just pick active station
            station_list = [
                app.gui.getvar("tide_stations", "station_names")[
                    app.gui.getvar("tide_stations", "active_station_index")
                ]
            ]
        else:
            # Get all stations within polygon
            station_list = []
            pol = app.toolbox["tide_stations"].polygon.to_crs(epsg=4326)
            for index, row in self.gdf.iterrows():
                if pol.contains(row.geometry)[0]:
                    station_list.append(row[opt])

        for station_name in station_list:
            stname = station_name
            stname = stname.replace(" ", "_")
            # Replace all special characters by _
            stname = "".join(e if e.isalnum() else "" for e in stname)
            filename = f"{stname}.{fmt}"
            if opt == "name":
                prd = dataset.predict(
                    name=station_name,
                    start=tstart,
                    end=tend,
                    dt=dt,
                    filename=filename,
                    format=fmt,
                    offset=offset,
                )
            else:
                prd = dataset.predict(
                    id=station_name,
                    start=tstart,
                    end=tend,
                    dt=dt,
                    filename=filename,
                    format=fmt,
                    offset=offset,
                )

        dlg.close()

    def update(self) -> None:
        """Refresh the station name list in the GUI."""
        stnames = []
        opt = app.gui.getvar("tide_stations", "naming_option")
        for index, row in self.gdf.iterrows():
            stnames.append(row[opt])
        app.gui.setvar("tide_stations", "station_names", stnames)

    def update_constituent_table(self) -> None:
        """Refresh the constituent table for the active station."""
        dataset_name = app.gui.getvar("tide_stations", "dataset_name")
        opt = app.gui.getvar("tide_stations", "naming_option")
        dataset = app.tide_stations_database.dataset[dataset_name]
        station_name = app.gui.getvar("tide_stations", "station_names")[
            app.gui.getvar("tide_stations", "active_station_index")
        ]
        if opt == "name":
            tbl = dataset.get_components(name=station_name)
        else:
            tbl = dataset.get_components(id=station_name)
        app.gui.setvar("tide_stations", "constituent_table", tbl)


def select(*args: Any) -> None:
    """GUI callback to select the tide stations tab.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    app.toolbox["tide_stations"].select_tab()


def select_dataset(*args: Any) -> None:
    """GUI callback to change the active dataset.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    app.toolbox["tide_stations"].select_dataset()


def select_station(*args: Any) -> None:
    """GUI callback to select a station from the list.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    app.toolbox["tide_stations"].select_station_from_list()


def select_naming_option(*args: Any) -> None:
    """GUI callback to change the naming option.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    app.toolbox["tide_stations"].select_naming_option()


def add_stations_to_model(*args: Any) -> None:
    """GUI callback to add stations to the active model.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    app.toolbox["tide_stations"].add_stations_to_model()


def view_tide_signal(*args: Any) -> None:
    """GUI callback to view the tidal prediction plot.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    app.toolbox["tide_stations"].view_tide_signal()


def export_tide_signal(*args: Any) -> None:
    """GUI callback to export tidal predictions.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    app.toolbox["tide_stations"].export_tide_signal()


def export_tidal_components(*args: Any) -> None:
    """GUI callback to export tidal components.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    app.toolbox["tide_stations"].export_tidal_components()


def draw_polygon(*args: Any) -> None:
    """GUI callback to start drawing a polygon for station filtering.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    app.map.layer["tide_stations"].layer["polygon"].draw()


def delete_polygon(*args: Any) -> None:
    """GUI callback to delete the drawn polygon.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    app.map.layer["tide_stations"].layer["polygon"].clear()
    app.toolbox["tide_stations"].polygon = None
