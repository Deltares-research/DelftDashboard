"""GUI callbacks for the active-cell mask tab of the SFINCS HMT model-maker toolbox.

Handles include and exclude polygon drawing, loading, saving, and mask
generation for the SFINCS flow grid.
"""

from typing import Any

import geopandas as gpd

from delftdashboard.app import app
from delftdashboard.operations import map

_TB = "modelmaker_sfincs_hmt"
_MODEL = "sfincs_hmt"


def select(*args: Any) -> None:
    """Activate the mask tab and display include/exclude polygon layers.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    map.update()
    # Show the mask include and exclude polygons
    app.map.layer[_TB].layer["include_polygon"].activate()
    app.map.layer[_TB].layer["exclude_polygon"].activate()
    # Show the grid and mask
    app.map.layer[_MODEL].layer["grid"].activate()
    app.map.layer[_MODEL].layer["mask"].activate()
    update()


def deselect(*args: Any) -> None:
    """Prompt to save unsaved polygon changes when leaving the tab.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    changed = False
    if (
        app.toolbox[_TB].include_polygon_changed
        and len(app.toolbox[_TB].include_polygon) > 0
    ):
        changed = True
    if (
        app.toolbox[_TB].exclude_polygon_changed
        and len(app.toolbox[_TB].exclude_polygon) > 0
    ):
        changed = True
    if changed:
        ok = app.gui.window.dialog_yes_no(
            "Your polygons have changed. Would you like to save the changes?"
        )
        if ok:
            if (
                app.toolbox[_TB].include_polygon_changed
                and len(app.toolbox[_TB].include_polygon) > 0
            ):
                save_include_polygon()
            if (
                app.toolbox[_TB].exclude_polygon_changed
                and len(app.toolbox[_TB].exclude_polygon) > 0
            ):
                save_exclude_polygon()


def draw_include_polygon(*args: Any) -> None:
    """Start interactive drawing of an include polygon on the map.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    app.map.layer[_TB].layer["include_polygon"].crs = app.crs
    app.map.layer[_TB].layer["include_polygon"].draw()


def delete_include_polygon(*args: Any) -> None:
    """Delete the currently selected include polygon.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    if len(app.toolbox[_TB].include_polygon) == 0:
        return
    index = app.gui.getvar(_TB, "include_polygon_index")
    gdf = app.map.layer[_TB].layer["include_polygon"].delete_feature(index)
    app.toolbox[_TB].include_polygon = gdf
    app.toolbox[_TB].include_polygon_changed = True
    update()


def load_include_polygon(*args: Any) -> None:
    """Load include polygons from a GeoJSON file via a file dialog.

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
    if app.gui.getvar(_TB, "nr_include_polygons"):
        append = app.gui.window.dialog_yes_no("Add to existing include polygons?", " ")
    app.toolbox[_TB].read_include_polygon(full_name, append)
    app.toolbox[_TB].plot_include_polygon()
    if append:
        app.toolbox[_TB].include_polygon_changed = True
    else:
        save_include_polygon()
    update()


def save_include_polygon(*args: Any) -> None:
    """Save include polygons to include.geojson.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    app.gui.window.dialog_fade_label("Saving include polygons to include.geojson ...")
    app.toolbox[_TB].write_include_polygon()
    app.toolbox[_TB].include_polygon_changed = False


def select_include_polygon(*args: Any) -> None:
    """Activate the include polygon at the given index on the map.

    Parameters
    ----------
    *args : Any
        The first element is the index of the polygon to select.
    """
    index = args[0]
    app.map.layer[_TB].layer["include_polygon"].activate_feature(index)


def include_polygon_created(gdf: gpd.GeoDataFrame, index: int, id: Any) -> None:
    """Handle creation of a new include polygon on the map.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing all include polygons.
    index : int
        Index of the created feature.
    id : Any
        Identifier of the created feature.
    """
    app.toolbox[_TB].include_polygon = gdf
    nrp = len(app.toolbox[_TB].include_polygon)
    app.gui.setvar(_TB, "include_polygon_index", nrp - 1)
    app.toolbox[_TB].include_polygon_changed = True
    update()


def include_polygon_modified(gdf: gpd.GeoDataFrame, index: int, id: Any) -> None:
    """Handle modification of an include polygon on the map.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing all include polygons.
    index : int
        Index of the modified feature.
    id : Any
        Identifier of the modified feature.
    """
    app.toolbox[_TB].include_polygon = gdf
    app.toolbox[_TB].include_polygon_changed = True


def include_polygon_selected(index: int) -> None:
    """Handle selection of an include polygon from the map.

    Parameters
    ----------
    index : int
        Index of the selected polygon.
    """
    # Selected from map
    app.gui.setvar(_TB, "include_polygon_index", index)
    update()


def draw_exclude_polygon(*args: Any) -> None:
    """Start interactive drawing of an exclude polygon on the map.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    app.map.layer[_TB].layer["exclude_polygon"].draw()


def delete_exclude_polygon(*args: Any) -> None:
    """Delete the currently selected exclude polygon.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    if len(app.toolbox[_TB].exclude_polygon) == 0:
        return
    index = app.gui.getvar(_TB, "exclude_polygon_index")
    # Delete from map
    gdf = app.map.layer[_TB].layer["exclude_polygon"].delete_feature(index)
    app.toolbox[_TB].exclude_polygon = gdf
    app.toolbox[_TB].exclude_polygon_changed = True
    update()


def load_exclude_polygon(*args: Any) -> None:
    """Load exclude polygons from a GeoJSON file via a file dialog.

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
    if app.gui.getvar(_TB, "nr_exclude_polygons"):
        append = app.gui.window.dialog_yes_no("Add to existing exclude polygons?", " ")
    app.toolbox[_TB].read_exclude_polygon(full_name, append)
    if append:
        app.toolbox[_TB].exclude_polygon_changed = True
    else:
        save_exclude_polygon()
    app.toolbox[_TB].plot_exclude_polygon()
    update()


def save_exclude_polygon(*args: Any) -> None:
    """Save exclude polygons to exclude.geojson.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    app.gui.window.dialog_fade_label("Saving exclude polygons to exclude.geojson ...")
    app.toolbox[_TB].write_exclude_polygon()
    app.toolbox[_TB].exclude_polygon_changed = False


def select_exclude_polygon(*args: Any) -> None:
    """Activate the exclude polygon at the given index on the map.

    Parameters
    ----------
    *args : Any
        The first element is the index of the polygon to select.
    """
    index = args[0]
    app.map.layer[_TB].layer["exclude_polygon"].activate_feature(index)


def exclude_polygon_created(gdf: gpd.GeoDataFrame, index: int, id: Any) -> None:
    """Handle creation of a new exclude polygon on the map.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing all exclude polygons.
    index : int
        Index of the created feature.
    id : Any
        Identifier of the created feature.
    """
    app.toolbox[_TB].exclude_polygon = gdf
    nrp = len(app.toolbox[_TB].exclude_polygon)
    app.gui.setvar(_TB, "exclude_polygon_index", nrp - 1)
    app.toolbox[_TB].exclude_polygon_changed = True
    update()


def exclude_polygon_modified(gdf: gpd.GeoDataFrame, index: int, id: Any) -> None:
    """Handle modification of an exclude polygon on the map.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing all exclude polygons.
    index : int
        Index of the modified feature.
    id : Any
        Identifier of the modified feature.
    """
    app.toolbox[_TB].exclude_polygon = gdf
    app.toolbox[_TB].exclude_polygon_changed = True


def exclude_polygon_selected(index: int) -> None:
    """Handle selection of an exclude polygon from the map.

    Parameters
    ----------
    index : int
        Index of the selected polygon.
    """
    app.gui.setvar(_TB, "exclude_polygon_index", index)
    update()


def update() -> None:
    """Synchronize GUI variables with the current include/exclude polygon state."""
    # Include
    nrp = len(app.toolbox[_TB].include_polygon)
    incnames = []
    for ip in range(nrp):
        incnames.append(str(ip + 1))
    app.gui.setvar(_TB, "nr_include_polygons", nrp)
    app.gui.setvar(_TB, "include_polygon_names", incnames)
    index = app.gui.getvar(_TB, "include_polygon_index")
    if index > nrp - 1:
        index = max(nrp - 1, 0)
    app.gui.setvar(_TB, "include_polygon_index", index)

    # Exclude
    nrp = len(app.toolbox[_TB].exclude_polygon)
    excnames = []
    for ip in range(nrp):
        excnames.append(str(ip + 1))
    app.gui.setvar(_TB, "nr_exclude_polygons", nrp)
    app.gui.setvar(_TB, "exclude_polygon_names", excnames)
    index = app.gui.getvar(_TB, "exclude_polygon_index")
    if index > nrp - 1:
        index = max(nrp - 1, 0)
    app.gui.setvar(_TB, "exclude_polygon_index", index)
    # Update GUI
    app.gui.window.update()


def update_mask(*args: Any) -> None:
    """Regenerate the active-cell mask from the current polygons and settings.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    app.toolbox[_TB].update_mask()


def cut_inactive_cells(*args: Any) -> None:
    """Remove inactive cells from the grid.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    app.toolbox[_TB].cut_inactive_cells()
