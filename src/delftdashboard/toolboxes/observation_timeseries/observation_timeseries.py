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
        # Standalone comparison plot window (matplotlib) and its lines by key.
        self.fig = None
        self.ax = None
        self._plot_lines: dict = {}

        var_values = [v[0] for v in _VARIABLES]
        var_strings = [v[1] for v in _VARIABLES]
        app.gui.setvar(_GROUP, "variable_values", var_values)
        app.gui.setvar(_GROUP, "variable_strings", var_strings)
        app.gui.setvar(_GROUP, "variable", var_values[0])

        app.gui.setvar(_GROUP, "his_file_labels", [])
        app.gui.setvar(_GROUP, "active_his_index", 0)
        app.gui.setvar(_GROUP, "his_file_label", "")
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
        app.gui.setvar(_GROUP, "his_file_label", label)
        app.gui.window.update()

    def delete_his_file(self) -> None:
        """Delete the currently selected his file from the comparison."""
        if not self.datasets:
            return
        index = app.gui.getvar(_GROUP, "active_his_index")
        if index < 0 or index >= len(self.datasets):
            return

        d = self.datasets.pop(index)
        try:
            d["ds"].close()
        except Exception:
            pass

        if not self.datasets:
            # Nothing left: also drop the reference points and popup.
            self.station_names = []
            self.gdf = gpd.GeoDataFrame()
            if self.name in app.map.layer:
                app.map.layer[self.name].layer["points"].clear()
            app.map.close_popup()
            app.gui.setvar(_GROUP, "station_names", [])
            app.gui.setvar(_GROUP, "nr_stations", 0)

        labels = [x["label"] for x in self.datasets]
        new_index = max(0, min(index, len(labels) - 1))
        app.gui.setvar(_GROUP, "his_file_labels", labels)
        app.gui.setvar(_GROUP, "nr_his_files", len(labels))
        app.gui.setvar(_GROUP, "active_his_index", new_index)
        app.gui.setvar(_GROUP, "his_file_label", labels[new_index] if labels else "")
        app.gui.window.update()

    def rename_his_file(self) -> None:
        """Apply the edited label to the selected his file (used in the legend)."""
        if not self.datasets:
            return
        index = app.gui.getvar(_GROUP, "active_his_index")
        if index < 0 or index >= len(self.datasets):
            return
        new = (app.gui.getvar(_GROUP, "his_file_label") or "").strip()
        if not new:
            # Empty input: restore the current label in the edit box.
            app.gui.setvar(_GROUP, "his_file_label", self.datasets[index]["label"])
            return
        # Keep labels unique across the other loaded files.
        others = [d for i, d in enumerate(self.datasets) if i != index]
        new = _unique_label(new, others)
        self.datasets[index]["label"] = new

        labels = [x["label"] for x in self.datasets]
        app.gui.setvar(_GROUP, "his_file_labels", labels)
        app.gui.setvar(_GROUP, "his_file_label", new)
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
        # Empty the comparison plot too (window stays open if it was).
        self.clear_plot()

        if self.name in app.map.layer:
            app.map.layer[self.name].layer["points"].clear()
        app.map.close_popup()

        app.gui.setvar(_GROUP, "his_file_labels", [])
        app.gui.setvar(_GROUP, "his_file_label", "")
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

    def create_plot(self) -> None:
        """Open a new, empty comparison plot window.

        If a plot window is already open it is simply raised (a new one is not
        created), so there is at most one comparison window at a time.
        """
        import matplotlib.pyplot as plt

        if self.fig is not None and plt.fignum_exists(self.fig.number):
            try:
                self.fig.canvas.manager.window.raise_()
            except Exception:
                pass
            return

        self.fig, self.ax = plt.subplots(num="Observation timeseries")
        self._plot_lines = {}
        self._reset_axes()
        # Closing the window is equivalent to clearing the plot.
        self.fig.canvas.mpl_connect("close_event", self._on_plot_closed)
        self.fig.show()

    def add_to_plot(self) -> None:
        """Add the selected station's timeseries to the open plot window.

        A window is created automatically if none is open yet. Re-adding the
        same station/run refreshes its line instead of duplicating it.
        """
        import matplotlib.pyplot as plt

        if not self.datasets or self.gdf.empty:
            return
        his_index = app.gui.getvar(_GROUP, "active_his_index")
        if his_index < 0 or his_index >= len(self.datasets):
            his_index = 0
        station_index = app.gui.getvar(_GROUP, "active_station_index")
        if station_index < 0 or station_index >= len(self.station_names):
            app.gui.window.dialog_info("Select a station first.")
            return

        d = self.datasets[his_index]
        ds = d["ds"]
        variable = app.gui.getvar(_GROUP, "variable")
        var_label = dict(_VARIABLES).get(variable, variable)
        if variable not in ds:
            app.gui.window.dialog_info(
                f"File '{d['label']}' does not contain '{variable}'."
            )
            return

        # Make sure a plot window exists (auto-create on first Add).
        if self.fig is None or not plt.fignum_exists(self.fig.number):
            self.create_plot()

        station = self.station_names[station_index]
        # Disambiguate by file only when more than one file is loaded.
        key = station if len(self.datasets) == 1 else f"{station} [{d['label']}]"
        time = pd.to_datetime(ds["time"].values)
        vals = np.asarray(ds[variable].isel(stations=station_index).values, dtype=float)

        # Replace an existing line with the same key (re-adding = refresh).
        old = self._plot_lines.pop(key, None)
        if old is not None:
            try:
                old.remove()
            except Exception:
                pass
        (line,) = self.ax.plot(time, vals, label=key)
        self._plot_lines[key] = line

        self.ax.set_ylabel(f"{var_label} (m)")
        self.ax.legend(loc="best", fontsize=8)
        self.ax.relim()
        self.ax.autoscale_view()
        self.fig.canvas.draw_idle()
        try:
            self.fig.canvas.manager.window.raise_()
        except Exception:
            pass

    def clear_plot(self) -> None:
        """Empty the open plot window (keeps the window open)."""
        import matplotlib.pyplot as plt

        if self.fig is not None and plt.fignum_exists(self.fig.number):
            self.ax.clear()
            self._plot_lines = {}
            self._reset_axes()
            self.fig.canvas.draw_idle()

    def _reset_axes(self) -> None:
        """Apply the default title/labels/grid to an empty axes."""
        self.ax.set_title("Observation timeseries")
        self.ax.set_xlabel("Time (UTC)")
        self.ax.grid(True, alpha=0.3)

    def _on_plot_closed(self, event: Any) -> None:
        """Reset plot state when the user closes the window."""
        self.fig = None
        self.ax = None
        self._plot_lines = {}


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


def delete_his_file(*args: Any) -> None:
    app.toolbox[_GROUP].delete_his_file()


def rename_his_file(*args: Any) -> None:
    app.toolbox[_GROUP].rename_his_file()


def create_plot(*args: Any) -> None:
    """Open a new, empty comparison plot window."""
    app.toolbox[_GROUP].create_plot()


def add_to_plot(*args: Any) -> None:
    """Add the selected station's timeseries to the comparison plot."""
    app.toolbox[_GROUP].add_to_plot()


def clear_plot(*args: Any) -> None:
    """Empty the comparison plot."""
    app.toolbox[_GROUP].clear_plot()


def select_variable(*args: Any) -> None:
    """Re-plot the active station with the newly selected variable."""
    index = app.gui.getvar(_GROUP, "active_station_index")
    app.toolbox[_GROUP].plot_station(index)


def select_his_file(*args: Any) -> None:
    """Show the selected file's label in the edit box for renaming."""
    labels = app.gui.getvar(_GROUP, "his_file_labels")
    index = app.gui.getvar(_GROUP, "active_his_index")
    label = labels[index] if labels and 0 <= index < len(labels) else ""
    app.gui.setvar(_GROUP, "his_file_label", label)
    app.gui.window.update()


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
