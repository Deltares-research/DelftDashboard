"""Observation timeseries toolbox for DelftDashboard.

Loads one or more SFINCS his (point output) netCDF files, plots the
observation-point locations on the map, and lets the user click a point (or
pick it from the list) to view its timeseries as an on-map popup. Several his
files can be loaded at once to compare output for the same (identical)
observation points - each file is drawn as a separate line.
"""

from __future__ import annotations

import os
from typing import Any, List

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
from pyproj import CRS
from shapely.geometry import Point

from delftdashboard.app import app
from delftdashboard.operations import map
from delftdashboard.operations.toolbox import GenericToolbox

_GROUP = "observation_timeseries"

# (netCDF variable, GUI label). First entry is the default.
_VARIABLES: List[tuple[str, str]] = [
    ("point_zs", "Water level"),
    ("point_h", "Water depth"),
]


class Toolbox(GenericToolbox):
    """Toolbox for viewing and comparing SFINCS his (point output) timeseries."""

    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name
        self.long_name = "Observation Timeseries"

    def initialize(self) -> None:
        """Register GUI defaults and reset the loaded-file state."""
        # State: one entry per loaded his file.
        self.datasets: List[dict] = []  # {"label", "path", "ds"}
        # Reference stations (from the first loaded file), in EPSG:4326.
        self.gdf = gpd.GeoDataFrame()
        self.station_names: List[str] = []

        var_values = [v[0] for v in _VARIABLES]
        var_strings = [v[1] for v in _VARIABLES]
        app.gui.setvar(_GROUP, "variable_values", var_values)
        app.gui.setvar(_GROUP, "variable_strings", var_strings)
        app.gui.setvar(_GROUP, "variable", var_values[0])

        app.gui.setvar(_GROUP, "his_file_labels", [])
        app.gui.setvar(_GROUP, "active_his_index", 0)
        app.gui.setvar(_GROUP, "station_names", [])
        app.gui.setvar(_GROUP, "active_station_index", 0)
        app.gui.setvar(_GROUP, "nr_his_files", 0)
        app.gui.setvar(_GROUP, "nr_stations", 0)

    # ------------------------------------------------------------------
    # Map layers
    # ------------------------------------------------------------------

    def add_layers(self) -> None:
        """Register the clickable observation-point layer."""
        layer = app.map.add_layer(self.name)
        layer.add_layer(
            "points",
            type="circle_selector",
            select=select_point_from_map,
            hover_property="name",
            line_color="white",
            line_opacity=1.0,
            fill_color="orange",
            fill_opacity=1.0,
            circle_radius=4,
            circle_radius_selected=5,
            line_color_selected="white",
            fill_color_selected="red",
            legend_label="observation point",
        )

    def set_layer_mode(self, mode: str) -> None:
        """Show/hide the observation-point layer for this toolbox."""
        if mode == "active":
            app.map.layer[self.name].show()
            app.map.layer[self.name].layer["points"].activate()
        elif mode in ("inactive", "invisible"):
            app.map.layer[self.name].hide()

    # ------------------------------------------------------------------
    # File handling
    # ------------------------------------------------------------------

    def load_his_file(self) -> None:
        """Load a SFINCS his file, adding its points/series to the comparison."""
        full_name, path, name, ext, fltr = app.gui.window.dialog_open_file(
            "Select SFINCS his file", filter="*.nc"
        )
        if not full_name:
            return

        try:
            ds = xr.open_dataset(full_name)
        except Exception as e:
            app.gui.window.dialog_warning(f"Could not open file:\n{e}")
            return

        if "point_zs" not in ds and "point_h" not in ds:
            ds.close()
            app.gui.window.dialog_warning(
                "This file does not look like a SFINCS his file "
                "(no 'point_zs' / 'point_h' variables)."
            )
            return

        names = _station_names(ds)

        if self.datasets:
            # Additional file: station set must match the reference file.
            if len(names) != len(self.station_names):
                ds.close()
                app.gui.window.dialog_warning(
                    f"This his file has {len(names)} observation points, but the "
                    f"already-loaded file(s) have {len(self.station_names)}. The "
                    "observation points must be identical to compare."
                )
                return
        else:
            # First file defines the reference stations and the map points.
            self.station_names = names
            self.gdf = _points_gdf(ds, names)
            app.map.layer[self.name].layer["points"].set_data(self.gdf, 0)
            app.gui.setvar(_GROUP, "station_names", names)
            app.gui.setvar(_GROUP, "nr_stations", len(names))

        label = _unique_label(os.path.splitext(name)[0], self.datasets)
        self.datasets.append({"label": label, "path": full_name, "ds": ds})

        labels = [d["label"] for d in self.datasets]
        app.gui.setvar(_GROUP, "his_file_labels", labels)
        app.gui.setvar(_GROUP, "nr_his_files", len(labels))
        app.gui.setvar(_GROUP, "active_his_index", len(labels) - 1)
        app.gui.window.update()

    def clear(self) -> None:
        """Unload all his files and clear the map points and popup."""
        for d in self.datasets:
            try:
                d["ds"].close()
            except Exception:
                pass
        self.datasets = []
        self.station_names = []
        self.gdf = gpd.GeoDataFrame()

        if self.name in app.map.layer:
            app.map.layer[self.name].layer["points"].clear()
        app.map.close_popup()

        app.gui.setvar(_GROUP, "his_file_labels", [])
        app.gui.setvar(_GROUP, "station_names", [])
        app.gui.setvar(_GROUP, "active_his_index", 0)
        app.gui.setvar(_GROUP, "active_station_index", 0)
        app.gui.setvar(_GROUP, "nr_his_files", 0)
        app.gui.setvar(_GROUP, "nr_stations", 0)
        app.gui.window.update()

    # ------------------------------------------------------------------
    # Plotting
    # ------------------------------------------------------------------

    def plot_station(self, index: int) -> None:
        """Show a timeseries popup for station *index* across all loaded files."""
        if not self.datasets or self.gdf.empty:
            return
        if index < 0 or index >= len(self.station_names):
            return

        variable = app.gui.getvar(_GROUP, "variable")
        var_label = dict(_VARIABLES).get(variable, variable)

        # One column per loaded his file.
        series: dict[str, pd.Series] = {}
        for d in self.datasets:
            ds = d["ds"]
            if variable not in ds:
                continue
            da = ds[variable].isel(stations=index)
            series[d["label"]] = pd.Series(
                np.asarray(da.values, dtype=float),
                index=pd.to_datetime(ds["time"].values),
            )
        if not series:
            app.gui.window.dialog_info(
                f"None of the loaded files contain '{variable}'."
            )
            return

        df = pd.DataFrame(series)
        station_label = self.station_names[index]
        geom = self.gdf.iloc[index].geometry
        map.show_timeseries_popup(
            df,
            lon=geom.x,
            lat=geom.y,
            title=f"{station_label} - {var_label}",
            y_label=f"{var_label} (m)",
            show_legend=len(series) > 1,
            html_name="obs_timeseries_popup.html",
        )


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def _station_names(ds: xr.Dataset) -> List[str]:
    """Return decoded, stripped station names (falling back to point<i>)."""
    if "station_name" in ds:
        names = []
        for raw in ds["station_name"].values:
            if isinstance(raw, bytes):
                names.append(raw.decode("utf-8", "ignore").strip())
            else:
                names.append(str(raw).strip())
        return names
    n = int(ds.sizes.get("stations", 0))
    return [f"point{i}" for i in range(n)]


def _file_epsg(ds: xr.Dataset) -> CRS | None:
    """Return the CRS declared on the his file's ``crs`` variable, if any."""
    if "crs" in ds:
        code = ds["crs"].attrs.get("epsg_code") or ds["crs"].attrs.get("EPSG")
        if code and str(code) not in ("-", ""):
            try:
                return CRS.from_user_input(str(code))
            except Exception:
                return None
    return None


def _points_gdf(ds: xr.Dataset, names: List[str]) -> gpd.GeoDataFrame:
    """Build a lon/lat GeoDataFrame of the station points for the map."""
    x = np.asarray(ds["point_x"].values, dtype=float)
    y = np.asarray(ds["point_y"].values, dtype=float)
    crs = _file_epsg(ds) or CRS(4326)
    gdf = gpd.GeoDataFrame(
        {"name": names},
        geometry=[Point(xi, yi) for xi, yi in zip(x, y)],
        crs=crs,
    )
    # The map and the timeseries popup work in lon/lat (EPSG:4326).
    return gdf.to_crs(4326)


def _unique_label(base: str, datasets: List[dict]) -> str:
    """Return *base*, suffixed with a counter if it is already in use."""
    existing = {d["label"] for d in datasets}
    if base not in existing:
        return base
    i = 2
    while f"{base} ({i})" in existing:
        i += 1
    return f"{base} ({i})"


# ----------------------------------------------------------------------
# GUI callback shims
# ----------------------------------------------------------------------


def select(*args: Any) -> None:
    """Activate the toolbox tab: show the points layer."""
    map.update()
    tb = app.toolbox[_GROUP]
    tb.set_layer_mode("active")
    if not tb.gdf.empty:
        index = app.gui.getvar(_GROUP, "active_station_index")
        app.map.layer[_GROUP].layer["points"].set_data(tb.gdf, index)


def load_his_file(*args: Any) -> None:
    app.toolbox[_GROUP].load_his_file()


def clear_his_files(*args: Any) -> None:
    app.toolbox[_GROUP].clear()


def select_variable(*args: Any) -> None:
    """Re-plot the active station with the newly selected variable."""
    index = app.gui.getvar(_GROUP, "active_station_index")
    app.toolbox[_GROUP].plot_station(index)


def select_his_file(*args: Any) -> None:
    """Selecting a file in the list has no side effect (display only)."""


def select_station_from_list(*args: Any) -> None:
    """Highlight the station on the map and plot it."""
    index = app.gui.getvar(_GROUP, "active_station_index")
    app.map.layer[_GROUP].layer["points"].select_by_index(index)
    app.toolbox[_GROUP].plot_station(index)


def select_point_from_map(*args: Any) -> None:
    """Handle a click on an observation point on the map."""
    a = args[0] if args else {}
    index = None
    if isinstance(a, dict):
        props = a.get("properties")
        if isinstance(props, dict) and "index" in props:
            index = props["index"]
        elif "id" in a:
            index = a["id"]
    elif isinstance(a, int):
        index = a
    if index is None:
        index = app.gui.getvar(_GROUP, "active_station_index")

    app.gui.setvar(_GROUP, "active_station_index", index)
    app.toolbox[_GROUP].plot_station(index)
    app.gui.window.update()
