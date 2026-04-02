"""GUI callbacks for the SnapWave mask-active-cells tab (SFINCS CHT variant, legacy)."""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map

_TB = "modelmaker_sfincs_cht"
_MODEL = "sfincs_cht"


def select(*args: Any) -> None:
    """Activate the SnapWave mask tab and show relevant map layers."""
    map.update()
    # Show the mask include and exclude polygons
    app.map.layer[_TB].layer["include_polygon_snapwave"].activate()
    app.map.layer[_TB].layer["exclude_polygon_snapwave"].activate()
    # Show the grid and mask
    app.map.layer[_MODEL].layer["grid"].activate()
    app.map.layer[_MODEL].layer["mask_include_snapwave"].activate()
    update()


def draw_include_polygon_snapwave(*args: Any) -> None:
    """Start interactive drawing of a SnapWave include polygon."""
    app.map.layer[_TB].layer["include_polygon_snapwave"].crs = app.crs
    app.map.layer[_TB].layer["include_polygon_snapwave"].draw()


def delete_include_polygon_snapwave(*args: Any) -> None:
    """Delete the currently selected SnapWave include polygon."""
    if len(app.toolbox[_TB].include_polygon_snapwave) == 0:
        return
    index = app.gui.getvar(_TB, "include_polygon_index_snapwave")
    gdf = app.map.layer[_TB].layer["include_polygon_snapwave"].delete_feature(index)
    app.toolbox[_TB].include_polygon_snapwave = gdf
    update()


def load_include_polygon_snapwave(*args: Any) -> None:
    """Open a file dialog and load SnapWave include polygons from a file."""
    fname, okay = app.gui.window.dialog_open_file(
        "Select include polygon file ...", filter="*.geojson"
    )
    if not okay:
        return
    app.gui.setvar(_TB, "include_polygon_file_snapwave", fname[2])
    app.toolbox[_TB].read_include_polygon_snapwave()
    app.toolbox[_TB].plot_include_polygon_snapwave()


def save_include_polygon_snapwave(*args: Any) -> None:
    """Save the SnapWave include polygons to a file."""
    app.toolbox[_TB].write_include_polygon_snapwave()


def select_include_polygon_snapwave(*args: Any) -> None:
    """Activate the SnapWave include polygon feature at the given index.

    Parameters
    ----------
    *args : Any
        First element is the polygon index.
    """
    index = args[0]
    app.map.layer[_TB].layer["include_polygon_snapwave"].activate_feature(index)


def include_polygon_created_snapwave(gdf: Any, index: int, id: Any) -> None:
    """Store a newly drawn SnapWave include polygon.

    Parameters
    ----------
    gdf : GeoDataFrame
        The GeoDataFrame containing the drawn polygons.
    index : int
        Index of the created feature.
    id : Any
        Feature identifier.
    """
    app.toolbox[_TB].include_polygon_snapwave = gdf
    nrp = len(app.toolbox[_TB].include_polygon_snapwave)
    app.gui.setvar(_TB, "include_polygon_index_snapwave", nrp - 1)
    update()


def include_polygon_modified_snapwave(gdf: Any, index: int, id: Any) -> None:
    """Update the stored SnapWave include polygon after modification.

    Parameters
    ----------
    gdf : GeoDataFrame
        The modified GeoDataFrame.
    index : int
        Index of the modified feature.
    id : Any
        Feature identifier.
    """
    app.toolbox[_TB].include_polygon_snapwave = gdf


def include_polygon_selected_snapwave(index: int) -> None:
    """Handle selection of a SnapWave include polygon on the map.

    Parameters
    ----------
    index : int
        Index of the selected polygon.
    """
    app.gui.setvar(_TB, "include_polygon_index_snapwave", index)
    update()


def draw_exclude_polygon_snapwave(*args: Any) -> None:
    """Start interactive drawing of a SnapWave exclude polygon."""
    app.map.layer[_TB].layer["include_polygon_snapwave"].crs = app.crs
    app.map.layer[_TB].layer["exclude_polygon_snapwave"].draw()


def delete_exclude_polygon_snapwave(*args: Any) -> None:
    """Delete the currently selected SnapWave exclude polygon."""
    if len(app.toolbox[_TB].exclude_polygon_snapwave) == 0:
        return
    index = app.gui.getvar(_TB, "exclude_polygon_index_snapwave")
    gdf = app.map.layer[_TB].layer["exclude_polygon_snapwave"].delete_feature(index)
    app.toolbox[_TB].exclude_polygon_snapwave = gdf
    update()


def load_exclude_polygon_snapwave(*args: Any) -> None:
    """Open a file dialog and load SnapWave exclude polygons from a file."""
    fname, okay = app.gui.window.dialog_open_file(
        "Select exclude polygon file ...", filter="*.geojson"
    )
    if not okay:
        return
    app.gui.setvar(_TB, "exclude_polygon_file_snapwave", fname[2])
    app.toolbox[_TB].read_exclude_polygon_snapwave()
    app.toolbox[_TB].plot_exclude_polygon_snapwave()


def save_exclude_polygon_snapwave(*args: Any) -> None:
    """Save the SnapWave exclude polygons to a file."""
    app.toolbox[_TB].write_exclude_polygon_snapwave()


def select_exclude_polygon_snapwave(*args: Any) -> None:
    """Activate the SnapWave exclude polygon feature at the given index.

    Parameters
    ----------
    *args : Any
        First element is the polygon index.
    """
    index = args[0]
    app.map.layer[_TB].layer["exclude_polygon_snapwave"].activate_feature(index)


def exclude_polygon_created_snapwave(gdf: Any, index: int, id: Any) -> None:
    """Store a newly drawn SnapWave exclude polygon.

    Parameters
    ----------
    gdf : GeoDataFrame
        The GeoDataFrame containing the drawn polygons.
    index : int
        Index of the created feature.
    id : Any
        Feature identifier.
    """
    app.toolbox[_TB].exclude_polygon_snapwave = gdf
    nrp = len(app.toolbox[_TB].exclude_polygon_snapwave)
    app.gui.setvar(_TB, "exclude_polygon_index_snapwave", nrp - 1)
    update()


def exclude_polygon_modified_snapwave(gdf: Any, index: int, id: Any) -> None:
    """Update the stored SnapWave exclude polygon after modification.

    Parameters
    ----------
    gdf : GeoDataFrame
        The modified GeoDataFrame.
    index : int
        Index of the modified feature.
    id : Any
        Feature identifier.
    """
    app.toolbox[_TB].exclude_polygon_snapwave = gdf


def exclude_polygon_selected_snapwave(index: int) -> None:
    """Handle selection of a SnapWave exclude polygon on the map.

    Parameters
    ----------
    index : int
        Index of the selected polygon.
    """
    app.gui.setvar(_TB, "exclude_polygon_index_snapwave", index)
    update()


def update() -> None:
    """Synchronize the GUI with the current SnapWave polygon state."""
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
    """Update the SnapWave active cell mask."""
    app.toolbox[_TB].update_mask_snapwave()


def cut_inactive_cells(*args: Any) -> None:
    """Remove inactive cells from the grid."""
    app.toolbox[_TB].cut_inactive_cells()
