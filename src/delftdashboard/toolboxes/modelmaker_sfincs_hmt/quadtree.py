"""GUI callbacks for the quadtree refinement tab of the SFINCS HMT model-maker toolbox.

Handles drawing, loading, saving, and selecting quadtree refinement polygons
and their associated refinement levels and elevation bounds.
"""

from typing import Any

import geopandas as gpd

from delftdashboard.app import app
from delftdashboard.operations import map

_TB = "modelmaker_sfincs_hmt"
_MODEL = "sfincs_hmt"


def select(*args: Any) -> None:
    """Activate the quadtree tab and display refinement-related map layers.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    map.update()
    # Show the refinement layer
    app.map.layer[_TB].layer["quadtree_refinement"].activate()
    app.map.layer[_MODEL].layer["grid"].activate()
    app.map.layer[_TB].layer["grid_outline"].activate()
    # Strings for refinement levels
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
    """Prompt to save unsaved refinement polygon changes when leaving the tab.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    if len(app.toolbox[_TB].refinement_polygon) == 0:
        return
    if app.toolbox[_TB].refinement_polygons_changed:
        ok = app.gui.window.dialog_yes_no(
            "The refinement polygons have changed. Would you like to save the changes?"
        )
        if ok:
            save_refinement_polygon()


def draw_refinement_polygon(*args: Any) -> None:
    """Start interactive drawing of a refinement polygon on the map.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    app.map.layer[_TB].layer["quadtree_refinement"].crs = app.crs
    app.map.layer[_TB].layer["quadtree_refinement"].draw()


def delete_refinement_polygon(*args: Any) -> None:
    """Delete the currently selected refinement polygon.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    if len(app.toolbox[_TB].refinement_polygon) == 0:
        return
    index = app.gui.getvar(_TB, "refinement_polygon_index")
    # Delete from app
    app.toolbox[_TB].refinement_polygon = app.toolbox[_TB].refinement_polygon.drop(
        index
    )
    if len(app.toolbox[_TB].refinement_polygon) > 0:
        app.toolbox[_TB].refinement_polygon = app.toolbox[
            _TB
        ].refinement_polygon.reset_index(drop=True)
    app.toolbox[_TB].plot_refinement_polygon()

    # If the last polygon was deleted, set index to last available polygon
    if index > len(app.toolbox[_TB].refinement_polygon) - 1:
        index = max(len(app.toolbox[_TB].refinement_polygon) - 1, 0)
        app.gui.setvar(_TB, "refinement_polygon_index", index)

    app.toolbox[_TB].refinement_polygons_changed = True

    update()


def load_refinement_polygon(*args: Any) -> None:
    """Load refinement polygons from a GeoJSON file via a file dialog.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
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
        # We want to save it as quadtree.geojson (just in case the original file
        # has a different name, or does not specify the refinememnt levels)
        save_refinement_polygon()
        # app.toolbox[_TB].write_refinement_polygon()
        # app.toolbox[_TB].refinement_polygons_changed = False

    update()


def save_refinement_polygon(*args: Any) -> None:
    """Save refinement polygons to the quadtree.geojson file.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    app.gui.window.dialog_fade_label(
        "Saving refinement polygons to quadtree.geojson ..."
    )
    app.toolbox[_TB].write_refinement_polygon()
    app.toolbox[_TB].refinement_polygons_changed = False


def select_refinement_polygon(*args: Any) -> None:
    """Activate the refinement polygon at the given index on the map.

    Parameters
    ----------
    *args : Any
        The first element is the index of the polygon to select.
    """
    index = args[0]
    app.map.layer[_TB].layer["quadtree_refinement"].activate_feature(index)


def select_refinement_level(*args: Any) -> None:
    """Set the refinement level for the currently selected polygon.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    # level_index = args[0]
    level_index = app.gui.getvar(_TB, "refinement_polygon_level")
    # Get index of selected polygon
    index = app.gui.getvar(_TB, "refinement_polygon_index")
    app.toolbox[_TB].refinement_polygon.at[index, "refinement_level"] = level_index + 1
    app.toolbox[_TB].refinement_polygons_changed = True
    update()


def edit_zmin_zmax(*args: Any) -> None:
    """Update zmin/zmax elevation bounds for the currently selected polygon.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    # Get index of selected polygon
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
        GeoDataFrame containing all refinement polygons.
    index : int
        Index of the created feature.
    feature_id : Any
        Identifier of the created feature.
    """
    app.toolbox[_TB].refinement_polygon = gdf
    nrp = len(app.toolbox[_TB].refinement_polygon)
    app.gui.setvar(_TB, "refinement_polygon_index", nrp - 1)
    app.toolbox[_TB].refinement_polygons_changed = True
    update()


def refinement_polygon_modified(gdf: gpd.GeoDataFrame, index: int, id: Any) -> None:
    """Handle modification of a refinement polygon on the map.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing all refinement polygons.
    index : int
        Index of the modified feature.
    id : Any
        Identifier of the modified feature.
    """
    app.toolbox[_TB].refinement_polygon = gdf
    app.toolbox[_TB].refinement_polygons_changed = True


def refinement_polygon_selected(index: int) -> None:
    """Handle selection of a refinement polygon from the map.

    Parameters
    ----------
    index : int
        Index of the selected polygon.
    """
    app.gui.setvar(_TB, "refinement_polygon_index", index)
    update()


def update() -> None:
    """Synchronize GUI variables with the current refinement polygon state."""
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
    if nrp > 0:
        for ip in range(nrp):
            ilev = int(app.toolbox[_TB].refinement_polygon.loc[ip, "refinement_level"])
            refnames.append(f"{ip + 1} ({levstr[ilev - 1]})")
    else:
        pass
    app.gui.setvar(_TB, "nr_refinement_polygons", nrp)
    app.gui.setvar(_TB, "refinement_polygon_names", refnames)
    # Now update the refinement_polygon_level
    if nrp > 0:
        ilev = app.toolbox[_TB].refinement_polygon.at[index, "refinement_level"]
        app.gui.setvar(_TB, "refinement_polygon_level", ilev - 1)
    else:
        app.gui.setvar(_TB, "refinement_polygon_level", 0)
    # And update the GUI
    app.gui.window.update()


def build_quadtree_grid(*args: Any) -> None:
    """Build the quadtree grid, validating polygon elevation bounds first.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    # First check if zmin and zmax are set for any of the polygons. If so, check that bathy sets have been defined. If not, give a warning.
    # Loop though polygons
    zminzmax = False
    for i, row in app.toolbox[_TB].refinement_polygon.iterrows():
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
