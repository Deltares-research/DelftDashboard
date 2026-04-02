"""GUI callbacks for the SFINCS HydroMT Wave Makers sub-tab.

Handles drawing, editing, deleting, loading, saving, and importing
wave maker polylines used for internal wave generation.
"""

from typing import Any

import geopandas as gpd

from delftdashboard.app import app
from delftdashboard.operations import map

_MODEL = "sfincs_hmt"
_GROUP = "sfincs_hmt"


def select(*args: Any) -> None:
    """Activate the Wave Makers sub-tab and show polylines on map."""
    map.update()
    app.map.layer[_MODEL].layer["wave_makers"].activate()
    update()


def deselect(*args: Any) -> None:
    """Prompt to save unsaved wave maker changes when leaving the tab."""
    if app.model[_MODEL].wave_makers_changed:
        if app.model[_MODEL].domain.wave_makers.nr_lines == 0:
            # No wave makers, so just reset the flag and return
            app.model[_MODEL].wave_makers_changed = False
            return
        ok = app.gui.window.dialog_yes_no(
            "The wave makers have changed. Would you like to save the changes?"
        )
        if ok:
            save()


def set_model_variables(*args: Any) -> None:
    """Copy current GUI variables back to the model config."""
    app.model[_MODEL].set_model_variables()


def add_on_map(*args: Any) -> None:
    """Start the map draw interaction for a new wave maker polyline."""
    app.map.layer[_MODEL].layer["wave_makers"].draw()


def select_from_list(*args: Any) -> None:
    """Select a wave maker on the map from the GUI list.

    Parameters
    ----------
    *args : Any
        First element is the list index.
    """
    index = args[0]
    feature_id = app.model[_MODEL].domain.wave_makers.gdf.loc[index, "id"]
    app.map.layer[_MODEL].layer["wave_makers"].activate_feature(feature_id)


def delete_from_list(*args: Any) -> None:
    """Delete the currently selected wave maker.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    map.reset_cursor()
    index = app.gui.getvar(_GROUP, "active_wave_maker")
    app.model[_MODEL].domain.wave_makers.delete(index)
    gdf = app.model[_MODEL].domain.wave_makers.gdf
    index = max(min(index, len(gdf) - 1), 0)
    app.map.layer[_MODEL].layer["wave_makers"].set_data(gdf)
    app.gui.setvar(_GROUP, "active_wave_maker", index)
    app.model[_MODEL].wave_makers_changed = True
    update()


def wave_maker_created(gdf: Any, index: int, id: Any) -> None:
    """Handle creation of a new wave maker polyline on the map.

    Parameters
    ----------
    gdf : GeoDataFrame
        The GeoDataFrame containing all wave maker features.
    index : int
        Index of the newly created feature.
    id : Any
        Feature identifier.
    """
    app.model[_MODEL].domain.wave_makers.set(gdf, merge=False)
    nrp = len(app.model[_MODEL].domain.wave_makers.gdf)
    app.gui.setvar(_GROUP, "active_wave_maker", nrp - 1)
    app.model[_MODEL].wave_makers_changed = True
    update()


def wave_maker_modified(gdf: Any, index: int, id: Any) -> None:
    """Handle modification of an existing wave maker polyline.

    Parameters
    ----------
    gdf : GeoDataFrame
        The GeoDataFrame containing all wave maker features.
    index : int
        Index of the modified feature.
    id : Any
        Feature identifier.
    """
    app.model[_MODEL].domain.wave_makers.set(gdf, merge=False)
    app.model[_MODEL].wave_makers_changed = True


def wave_maker_selected(index: int) -> None:
    """Handle selection of a wave maker on the map.

    Parameters
    ----------
    index : int
        Index of the selected wave maker.
    """
    app.gui.setvar(_GROUP, "active_wave_maker", index)
    update()


def load(*args: Any) -> None:
    """Load wave makers from a .wvm file selected by the user.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    map.reset_cursor()
    rsp = app.gui.window.dialog_open_file(
        "Select file ...",
        file_name="sfincs.wvm",
        filter="*.wvm",
        allow_directory_change=False,
    )
    if rsp[0]:
        app.model[_MODEL].domain.config.set("wvmfile", rsp[2])
        app.model[_MODEL].domain.wave_makers.read()
        gdf = app.model[_MODEL].domain.wave_makers.gdf
        app.map.layer[_MODEL].layer["wave_makers"].set_data(gdf)
        app.gui.setvar(_GROUP, "active_wave_maker", 0)
        app.model[_MODEL].wave_makers_changed = False
        update()


def import_geojson(*args: Any) -> None:
    """Import wave makers from a GeoJSON file.

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
        app.model[_MODEL].domain.wave_makers.set(gdf, merge=False)
        app.map.layer[_MODEL].layer["wave_makers"].set_data(gdf)
        app.gui.setvar(_GROUP, "active_wave_maker", 0)
        app.model[_MODEL].wave_makers_changed = True
        update()


def save(*args: Any) -> None:
    """Save wave makers to a .wvm file selected by the user.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    filename = app.model[_MODEL].domain.config.get("wvmfile")
    if not filename:
        filename = "sfincs.wvm"
    rsp = app.gui.window.dialog_save_file(
        "Select file ...",
        file_name=filename,
        filter="*.wvm",
        allow_directory_change=False,
    )
    if rsp[0]:
        app.model[_MODEL].domain.config.set("wvmfile", rsp[2])
        app.model[_MODEL].domain.wave_makers.write()
    app.model[_MODEL].wave_makers_changed = False


def update() -> None:
    """Refresh the wave maker list and count in the GUI."""
    gdf = app.model[_MODEL].domain.wave_makers.gdf
    app.gui.setvar(
        _GROUP, "wave_maker_names", app.model[_MODEL].domain.wave_makers.list_names
    )
    app.gui.setvar(_GROUP, "nr_wave_makers", len(gdf))
    app.gui.window.update()
