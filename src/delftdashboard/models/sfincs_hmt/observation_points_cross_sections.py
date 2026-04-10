"""GUI callbacks for the SFINCS HydroMT Cross Sections sub-tab.

Handles drawing, editing, deleting, loading, and saving cross-section
polylines, including grid snapping and map interaction callbacks.
"""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map

_MODEL = "sfincs_hmt"
_GROUP = "sfincs_hmt"


def select(*args: Any) -> None:
    """Activate the Cross Sections sub-tab and show polylines on map."""
    map.update()
    # Activate draw layer
    app.map.layer[_MODEL].layer["cross_sections"].layer["polylines"].activate()
    app.map.layer[_MODEL].layer["cross_sections"].layer["snapped"].activate()
    update()


def deselect(*args: Any) -> None:
    """Prompt to save unsaved cross section changes when leaving the tab."""
    if app.model[_MODEL].cross_sections_changed:
        if app.model[_MODEL].domain.cross_sections.nr_lines == 0:
            # No cross sections, so just reset the flag and return
            app.model[_MODEL].cross_sections_changed = False
            return
        ok = app.gui.window.dialog_yes_no(
            "The cross sections have changed. Would you like to save the changes?"
        )
        if ok:
            save()


def load(*args: Any) -> None:
    """Load cross sections from a .crs file selected by the user.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    map.reset_cursor()
    rsp = app.gui.window.dialog_open_file(
        "Select file ...",
        file_name="sfincs.crs",
        filter="*.crs",
        allow_directory_change=False,
    )
    if rsp[0]:
        app.model[_MODEL].domain.config.set("crsfile", rsp[2])
        app.model[_MODEL].domain.cross_sections.read()
        gdf = app.model[_MODEL].domain.cross_sections.gdf
        app.map.layer[_MODEL].layer["cross_sections"].layer["polylines"].set_data(gdf)
        app.gui.setvar(_GROUP, "active_cross_section", 0)
        update()
    app.model[_MODEL].cross_sections_changed = False


def save(*args: Any) -> None:
    """Save cross sections to a .crs file selected by the user.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    map.reset_cursor()
    filename = app.model[_MODEL].domain.config.get("crsfile")
    if not filename:
        filename = "sfincs.crs"
    rsp = app.gui.window.dialog_save_file(
        "Select file ...",
        file_name=filename,
        filter="*.crs",
        allow_directory_change=False,
    )
    if rsp[0]:
        app.model[_MODEL].domain.config.set("crsfile", rsp[2])
        app.model[_MODEL].domain.cross_sections.write()
    app.model[_MODEL].cross_sections_changed = False


def draw_cross_section(*args: Any) -> None:
    """Start the map draw interaction for a new cross section polyline."""
    app.map.layer[_MODEL].layer["cross_sections"].layer["polylines"].draw()


def delete_cross_section(*args: Any) -> None:
    """Delete the currently selected cross section.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    gdf = app.model[_MODEL].domain.cross_sections.gdf
    if len(gdf) == 0:
        return
    index = app.gui.getvar(_GROUP, "active_cross_section")
    # Delete from map
    app.map.layer[_MODEL].layer["cross_sections"].layer["polylines"].delete_feature(
        index
    )
    # Delete from app
    app.model[_MODEL].domain.cross_sections.delete(index)
    app.model[_MODEL].cross_sections_changed = True
    update()

    # update_grid_snapper()


def select_cross_section_from_list(*args: Any) -> None:
    """Select a cross section on the map from the GUI list.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    map.reset_cursor()
    index = app.gui.getvar(_GROUP, "active_cross_section")
    app.map.layer[_MODEL].layer["cross_sections"].layer["polylines"].activate_feature(
        index
    )
    update()


def edit_name(*args: Any) -> None:
    """Rename the currently selected cross section.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    name = app.gui.getvar(_GROUP, "cross_section_name")
    index = app.gui.getvar(_GROUP, "active_cross_section")
    # Trim the name
    name = name.strip()
    # Check that name is not empty
    if len(name) == 0:
        return
    # Check it does not already exist
    if name in app.model[_MODEL].domain.cross_sections.list_names:
        app.gui.window.dialog_info("A cross section with this name already exists !")
        return
    gdf = app.model[_MODEL].domain.cross_sections.gdf
    gdf.at[index, "name"] = name
    app.map.layer[_MODEL].layer["cross_sections"].layer["polylines"].set_data(gdf)
    update()


def cross_section_created(gdf: Any, index: int, id: Any) -> None:
    """Handle creation of a new cross section polyline on the map.

    Parameters
    ----------
    gdf : GeoDataFrame
        The GeoDataFrame containing all cross section features.
    index : int
        Index of the newly created feature.
    id : Any
        Feature identifier.
    """
    name, okay = app.gui.window.dialog_string("Edit name for new cross section")
    if not okay:
        # Cancel was clicked
        return
    if name in app.gui.getvar(_GROUP, "cross_section_names"):
        app.gui.window.dialog_info("A cross section with this name already exists !")
        # Keep asking until a unique name is given or cancel is clicked
        while name in app.gui.getvar(_GROUP, "cross_section_names"):
            name, okay = app.gui.window.dialog_string("Edit name for new cross section")
            if not okay:
                # Cancel was clicked
                return
    new_crs = gdf.loc[[index]]
    # add "name" to gdf
    new_crs["name"] = name
    # app.model[_MODEL].domain.cross_sections.add(new_crs)
    app.model[_MODEL].domain.cross_sections.create(new_crs, merge=True)
    # Need to update map layer because name has changed
    gdf = app.model[_MODEL].domain.cross_sections.gdf
    app.map.layer[_MODEL].layer["cross_sections"].layer["polylines"].set_data(gdf)
    nrt = len(gdf)
    app.gui.setvar(_GROUP, "active_cross_section", nrt - 1)
    app.model[_MODEL].cross_sections_changed = True
    update()


def cross_section_modified(gdf: Any, index: int, id: Any) -> None:
    """Handle modification of an existing cross section polyline.

    Parameters
    ----------
    gdf : GeoDataFrame
        The GeoDataFrame containing all cross section features.
    index : int
        Index of the modified feature.
    id : Any
        Feature identifier.
    """
    app.model[_MODEL].domain.cross_sections.set(gdf, merge=False)
    app.model[_MODEL].cross_sections_changed = True
    update()


def cross_section_selected(index: int) -> None:
    """Handle selection of a cross section on the map.

    Parameters
    ----------
    index : int
        Index of the selected cross section.
    """
    app.gui.setvar(_GROUP, "active_cross_section", index)
    update()


def set_model_variables(*args: Any) -> None:
    """Copy current GUI variables back to the model config."""
    app.model[_MODEL].set_model_variables()


def update_grid_snapper() -> None:
    """Snap cross sections to the grid and update the snapped layer."""
    snap_gdf = app.model[_MODEL].domain.cross_sections.snap_to_grid()
    if len(snap_gdf) > 0:
        app.map.layer[_MODEL].layer["cross_sections"].layer["snapped"].set_data(
            snap_gdf
        )


def update() -> None:
    """Refresh the cross section list and active name in the GUI."""
    nrt = len(app.model[_MODEL].domain.cross_sections.gdf)
    app.gui.setvar(_GROUP, "nr_cross_sections", nrt)
    if app.gui.getvar(_GROUP, "active_cross_section") > nrt - 1:
        app.gui.setvar(_GROUP, "active_cross_section", max(nrt - 1, 0))
    iac = app.gui.getvar(_GROUP, "active_cross_section")
    names = app.model[_MODEL].domain.cross_sections.list_names
    app.gui.setvar(_GROUP, "cross_section_names", names)
    if nrt > 0:
        app.gui.setvar(_GROUP, "cross_section_name", names[iac])
    else:
        app.gui.setvar(_GROUP, "cross_section_name", "")
    app.gui.window.update()
