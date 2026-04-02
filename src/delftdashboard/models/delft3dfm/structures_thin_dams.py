"""GUI callbacks for Delft3D-FM thin dam structure management."""

from pathlib import Path
from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map

_MODEL = "delft3dfm"


def select(*args: Any) -> None:
    """Activate the thin dams layer when the tab is selected."""
    map.update()
    app.map.layer[_MODEL].layer["thin_dams"].activate()
    update()


def deselect(*args: Any) -> None:
    """Prompt the user to save unsaved thin dam changes on tab deselect."""
    if app.model[_MODEL].thin_dams_changed:
        ok = app.gui.window.dialog_yes_no(
            "The thin dams have changed. Would you like to save the changes?"
        )
        if ok:
            save()
        else:
            app.model[_MODEL].thin_dams_changed = False
    app.map.layer[_MODEL].layer["thin_dams"].hide()
    update()


def load(*args: Any) -> None:
    """Open a thin dam file via dialog and load it into the model."""
    map.reset_cursor()
    rsp = app.gui.window.dialog_open_file(
        "Select file ...", filter="*_thd.pli", allow_directory_change=False
    )
    if rsp[0]:
        app.model[_MODEL].domain.input.geometry.thindamfile = rsp[0]
        app.model[_MODEL].domain.thin_dams.read()
        gdf = app.model[_MODEL].domain.thin_dams.gdf
        app.map.layer[_MODEL].layer["thin_dams"].set_data(gdf)
        app.gui.setvar(_MODEL, "active_thin_dam", 0)
        update()
    app.model[_MODEL].thin_dams_changed = False


def save(*args: Any) -> None:
    """Save thin dams to a user-selected file."""
    from hydrolib.core.dflowfm import ObservationCrossSectionModel

    map.reset_cursor()
    filename = app.model[_MODEL].domain.input.geometry.thindamfile
    if not filename:
        filename = "delft3dfm_thd.pli"
    rsp = app.gui.window.dialog_save_file(
        "Select file ...",
        file_name=filename,
        filter="*.pli",
        allow_directory_change=False,
    )
    if rsp[0]:
        app.model[_MODEL].domain.input.geometry.thindamfile = []
        app.model[_MODEL].domain.input.geometry.thindamfile.append(
            ObservationCrossSectionModel()
        )
        app.model[_MODEL].domain.input.geometry.thindamfile[0].filepath = Path(rsp[2])
        app.model[_MODEL].domain.thin_dams.write()
    app.model[_MODEL].thin_dams_changed = False


def draw_thin_dam(*args: Any) -> None:
    """Enable interactive thin dam drawing on the map."""
    app.map.layer[_MODEL].layer["thin_dams"].draw()


def delete_thin_dam(*args: Any) -> None:
    """Delete the currently selected thin dam from the model and map."""
    gdf = app.model[_MODEL].domain.thin_dams.gdf
    if len(gdf) == 0:
        return
    index = app.gui.getvar(_MODEL, "active_thin_dam")
    app.map.layer[_MODEL].layer["thin_dams"].delete_feature(index)
    app.model[_MODEL].domain.thin_dams.delete(index)
    app.gui.setvar(_MODEL, "active_thin_dam", index)
    app.model[_MODEL].thin_dams_changed = True
    update()


def select_thin_dam(*args: Any) -> None:
    """Activate the thin dam selected in the GUI list on the map."""
    map.reset_cursor()
    index = app.gui.getvar(_MODEL, "active_thin_dam")
    app.map.layer[_MODEL].layer["thin_dams"].activate_feature(index)
    update()


def thin_dam_created(gdf: Any, index: int, id: Any) -> None:
    """Handle creation of a new thin dam drawn on the map.

    Parameters
    ----------
    gdf : Any
        GeoDataFrame containing the drawn features.
    index : int
        Index of the newly created feature.
    id : Any
        Feature identifier from the map layer.
    """
    while True:
        name, okay = app.gui.window.dialog_string("Edit name for new thin dam")
        if not okay:
            app.map.layer[_MODEL].layer["thin_dams"].delete_feature(index)
            return
        if name in app.gui.getvar(_MODEL, "thin_dam_names"):
            app.gui.window.dialog_info("A thin dam with this name already exists !")
        else:
            break
    new_thd = gdf.loc[[index]]
    new_thd["name"] = name
    app.model[_MODEL].domain.thin_dams.add(new_thd)
    gdf = app.model[_MODEL].domain.thin_dams.gdf
    app.map.layer[_MODEL].layer["thin_dams"].set_data(gdf)
    nrt = len(gdf)
    app.gui.setvar(_MODEL, "active_thin_dam", nrt - 1)
    app.model[_MODEL].thin_dams_changed = True
    update()


def thin_dam_modified(gdf: Any, index: int, id: Any) -> None:
    """Handle modification of an existing thin dam on the map.

    Parameters
    ----------
    gdf : Any
        GeoDataFrame containing the updated features.
    index : int
        Index of the modified feature.
    id : Any
        Feature identifier from the map layer.
    """
    app.model[_MODEL].domain.thin_dams.gdf = gdf
    app.model[_MODEL].thin_dams_changed = True
    update()


def thin_dam_selected(index: int) -> None:
    """Handle selection of a thin dam on the map.

    Parameters
    ----------
    index : int
        Index of the selected thin dam.
    """
    app.gui.setvar(_MODEL, "active_thin_dam", index)
    update()


def set_model_variables(*args: Any) -> None:
    """Copy all GUI variable values into the domain input object."""
    app.model[_MODEL].set_model_variables()


def update() -> None:
    """Refresh thin dam names and counts in the GUI."""
    nrt = len(app.model[_MODEL].domain.thin_dams.gdf)
    app.gui.setvar(_MODEL, "nr_thin_dams", nrt)
    if app.gui.getvar(_MODEL, "active_thin_dam") > nrt - 1:
        app.gui.setvar(_MODEL, "active_thin_dam", max(nrt - 1, 0))
    iac = app.gui.getvar(_MODEL, "active_thin_dam")
    names = app.model[_MODEL].domain.thin_dams.list_names()
    app.gui.setvar(_MODEL, "thin_dam_names", names)
    if nrt > 0:
        app.gui.setvar(_MODEL, "thin_dam_name", names[iac])
    else:
        app.gui.setvar(_MODEL, "thin_dam_name", "")
    app.gui.window.update()
