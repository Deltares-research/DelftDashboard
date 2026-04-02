"""GUI callbacks for the SnapWave active-cell mask tab of the SFINCS HMT model-maker toolbox.

Handles include and exclude polygon drawing, loading, saving, and mask
generation for the SnapWave wave grid.
"""

from typing import Any

import geopandas as gpd

from delftdashboard.app import app
from delftdashboard.operations import map

_TB = "modelmaker_sfincs_hmt"
_MODEL = "sfincs_hmt"


def select(*args: Any) -> None:
    """Activate the SnapWave mask tab and display include/exclude polygon layers.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    map.update()
    # Show the mask include and exclude polygons
    app.map.layer[_TB].layer["include_polygon_snapwave"].activate()
    app.map.layer[_TB].layer["exclude_polygon_snapwave"].activate()
    # Show the grid and mask
    app.map.layer[_MODEL].layer["grid"].activate()
    app.map.layer[_MODEL].layer["mask_snapwave"].activate()
    update()


def deselect(*args: Any) -> None:
    """Prompt to save unsaved SnapWave polygon changes when leaving the tab.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    # Check if there are include polygons
    changed = False
    if (
        app.toolbox[_TB].include_polygon_snapwave_changed
        and len(app.toolbox[_TB].include_polygon_snapwave) > 0
    ):
        changed = True
    if (
        app.toolbox[_TB].exclude_polygon_snapwave_changed
        and len(app.toolbox[_TB].exclude_polygon_snapwave) > 0
    ):
        changed = True
    if changed:
        ok = app.gui.window.dialog_yes_no(
            "Your polygons have changed. Would you like to save the changes?"
        )
        if ok:
            if (
                app.toolbox[_TB].include_polygon_snapwave_changed
                and len(app.toolbox[_TB].include_polygon_snapwave) > 0
            ):
                save_include_polygon_snapwave()
            if (
                app.toolbox[_TB].exclude_polygon_snapwave_changed
                and len(app.toolbox[_TB].exclude_polygon_snapwave) > 0
            ):
                save_exclude_polygon_snapwave()


def draw_include_polygon_snapwave(*args: Any) -> None:
    """Start interactive drawing of a SnapWave include polygon on the map.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    app.map.layer[_TB].layer["include_polygon_snapwave"].crs = app.crs
    app.map.layer[_TB].layer["include_polygon_snapwave"].draw()


def delete_include_polygon_snapwave(*args: Any) -> None:
    """Delete the currently selected SnapWave include polygon.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    if len(app.toolbox[_TB].include_polygon_snapwave) == 0:
        return
    index = app.gui.getvar(_TB, "include_polygon_index_snapwave")
    gdf = app.map.layer[_TB].layer["include_polygon_snapwave"].delete_feature(index)
    app.toolbox[_TB].include_polygon_snapwave = gdf
    app.toolbox[_TB].include_polygon_snapwave_changed = True
    update()


def load_include_polygon_snapwave(*args: Any) -> None:
    """Load SnapWave include polygons from a GeoJSON file via a file dialog.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    full_name, path, name, ext, fltr = app.gui.window.dialog_open_file(
        "Select include polygon file ...", filter="*.geojson"
    )
    if not full_name:
        return
    append = False
    if app.gui.getvar(_TB, "nr_include_polygons_snapwave"):
        append = app.gui.window.dialog_yes_no("Add to existing include polygons?", " ")
    app.toolbox[_TB].read_include_polygon_snapwave(full_name, append)
    app.toolbox[_TB].plot_include_polygon_snapwave()
    if append:
        app.toolbox[_TB].include_polygon_snapwave_changed = True
    else:
        save_include_polygon_snapwave()
    update()


def save_include_polygon_snapwave(*args: Any) -> None:
    """Save SnapWave include polygons to include_snapwave.geojson.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    app.gui.window.dialog_fade_label(
        "Saving include polygons to include_snapwave.geojson ..."
    )
    app.toolbox[_TB].include_polygon_snapwave_changed = False
    app.toolbox[_TB].write_include_polygon_snapwave()


def select_include_polygon_snapwave(*args: Any) -> None:
    """Activate the SnapWave include polygon at the given index on the map.

    Parameters
    ----------
    *args : Any
        The first element is the index of the polygon to select.
    """
    index = args[0]
    app.map.layer[_TB].layer["include_polygon_snapwave"].activate_feature(index)


def include_polygon_created_snapwave(
    gdf: gpd.GeoDataFrame, index: int, id: Any
) -> None:
    """Handle creation of a new SnapWave include polygon on the map.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing all SnapWave include polygons.
    index : int
        Index of the created feature.
    id : Any
        Identifier of the created feature.
    """
    app.toolbox[_TB].include_polygon_snapwave = gdf
    nrp = len(app.toolbox[_TB].include_polygon_snapwave)
    app.gui.setvar(_TB, "include_polygon_index_snapwave", nrp - 1)
    app.toolbox[_TB].include_polygon_snapwave_changed = True
    update()


def include_polygon_modified_snapwave(
    gdf: gpd.GeoDataFrame, index: int, id: Any
) -> None:
    """Handle modification of a SnapWave include polygon on the map.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing all SnapWave include polygons.
    index : int
        Index of the modified feature.
    id : Any
        Identifier of the modified feature.
    """
    app.toolbox[_TB].include_polygon_snapwave = gdf
    app.toolbox[_TB].include_polygon_snapwave_changed = True


def include_polygon_selected_snapwave(index: int) -> None:
    """Handle selection of a SnapWave include polygon from the map.

    Parameters
    ----------
    index : int
        Index of the selected polygon.
    """
    app.gui.setvar(_TB, "include_polygon_index_snapwave", index)
    update()


def draw_exclude_polygon_snapwave(*args: Any) -> None:
    """Start interactive drawing of a SnapWave exclude polygon on the map.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    app.map.layer[_TB].layer["include_polygon_snapwave"].crs = app.crs
    app.map.layer[_TB].layer["exclude_polygon_snapwave"].draw()


def delete_exclude_polygon_snapwave(*args: Any) -> None:
    """Delete the currently selected SnapWave exclude polygon.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    if len(app.toolbox[_TB].exclude_polygon_snapwave) == 0:
        return
    index = app.gui.getvar(_TB, "exclude_polygon_index_snapwave")
    gdf = app.map.layer[_TB].layer["exclude_polygon_snapwave"].delete_feature(index)
    app.toolbox[_TB].exclude_polygon_snapwave = gdf
    app.toolbox[_TB].exclude_polygon_snapwave_changed = True
    update()


def load_exclude_polygon_snapwave(*args: Any) -> None:
    """Load SnapWave exclude polygons from a GeoJSON file via a file dialog.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    full_name, path, name, ext, fltr = app.gui.window.dialog_open_file(
        "Select exclude polygon file ...", filter="*.geojson"
    )
    if not full_name:
        return
    append = False
    if app.gui.getvar(_TB, "nr_exclude_polygons_snapwave"):
        append = app.gui.window.dialog_yes_no("Add to existing exclude polygons?", " ")
    app.toolbox[_TB].read_exclude_polygon_snapwave(full_name, append)
    app.toolbox[_TB].plot_exclude_polygon_snapwave()
    if append:
        app.toolbox[_TB].exclude_polygon_snapwave_changed = True
    else:
        save_exclude_polygon_snapwave()
    update()


def save_exclude_polygon_snapwave(*args: Any) -> None:
    """Save SnapWave exclude polygons to exclude_snapwave.geojson.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    app.gui.window.dialog_fade_label(
        "Saving exclude polygons to exclude_snapwave.geojson ..."
    )
    app.toolbox[_TB].exclude_polygon_snapwave_changed = False
    app.toolbox[_TB].write_exclude_polygon_snapwave()


def select_exclude_polygon_snapwave(*args: Any) -> None:
    """Activate the SnapWave exclude polygon at the given index on the map.

    Parameters
    ----------
    *args : Any
        The first element is the index of the polygon to select.
    """
    index = args[0]
    app.map.layer[_TB].layer["exclude_polygon_snapwave"].activate_feature(index)


def exclude_polygon_created_snapwave(
    gdf: gpd.GeoDataFrame, index: int, id: Any
) -> None:
    """Handle creation of a new SnapWave exclude polygon on the map.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing all SnapWave exclude polygons.
    index : int
        Index of the created feature.
    id : Any
        Identifier of the created feature.
    """
    app.toolbox[_TB].exclude_polygon_snapwave = gdf
    nrp = len(app.toolbox[_TB].exclude_polygon_snapwave)
    app.gui.setvar(_TB, "exclude_polygon_index_snapwave", nrp - 1)
    app.toolbox[_TB].exclude_polygon_snapwave_changed = True
    update()


def exclude_polygon_modified_snapwave(
    gdf: gpd.GeoDataFrame, index: int, id: Any
) -> None:
    """Handle modification of a SnapWave exclude polygon on the map.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing all SnapWave exclude polygons.
    index : int
        Index of the modified feature.
    id : Any
        Identifier of the modified feature.
    """
    app.toolbox[_TB].exclude_polygon_snapwave = gdf
    app.toolbox[_TB].exclude_polygon_snapwave_changed = True


def exclude_polygon_selected_snapwave(index: int) -> None:
    """Handle selection of a SnapWave exclude polygon from the map.

    Parameters
    ----------
    index : int
        Index of the selected polygon.
    """
    app.gui.setvar(_TB, "exclude_polygon_index_snapwave", index)
    update()


def update() -> None:
    """Synchronize GUI variables with the current SnapWave include/exclude polygon state."""
    # Include
    nrp = len(app.toolbox[_TB].include_polygon_snapwave)
    incnames = []
    for ip in range(nrp):
        incnames.append(str(ip + 1))
    app.gui.setvar(_TB, "nr_include_polygons_snapwave", nrp)
    app.gui.setvar(_TB, "include_polygon_names_snapwave", incnames)
    index = app.gui.getvar(_TB, "include_polygon_index_snapwave")
    if index > nrp - 1:
        index = max(nrp - 1, 0)
    app.gui.setvar(_TB, "include_polygon_index_snapwave", index)
    # Exclude
    nrp = len(app.toolbox[_TB].exclude_polygon_snapwave)
    excnames = []
    for ip in range(nrp):
        excnames.append(str(ip + 1))
    app.gui.setvar(_TB, "nr_exclude_polygons_snapwave", nrp)
    app.gui.setvar(_TB, "exclude_polygon_names_snapwave", excnames)
    index = app.gui.getvar(_TB, "exclude_polygon_index_snapwave")
    if index > nrp - 1:
        index = max(nrp - 1, 0)
    app.gui.setvar(_TB, "exclude_polygon_index_snapwave", index)
    # Update GUI
    app.gui.window.update()


def update_mask(*args: Any) -> None:
    """Regenerate the SnapWave active-cell mask from current polygons and settings.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    app.toolbox[_TB].update_mask_snapwave()


def cut_inactive_cells(*args: Any) -> None:
    """Remove inactive cells from the grid.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    app.toolbox[_TB].cut_inactive_cells()
