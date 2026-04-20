"""GUI callbacks for the SFINCS HydroMT Thin Dams sub-tab.

Handles drawing, editing, deleting, loading, saving, and importing
thin dam polylines, including grid snapping visualization.
"""

from typing import Any

import geopandas as gpd

from delftdashboard.app import app
from delftdashboard.operations import map

_MODEL = "sfincs_hmt"
_GROUP = "sfincs_hmt"


def select(*args: Any) -> None:
    """Activate the Thin Dams sub-tab and show polylines on map."""
    map.update()
    # Activate draw layer
    app.map.layer[_MODEL].layer["thin_dams"].layer["polylines"].activate()
    app.map.layer[_MODEL].layer["thin_dams"].layer["snapped"].activate()
    update_grid_snapper()
    update()


def deselect(*args: Any) -> None:
    """Prompt to save unsaved thin dam changes when leaving the tab."""
    if app.model[_MODEL].thin_dams_changed:
        if app.model[_MODEL].domain.thin_dams.nr_lines == 0:
            # No thin dams, so just reset the flag and return
            app.model[_MODEL].thin_dams_changed = False
            return
        ok = app.gui.window.dialog_yes_no(
            "The thin dams have changed. Would you like to save the changes?"
        )
        if ok:
            save()


def load(*args: Any) -> None:
    """Load thin dams from a .thd file selected by the user.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    map.reset_cursor()
    rsp = app.gui.window.dialog_open_file(
        "Select file ...",
        file_name="sfincs.thd",
        filter="*.thd",
        allow_directory_change=False,
    )
    if rsp[0]:
        app.model[_MODEL].domain.config.set("thdfile", rsp[2])
        app.model[_MODEL].domain.thin_dams.read()
        gdf = app.model[_MODEL].domain.thin_dams.gdf
        app.map.layer[_MODEL].layer["thin_dams"].layer["polylines"].set_data(gdf)
        app.gui.setvar(_GROUP, "active_thin_dam", 0)
        update()
    app.model[_MODEL].thin_dams_changed = False


def import_geojson(*args: Any) -> None:
    """Import thin dams from a GeoJSON file, optionally merging with existing.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    map.reset_cursor()

    rsp = app.gui.window.dialog_open_file(
        "Select file ...", filter="*.geojson", allow_directory_change=False
    )
    if rsp[0]:
        filename = rsp[0]
        gdf = gpd.read_file(filename)
        # Extract only LineStrings
        gdf = gdf[gdf.geometry.type == "LineString"].copy()
        # Check if there are any LineStrings
        if len(gdf) == 0:
            app.gui.window.dialog_warning(
                "No LineString geometries found in the selected file."
            )
            return
        merge = False
        if app.model[_MODEL].domain.thin_dams.nr_lines > 0:
            ok = app.gui.window.dialog_yes_no(
                "Do you want to merge these with the existing thin dams?"
            )
            if ok:
                merge = True
        app.model[_MODEL].domain.thin_dams.set(gdf, merge=merge)
        app.map.layer[_MODEL].layer["thin_dams"].set_data(gdf)
        app.gui.setvar(_GROUP, "active_thin_dam", 0)
        app.model[_MODEL].thin_dams_changed = True
        update()


def save(*args: Any) -> None:
    """Save thin dams to a .thd file selected by the user.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    map.reset_cursor()
    filename = app.model[_MODEL].domain.config.get("thdfile")
    if not filename:
        filename = "sfincs.thd"
    rsp = app.gui.window.dialog_save_file(
        "Select file ...",
        file_name=filename,
        filter="*.thd",
        allow_directory_change=False,
    )
    if rsp[0]:
        app.model[_MODEL].domain.config.set("thdfile", rsp[2])
        app.model[_MODEL].domain.thin_dams.write()
    app.model[_MODEL].thin_dams_changed = False


def draw_thin_dam(*args: Any) -> None:
    """Start the map draw interaction for a new thin dam polyline."""
    app.map.layer[_MODEL].layer["thin_dams"].layer["polylines"].draw()


def delete_thin_dam(*args: Any) -> None:
    """Delete the currently selected thin dam.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    gdf = app.model[_MODEL].domain.thin_dams.gdf
    if len(gdf) == 0:
        return
    index = app.gui.getvar(_GROUP, "thin_dam_index")
    # Delete from map
    app.map.layer[_MODEL].layer["thin_dams"].layer["polylines"].delete_feature(index)
    # Delete from app
    app.model[_MODEL].domain.thin_dams.delete(index)
    app.model[_MODEL].thin_dams_changed = True
    update()

    update_grid_snapper()


def select_thin_dam(*args: Any) -> None:
    """Handle selection of a thin dam from the GUI list (no-op)."""
    pass


def thin_dam_created(gdf: Any, index: int, id: Any) -> None:
    """Handle creation of a new thin dam polyline on the map.

    Parameters
    ----------
    gdf : GeoDataFrame
        The GeoDataFrame containing all thin dam features.
    index : int
        Index of the newly created feature.
    id : Any
        Feature identifier.
    """
    app.model[_MODEL].domain.thin_dams.set(gdf, merge=False)
    nrt = len(gdf)
    app.gui.setvar(_GROUP, "thin_dam_index", nrt - 1)
    app.model[_MODEL].thin_dams_changed = True
    update()
    update_grid_snapper()


def thin_dam_modified(gdf: Any, index: int, id: Any) -> None:
    """Handle modification of an existing thin dam polyline.

    Parameters
    ----------
    gdf : GeoDataFrame
        The GeoDataFrame containing all thin dam features.
    index : int
        Index of the modified feature.
    id : Any
        Feature identifier.
    """
    app.model[_MODEL].domain.thin_dams.set(gdf, merge=False)
    app.model[_MODEL].thin_dams_changed = True
    update_grid_snapper()


def thin_dam_selected(index: int) -> None:
    """Handle selection of a thin dam on the map.

    Parameters
    ----------
    index : int
        Index of the selected thin dam.
    """
    app.gui.setvar(_GROUP, "thin_dam_index", index)
    update()


def set_model_variables(*args: Any) -> None:
    """Copy current GUI variables back to the model config."""
    app.model[_MODEL].set_model_variables()


def update_grid_snapper() -> None:
    """Snap thin dams to the grid and update the snapped layer."""
    if app.model[_MODEL].domain.thin_dams.nr_lines == 0:
        app.map.layer[_MODEL].layer["thin_dams"].layer["snapped"].clear()
        return
    snap_gdf = app.model[_MODEL].domain.thin_dams.snap_to_grid()
    if len(snap_gdf) > 0:
        app.map.layer[_MODEL].layer["thin_dams"].layer["snapped"].set_data(snap_gdf)
    else:
        app.map.layer[_MODEL].layer["thin_dams"].layer["snapped"].clear()


def update() -> None:
    """Refresh the thin dam list and active index in the GUI."""
    nrt = len(app.model[_MODEL].domain.thin_dams.gdf)
    app.gui.setvar(_GROUP, "nr_thin_dams", nrt)
    if app.gui.getvar(_GROUP, "thin_dam_index") > nrt - 1:
        app.gui.setvar(_GROUP, "thin_dam_index", max(nrt - 1, 0))
    app.gui.setvar(
        _GROUP, "thin_dam_names", app.model[_MODEL].domain.thin_dams.list_names
    )
    app.gui.window.update()
