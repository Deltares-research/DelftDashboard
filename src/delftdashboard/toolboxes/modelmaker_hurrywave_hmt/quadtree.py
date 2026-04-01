"""GUI callbacks for the HurryWave Model Maker Quadtree tab.

Handles drawing, editing, loading, and saving refinement polygons,
and triggering quadtree grid generation.
"""

from typing import Any

import geopandas as gpd

from delftdashboard.app import app
from delftdashboard.operations import map

_TB = "modelmaker_hurrywave_hmt"
_MODEL = "hurrywave_hmt"


def select(*args: Any) -> None:
    """Activate the Quadtree tab and compute refinement level labels."""
    map.update()
    app.map.layer[_TB].layer["quadtree_refinement"].activate()
    app.map.layer[_MODEL].layer["grid"].activate()
    app.map.layer[_TB].layer["grid_outline"].activate()
    levstr = []
    for i in range(10):
        dx = app.gui.getvar(_TB, "dx")
        if app.map.crs.is_geographic:
            sfx = f"{dx / (2 ** (i + 1))}°  ~{int(dx * 111000 / (2 ** (i + 1)))} m"
        else:
            sfx = f"{dx / (2 ** (i + 1))} m"
        levstr.append(f"x{2 ** (i + 1)} ({sfx})")
    app.gui.setvar(_TB, "refinement_polygon_levels", levstr)
    app.gui.window.statusbar.show_message(
        "Select refinement polygon(s) and set refinement levels.", 5000
    )
    update()


def deselect(*args: Any) -> None:
    """Prompt to save unsaved refinement polygon changes on tab switch."""
    if len(app.toolbox[_TB].refinement_polygon) == 0:
        return
    if app.toolbox[_TB].refinement_polygons_changed:
        ok = app.gui.window.dialog_yes_no(
            "The refinement polygons have changed. Would you like to save the changes?"
        )
        if ok:
            save_refinement_polygon()


def draw_refinement_polygon(*args: Any) -> None:
    """Start interactive polygon drawing for refinement zones."""
    app.map.layer[_TB].layer["quadtree_refinement"].crs = app.crs
    app.map.layer[_TB].layer["quadtree_refinement"].draw()


def delete_refinement_polygon(*args: Any) -> None:
    """Delete the currently selected refinement polygon."""
    if len(app.toolbox[_TB].refinement_polygon) == 0:
        return
    index = app.gui.getvar(_TB, "refinement_polygon_index")
    app.toolbox[_TB].refinement_polygon = app.toolbox[_TB].refinement_polygon.drop(
        index
    )
    if len(app.toolbox[_TB].refinement_polygon) > 0:
        app.toolbox[_TB].refinement_polygon = app.toolbox[
            _TB
        ].refinement_polygon.reset_index(drop=True)
    app.toolbox[_TB].plot_refinement_polygon()
    if index > len(app.toolbox[_TB].refinement_polygon) - 1:
        index = max(len(app.toolbox[_TB].refinement_polygon) - 1, 0)
        app.gui.setvar(_TB, "refinement_polygon_index", index)
    app.toolbox[_TB].refinement_polygons_changed = True
    update()


def load_refinement_polygon(*args: Any) -> None:
    """Load refinement polygons from a GeoJSON file."""
    full_name, path, name, ext, fltr = app.gui.window.dialog_open_file(
        "Select refinement polygon file ...", filter="*.geojson"
    )
    if not full_name:
        return
    append = False
    if app.gui.getvar(_TB, "nr_refinement_polygons") > 0:
        append = app.gui.window.dialog_yes_no(
            "Add to existing refinement polygons?", " "
        )
    app.toolbox[_TB].read_refinement_polygon(full_name, append)
    app.toolbox[_TB].plot_refinement_polygon()
    if append:
        app.toolbox[_TB].refinement_polygons_changed = True
    else:
        save_refinement_polygon()
    update()


def save_refinement_polygon(*args: Any) -> None:
    """Save refinement polygons to quadtree.geojson."""
    app.gui.window.dialog_fade_label(
        "Saving refinement polygons to quadtree.geojson ..."
    )
    app.toolbox[_TB].write_refinement_polygon()
    app.toolbox[_TB].refinement_polygons_changed = False


def select_refinement_polygon(*args: Any) -> None:
    """Highlight the selected refinement polygon on the map."""
    index = args[0]
    app.map.layer[_TB].layer["quadtree_refinement"].activate_feature(index)


def select_refinement_level(*args: Any) -> None:
    """Assign the chosen refinement level to the selected polygon."""
    level_index = app.gui.getvar(_TB, "refinement_polygon_level")
    index = app.gui.getvar(_TB, "refinement_polygon_index")
    app.toolbox[_TB].refinement_polygon.at[index, "refinement_level"] = level_index + 1
    app.toolbox[_TB].refinement_polygons_changed = True
    update()


def edit_zmin_zmax(*args: Any) -> None:
    """Update elevation thresholds for the selected refinement polygon."""
    index = app.gui.getvar(_TB, "refinement_polygon_index")
    app.toolbox[_TB].refinement_polygon.at[index, "zmin"] = app.gui.getvar(
        _TB, "refinement_polygon_zmin"
    )
    app.toolbox[_TB].refinement_polygon.at[index, "zmax"] = app.gui.getvar(
        _TB, "refinement_polygon_zmax"
    )
    update()


def refinement_polygon_created(
    gdf: gpd.GeoDataFrame, index: int, feature_id: Any
) -> None:
    """Handle creation of a new refinement polygon on the map.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        Updated GeoDataFrame with all refinement polygons.
    index : int
        Index of the created feature.
    feature_id : Any
        Feature identifier.
    """
    app.toolbox[_TB].refinement_polygon = gdf
    nrp = len(app.toolbox[_TB].refinement_polygon)
    app.gui.setvar(_TB, "refinement_polygon_index", nrp - 1)
    app.toolbox[_TB].refinement_polygons_changed = True
    update()


def refinement_polygon_modified(gdf: gpd.GeoDataFrame, index: int, id: Any) -> None:
    """Handle modification of an existing refinement polygon.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        Updated GeoDataFrame.
    index : int
        Index of the modified feature.
    id : Any
        Feature identifier.
    """
    app.toolbox[_TB].refinement_polygon = gdf
    app.toolbox[_TB].refinement_polygons_changed = True


def refinement_polygon_selected(index: int) -> None:
    """Sync the GUI when a refinement polygon is selected on the map.

    Parameters
    ----------
    index : int
        Index of the selected polygon.
    """
    app.gui.setvar(_TB, "refinement_polygon_index", index)
    update()


def update() -> None:
    """Refresh refinement polygon names and attributes in the GUI."""
    index = app.gui.getvar(_TB, "refinement_polygon_index")
    nrp = len(app.toolbox[_TB].refinement_polygon)
    if nrp > 0:
        zmin = app.toolbox[_TB].refinement_polygon.loc[index, "zmin"]
        zmax = app.toolbox[_TB].refinement_polygon.loc[index, "zmax"]
        app.gui.setvar(_TB, "refinement_polygon_zmin", zmin)
        app.gui.setvar(_TB, "refinement_polygon_zmax", zmax)
    else:
        app.gui.setvar(_TB, "refinement_polygon_zmin", -1000000.0)
        app.gui.setvar(_TB, "refinement_polygon_zmax", 1000000.0)
    refnames = []
    levstr = app.gui.getvar(_TB, "refinement_polygon_levels")
    for ip in range(nrp):
        ilev = int(app.toolbox[_TB].refinement_polygon.loc[ip, "refinement_level"])
        refnames.append(f"{ip + 1} ({levstr[ilev - 1]})")
    app.gui.setvar(_TB, "nr_refinement_polygons", nrp)
    app.gui.setvar(_TB, "refinement_polygon_names", refnames)
    if nrp > 0:
        ilev = app.toolbox[_TB].refinement_polygon.at[index, "refinement_level"]
        app.gui.setvar(_TB, "refinement_polygon_level", ilev - 1)
    else:
        app.gui.setvar(_TB, "refinement_polygon_level", 0)
    app.gui.window.update()


def build_quadtree_grid(*args: Any) -> None:
    """Validate inputs and trigger quadtree grid generation."""
    zminzmax = False
    for _i, row in app.toolbox[_TB].refinement_polygon.iterrows():
        if row["zmin"] > -20000.0 or row["zmax"] < 20000.0:
            zminzmax = True
    if zminzmax:
        if (
            app.gui.getvar("bathy_topo_selector", "nr_selected_bathymetry_datasets")
            == 0
        ):
            app.gui.window.dialog_warning(
                "Please select at least one bathymetry dataset (see next tab)."
            )
            return
    nmax = app.gui.getvar(_TB, "nmax")
    mmax = app.gui.getvar(_TB, "mmax")
    if nmax == 0 or mmax == 0:
        app.gui.window.dialog_warning("Please first draw bounding box for grid.")
        return
    app.toolbox[_TB].generate_grid()
