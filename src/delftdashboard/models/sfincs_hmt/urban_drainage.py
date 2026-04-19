"""GUI callbacks for the SFINCS HydroMT Urban Drainage tab.

Handles drawing, editing, deleting, loading, and saving urban-drainage
area polygons (piped_drainage and injection_well zones).
"""

from typing import Any

import geopandas as gpd
import numpy as np

from delftdashboard.app import app
from delftdashboard.operations import map

_MODEL = "sfincs_hmt"
_GROUP = "sfincs_hmt"


# ---------------------------------------------------------------------------
# Tab lifecycle
# ---------------------------------------------------------------------------


def select(*args: Any) -> None:
    """Activate the Urban Drainage tab and its polygon draw layer."""
    map.update()
    app.map.layer[_MODEL].layer["urban_drainage_areas"].activate()
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
        app.map.layer[_MODEL].layer["urban_drainage_areas"].set_data(gdf)
        app.gui.setvar(_GROUP, "urban_drainage_area_index", 0)
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
    app.map.layer[_MODEL].layer["urban_drainage_areas"].draw()


def delete_urban_drainage_area(*args: Any) -> None:
    """Delete the currently selected urban drainage area."""
    gdf = app.model[_MODEL].domain.urban_drainage_areas.gdf
    if len(gdf) == 0:
        return
    index = app.gui.getvar(_GROUP, "urban_drainage_area_index")
    app.map.layer[_MODEL].layer["urban_drainage_areas"].delete_feature(index)
    app.model[_MODEL].domain.urban_drainage_areas.delete(index)
    app.model[_MODEL].urban_drainage_changed = True
    update()


def select_urban_drainage_area(*args: Any) -> None:
    """Handle list-box selection of an urban drainage area."""
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
    gdf_new["polygon_file"] = "sfincs.pol"
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
    app.map.layer[_MODEL].layer["urban_drainage_areas"].set_data(gdf)
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
        app.gui.window.update()
        return

    index = app.gui.getvar(_GROUP, "urban_drainage_area_index")
    row = app.model[_MODEL].domain.urban_drainage_areas.gdf.iloc[index]
    ztype = str(row["type"])
    app.gui.setvar(_GROUP, "urban_drainage_area_type", ztype)

    h_threshold = row.get("h_threshold", 0.0)
    app.gui.setvar(
        _GROUP,
        "urban_drainage_area_h_threshold",
        float(h_threshold) if _is_set(h_threshold) else 0.0,
    )

    if ztype == "piped_drainage":
        app.gui.setvar(
            _GROUP,
            "urban_drainage_area_outfall_x",
            float(row["outfall_x"]) if _is_set(row.get("outfall_x")) else 0.0,
        )
        app.gui.setvar(
            _GROUP,
            "urban_drainage_area_outfall_y",
            float(row["outfall_y"]) if _is_set(row.get("outfall_y")) else 0.0,
        )
        if _is_set(row.get("design_precip")):
            app.gui.setvar(_GROUP, "urban_drainage_area_capacity_mode", "design_precip")
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
                float(row["max_outfall_rate"]) if _is_set(row.get("max_outfall_rate")) else 0.0,
            )
        app.gui.setvar(
            _GROUP,
            "urban_drainage_area_dh_design_min",
            float(row["dh_design_min"]) if _is_set(row.get("dh_design_min")) else 0.1,
        )
        app.gui.setvar(
            _GROUP,
            "urban_drainage_area_include_outfall",
            bool(row["include_outfall"]) if _is_set(row.get("include_outfall")) else True,
        )
        app.gui.setvar(
            _GROUP,
            "urban_drainage_area_check_valve",
            bool(row["check_valve"]) if _is_set(row.get("check_valve")) else False,
        )
    elif ztype == "injection_well":
        app.gui.setvar(
            _GROUP,
            "urban_drainage_area_injection_rate",
            float(row["injection_rate"]) if _is_set(row.get("injection_rate")) else 0.0,
        )
        app.gui.setvar(
            _GROUP,
            "urban_drainage_area_maximum_capacity",
            float(row["maximum_capacity"]) if _is_set(row.get("maximum_capacity")) else 0.0,
        )

    app.gui.window.update()


def _is_set(value) -> bool:
    if value is None:
        return False
    try:
        return not (isinstance(value, float) and np.isnan(value))
    except TypeError:
        return True
