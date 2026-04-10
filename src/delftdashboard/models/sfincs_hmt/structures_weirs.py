"""GUI callbacks for the SFINCS HydroMT Weirs sub-tab.

Handles drawing, editing, deleting, loading, saving, and importing
weir polylines, including elevation and discharge coefficient editing.
"""

from typing import Any

import geopandas as gpd

from delftdashboard.app import app
from delftdashboard.operations import map

_MODEL = "sfincs_hmt"
_GROUP = "sfincs_hmt"


def select(*args: Any) -> None:
    """Activate the Weirs sub-tab and show polylines on map."""
    map.update()
    # Activate draw layer
    app.map.layer[_MODEL].layer["weirs"].layer["polylines"].activate()
    app.map.layer[_MODEL].layer["weirs"].layer["snapped"].activate()
    update()


def deselect(*args: Any) -> None:
    """Prompt to save unsaved weir changes when leaving the tab."""
    if app.model[_MODEL].weirs_changed:
        if app.model[_MODEL].domain.weirs.nr_lines == 0:
            # No weirs, so just reset the flag and return
            app.model[_MODEL].weirs_changed = False
            return
        ok = app.gui.window.dialog_yes_no(
            "The weirs have changed. Would you like to save the changes?"
        )
        if ok:
            save()


def load(*args: Any) -> None:
    """Load weirs from a .weir file selected by the user.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    map.reset_cursor()
    rsp = app.gui.window.dialog_open_file(
        "Select file ...",
        file_name="sfincs.weir",
        filter="*.weir",
        allow_directory_change=False,
    )
    if rsp[0]:
        app.model[_MODEL].domain.config.set("weirfile", rsp[2])
        app.model[_MODEL].domain.weirs.read()
        gdf = app.model[_MODEL].domain.weirs.gdf
        app.map.layer[_MODEL].layer["weirs"].layer["polylines"].set_data(gdf)
        app.gui.setvar(_GROUP, "active_weir", 0)
        update()
    app.model[_MODEL].weirs_changed = False


def import_geojson(*args: Any) -> None:
    """Import weirs from a GeoJSON file, optionally merging with existing.

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
        if app.model[_MODEL].domain.weirs.nr_lines > 0:
            ok = app.gui.window.dialog_yes_no(
                "Do you want to merge these with the existing weirs?"
            )
            if ok:
                merge = True
        app.model[_MODEL].domain.weirs.set(gdf, merge=merge)
        app.map.layer[_MODEL].layer["weirs"].set_data(gdf)
        app.gui.setvar(_GROUP, "active_weir", 0)
        app.model[_MODEL].weirs_changed = True
        update()


def save(*args: Any) -> None:
    """Save weirs to a .weir file selected by the user.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    map.reset_cursor()
    filename = app.model[_MODEL].domain.config.get("weirfile")
    if not filename:
        filename = "sfincs.weir"
    rsp = app.gui.window.dialog_save_file(
        "Select file ...",
        file_name=filename,
        filter="*.weir",
        allow_directory_change=False,
    )
    if rsp[0]:
        app.model[_MODEL].domain.config.set("weirfile", rsp[2])
        app.model[_MODEL].domain.weirs.write()
    app.model[_MODEL].weirs_changed = False


def draw_weir(*args: Any) -> None:
    """Start the map draw interaction for a new weir polyline."""
    app.map.layer[_MODEL].layer["weirs"].layer["polylines"].draw()


def delete_weir(*args: Any) -> None:
    """Delete the currently selected weir.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    gdf = app.model[_MODEL].domain.weirs.gdf
    if len(gdf) == 0:
        return
    index = app.gui.getvar(_GROUP, "weir_index")
    # Delete from map
    app.map.layer[_MODEL].layer["weirs"].layer["polylines"].delete_feature(index)
    # Delete from app
    app.model[_MODEL].domain.weirs.delete(index)
    app.model[_MODEL].weirs_changed = True
    update()

    update_grid_snapper()


def select_weir(*args: Any) -> None:
    """Handle selection of a weir from the GUI list."""
    update()


def weir_created(gdf: Any, index: int, id: Any) -> None:
    """Handle creation of a new weir polyline on the map.

    Parameters
    ----------
    gdf : GeoDataFrame
        The GeoDataFrame containing all weir features.
    index : int
        Index of the newly created feature.
    id : Any
        Feature identifier.
    """
    # Get new gdf with the new drainage structure, and update the app
    gdf_new = gdf.iloc[[index]]
    # Drop everything except geometry, and reset index to avoid issues with merging
    gdf_new = gdf_new[["geometry"]].reset_index(drop=True)
    app.model[_MODEL].domain.weirs.create(gdf_new, elevation=0.0, par1=0.6, merge=True)
    nrt = app.model[_MODEL].domain.weirs.nr_lines
    app.gui.setvar(_GROUP, "weir_index", nrt - 1)
    app.model[_MODEL].weirs_changed = True
    update()
    update_grid_snapper()


def weir_modified(gdf: Any, index: int, id: Any) -> None:
    """Handle modification of an existing weir polyline.

    Parameters
    ----------
    gdf : GeoDataFrame
        The GeoDataFrame containing all weir features.
    index : int
        Index of the modified feature.
    id : Any
        Feature identifier.
    """
    app.model[_MODEL].domain.weirs.set(gdf, merge=False)
    app.model[_MODEL].weirs_changed = True
    update_grid_snapper()


def weir_selected(index: int) -> None:
    """Handle selection of a weir on the map.

    Parameters
    ----------
    index : int
        Index of the selected weir.
    """
    app.gui.setvar(_GROUP, "weir_index", index)
    update()


def edit_weir_elevation(*args: Any) -> None:
    """Apply a uniform elevation to all vertices of the selected weir.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    index = app.gui.getvar(_GROUP, "weir_index")
    elevation = app.gui.getvar(_GROUP, "weir_elevation")
    geom = app.model[_MODEL].domain.weirs.gdf.at[index, "geometry"]
    app.model[_MODEL].domain.weirs.data.at[index, "elevation"] = [elevation] * len(
        geom.coords
    )
    app.model[_MODEL].weirs_changed = True
    update()


def edit_weir_par1(*args: Any) -> None:
    """Apply a uniform discharge coefficient to all vertices of the selected weir.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    index = app.gui.getvar(_GROUP, "weir_index")
    par1 = app.gui.getvar(_GROUP, "weir_par1")
    geom = app.model[_MODEL].domain.weirs.gdf.at[index, "geometry"]
    app.model[_MODEL].domain.weirs.data.at[index, "par1"] = [par1] * len(geom.coords)
    app.model[_MODEL].weirs_changed = True
    update()


def set_model_variables(*args: Any) -> None:
    """Copy current GUI variables back to the model config."""
    app.model[_MODEL].set_model_variables()


def update_grid_snapper() -> None:
    """Snap weirs to the grid and update the snapped layer (currently disabled)."""
    return  # Weirs are not snapped to grid for now, so just return
    snap_gdf = app.model[_MODEL].domain.weirs.snap_to_grid()
    if len(snap_gdf) > 0:
        app.map.layer[_MODEL].layer["weirs"].layer["snapped"].set_data(snap_gdf)
    else:
        app.map.layer[_MODEL].layer["weirs"].layer["snapped"].clear()


def update() -> None:
    """Refresh the weir list, active index, elevation, and Cd in the GUI."""
    # Update weir list and index
    nrt = len(app.model[_MODEL].domain.weirs.gdf)
    app.gui.setvar(_GROUP, "nr_weirs", nrt)
    if app.gui.getvar(_GROUP, "weir_index") > nrt - 1:
        app.gui.setvar(_GROUP, "weir_index", max(nrt - 1, 0))
    app.gui.setvar(_GROUP, "weir_names", app.model[_MODEL].domain.weirs.list_names)

    # Check if enabling elevation and Cd editing.
    if nrt > 0:
        index = app.gui.getvar(_GROUP, "weir_index")
        gdf_weir = (
            app.model[_MODEL].domain.weirs.gdf.iloc[[index]].reset_index(drop=True)
        )

        # Elevation
        elev = gdf_weir.at[0, "elevation"]
        app.gui.setvar(_GROUP, "weir_elevation", gdf_weir.at[0, "elevation"][0])

        # Check if all values in the list are the same
        if len(set(elev)) == 1:
            # We can enable editing, and set the value to the unique value in the list
            app.gui.setvar(_GROUP, "weir_enable_editing_elevation", True)
        else:
            app.gui.setvar(_GROUP, "weir_enable_editing_elevation", False)

        # Par1
        par1 = gdf_weir.at[0, "par1"]
        app.gui.setvar(_GROUP, "weir_par1", par1[0])

        # Check if all values in the list are the same
        if len(set(par1)) == 1:
            # We can enable editing, and set the value to the unique value in the list
            app.gui.setvar(_GROUP, "weir_enable_editing_par1", True)
        else:
            app.gui.setvar(_GROUP, "weir_enable_editing_par1", False)

    app.gui.window.update()
