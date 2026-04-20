"""GUI callbacks for the SFINCS HydroMT Urban Drainage tab.

Handles drawing, editing, deleting, loading, and saving urban-drainage
area polygons (piped_drainage and injection_well zones).
"""

from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point

from delftdashboard.app import app
from delftdashboard.operations import map

_MODEL = "sfincs_hmt"
_GROUP = "sfincs_hmt"


# ---------------------------------------------------------------------------
# Tab lifecycle
# ---------------------------------------------------------------------------


def select(*args: Any) -> None:
    """Activate the Urban Drainage tab, show its layers and plot outfalls."""
    map.update()
    container = app.map.layer[_MODEL].layer["urban_drainage"]
    container.show()
    container.layer["urban_drainage_areas"].activate()
    plot_outfall_layer()
    update()


def deselect(*args: Any) -> None:
    """Prompt to save unsaved urban-drainage changes when leaving the tab."""
    if app.model[_MODEL].urban_drainage_changed:
        if app.model[_MODEL].domain.urban_drainage_areas.nr_areas == 0:
            app.model[_MODEL].urban_drainage_changed = False
            return
        ok = app.gui.window.dialog_yes_no(
            "The urban drainage areas have changed. Would you like to save the changes?"
        )
        if ok:
            save()


# ---------------------------------------------------------------------------
# File I/O
# ---------------------------------------------------------------------------


def load(*args: Any) -> None:
    """Load urban drainage areas from a .urb TOML file."""
    map.reset_cursor()
    rsp = app.gui.window.dialog_open_file(
        "Select file ...",
        file_name="sfincs.urb",
        filter="*.urb",
        allow_directory_change=False,
    )
    if rsp[0]:
        app.model[_MODEL].domain.config.set("urbfile", rsp[2])
        app.model[_MODEL].domain.urban_drainage_areas.read()
        gdf = app.model[_MODEL].domain.urban_drainage_areas.gdf
        app.map.layer[_MODEL].layer["urban_drainage"].layer["urban_drainage_areas"].set_data(gdf)
        app.gui.setvar(_GROUP, "urban_drainage_area_index", 0)
        plot_outfall_layer()
        update()
    app.model[_MODEL].urban_drainage_changed = False


def save(*args: Any) -> None:
    """Save urban drainage areas to a .urb TOML file."""
    map.reset_cursor()
    filename = app.model[_MODEL].domain.config.get("urbfile")
    if not filename:
        filename = "sfincs.urb"
    rsp = app.gui.window.dialog_save_file(
        "Select file ...",
        file_name=filename,
        filter="*.urb",
        allow_directory_change=False,
    )
    if rsp[0]:
        app.model[_MODEL].domain.config.set("urbfile", rsp[2])
        app.model[_MODEL].domain.urban_drainage_areas.write()
    app.model[_MODEL].urban_drainage_changed = False


# ---------------------------------------------------------------------------
# Drawing and editing
# ---------------------------------------------------------------------------


def draw_urban_drainage_area(*args: Any) -> None:
    """Ask the user which zone type to draw and start the polygon tool."""
    tp, ok = app.gui.window.dialog_popupmenu(
        "Select urban drainage zone type",
        title="Zone type",
        options=app.gui.getvar(_GROUP, "urban_drainage_area_type_names"),
    )
    if not ok:
        return
    index = app.gui.getvar(_GROUP, "urban_drainage_area_type_names").index(tp)
    type_to_add = app.gui.getvar(_GROUP, "urban_drainage_area_types")[index]
    app.gui.setvar(_GROUP, "urban_drainage_area_type_to_add", type_to_add)
    app.map.layer[_MODEL].layer["urban_drainage"].layer["urban_drainage_areas"].draw()


def delete_urban_drainage_area(*args: Any) -> None:
    """Delete the currently selected urban drainage area."""
    gdf = app.model[_MODEL].domain.urban_drainage_areas.gdf
    if len(gdf) == 0:
        return
    index = app.gui.getvar(_GROUP, "urban_drainage_area_index")
    app.map.layer[_MODEL].layer["urban_drainage"].layer["urban_drainage_areas"].delete_feature(index)
    app.model[_MODEL].domain.urban_drainage_areas.delete(index)
    app.model[_MODEL].urban_drainage_changed = True
    plot_outfall_layer()
    update()


def select_urban_drainage_area(*args: Any) -> None:
    """Handle list-box selection of an urban drainage area."""
    update()


def edit_urban_drainage_area_name(*args: Any) -> None:
    """Rename the currently selected urban drainage area."""
    nrt = app.model[_MODEL].domain.urban_drainage_areas.nr_areas
    if nrt == 0:
        return
    index = app.gui.getvar(_GROUP, "urban_drainage_area_index")
    new_name = str(app.gui.getvar(_GROUP, "selected_urban_drainage_area_name"))
    gdf = app.model[_MODEL].domain.urban_drainage_areas.data
    gdf.at[index, "name"] = new_name
    app.model[_MODEL].urban_drainage_changed = True
    update()


def edit_urban_drainage_area_parameter(*args: Any) -> None:
    """Write edited parameters back to the underlying GeoDataFrame."""
    nrt = app.model[_MODEL].domain.urban_drainage_areas.nr_areas
    if nrt == 0:
        return
    index = app.gui.getvar(_GROUP, "urban_drainage_area_index")
    gdf = app.model[_MODEL].domain.urban_drainage_areas.data

    gdf.at[index, "h_threshold"] = app.gui.getvar(
        _GROUP, "urban_drainage_area_h_threshold"
    )

    ztype = str(gdf.iloc[index]["type"])
    if ztype == "piped_drainage":
        gdf.at[index, "outfall_x"] = app.gui.getvar(
            _GROUP, "urban_drainage_area_outfall_x"
        )
        gdf.at[index, "outfall_y"] = app.gui.getvar(
            _GROUP, "urban_drainage_area_outfall_y"
        )
        mode = app.gui.getvar(_GROUP, "urban_drainage_area_capacity_mode")
        if mode == "design_precip":
            gdf.at[index, "design_precip"] = app.gui.getvar(
                _GROUP, "urban_drainage_area_design_precip"
            )
            gdf.at[index, "max_outfall_rate"] = np.nan
        else:
            gdf.at[index, "max_outfall_rate"] = app.gui.getvar(
                _GROUP, "urban_drainage_area_max_outfall_rate"
            )
            gdf.at[index, "design_precip"] = np.nan
        gdf.at[index, "dh_design_min"] = app.gui.getvar(
            _GROUP, "urban_drainage_area_dh_design_min"
        )
        gdf.at[index, "include_outfall"] = bool(
            app.gui.getvar(_GROUP, "urban_drainage_area_include_outfall")
        )
        gdf.at[index, "check_valve"] = bool(
            app.gui.getvar(_GROUP, "urban_drainage_area_check_valve")
        )
    elif ztype == "injection_well":
        gdf.at[index, "injection_rate"] = app.gui.getvar(
            _GROUP, "urban_drainage_area_injection_rate"
        )
        gdf.at[index, "maximum_capacity"] = app.gui.getvar(
            _GROUP, "urban_drainage_area_maximum_capacity"
        )

    app.model[_MODEL].urban_drainage_changed = True
    plot_outfall_layer()


# ---------------------------------------------------------------------------
# Draw-layer callbacks
# ---------------------------------------------------------------------------


def urban_drainage_area_created(gdf: Any, index: int, id: Any) -> None:
    """Handle creation of a new zone polygon drawn on the map."""
    gdf_new = gdf.iloc[[index]][["geometry"]].reset_index(drop=True)

    ztype = str(app.gui.getvar(_GROUP, "urban_drainage_area_type_to_add"))

    existing = app.model[_MODEL].domain.urban_drainage_areas.nr_areas
    name = f"area_{existing + 1:04d}"
    gdf_new["name"] = name
    gdf_new["type"] = ztype

    # Reuse the existing polygon_file when every current area already
    # shares one; fall back to the default name otherwise (either no
    # areas yet, or the existing ones are split across multiple files).
    default_polygon_file = "urban_drainage_areas.pol"
    if existing == 0:
        polygon_file = default_polygon_file
    else:
        existing_files = (
            app.model[_MODEL].domain.urban_drainage_areas.data["polygon_file"].unique()
        )
        polygon_file = (
            existing_files[0] if len(existing_files) == 1 else default_polygon_file
        )
    gdf_new["polygon_file"] = polygon_file
    gdf_new["h_threshold"] = app.gui.getvar(_GROUP, "urban_drainage_area_h_threshold")

    if ztype == "piped_drainage":
        gdf_new["outfall_x"] = app.gui.getvar(_GROUP, "urban_drainage_area_outfall_x")
        gdf_new["outfall_y"] = app.gui.getvar(_GROUP, "urban_drainage_area_outfall_y")
        mode = app.gui.getvar(_GROUP, "urban_drainage_area_capacity_mode")
        if mode == "design_precip":
            gdf_new["design_precip"] = app.gui.getvar(
                _GROUP, "urban_drainage_area_design_precip"
            )
            gdf_new["max_outfall_rate"] = np.nan
        else:
            gdf_new["max_outfall_rate"] = app.gui.getvar(
                _GROUP, "urban_drainage_area_max_outfall_rate"
            )
            gdf_new["design_precip"] = np.nan
        gdf_new["dh_design_min"] = app.gui.getvar(
            _GROUP, "urban_drainage_area_dh_design_min"
        )
        gdf_new["include_outfall"] = bool(
            app.gui.getvar(_GROUP, "urban_drainage_area_include_outfall")
        )
        gdf_new["check_valve"] = bool(
            app.gui.getvar(_GROUP, "urban_drainage_area_check_valve")
        )
    elif ztype == "injection_well":
        gdf_new["injection_rate"] = app.gui.getvar(
            _GROUP, "urban_drainage_area_injection_rate"
        )
        gdf_new["maximum_capacity"] = app.gui.getvar(
            _GROUP, "urban_drainage_area_maximum_capacity"
        )

    app.model[_MODEL].domain.urban_drainage_areas.set(gdf_new, merge=True)

    nrt = app.model[_MODEL].domain.urban_drainage_areas.nr_areas
    app.gui.setvar(_GROUP, "urban_drainage_area_type", ztype)
    app.gui.setvar(_GROUP, "urban_drainage_area_index", nrt - 1)
    app.model[_MODEL].urban_drainage_changed = True

    gdf = app.model[_MODEL].domain.urban_drainage_areas.gdf
    app.map.layer[_MODEL].layer["urban_drainage"].layer["urban_drainage_areas"].set_data(gdf)
    plot_outfall_layer()
    update()


def urban_drainage_area_modified(gdf: Any, index: int, id: Any) -> None:
    """Handle geometry edit of an existing zone polygon."""
    existing = app.model[_MODEL].domain.urban_drainage_areas.data
    if 0 <= index < len(existing):
        existing.at[index, "geometry"] = gdf.iloc[index].geometry
    app.model[_MODEL].urban_drainage_changed = True


def urban_drainage_area_selected(index: int) -> None:
    """Handle selection of a zone polygon on the map."""
    app.gui.setvar(_GROUP, "urban_drainage_area_index", index)
    update()


# ---------------------------------------------------------------------------
# Map helpers
# ---------------------------------------------------------------------------


def plot_outfall_layer() -> None:
    """Rebuild the outfall-circle GeoDataFrame from scratch and push it to the map.

    Called whenever the set of urban drainage areas changes (tab select,
    file load, area add/delete, outfall edit).
    """

    if app.model[_MODEL].domain.urban_drainage_areas.nr_areas == 0:
        app.map.layer[_MODEL].layer["urban_drainage"].layer["outfall_locations"].clear()
        return

    gdf = app.model[_MODEL].domain.urban_drainage_areas.gdf
    crs = app.model[_MODEL].domain.crs

    piped = gdf[gdf["type"] == "piped_drainage"]

    if len(piped) == 0:
        # Probably only injection_well zones, which don't have outfalls. Clear the layer just in case.
        app.map.layer[_MODEL].layer["urban_drainage"].layer["outfall_locations"].clear()
        return

    outfall_gdf = gpd.GeoDataFrame(
        {"name": list(piped["name"].astype(str).values)},
        geometry=[
            Point(x, y)
            for x, y in zip(piped["outfall_x"], piped["outfall_y"])
        ],
        crs=crs,
    )

    app.map.layer[_MODEL].layer["urban_drainage"].layer["outfall_locations"].set_data(outfall_gdf)


# ---------------------------------------------------------------------------
# Refresh
# ---------------------------------------------------------------------------


def update() -> None:
    """Refresh the listbox, type and parameter fields in the GUI."""
    nrt = app.model[_MODEL].domain.urban_drainage_areas.nr_areas
    app.gui.setvar(_GROUP, "nr_urban_drainage_areas", nrt)

    if app.gui.getvar(_GROUP, "urban_drainage_area_index") > nrt - 1:
        app.gui.setvar(_GROUP, "urban_drainage_area_index", max(nrt - 1, 0))

    app.gui.setvar(
        _GROUP,
        "urban_drainage_area_names",
        app.model[_MODEL].domain.urban_drainage_areas.list_names,
    )

    if nrt == 0:
        app.gui.setvar(_GROUP, "urban_drainage_area_type", "piped_drainage")
        app.gui.setvar(_GROUP, "selected_urban_drainage_area_name", "")
        app.gui.window.update()
        return

    index = app.gui.getvar(_GROUP, "urban_drainage_area_index")
    row = app.model[_MODEL].domain.urban_drainage_areas.gdf.iloc[index]
    ztype = str(row["type"])
    app.gui.setvar(_GROUP, "urban_drainage_area_type", ztype)
    app.gui.setvar(
        _GROUP, "selected_urban_drainage_area_name", str(row["name"])
    )

    app.gui.setvar(
        _GROUP, "urban_drainage_area_h_threshold", float(row["h_threshold"])
    )

    if ztype == "piped_drainage":
        app.gui.setvar(
            _GROUP, "urban_drainage_area_outfall_x", float(row["outfall_x"])
        )
        app.gui.setvar(
            _GROUP, "urban_drainage_area_outfall_y", float(row["outfall_y"])
        )
        # design_precip XOR max_outfall_rate — exactly one is NaN by design.
        if pd.notna(row["design_precip"]):
            app.gui.setvar(
                _GROUP, "urban_drainage_area_capacity_mode", "design_precip"
            )
            app.gui.setvar(
                _GROUP,
                "urban_drainage_area_design_precip",
                float(row["design_precip"]),
            )
        else:
            app.gui.setvar(
                _GROUP, "urban_drainage_area_capacity_mode", "max_outfall_rate"
            )
            app.gui.setvar(
                _GROUP,
                "urban_drainage_area_max_outfall_rate",
                float(row["max_outfall_rate"]),
            )
        app.gui.setvar(
            _GROUP, "urban_drainage_area_dh_design_min", float(row["dh_design_min"])
        )
        app.gui.setvar(
            _GROUP,
            "urban_drainage_area_include_outfall",
            bool(row["include_outfall"]),
        )
        app.gui.setvar(
            _GROUP, "urban_drainage_area_check_valve", bool(row["check_valve"])
        )
    elif ztype == "injection_well":
        app.gui.setvar(
            _GROUP,
            "urban_drainage_area_injection_rate",
            float(row["injection_rate"]),
        )
        app.gui.setvar(
            _GROUP,
            "urban_drainage_area_maximum_capacity",
            float(row["maximum_capacity"]),
        )

    app.gui.window.update()
