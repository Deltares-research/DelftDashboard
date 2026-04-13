"""Observation stations toolbox: browse, view, export, and add stations to a model."""

from __future__ import annotations

import datetime
from typing import Any

import geopandas as gpd
import matplotlib.pyplot as plt

from cht_observations.observation_stations import source

from delftdashboard.app import app
from delftdashboard.operations import map
from delftdashboard.operations.toolbox import GenericToolbox


# Providers exposed in the GUI. Online + no-auth only — the bulk/auth
# providers (gesla, grdc, copernicus) can still be used from code.
_PROVIDERS: list[tuple[str, str]] = [
    ("noaa_coops", "NOAA CO-OPS"),
    ("ndbc", "NOAA NDBC"),
    ("ioc", "IOC Sea Level"),
    ("usgs", "USGS NWIS"),
    ("waterinfo", "Rijkswaterstaat"),
    ("emodnet", "EMODnet Physics"),
]

# Default parameter codes per provider.
_DEFAULT_PARAM: dict[str, str] = {
    "noaa_coops": "water_level",
    "ndbc": "wvht",
    "ioc": "water_level",
    "usgs": "00060",
    "waterinfo": "WATHTE",
    "emodnet": "SLEV",
}


class Toolbox(GenericToolbox):
    """Toolbox for browsing observation stations from multiple providers."""

    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name
        self.long_name = "Observation Stations"

    def initialize(self) -> None:
        """Register GUI defaults."""
        self.gdf = gpd.GeoDataFrame()
        self.polygon = None
        self.source = None
        self.legend_list: list[str] = []

        group = "observation_stations"
        short_names = [p[0] for p in _PROVIDERS]
        long_names = [p[1] for p in _PROVIDERS]
        app.gui.setvar(group, "provider_names", short_names)
        app.gui.setvar(group, "provider_long_names", long_names)
        app.gui.setvar(group, "provider_name", short_names[0])

        app.gui.setvar(group, "station_names", [])
        app.gui.setvar(group, "active_station_index", 0)
        app.gui.setvar(group, "naming_option", "name")

        tnow = datetime.datetime.now()
        tstart = datetime.datetime(tnow.year, tnow.month, tnow.day) - datetime.timedelta(days=7)
        tend = datetime.datetime(tnow.year, tnow.month, tnow.day)
        app.gui.setvar(group, "tstart", tstart)
        app.gui.setvar(group, "tend", tend)
        app.gui.setvar(group, "parameter", _DEFAULT_PARAM[short_names[0]])
        app.gui.setvar(group, "format_text", ["*.csv", "*.tek"])
        app.gui.setvar(group, "format_value", ["csv", "tek"])
        app.gui.setvar(group, "format", "csv")

    def add_layers(self) -> None:
        layer = app.map.add_layer("observation_stations")
        layer.add_layer(
            "stations",
            type="circle_selector",
            hover_property="name",
            line_color="white",
            line_color_selected="white",
            select=self.select_station_from_map,
        )
        layer.add_layer(
            "polygon",
            type="draw",
            shape="polygon",
            create=self.polygon_created,
        )

    def set_layer_mode(self, mode: str) -> None:
        if mode in ("inactive", "invisible"):
            app.map.layer["observation_stations"].hide()

    def select_tab(self) -> None:
        map.update()
        app.map.layer["observation_stations"].show()
        app.map.layer["observation_stations"].layer["stations"].activate()
        app.map.layer["observation_stations"].layer["polygon"].activate()
        if self.source is None:
            self.select_provider()

    # ------------------------------------------------------------------
    # Providers
    # ------------------------------------------------------------------

    def select_provider(self) -> None:
        """(Re)load the station list from the selected provider."""
        name = app.gui.getvar("observation_stations", "provider_name")
        app.gui.setvar("observation_stations", "parameter", _DEFAULT_PARAM.get(name, ""))

        dlg = app.gui.window.dialog_wait(f"Fetching stations from {name} ...")
        try:
            src = source(name)
            src.get_active_stations()
            self.source = src
            self.gdf = src.gdf()
        except Exception as e:
            dlg.close()
            app.gui.window.dialog_warning(
                f"Could not load stations from {name}:\n{e}"
            )
            self.source = None
            self.gdf = gpd.GeoDataFrame()
            return
        dlg.close()

        app.gui.setvar("observation_stations", "active_station_index", 0)
        self.update()
        app.map.layer["observation_stations"].layer["stations"].set_data(self.gdf, 0)

    # ------------------------------------------------------------------
    # Polygon filter
    # ------------------------------------------------------------------

    def polygon_created(self, gdf: gpd.GeoDataFrame, index: int, id: Any) -> None:
        self.polygon = gdf

    # ------------------------------------------------------------------
    # Selection
    # ------------------------------------------------------------------

    def select_naming_option(self) -> None:
        self.update()
        opt = app.gui.getvar("observation_stations", "naming_option")
        index = app.gui.getvar("observation_stations", "active_station_index")
        app.map.layer["observation_stations"].layer["stations"].hover_property = opt
        app.map.layer["observation_stations"].layer["stations"].set_data(
            self.gdf, index
        )

    def select_station_from_map(self, *args: Any) -> None:
        index = args[0]["properties"]["index"]
        app.gui.setvar("observation_stations", "active_station_index", index)
        app.gui.window.update()

    def select_station_from_list(self) -> None:
        index = app.gui.getvar("observation_stations", "active_station_index")
        app.map.layer["observation_stations"].layer["stations"].select_by_index(index)

    def update(self) -> None:
        """Refresh the station-name list shown in the GUI."""
        opt = app.gui.getvar("observation_stations", "naming_option")
        names = [row[opt] for _, row in self.gdf.iterrows()] if not self.gdf.empty else []
        app.gui.setvar("observation_stations", "station_names", names)

    # ------------------------------------------------------------------
    # Data retrieval + view / export
    # ------------------------------------------------------------------

    def _active_station_id(self) -> str | None:
        if self.gdf.empty:
            return None
        index = app.gui.getvar("observation_stations", "active_station_index")
        if index is None or index >= len(self.gdf):
            return None
        return str(self.gdf.iloc[index]["id"])

    def _fetch_active_timeseries(self):
        """Return (station_name, DataFrame) for the active station, or (None, None)."""
        if self.source is None or self.gdf.empty:
            return None, None
        index = app.gui.getvar("observation_stations", "active_station_index")
        row = self.gdf.iloc[index]
        opt = app.gui.getvar("observation_stations", "naming_option")
        station_label = row[opt]

        tstart = app.gui.getvar("observation_stations", "tstart")
        tend = app.gui.getvar("observation_stations", "tend")
        parameter = app.gui.getvar("observation_stations", "parameter")

        dlg = app.gui.window.dialog_wait(f"Fetching data for {station_label} ...")
        try:
            df = self.source.get_data(
                str(row["id"]),
                tstart=tstart,
                tstop=tend,
                **({"parameter": parameter} if parameter else {}),
            )
        except TypeError:
            # Provider doesn't accept a `parameter` kwarg.
            df = self.source.get_data(str(row["id"]), tstart=tstart, tstop=tend)
        except Exception as e:
            dlg.close()
            app.gui.window.dialog_warning(f"Could not fetch data:\n{e}")
            return station_label, None
        dlg.close()
        return station_label, df

    def view_time_series(self) -> None:
        station_label, df = self._fetch_active_timeseries()
        if df is None or df.empty:
            if df is not None:
                app.gui.window.dialog_info("No data returned for this station/window.")
            return
        if len(plt.get_fignums()) > 0:
            df.plot(ax=plt.gca())
        else:
            self.legend_list = []
            df.plot()
        self.legend_list.append(station_label)
        plt.legend(self.legend_list)
        fig = plt.gcf()
        fig.canvas.draw()
        fig.canvas.flush_events()
        plt.show()

    def export_time_series(self) -> None:
        station_label, df = self._fetch_active_timeseries()
        if df is None or df.empty:
            return
        fmt = app.gui.getvar("observation_stations", "format")
        stname = "".join(e if e.isalnum() else "_" for e in str(station_label)) or "station"
        filename = f"{stname}.{fmt}"
        if fmt == "csv":
            df.to_csv(filename)
        else:
            # Simple whitespace-separated dump for .tek etc.
            df.to_csv(filename, sep=" ")

    # ------------------------------------------------------------------
    # Add to model
    # ------------------------------------------------------------------

    def add_stations_to_model(self) -> None:
        if self.gdf.empty:
            return
        app.active_model.add_stations(
            self.gdf,
            naming_option=app.gui.getvar("observation_stations", "naming_option"),
        )


# ----- GUI callback shims --------------------------------------------------


def select(*args: Any) -> None:
    app.toolbox["observation_stations"].select_tab()


def select_provider(*args: Any) -> None:
    app.toolbox["observation_stations"].select_provider()


def select_station(*args: Any) -> None:
    app.toolbox["observation_stations"].select_station_from_list()


def select_naming_option(*args: Any) -> None:
    app.toolbox["observation_stations"].select_naming_option()


def add_stations_to_model(*args: Any) -> None:
    app.toolbox["observation_stations"].add_stations_to_model()


def view_time_series(*args: Any) -> None:
    app.toolbox["observation_stations"].view_time_series()


def export_time_series(*args: Any) -> None:
    app.toolbox["observation_stations"].export_time_series()


def draw_polygon(*args: Any) -> None:
    app.map.layer["observation_stations"].layer["polygon"].draw()


def delete_polygon(*args: Any) -> None:
    app.map.layer["observation_stations"].layer["polygon"].clear()
    app.toolbox["observation_stations"].polygon = None
