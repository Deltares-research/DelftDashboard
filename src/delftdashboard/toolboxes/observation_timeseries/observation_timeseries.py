"""Observation timeseries toolbox for DelftDashboard.

Loads one or more SFINCS his (point output) netCDF files and plots the
observation-point locations on the map. Timeseries are shown only in a
standalone plot window (never on the map):

* Select a station (from the list or by clicking it on the map) and add it to
  the plot. Added series are listed in the "Plotted" panel and drawn in the
  window.
* Several his files can be loaded to compare output for the same (identical)
  observation points - each added series is one line.
* "New Plot" starts a fresh, empty window; closing the window clears it too.
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
        self.long_name = "Output Visualization"

    def initialize(self) -> None:
        """Register GUI defaults and reset all state."""
        # Loaded his files: one entry per file {"label", "path", "ds"}.
        self.datasets: List[dict] = []
        # Reference stations (from the first loaded file), in EPSG:4326.
        self.gdf = gpd.GeoDataFrame()
        self.station_names: List[str] = []
        # Series currently plotted: {"key", "time", "values", "var_label"}.
        self.plot_items: List[dict] = []
        # Standalone matplotlib plot window.
        self.fig = None
        self.ax = None

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

        app.gui.setvar(_GROUP, "plot_item_labels", [])
        app.gui.setvar(_GROUP, "active_plot_item_index", 0)

        # Spatial output tab state + GUI variables.
        from . import spatial

        spatial.initialize(self)

    # ------------------------------------------------------------------
    # Map layers
    # ------------------------------------------------------------------

    def add_layers(self) -> None:
        """Register the observation-point and spatial-overlay layers."""
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
        # Spatial output overlay (map result as datashader trimesh).
        from . import spatial

        spatial.add_layer(layer)

    def set_layer_mode(self, mode: str) -> None:
        """Show/hide the observation-point layer for this toolbox."""
        if mode == "active":
            app.map.layer[self.name].show()
            app.map.layer[self.name].layer["points"].activate()
        elif mode in ("inactive", "invisible"):
            app.map.layer[self.name].hide()

    def zoom_to_points(self, buffer: float = 0.1) -> None:
        """Zoom the map to the extent of the loaded observation points.

        Parameters
        ----------
        buffer : float, optional
            Fractional padding around the extent (a minimum padding is applied
            for a single point or a degenerate extent), by default 0.1 (10 %).
        """
        if self.gdf.empty:
            return
        x0, y0, x1, y1 = (float(v) for v in self.gdf.total_bounds)
        dx = x1 - x0
        dy = y1 - y0
        # Pad; fall back to a small fixed margin for a single point / no spread.
        px = buffer * dx if dx > 0 else 0.05
        py = buffer * dy if dy > 0 else 0.05
        app.map.fit_bounds(x0 - px, y0 - py, x1 + px, y1 + py)

    # ------------------------------------------------------------------
    # File handling
    # ------------------------------------------------------------------

    def load_his_file(self) -> None:
        """Load a SFINCS his file, adding its points to the map."""
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
            if len(names) != len(self.station_names):
                ds.close()
                app.gui.window.dialog_warning(
                    f"This his file has {len(names)} observation points, but the "
                    f"already-loaded file(s) have {len(self.station_names)}. The "
                    "observation points must be identical to compare."
                )
                return
        else:
            self.station_names = names
            self.gdf = _points_gdf(ds, names)
            app.map.layer[self.name].layer["points"].set_data(self.gdf, 0)
            app.gui.setvar(_GROUP, "station_names", names)
            # Zoom the map to the observation points of the first loaded file.
            self.zoom_to_points()

        label = _unique_label(os.path.splitext(name)[0], self.datasets)
        self.datasets.append({"label": label, "path": full_name, "ds": ds})

        labels = [d["label"] for d in self.datasets]
        app.gui.setvar(_GROUP, "his_file_labels", labels)
        app.gui.setvar(_GROUP, "active_his_index", len(labels) - 1)
        app.gui.setvar(_GROUP, "his_file_label", label)
        app.gui.window.update()

    def delete_his_file(self) -> None:
        """Delete the currently selected his file."""
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
            self.station_names = []
            self.gdf = gpd.GeoDataFrame()
            if self.name in app.map.layer:
                app.map.layer[self.name].layer["points"].clear()
            app.gui.setvar(_GROUP, "station_names", [])

        labels = [x["label"] for x in self.datasets]
        new_index = max(0, min(index, len(labels) - 1))
        app.gui.setvar(_GROUP, "his_file_labels", labels)
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
            app.gui.setvar(_GROUP, "his_file_label", self.datasets[index]["label"])
            return
        others = [d for i, d in enumerate(self.datasets) if i != index]
        new = _unique_label(new, others)
        self.datasets[index]["label"] = new
        app.gui.setvar(_GROUP, "his_file_labels", [x["label"] for x in self.datasets])
        app.gui.setvar(_GROUP, "his_file_label", new)
        app.gui.window.update()

    def clear(self) -> None:
        """Unload all his files, clear the map points and the plot."""
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

        self.plot_items = []
        app.gui.setvar(_GROUP, "plot_item_labels", [])
        self._redraw_window()

        app.gui.setvar(_GROUP, "his_file_labels", [])
        app.gui.setvar(_GROUP, "his_file_label", "")
        app.gui.setvar(_GROUP, "station_names", [])
        app.gui.setvar(_GROUP, "active_his_index", 0)
        app.gui.setvar(_GROUP, "active_station_index", 0)
        app.gui.window.update()

    # ------------------------------------------------------------------
    # Selection (map / list) - selection only, no plotting
    # ------------------------------------------------------------------

    def select_station(self, index: int) -> None:
        """Set and highlight the active station (does not plot)."""
        if self.gdf.empty or index < 0 or index >= len(self.station_names):
            return
        app.gui.setvar(_GROUP, "active_station_index", index)
        if self.name in app.map.layer:
            app.map.layer[self.name].layer["points"].select_by_index(index)

    # ------------------------------------------------------------------
    # Plot (standalone window only)
    # ------------------------------------------------------------------

    def add_to_plot(self) -> None:
        """Copy the selected station's timeseries into the plot window."""
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

        station = self.station_names[station_index]
        # Disambiguate by file only when more than one file is loaded.
        key = station if len(self.datasets) == 1 else f"{station} [{d['label']}]"
        # Include the variable in the key when mixing variables.
        key = f"{key} - {var_label}"

        item = {
            "key": key,
            "time": pd.to_datetime(ds["time"].values),
            "values": np.asarray(
                ds[variable].isel(stations=station_index).values, dtype=float
            ),
            "var_label": var_label,
        }
        # Replace an existing entry with the same key (re-adding = refresh).
        self.plot_items = [p for p in self.plot_items if p["key"] != key]
        self.plot_items.append(item)

        app.gui.setvar(
            _GROUP, "plot_item_labels", [p["key"] for p in self.plot_items]
        )
        app.gui.setvar(_GROUP, "active_plot_item_index", len(self.plot_items) - 1)
        self._ensure_window()
        self._redraw_window()
        app.gui.window.update()

    def remove_from_plot(self) -> None:
        """Remove the selected series from the plot."""
        if not self.plot_items:
            return
        index = app.gui.getvar(_GROUP, "active_plot_item_index")
        if index < 0 or index >= len(self.plot_items):
            return
        self.plot_items.pop(index)
        labels = [p["key"] for p in self.plot_items]
        app.gui.setvar(_GROUP, "plot_item_labels", labels)
        app.gui.setvar(
            _GROUP, "active_plot_item_index", max(0, min(index, len(labels) - 1))
        )
        self._redraw_window()
        app.gui.window.update()

    def new_plot(self) -> None:
        """Start a fresh, empty plot window."""
        self.plot_items = []
        app.gui.setvar(_GROUP, "plot_item_labels", [])
        app.gui.setvar(_GROUP, "active_plot_item_index", 0)
        self._ensure_window()
        self._redraw_window()
        app.gui.window.update()

    # ------------------------------------------------------------------
    # Matplotlib window helpers
    # ------------------------------------------------------------------

    def _ensure_window(self) -> None:
        """Create the plot window if it is not open."""
        import matplotlib.pyplot as plt

        if self.fig is not None and plt.fignum_exists(self.fig.number):
            return
        self.fig, self.ax = plt.subplots(num="Observation timeseries")
        self.fig.canvas.mpl_connect("close_event", self._on_plot_closed)
        self.fig.show()

    def _redraw_window(self) -> None:
        """Redraw the plot window from the current plot items."""
        import matplotlib.pyplot as plt

        if self.fig is None or not plt.fignum_exists(self.fig.number):
            return
        self.ax.clear()
        self.ax.set_title("Observation timeseries")
        self.ax.set_xlabel("Time (UTC)")
        self.ax.grid(True, alpha=0.3)

        y_labels = set()
        for p in self.plot_items:
            self.ax.plot(p["time"], p["values"], label=p["key"])
            y_labels.add(p["var_label"])
        if self.plot_items:
            self.ax.set_ylabel(
                f"{y_labels.pop()} (m)" if len(y_labels) == 1 else "Value"
            )
            self.ax.legend(loc="best", fontsize=8)
        self.ax.relim()
        self.ax.autoscale_view()
        self.fig.canvas.draw_idle()
        try:
            self.fig.canvas.manager.window.raise_()
        except Exception:
            pass

    def _on_plot_closed(self, event: Any) -> None:
        """Reset plot state when the user closes the window."""
        self.fig = None
        self.ax = None
        self.plot_items = []
        app.gui.setvar(_GROUP, "plot_item_labels", [])


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
    """Activate the Timeseries output tab: show points, hide spatial overlay."""
    map.update()
    tb = app.toolbox[_GROUP]
    tb.set_layer_mode("active")
    if "spatial" in app.map.layer[_GROUP].layer:
        app.map.layer[_GROUP].layer["spatial"].hide()
    if not tb.gdf.empty:
        index = app.gui.getvar(_GROUP, "active_station_index")
        app.map.layer[_GROUP].layer["points"].set_data(tb.gdf, index)


def load_his_file(*args: Any) -> None:
    app.toolbox[_GROUP].load_his_file()


def delete_his_file(*args: Any) -> None:
    app.toolbox[_GROUP].delete_his_file()


def rename_his_file(*args: Any) -> None:
    app.toolbox[_GROUP].rename_his_file()


def clear_his_files(*args: Any) -> None:
    app.toolbox[_GROUP].clear()


def select_his_file(*args: Any) -> None:
    """Show the selected file's label in the edit box for renaming."""
    labels = app.gui.getvar(_GROUP, "his_file_labels")
    index = app.gui.getvar(_GROUP, "active_his_index")
    label = labels[index] if labels and 0 <= index < len(labels) else ""
    app.gui.setvar(_GROUP, "his_file_label", label)
    app.gui.window.update()


def select_variable(*args: Any) -> None:
    """Variable selection only affects the next Add (no immediate plotting)."""


def select_station_from_list(*args: Any) -> None:
    """Highlight the station selected in the list on the map."""
    index = app.gui.getvar(_GROUP, "active_station_index")
    app.toolbox[_GROUP].select_station(index)


def select_point_from_map(*args: Any) -> None:
    """Handle a click on an observation point: select/highlight it."""
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
    app.toolbox[_GROUP].select_station(index)
    app.gui.window.update()


def add_to_plot(*args: Any) -> None:
    app.toolbox[_GROUP].add_to_plot()


def remove_from_plot(*args: Any) -> None:
    app.toolbox[_GROUP].remove_from_plot()


def new_plot(*args: Any) -> None:
    app.toolbox[_GROUP].new_plot()


def select_plot_item(*args: Any) -> None:
    """Selecting an item in the Plotted list has no side effect."""
