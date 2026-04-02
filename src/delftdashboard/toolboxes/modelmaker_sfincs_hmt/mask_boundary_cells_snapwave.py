"""GUI callbacks for the SnapWave boundary-cell mask tab of the SFINCS HMT model-maker toolbox.

Handles drawing, loading, saving, and selecting boundary polygons for open
and Neumann boundary types on the SnapWave wave grid.
"""

from typing import Any

import geopandas as gpd

from delftdashboard.app import app
from delftdashboard.operations import map

_TB = "modelmaker_sfincs_hmt"
_MODEL = "sfincs_hmt"


def select(*args: Any) -> None:
    """Activate the SnapWave boundary mask tab and display boundary polygon layers.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    map.update()
    # Show the boundary polygons
    app.map.layer[_TB].layer["open_boundary_polygon_snapwave"].activate()
    app.map.layer[_TB].layer["neumann_boundary_polygon_snapwave"].activate()
    # Show the grid and mask
    app.map.layer[_MODEL].layer["grid"].activate()
    app.map.layer[_MODEL].layer["mask_snapwave"].activate()
    update()


def deselect(*args: Any) -> None:
    """Prompt to save unsaved SnapWave boundary polygon changes when leaving the tab.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    changed = False
    if (
        app.toolbox[_TB].open_boundary_polygon_snapwave_changed
        and len(app.toolbox[_TB].open_boundary_polygon_snapwave) > 0
    ):
        changed = True
    if (
        app.toolbox[_TB].neumann_boundary_polygon_snapwave_changed
        and len(app.toolbox[_TB].neumann_boundary_polygon_snapwave) > 0
    ):
        changed = True
    if changed:
        ok = app.gui.window.dialog_yes_no(
            "Your polygons have changed. Would you like to save the changes?"
        )
        if ok:
            if (
                app.toolbox[_TB].open_boundary_polygon_snapwave_changed
                and len(app.toolbox[_TB].open_boundary_polygon_snapwave) > 0
            ):
                save_open_boundary_polygon_snapwave()
            if (
                app.toolbox[_TB].neumann_boundary_polygon_snapwave_changed
                and len(app.toolbox[_TB].neumann_boundary_polygon_snapwave) > 0
            ):
                save_neumann_boundary_polygon_snapwave()


def draw_open_boundary_polygon_snapwave(*args: Any) -> None:
    """Start interactive drawing of a SnapWave open boundary polygon on the map.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    app.map.layer[_TB].layer["open_boundary_polygon_snapwave"].draw()


def delete_open_boundary_polygon_snapwave(*args: Any) -> None:
    """Delete the currently selected SnapWave open boundary polygon.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    if len(app.toolbox[_TB].open_boundary_polygon_snapwave) == 0:
        return
    index = app.gui.getvar(_TB, "open_boundary_polygon_index_snapwave")
    # Delete from map
    gdf = (
        app.map.layer[_TB].layer["open_boundary_polygon_snapwave"].delete_feature(index)
    )
    app.toolbox[_TB].open_boundary_polygon_snapwave = gdf
    app.toolbox[_TB].open_boundary_polygon_snapwave_changed = True
    update()


def load_open_boundary_polygon_snapwave(*args: Any) -> None:
    """Load SnapWave open boundary polygons from a GeoJSON file via a file dialog.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    full_name, path, name, ext, fltr = app.gui.window.dialog_open_file(
        "Select open boundary polygon file ...", filter="*.geojson"
    )
    if not full_name:
        return
    append = False
    if app.gui.getvar(_TB, "nr_open_boundary_polygons_snapwave"):
        append = app.gui.window.dialog_yes_no(
            "Add to existing open boundary polygons?", " "
        )
    app.toolbox[_TB].read_open_boundary_polygon_snapwave(full_name, append)
    app.toolbox[_TB].plot_open_boundary_polygon_snapwave()
    if append:
        app.toolbox[_TB].open_boundary_polygon_snapwave_changed = True
    else:
        save_open_boundary_polygon_snapwave()
    update()


def save_open_boundary_polygon_snapwave(*args: Any) -> None:
    """Save SnapWave open boundary polygons to open_boundary_snapwave.geojson.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    app.gui.window.dialog_fade_label(
        "Saving open boundary polygons to open_boundary_snapwave.geojson ..."
    )
    app.toolbox[_TB].open_boundary_polygon_snapwave_changed = False
    app.toolbox[_TB].write_open_boundary_polygon_snapwave()


def select_open_boundary_polygon_snapwave(*args: Any) -> None:
    """Activate the SnapWave open boundary polygon at the given index on the map.

    Parameters
    ----------
    *args : Any
        The first element is the index of the polygon to select.
    """
    index = args[0]
    app.map.layer[_TB].layer["open_boundary_polygon_snapwave"].activate_feature(index)


def open_boundary_polygon_created_snapwave(
    gdf: gpd.GeoDataFrame, index: int, id: Any
) -> None:
    """Handle creation of a new SnapWave open boundary polygon on the map.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing all SnapWave open boundary polygons.
    index : int
        Index of the created feature.
    id : Any
        Identifier of the created feature.
    """
    app.toolbox[_TB].open_boundary_polygon_snapwave = gdf
    nrp = len(app.toolbox[_TB].open_boundary_polygon_snapwave)
    app.gui.setvar(_TB, "open_boundary_polygon_index_snapwave", nrp - 1)
    app.toolbox[_TB].open_boundary_polygon_snapwave_changed = True
    update()


def open_boundary_polygon_modified_snapwave(
    gdf: gpd.GeoDataFrame, index: int, id: Any
) -> None:
    """Handle modification of a SnapWave open boundary polygon on the map.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing all SnapWave open boundary polygons.
    index : int
        Index of the modified feature.
    id : Any
        Identifier of the modified feature.
    """
    app.toolbox[_TB].open_boundary_polygon_snapwave = gdf
    app.toolbox[_TB].open_boundary_polygon_snapwave_changed = True


def open_boundary_polygon_selected_snapwave(index: int) -> None:
    """Handle selection of a SnapWave open boundary polygon from the map.

    Parameters
    ----------
    index : int
        Index of the selected polygon.
    """
    app.gui.setvar(_TB, "open_boundary_polygon_index_snapwave", index)
    update()


def draw_neumann_boundary_polygon_snapwave(*args: Any) -> None:
    """Start interactive drawing of a SnapWave Neumann boundary polygon on the map.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    app.map.layer[_TB].layer["neumann_boundary_polygon_snapwave"].crs = app.crs
    app.map.layer[_TB].layer["neumann_boundary_polygon_snapwave"].draw()


def delete_neumann_boundary_polygon_snapwave(*args: Any) -> None:
    """Delete the currently selected SnapWave Neumann boundary polygon.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    if len(app.toolbox[_TB].neumann_boundary_polygon_snapwave) == 0:
        return
    index = app.gui.getvar(_TB, "neumann_boundary_polygon_index_snapwave")
    # Delete from map
    gdf = (
        app.map.layer[_TB]
        .layer["neumann_boundary_polygon_snapwave"]
        .delete_feature(index)
    )
    app.toolbox[_TB].neumann_boundary_polygon_snapwave = gdf
    app.toolbox[_TB].neumann_boundary_polygon_snapwave_changed = True
    update()


def load_neumann_boundary_polygon_snapwave(*args: Any) -> None:
    """Load SnapWave Neumann boundary polygons from a GeoJSON file via a file dialog.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    full_name, path, name, ext, fltr = app.gui.window.dialog_open_file(
        "Select neumann boundary polygon file ...", filter="*.geojson"
    )
    if not full_name:
        return
    append = False
    if app.gui.getvar(_TB, "nr_neumann_boundary_polygons_snapwave"):
        append = app.gui.window.dialog_yes_no(
            "Add to existing neumann boundary polygons?", " "
        )
    app.toolbox[_TB].read_neumann_boundary_polygon_snapwave(full_name, append)
    app.toolbox[_TB].plot_neumann_boundary_polygon_snapwave()
    if append:
        app.toolbox[_TB].neumann_boundary_polygon_snapwave_changed = True
    else:
        save_neumann_boundary_polygon_snapwave()
    update()

    app.toolbox[_TB].read_neumann_boundary_polygon_snapwave(full_name, append)
    app.toolbox[_TB].plot_neumann_boundary_polygon_snapwave()
    update()


def save_neumann_boundary_polygon_snapwave(*args: Any) -> None:
    """Save SnapWave Neumann boundary polygons to neumann_boundary_snapwave.geojson.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    app.gui.window.dialog_fade_label(
        "Saving neumann boundary polygons to neumann_boundary_snapwave.geojson ..."
    )
    app.toolbox[_TB].neumann_boundary_polygon_snapwave_changed = False
    app.toolbox[_TB].write_neumann_boundary_polygon_snapwave()


def select_neumann_boundary_polygon_snapwave(*args: Any) -> None:
    """Activate the SnapWave Neumann boundary polygon at the given index on the map.

    Parameters
    ----------
    *args : Any
        The first element is the index of the polygon to select.
    """
    index = args[0]
    app.map.layer[_TB].layer["neumann_boundary_polygon_snapwave"].activate_feature(
        index
    )


def neumann_boundary_polygon_created_snapwave(
    gdf: gpd.GeoDataFrame, index: int, id: Any
) -> None:
    """Handle creation of a new SnapWave Neumann boundary polygon on the map.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing all SnapWave Neumann boundary polygons.
    index : int
        Index of the created feature.
    id : Any
        Identifier of the created feature.
    """
    app.toolbox[_TB].neumann_boundary_polygon_snapwave = gdf
    nrp = len(app.toolbox[_TB].neumann_boundary_polygon_snapwave)
    app.gui.setvar(_TB, "neumann_boundary_polygon_index_snapwave", nrp - 1)
    app.toolbox[_TB].neumann_boundary_polygon_snapwave_changed = True
    update()


def neumann_boundary_polygon_modified_snapwave(
    gdf: gpd.GeoDataFrame, index: int, id: Any
) -> None:
    """Handle modification of a SnapWave Neumann boundary polygon on the map.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing all SnapWave Neumann boundary polygons.
    index : int
        Index of the modified feature.
    id : Any
        Identifier of the modified feature.
    """
    app.toolbox[_TB].neumann_boundary_polygon_snapwave = gdf
    app.toolbox[_TB].neumann_boundary_polygon_snapwave_changed = True


def neumann_boundary_polygon_selected_snapwave(index: int) -> None:
    """Handle selection of a SnapWave Neumann boundary polygon from the map.

    Parameters
    ----------
    index : int
        Index of the selected polygon.
    """
    app.gui.setvar(_TB, "neumann_boundary_polygon_index_snapwave", index)
    update()


def update() -> None:
    """Synchronize GUI variables with the current SnapWave boundary polygon state."""
    # Open
    nrp = len(app.toolbox[_TB].open_boundary_polygon_snapwave)
    names = []
    for ip in range(nrp):
        names.append(str(ip + 1))
    app.gui.setvar(_TB, "nr_open_boundary_polygons_snapwave", nrp)
    app.gui.setvar(_TB, "open_boundary_polygon_names_snapwave", names)
    index = app.gui.getvar(_TB, "open_boundary_polygon_index_snapwave")
    if index > nrp - 1:
        index = max(nrp - 1, 0)
    app.gui.setvar(_TB, "open_boundary_polygon_index_snapwave", index)

    # neumann
    nrp = len(app.toolbox[_TB].neumann_boundary_polygon_snapwave)
    names = []
    for ip in range(nrp):
        names.append(str(ip + 1))
    app.gui.setvar(_TB, "nr_neumann_boundary_polygons_snapwave", nrp)
    app.gui.setvar(_TB, "neumann_boundary_polygon_names_snapwave", names)
    index = app.gui.getvar(_TB, "neumann_boundary_polygon_index_snapwave")
    if index > nrp - 1:
        index = max(nrp - 1, 0)
    app.gui.setvar(_TB, "neumann_boundary_polygon_index_snapwave", index)
    # Update GUI
    app.gui.window.update()


def update_mask_snapwave(*args: Any) -> None:
    """Regenerate the SnapWave boundary-cell mask from current polygons and settings.

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
