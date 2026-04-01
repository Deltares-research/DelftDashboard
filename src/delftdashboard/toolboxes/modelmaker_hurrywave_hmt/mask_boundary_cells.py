"""GUI callbacks for the HurryWave Model Maker Mask Boundary Cells tab.

Handles boundary polygon drawing, loading, saving, and triggering
mask updates for open boundary cells.
"""

from typing import Any

import geopandas as gpd

from delftdashboard.app import app
from delftdashboard.operations import map

_TB = "modelmaker_hurrywave_hmt"
_MODEL = "hurrywave_hmt"


def select(*args: Any) -> None:
    """Activate the Mask Boundary Cells tab and show relevant layers."""
    map.update()
    app.map.layer[_TB].layer["mask_boundary"].activate()
    app.map.layer[_MODEL].layer["grid"].activate()
    app.map.layer[_MODEL].layer["mask"].activate()


def deselect(*args: Any) -> None:
    """Prompt to save unsaved boundary polygon changes on tab switch."""
    if (
        app.toolbox[_TB].boundary_polygon_changed
        and len(app.toolbox[_TB].boundary_polygon) > 0
    ):
        ok = app.gui.window.dialog_yes_no(
            "Your polygons have changed. Would you like to save the changes?"
        )
        if ok:
            save_boundary_polygon()


def draw_boundary_polygon(*args: Any) -> None:
    """Start interactive drawing of a boundary polygon."""
    app.map.layer[_TB].layer["mask_boundary"].crs = app.crs
    app.map.layer[_TB].layer["mask_boundary"].draw()


def delete_boundary_polygon(*args: Any) -> None:
    """Delete the currently selected boundary polygon."""
    if len(app.toolbox[_TB].boundary_polygon) == 0:
        return
    index = app.gui.getvar(_TB, "boundary_polygon_index")
    gdf = app.map.layer[_TB].layer["mask_boundary"].delete_feature(index)
    app.toolbox[_TB].boundary_polygon = gdf
    app.toolbox[_TB].boundary_polygon_changed = True
    if index > len(app.toolbox[_TB].boundary_polygon) - 1:
        app.gui.setvar(
            _TB,
            "boundary_polygon_index",
            len(app.toolbox[_TB].boundary_polygon) - 1,
        )
    update()


def load_boundary_polygon(*args: Any) -> None:
    """Load boundary polygons from a GeoJSON file."""
    full_name, path, name, ext, fltr = app.gui.window.dialog_open_file(
        "Select boundary polygon file ...", filter="*.geojson"
    )
    if not full_name:
        return
    append = False
    if app.gui.getvar(_TB, "nr_boundary_polygons"):
        append = app.gui.window.dialog_yes_no("Add to existing boundary polygons?", " ")
    app.toolbox[_TB].read_boundary_polygon(full_name, append)
    app.toolbox[_TB].plot_boundary_polygon()
    if append:
        app.toolbox[_TB].boundary_polygon_changed = True
    else:
        save_boundary_polygon()
    update()


def save_boundary_polygon(*args: Any) -> None:
    """Save boundary polygons to boundary.geojson."""
    app.gui.window.dialog_fade_label("Saving boundary polygons to boundary.geojson ...")
    app.toolbox[_TB].write_boundary_polygon()
    app.toolbox[_TB].boundary_polygon_changed = False


def select_boundary_polygon(*args: Any) -> None:
    """Highlight the selected boundary polygon on the map."""
    index = args[0]
    feature_id = app.toolbox[_TB].boundary_polygon.loc[index, "id"]
    app.map.layer[_TB].layer["mask_boundary"].activate_feature(feature_id)


def boundary_polygon_created(gdf: gpd.GeoDataFrame, index: int, id: Any) -> None:
    """Handle creation of a new boundary polygon on the map.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        Updated GeoDataFrame with all boundary polygons.
    index : int
        Index of the created feature.
    id : Any
        Feature identifier.
    """
    app.toolbox[_TB].boundary_polygon = gdf
    app.toolbox[_TB].boundary_polygon_changed = True
    nrp = len(app.toolbox[_TB].boundary_polygon)
    app.gui.setvar(_TB, "boundary_polygon_index", nrp - 1)
    update()


def boundary_polygon_modified(gdf: gpd.GeoDataFrame, index: int, id: Any) -> None:
    """Handle modification of a boundary polygon.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        Updated GeoDataFrame.
    index : int
        Index of the modified feature.
    id : Any
        Feature identifier.
    """
    app.toolbox[_TB].boundary_polygon = gdf
    app.toolbox[_TB].boundary_polygon_changed = True


def boundary_polygon_selected(index: int) -> None:
    """Sync the GUI when a boundary polygon is selected on the map.

    Parameters
    ----------
    index : int
        Index of the selected polygon.
    """
    app.gui.setvar(_TB, "boundary_polygon_index", index)
    update()


def update() -> None:
    """Refresh boundary polygon counts and names in the GUI."""
    nrp = len(app.toolbox[_TB].boundary_polygon)
    app.gui.setvar(_TB, "nr_boundary_polygons", nrp)
    app.gui.setvar(_TB, "boundary_polygon_names", [str(ip + 1) for ip in range(nrp)])
    app.gui.window.update()


def update_mask(*args: Any) -> None:
    """Trigger mask recomputation."""
    app.toolbox[_TB].update_mask()


def cut_inactive_cells(*args: Any) -> None:
    """Remove inactive cells from the grid."""
    app.toolbox[_TB].cut_inactive_cells()
