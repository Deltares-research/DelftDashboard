"""GUI callbacks for the mask-active-cells tab (SFINCS CHT variant, legacy)."""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map

_TB = "modelmaker_sfincs_cht"
_MODEL = "sfincs_cht"


def select(*args: Any) -> None:
    """Activate the mask tab and show include/exclude polygon layers."""
    map.update()
    # Show the mask include and exclude polygons
    app.map.layer[_TB].layer["include_polygon"].activate()
    app.map.layer[_TB].layer["exclude_polygon"].activate()
    # Show the grid and mask
    app.map.layer[_MODEL].layer["grid"].activate()
    app.map.layer[_MODEL].layer["mask_include"].activate()
    app.map.layer[_MODEL].layer["mask_open_boundary"].activate()
    app.map.layer[_MODEL].layer["mask_outflow_boundary"].activate()
    update()


def draw_include_polygon(*args: Any) -> None:
    """Start interactive drawing of an include polygon on the map."""
    app.map.layer[_TB].layer["include_polygon"].crs = app.crs
    app.map.layer[_TB].layer["include_polygon"].draw()


def delete_include_polygon(*args: Any) -> None:
    """Delete the currently selected include polygon."""
    if len(app.toolbox[_TB].include_polygon) == 0:
        return
    index = app.gui.getvar(_TB, "include_polygon_index")
    gdf = app.map.layer[_TB].layer["include_polygon"].delete_feature(index)
    app.toolbox[_TB].include_polygon = gdf
    update()


def load_include_polygon(*args: Any) -> None:
    """Open a file dialog and load include polygons from a GeoJSON file."""
    full_name, path, name, ext, fltr = app.gui.window.dialog_open_file(
        "Select include polygon file ...", filter="*.geojson"
    )
    okay = True
    if not okay:
        return
    app.gui.setvar(_TB, "include_polygon_file", name)
    app.toolbox[_TB].read_include_polygon()
    app.toolbox[_TB].plot_include_polygon()
    update()


def save_include_polygon(*args: Any) -> None:
    """Save the include polygons to a file."""
    app.toolbox[_TB].write_include_polygon()


def select_include_polygon(*args: Any) -> None:
    """Activate the include polygon feature at the given index on the map.

    Parameters
    ----------
    *args : Any
        First element is the polygon index.
    """
    index = args[0]
    app.map.layer[_TB].layer["include_polygon"].activate_feature(index)


def include_polygon_created(gdf: Any, index: int, id: Any) -> None:
    """Store a newly drawn include polygon.

    Parameters
    ----------
    gdf : GeoDataFrame
        The GeoDataFrame containing the drawn polygons.
    index : int
        Index of the created feature.
    id : Any
        Feature identifier.
    """
    app.toolbox[_TB].include_polygon = gdf
    nrp = len(app.toolbox[_TB].include_polygon)
    app.gui.setvar(_TB, "include_polygon_index", nrp - 1)
    update()


def include_polygon_modified(gdf: Any, index: int, id: Any) -> None:
    """Update the stored include polygon after the user modifies it.

    Parameters
    ----------
    gdf : GeoDataFrame
        The modified GeoDataFrame.
    index : int
        Index of the modified feature.
    id : Any
        Feature identifier.
    """
    app.toolbox[_TB].include_polygon = gdf


def include_polygon_selected(index: int) -> None:
    """Handle selection of an include polygon on the map.

    Parameters
    ----------
    index : int
        Index of the selected polygon.
    """
    app.gui.setvar(_TB, "include_polygon_index", index)
    update()


def draw_exclude_polygon(*args: Any) -> None:
    """Start interactive drawing of an exclude polygon on the map."""
    #    app.map.layer[_TB].layer["include_polygon"].crs = app.crs
    app.map.layer[_TB].layer["exclude_polygon"].draw()


def delete_exclude_polygon(*args: Any) -> None:
    """Delete the currently selected exclude polygon."""
    if len(app.toolbox[_TB].exclude_polygon) == 0:
        return
    index = app.gui.getvar(_TB, "exclude_polygon_index")
    # Delete from map
    gdf = app.map.layer[_TB].layer["exclude_polygon"].delete_feature(index)
    app.toolbox[_TB].exclude_polygon = gdf
    update()


def load_exclude_polygon(*args: Any) -> None:
    """Open a file dialog and load exclude polygons from a GeoJSON file."""
    fname, okay = app.gui.window.dialog_open_file(
        "Select exclude polygon file ...", filter="*.geojson"
    )
    if not okay:
        return
    app.gui.setvar(_TB, "exclude_polygon_file", fname[2])
    app.toolbox[_TB].read_exclude_polygon()
    app.toolbox[_TB].plot_exclude_polygon()
    update()


def save_exclude_polygon(*args: Any) -> None:
    """Save the exclude polygons to a file."""
    app.toolbox[_TB].write_exclude_polygon()


def select_exclude_polygon(*args: Any) -> None:
    """Activate the exclude polygon feature at the given index on the map.

    Parameters
    ----------
    *args : Any
        First element is the polygon index.
    """
    index = args[0]
    app.map.layer[_TB].layer["exclude_polygon"].activate_feature(index)


def exclude_polygon_created(gdf: Any, index: int, id: Any) -> None:
    """Store a newly drawn exclude polygon.

    Parameters
    ----------
    gdf : GeoDataFrame
        The GeoDataFrame containing the drawn polygons.
    index : int
        Index of the created feature.
    id : Any
        Feature identifier.
    """
    app.toolbox[_TB].exclude_polygon = gdf
    nrp = len(app.toolbox[_TB].exclude_polygon)
    app.gui.setvar(_TB, "exclude_polygon_index", nrp - 1)
    update()


def exclude_polygon_modified(gdf: Any, index: int, id: Any) -> None:
    """Update the stored exclude polygon after the user modifies it.

    Parameters
    ----------
    gdf : GeoDataFrame
        The modified GeoDataFrame.
    index : int
        Index of the modified feature.
    id : Any
        Feature identifier.
    """
    app.toolbox[_TB].exclude_polygon = gdf


def exclude_polygon_selected(index: int) -> None:
    """Handle selection of an exclude polygon on the map.

    Parameters
    ----------
    index : int
        Index of the selected polygon.
    """
    app.gui.setvar(_TB, "exclude_polygon_index", index)
    update()


def update() -> None:
    """Synchronize the GUI with the current include/exclude polygon state."""
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
    """Update the active cell mask based on current polygons."""
    app.toolbox[_TB].update_mask()


def cut_inactive_cells(*args: Any) -> None:
    """Remove inactive cells from the grid."""
    app.toolbox[_TB].cut_inactive_cells()
