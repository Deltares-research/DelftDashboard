"""GUI callbacks for Delft3D-FM observation cross-section management."""

from pathlib import Path
from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map

_MODEL = "delft3dfm"


def select(*args: Any) -> None:
    """Activate the cross-sections layer when the tab is selected."""
    map.update()
    app.map.layer[_MODEL].layer["cross_sections"].activate()
    update()


def deselect(*args: Any) -> None:
    """Prompt the user to save unsaved cross-section changes on tab deselect."""
    if app.model[_MODEL].cross_sections_changed:
        ok = app.gui.window.dialog_yes_no(
            "The cross sections have changed. Would you like to save the changes?"
        )
        if ok:
            save()
        else:
            app.model[_MODEL].cross_sections_changed = False
    app.map.layer[_MODEL].layer["cross_sections"].hide()
    update()


def edit(*args: Any) -> None:
    """Apply GUI edits to the domain model variables."""
    app.model[_MODEL].set_model_variables()


def load(*args: Any) -> None:
    """Open a cross-section file via dialog and load it into the model."""
    map.reset_cursor()
    rsp = app.gui.window.dialog_open_file(
        "Select file ...",
        file_name="obs_crs.pli",
        filter="*_crs.pli",
        allow_directory_change=False,
    )
    if rsp[0]:
        app.model[_MODEL].domain.input.output.crsfile = rsp[0]
        app.model[_MODEL].domain.cross_sections.read()
        gdf = app.model[_MODEL].domain.cross_sections.gdf
        app.map.layer[_MODEL].layer["cross_sections"].set_data(gdf)
        app.gui.setvar(_MODEL, "active_cross_section", 0)
        update()
    app.model[_MODEL].cross_sections_changed = False


def save(*args: Any) -> None:
    """Save cross-sections to a user-selected file."""
    from hydrolib.core.dflowfm import ObservationCrossSectionModel

    map.reset_cursor()
    rsp = app.gui.window.dialog_save_file(
        "Select file ...",
        file_name="delft3dfm_crs.pli",
        filter=None,
        allow_directory_change=False,
    )
    if rsp[0]:
        app.model[_MODEL].domain.input.output.crsfile = []
        app.model[_MODEL].domain.input.output.crsfile.append(
            ObservationCrossSectionModel()
        )
        app.model[_MODEL].domain.input.output.crsfile[0].filepath = Path(rsp[2])
        app.model[_MODEL].domain.cross_sections.write()
    app.model[_MODEL].cross_sections_changed = False


def draw_cross_section(*args: Any) -> None:
    """Enable interactive cross-section drawing on the map."""
    app.map.layer[_MODEL].layer["cross_sections"].draw()


def delete_cross_section(*args: Any) -> None:
    """Delete the currently selected cross-section from the model and map."""
    gdf = app.model[_MODEL].domain.cross_sections.gdf
    if len(gdf) == 0:
        return
    index = app.gui.getvar(_MODEL, "active_cross_section")
    app.map.layer[_MODEL].layer["cross_sections"].delete_feature(index)
    app.model[_MODEL].domain.cross_sections.delete(index)
    app.gui.setvar(_MODEL, "active_cross_section", index)
    app.model[_MODEL].cross_sections_changed = True
    update()


def select_cross_section_from_list(*args: Any) -> None:
    """Activate the cross-section selected in the GUI list on the map."""
    map.reset_cursor()
    index = app.gui.getvar(_MODEL, "active_cross_section")
    app.map.layer[_MODEL].layer["cross_sections"].activate_feature(index)
    update()


def cross_section_created(gdf: Any, index: int, id: Any) -> None:
    """Handle creation of a new cross-section drawn on the map.

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
        name, okay = app.gui.window.dialog_string("Edit name for new cross section")
        if not okay:
            app.map.layer[_MODEL].layer["cross_sections"].delete_feature(index)
            return
        if name in app.gui.getvar(_MODEL, "cross_section_names"):
            app.gui.window.dialog_info(
                "A cross section with this name already exists !"
            )
        else:
            break
    new_crs = gdf.loc[[index]]
    new_crs["name"] = name
    app.model[_MODEL].domain.cross_sections.add(new_crs)
    gdf = app.model[_MODEL].domain.cross_sections.gdf
    app.map.layer[_MODEL].layer["cross_sections"].set_data(gdf)
    nrt = len(gdf)
    app.gui.setvar(_MODEL, "active_cross_section", nrt - 1)
    app.model[_MODEL].cross_sections_changed = True
    update()


def cross_section_modified(gdf: Any, index: int, id: Any) -> None:
    """Handle modification of an existing cross-section on the map.

    Parameters
    ----------
    gdf : Any
        GeoDataFrame containing the updated features.
    index : int
        Index of the modified feature.
    id : Any
        Feature identifier from the map layer.
    """
    app.model[_MODEL].domain.cross_sections.gdf = gdf
    app.model[_MODEL].cross_sections_changed = True
    update()


def cross_section_selected(index: int) -> None:
    """Handle selection of a cross-section on the map.

    Parameters
    ----------
    index : int
        Index of the selected cross-section.
    """
    app.gui.setvar(_MODEL, "active_cross_section", index)
    update()


def set_model_variables(*args: Any) -> None:
    """Copy all GUI variable values into the domain input object."""
    app.model[_MODEL].set_model_variables()


def update() -> None:
    """Refresh cross-section names and counts in the GUI."""
    nrt = len(app.model[_MODEL].domain.cross_sections.gdf)
    app.gui.setvar(_MODEL, "nr_cross_sections", nrt)
    if app.gui.getvar(_MODEL, "active_cross_section") > nrt - 1:
        app.gui.setvar(_MODEL, "active_cross_section", max(nrt - 1, 0))
    iac = app.gui.getvar(_MODEL, "active_cross_section")
    names = app.model[_MODEL].domain.cross_sections.list_names()
    app.gui.setvar(_MODEL, "cross_section_names", names)
    if nrt > 0:
        app.gui.setvar(_MODEL, "cross_section_name", names[iac])
    else:
        app.gui.setvar(_MODEL, "cross_section_name", "")
    app.gui.window.update()
