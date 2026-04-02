"""GUI callbacks for the boundary-cell mask tab of the SFINCS HMT model-maker toolbox.

Handles drawing, loading, saving, and selecting boundary polygons for open,
downstream, Neumann, and outflow boundary types on the SFINCS flow grid.
"""

from typing import Any

import geopandas as gpd

from delftdashboard.app import app
from delftdashboard.operations import map

_TB = "modelmaker_sfincs_hmt"
_MODEL = "sfincs_hmt"


def select(*args: Any) -> None:
    """Activate the boundary mask tab and display all boundary polygon layers.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    map.update()
    # Show the boundary polygons
    app.map.layer[_TB].layer["open_boundary_polygon"].activate()
    app.map.layer[_TB].layer["downstream_boundary_polygon"].activate()
    app.map.layer[_TB].layer["neumann_boundary_polygon"].activate()
    app.map.layer[_TB].layer["outflow_boundary_polygon"].activate()
    # Show the grid and mask
    app.map.layer[_MODEL].layer["grid"].activate()
    app.map.layer[_MODEL].layer["mask"].activate()
    update()


def deselect(*args: Any) -> None:
    """Prompt to save unsaved boundary polygon changes when leaving the tab.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    changed = False
    if (
        app.toolbox[_TB].open_boundary_polygon_changed
        and len(app.toolbox[_TB].open_boundary_polygon) > 0
    ):
        changed = True
    if (
        app.toolbox[_TB].downstream_boundary_polygon_changed
        and len(app.toolbox[_TB].downstream_boundary_polygon) > 0
    ):
        changed = True
    if (
        app.toolbox[_TB].neumann_boundary_polygon_changed
        and len(app.toolbox[_TB].neumann_boundary_polygon) > 0
    ):
        changed = True
    if (
        app.toolbox[_TB].outflow_boundary_polygon_changed
        and len(app.toolbox[_TB].outflow_boundary_polygon) > 0
    ):
        changed = True
    if changed:
        ok = app.gui.window.dialog_yes_no(
            "Your polygons have changed. Would you like to save the changes?"
        )
        if ok:
            if (
                app.toolbox[_TB].open_boundary_polygon_changed
                and len(app.toolbox[_TB].open_boundary_polygon) > 0
            ):
                save_open_boundary_polygon()
            if (
                app.toolbox[_TB].downstream_boundary_polygon_changed
                and len(app.toolbox[_TB].downstream_boundary_polygon) > 0
            ):
                save_downstream_boundary_polygon()
            if (
                app.toolbox[_TB].neumann_boundary_polygon_changed
                and len(app.toolbox[_TB].neumann_boundary_polygon) > 0
            ):
                save_neumann_boundary_polygon()
            if (
                app.toolbox[_TB].outflow_boundary_polygon_changed
                and len(app.toolbox[_TB].outflow_boundary_polygon) > 0
            ):
                save_outflow_boundary_polygon()


# Open boundary (water level)


def draw_open_boundary_polygon(*args: Any) -> None:
    """Start interactive drawing of an open boundary polygon on the map.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    app.map.layer[_TB].layer["open_boundary_polygon"].draw()


def delete_open_boundary_polygon(*args: Any) -> None:
    """Delete the currently selected open boundary polygon.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    if len(app.toolbox[_TB].open_boundary_polygon) == 0:
        return
    index = app.gui.getvar(_TB, "open_boundary_polygon_index")
    # Delete from map
    gdf = app.map.layer[_TB].layer["open_boundary_polygon"].delete_feature(index)
    app.toolbox[_TB].open_boundary_polygon = gdf
    app.toolbox[_TB].open_boundary_polygon_changed = True
    update()


def load_open_boundary_polygon(*args: Any) -> None:
    """Load open boundary polygons from a GeoJSON file via a file dialog.

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
    if app.gui.getvar(_TB, "nr_open_boundary_polygons"):
        append = app.gui.window.dialog_yes_no(
            "Add to existing open boundary polygons?", " "
        )
    app.toolbox[_TB].read_open_boundary_polygon(full_name, append)
    app.toolbox[_TB].plot_open_boundary_polygon()
    if append:
        app.toolbox[_TB].open_boundary_polygon_changed = True
    else:
        save_open_boundary_polygon()
    update()


def save_open_boundary_polygon(*args: Any) -> None:
    """Save open boundary polygons to open_boundary.geojson.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    app.gui.window.dialog_fade_label(
        "Saving open boundary polygons to open_boundary.geojson ..."
    )
    app.toolbox[_TB].open_boundary_polygon_changed = False
    app.toolbox[_TB].write_open_boundary_polygon()


def select_open_boundary_polygon(*args: Any) -> None:
    """Activate the open boundary polygon at the given index on the map.

    Parameters
    ----------
    *args : Any
        The first element is the index of the polygon to select.
    """
    index = args[0]
    app.map.layer[_TB].layer["open_boundary_polygon"].activate_feature(index)


def open_boundary_polygon_created(gdf: gpd.GeoDataFrame, index: int, id: Any) -> None:
    """Handle creation of a new open boundary polygon on the map.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing all open boundary polygons.
    index : int
        Index of the created feature.
    id : Any
        Identifier of the created feature.
    """
    app.toolbox[_TB].open_boundary_polygon = gdf
    nrp = len(app.toolbox[_TB].open_boundary_polygon)
    app.gui.setvar(_TB, "open_boundary_polygon_index", nrp - 1)
    app.toolbox[_TB].open_boundary_polygon_changed = True
    update()


def open_boundary_polygon_modified(gdf: gpd.GeoDataFrame, index: int, id: Any) -> None:
    """Handle modification of an open boundary polygon on the map.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing all open boundary polygons.
    index : int
        Index of the modified feature.
    id : Any
        Identifier of the modified feature.
    """
    app.toolbox[_TB].open_boundary_polygon = gdf
    app.toolbox[_TB].open_boundary_polygon_changed = True


def open_boundary_polygon_selected(index: int) -> None:
    """Handle selection of an open boundary polygon from the map.

    Parameters
    ----------
    index : int
        Index of the selected polygon.
    """
    app.gui.setvar(_TB, "open_boundary_polygon_index", index)
    update()


# Downstream boundary


def draw_downstream_boundary_polygon(*args: Any) -> None:
    """Start interactive drawing of a downstream boundary polygon on the map.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    app.map.layer[_TB].layer["downstream_boundary_polygon"].draw()


def delete_downstream_boundary_polygon(*args: Any) -> None:
    """Delete the currently selected downstream boundary polygon.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    if len(app.toolbox[_TB].downstream_boundary_polygon) == 0:
        return
    index = app.gui.getvar(_TB, "downstream_boundary_polygon_index")
    # Delete from map
    gdf = app.map.layer[_TB].layer["downstream_boundary_polygon"].delete_feature(index)
    app.toolbox[_TB].downstream_boundary_polygon = gdf
    app.toolbox[_TB].downstream_boundary_polygon_changed = True
    update()


def load_downstream_boundary_polygon(*args: Any) -> None:
    """Load downstream boundary polygons from a GeoJSON file via a file dialog.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    full_name, path, name, ext, fltr = app.gui.window.dialog_open_file(
        "Select downstream boundary polygon file ...", filter="*.geojson"
    )
    if not full_name:
        return
    append = False
    if app.gui.getvar(_TB, "nr_downstream_boundary_polygons"):
        append = app.gui.window.dialog_yes_no(
            "Add to existing downstream boundary polygons?", " "
        )
    app.toolbox[_TB].read_downstream_boundary_polygon(full_name, append)
    app.toolbox[_TB].plot_downstream_boundary_polygon()
    if append:
        app.toolbox[_TB].downstream_boundary_polygon_changed = True
    else:
        save_downstream_boundary_polygon()
    update()


def save_downstream_boundary_polygon(*args: Any) -> None:
    """Save downstream boundary polygons to downstream_boundary.geojson.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    app.gui.window.dialog_fade_label(
        "Saving downstream boundary polygons to downstream_boundary.geojson ..."
    )
    app.toolbox[_TB].downstream_boundary_polygon_changed = False
    app.toolbox[_TB].write_downstream_boundary_polygon()


def select_downstream_boundary_polygon(*args: Any) -> None:
    """Activate the downstream boundary polygon at the given index on the map.

    Parameters
    ----------
    *args : Any
        The first element is the index of the polygon to select.
    """
    index = args[0]
    app.map.layer[_TB].layer["downstream_boundary_polygon"].activate_feature(index)


def downstream_boundary_polygon_created(
    gdf: gpd.GeoDataFrame, index: int, id: Any
) -> None:
    """Handle creation of a new downstream boundary polygon on the map.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing all downstream boundary polygons.
    index : int
        Index of the created feature.
    id : Any
        Identifier of the created feature.
    """
    app.toolbox[_TB].downstream_boundary_polygon = gdf
    nrp = len(app.toolbox[_TB].downstream_boundary_polygon)
    app.gui.setvar(_TB, "downstream_boundary_polygon_index", nrp - 1)
    app.toolbox[_TB].downstream_boundary_polygon_changed = True
    update()


def downstream_boundary_polygon_modified(
    gdf: gpd.GeoDataFrame, index: int, id: Any
) -> None:
    """Handle modification of a downstream boundary polygon on the map.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing all downstream boundary polygons.
    index : int
        Index of the modified feature.
    id : Any
        Identifier of the modified feature.
    """
    app.toolbox[_TB].downstream_boundary_polygon = gdf
    app.toolbox[_TB].downstream_boundary_polygon_changed = True


def downstream_boundary_polygon_selected(index: int) -> None:
    """Handle selection of a downstream boundary polygon from the map.

    Parameters
    ----------
    index : int
        Index of the selected polygon.
    """
    app.gui.setvar(_TB, "downstream_boundary_polygon_index", index)
    update()


# Neumann boundary


def draw_neumann_boundary_polygon(*args: Any) -> None:
    """Start interactive drawing of a Neumann boundary polygon on the map.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    app.map.layer[_TB].layer["neumann_boundary_polygon"].draw()


def delete_neumann_boundary_polygon(*args: Any) -> None:
    """Delete the currently selected Neumann boundary polygon.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    if len(app.toolbox[_TB].neumann_boundary_polygon) == 0:
        return
    index = app.gui.getvar(_TB, "neumann_boundary_polygon_index")
    # Delete from map
    gdf = app.map.layer[_TB].layer["neumann_boundary_polygon"].delete_feature(index)
    app.toolbox[_TB].neumann_boundary_polygon = gdf
    update()


def load_neumann_boundary_polygon(*args: Any) -> None:
    """Load Neumann boundary polygons from a GeoJSON file via a file dialog.

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
    if app.gui.getvar(_TB, "nr_neumann_boundary_polygons"):
        append = app.gui.window.dialog_yes_no(
            "Add to existing neumann boundary polygons?", " "
        )
    app.toolbox[_TB].read_neumann_boundary_polygon(full_name, append)
    app.toolbox[_TB].plot_neumann_boundary_polygon()
    if append:
        app.toolbox[_TB].neumann_boundary_polygon_changed = True
    else:
        save_neumann_boundary_polygon()
    update()


def save_neumann_boundary_polygon(*args: Any) -> None:
    """Save Neumann boundary polygons to neumann_boundary.geojson.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    app.gui.window.dialog_fade_label(
        "Saving neumann boundary polygons to neumann_boundary.geojson ..."
    )
    app.toolbox[_TB].neumann_boundary_polygon_changed = False
    app.toolbox[_TB].write_neumann_boundary_polygon()


def select_neumann_boundary_polygon(*args: Any) -> None:
    """Activate the Neumann boundary polygon at the given index on the map.

    Parameters
    ----------
    *args : Any
        The first element is the index of the polygon to select.
    """
    index = args[0]
    app.map.layer[_TB].layer["neumann_boundary_polygon"].activate_feature(index)


def neumann_boundary_polygon_created(
    gdf: gpd.GeoDataFrame, index: int, id: Any
) -> None:
    """Handle creation of a new Neumann boundary polygon on the map.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing all Neumann boundary polygons.
    index : int
        Index of the created feature.
    id : Any
        Identifier of the created feature.
    """
    app.toolbox[_TB].neumann_boundary_polygon = gdf
    nrp = len(app.toolbox[_TB].neumann_boundary_polygon)
    app.gui.setvar(_TB, "neumann_boundary_polygon_index", nrp - 1)
    app.toolbox[_TB].neumann_boundary_polygon_changed = True
    update()


def neumann_boundary_polygon_modified(
    gdf: gpd.GeoDataFrame, index: int, id: Any
) -> None:
    """Handle modification of a Neumann boundary polygon on the map.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing all Neumann boundary polygons.
    index : int
        Index of the modified feature.
    id : Any
        Identifier of the modified feature.
    """
    app.toolbox[_TB].neumann_boundary_polygon = gdf
    app.toolbox[_TB].neumann_boundary_polygon_changed = True


def neumann_boundary_polygon_selected(index: int) -> None:
    """Handle selection of a Neumann boundary polygon from the map.

    Parameters
    ----------
    index : int
        Index of the selected polygon.
    """
    app.gui.setvar(_TB, "neumann_boundary_polygon_index", index)
    update()


# Outflow boundary


def draw_outflow_boundary_polygon(*args: Any) -> None:
    """Start interactive drawing of an outflow boundary polygon on the map.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    app.map.layer[_TB].layer["outflow_boundary_polygon"].crs = app.crs
    app.map.layer[_TB].layer["outflow_boundary_polygon"].draw()


def delete_outflow_boundary_polygon(*args: Any) -> None:
    """Delete the currently selected outflow boundary polygon.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    if len(app.toolbox[_TB].outflow_boundary_polygon) == 0:
        return
    index = app.gui.getvar(_TB, "outflow_boundary_polygon_index")
    # Delete from map
    gdf = app.map.layer[_TB].layer["outflow_boundary_polygon"].delete_feature(index)
    app.toolbox[_TB].outflow_boundary_polygon = gdf
    update()


def load_outflow_boundary_polygon(*args: Any) -> None:
    """Load outflow boundary polygons from a GeoJSON file via a file dialog.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    full_name, path, name, ext, fltr = app.gui.window.dialog_open_file(
        "Select outflow boundary polygon file ...", filter="*.geojson"
    )
    if not full_name:
        return
    append = False
    if app.gui.getvar(_TB, "nr_outflow_boundary_polygons"):
        append = app.gui.window.dialog_yes_no(
            "Add to existing outflow boundary polygons?", " "
        )
    app.toolbox[_TB].read_outflow_boundary_polygon(full_name, append)
    app.toolbox[_TB].plot_outflow_boundary_polygon()
    update()


def save_outflow_boundary_polygon(*args: Any) -> None:
    """Save outflow boundary polygons to outflow_boundary.geojson.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    app.gui.window.dialog_fade_label(
        "Saving outflow boundary polygons to outflow_boundary.geojson ..."
    )
    app.toolbox[_TB].outflow_boundary_polygon_changed = False
    app.toolbox[_TB].write_outflow_boundary_polygon()


def select_outflow_boundary_polygon(*args: Any) -> None:
    """Activate the outflow boundary polygon at the given index on the map.

    Parameters
    ----------
    *args : Any
        The first element is the index of the polygon to select.
    """
    index = args[0]
    app.map.layer[_TB].layer["outflow_boundary_polygon"].activate_feature(index)


def outflow_boundary_polygon_created(
    gdf: gpd.GeoDataFrame, index: int, id: Any
) -> None:
    """Handle creation of a new outflow boundary polygon on the map.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing all outflow boundary polygons.
    index : int
        Index of the created feature.
    id : Any
        Identifier of the created feature.
    """
    app.toolbox[_TB].outflow_boundary_polygon = gdf
    nrp = len(app.toolbox[_TB].outflow_boundary_polygon)
    app.gui.setvar(_TB, "outflow_boundary_polygon_index", nrp - 1)
    app.toolbox[_TB].outflow_boundary_polygon_changed = True
    update()


def outflow_boundary_polygon_modified(
    gdf: gpd.GeoDataFrame, index: int, id: Any
) -> None:
    """Handle modification of an outflow boundary polygon on the map.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing all outflow boundary polygons.
    index : int
        Index of the modified feature.
    id : Any
        Identifier of the modified feature.
    """
    app.toolbox[_TB].outflow_boundary_polygon = gdf
    app.toolbox[_TB].outflow_boundary_polygon_changed = True


def outflow_boundary_polygon_selected(index: int) -> None:
    """Handle selection of an outflow boundary polygon from the map.

    Parameters
    ----------
    index : int
        Index of the selected polygon.
    """
    app.gui.setvar(_TB, "outflow_boundary_polygon_index", index)
    update()


def update() -> None:
    """Synchronize GUI variables with the current boundary polygon state."""
    # Open
    nrp = len(app.toolbox[_TB].open_boundary_polygon)
    names = []
    for ip in range(nrp):
        names.append(str(ip + 1))
    app.gui.setvar(_TB, "nr_open_boundary_polygons", nrp)
    app.gui.setvar(_TB, "open_boundary_polygon_names", names)
    index = app.gui.getvar(_TB, "open_boundary_polygon_index")
    if index > nrp - 1:
        index = max(nrp - 1, 0)
    app.gui.setvar(_TB, "open_boundary_polygon_index", index)

    # Downstream
    nrp = len(app.toolbox[_TB].downstream_boundary_polygon)
    names = []
    for ip in range(nrp):
        names.append(str(ip + 1))
    app.gui.setvar(_TB, "nr_downstream_boundary_polygons", nrp)
    app.gui.setvar(_TB, "downstream_boundary_polygon_names", names)
    index = app.gui.getvar(_TB, "downstream_boundary_polygon_index")
    if index > nrp - 1:
        index = max(nrp - 1, 0)
    app.gui.setvar(_TB, "downstream_boundary_polygon_index", index)

    # Neumann
    nrp = len(app.toolbox[_TB].neumann_boundary_polygon)
    names = []
    for ip in range(nrp):
        names.append(str(ip + 1))
    app.gui.setvar(_TB, "nr_neumann_boundary_polygons", nrp)
    app.gui.setvar(_TB, "neumann_boundary_polygon_names", names)
    index = app.gui.getvar(_TB, "neumann_boundary_polygon_index")
    if index > nrp - 1:
        index = max(nrp - 1, 0)
    app.gui.setvar(_TB, "neumann_boundary_polygon_index", index)

    # Outflow
    nrp = len(app.toolbox[_TB].outflow_boundary_polygon)
    names = []
    for ip in range(nrp):
        names.append(str(ip + 1))
    app.gui.setvar(_TB, "nr_outflow_boundary_polygons", nrp)
    app.gui.setvar(_TB, "outflow_boundary_polygon_names", names)
    index = app.gui.getvar(_TB, "outflow_boundary_polygon_index")
    if index > nrp - 1:
        index = max(nrp - 1, 0)
    app.gui.setvar(_TB, "outflow_boundary_polygon_index", index)
    # Update GUI
    app.gui.window.update()


def update_mask(*args: Any) -> None:
    """Regenerate the boundary-cell mask from the current polygons and settings.

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
