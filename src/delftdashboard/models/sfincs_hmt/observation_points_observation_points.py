"""GUI callbacks for the SFINCS HydroMT Observation Points sub-tab.

Handles adding, deleting, editing, loading, and saving observation
points, as well as map interaction for point selection.
"""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map

_MODEL = "sfincs_hmt"
_GROUP = "sfincs_hmt"


def select(*args: Any) -> None:
    """Activate the Observation Points sub-tab and show points on map."""
    map.update()
    app.map.layer[_MODEL].layer["observation_points"].activate()
    update()


def deselect(*args: Any) -> None:
    """Prompt to save unsaved observation point changes when leaving the tab."""
    if app.model[_MODEL].observation_points_changed:
        if app.model[_MODEL].domain.observation_points.nr_points == 0:
            # No observation points, so just reset the flag and return
            app.model[_MODEL].observation_points_changed = False
            return
        ok = app.gui.window.dialog_yes_no(
            "The observation points have changed. Would you like to save the changes?"
        )
        if ok:
            save()


def edit(*args: Any) -> None:
    """Synchronize GUI variables back to the model config."""
    app.model[_MODEL].set_model_variables()


def load(*args: Any) -> None:
    """Load observation points from an .obs file selected by the user.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    map.reset_cursor()
    rsp = app.gui.window.dialog_open_file(
        "Select file ...",
        file_name="sfincs.obs",
        filter="*.obs",
        allow_directory_change=False,
    )
    if rsp[0]:
        app.model[_MODEL].domain.config.set("obsfile", rsp[2])
        app.gui.setvar(_GROUP, "obsfile", rsp[2])
        app.model[_MODEL].domain.observation_points.read()
        gdf = app.model[_MODEL].domain.observation_points.gdf
        app.map.layer[_MODEL].layer["observation_points"].set_data(gdf, 0)
        app.gui.setvar(_GROUP, "active_observation_point", 0)
        update()
    app.model[_MODEL].observation_points_changed = False


def save(*args: Any) -> None:
    """Save observation points to an .obs file selected by the user.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    map.reset_cursor()
    file_name = app.model[_MODEL].domain.config.get("obsfile")
    if not file_name:
        file_name = "sfincs.obs"
    rsp = app.gui.window.dialog_save_file(
        "Select file ...",
        file_name=file_name,
        filter="*.obs",
        allow_directory_change=False,
    )
    if rsp[0]:
        app.model[_MODEL].domain.config.set("obsfile", rsp[2])
        app.gui.setvar(_GROUP, "obsfile", rsp[2])
        app.model[_MODEL].domain.observation_points.write()
    app.model[_MODEL].observation_points_changed = False


def update() -> None:
    """Refresh the observation point list and name in the GUI."""
    gdf = app.active_model.domain.observation_points.gdf
    names = app.active_model.domain.observation_points.list_names
    index = app.gui.getvar(_GROUP, "active_observation_point")
    name = gdf.loc[index, "name"] if index < len(gdf) else ""
    app.gui.setvar(_GROUP, "observation_point_names", names)
    app.gui.setvar(_GROUP, "observation_point_name", name)
    app.gui.setvar(_GROUP, "nr_observation_points", len(gdf))
    app.gui.window.update()


def add_observation_point_on_map(*args: Any) -> None:
    """Start map click interaction to add a new observation point."""
    app.map.click_point(point_clicked)


def point_clicked(x: float, y: float) -> None:
    """Handle a map click to add an observation point at *(x, y)*.

    Parameters
    ----------
    x : float
        Longitude or x-coordinate of the clicked location.
    y : float
        Latitude or y-coordinate of the clicked location.
    """
    # Point clicked on map. Add observation point.
    name, okay = app.gui.window.dialog_string("Edit name for new observation point")
    if not okay:
        # Cancel was clicked
        return
    if name in app.gui.getvar(_GROUP, "observation_point_names"):
        app.gui.window.dialog_info(
            "An observation point with this name already exists !"
        )
        return
    app.model[_MODEL].domain.observation_points.add_point(x, y, name=name)
    index = len(app.model[_MODEL].domain.observation_points.gdf) - 1
    gdf = app.model[_MODEL].domain.observation_points.gdf
    app.map.layer[_MODEL].layer["observation_points"].set_data(gdf, index)
    app.gui.setvar(_GROUP, "active_observation_point", index)
    app.model[_MODEL].observation_points_changed = True
    update()


def select_observation_point_from_list(*args: Any) -> None:
    """Select an observation point on the map from the GUI list.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    map.reset_cursor()
    index = app.gui.getvar(_GROUP, "active_observation_point")
    app.map.layer[_MODEL].layer["observation_points"].select_by_index(index)
    update()


def select_observation_point_from_map(*args: Any) -> None:
    """Handle map-based selection of an observation point.

    Parameters
    ----------
    *args : Any
        First element is a dict with an ``"id"`` key indicating the index.
    """
    map.reset_cursor()
    index = args[0]["id"]
    app.gui.setvar(_GROUP, "active_observation_point", index)
    update()


def delete_point_from_list(*args: Any) -> None:
    """Delete the currently selected observation point.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    map.reset_cursor()
    index = app.gui.getvar(_GROUP, "active_observation_point")
    app.model[_MODEL].domain.observation_points.delete(index)
    gdf = app.model[_MODEL].domain.observation_points.gdf
    index = max(min(index, len(gdf) - 1), 0)
    app.map.layer[_MODEL].layer["observation_points"].set_data(gdf, index)
    app.gui.setvar(_GROUP, "active_observation_point", index)
    app.model[_MODEL].observation_points_changed = True
    update()


def edit_observation_point_name(*args: Any) -> None:
    """Rename the currently selected observation point.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    map.reset_cursor()
    index = app.gui.getvar(_GROUP, "active_observation_point")
    name = app.gui.getvar(_GROUP, "observation_point_name")
    # Trim the name
    name = name.strip()
    # Check that name is not empty
    if len(name) == 0:
        return
    # Check it does not already exist
    if name in app.gui.getvar(_GROUP, "observation_point_names"):
        app.gui.window.dialog_info(
            "An observation point with this name already exists !"
        )
        return
    gdf = app.model[_MODEL].domain.observation_points.gdf
    gdf.loc[index, "name"] = name
    app.map.layer[_MODEL].layer["observation_points"].set_data(gdf, index)
    app.model[_MODEL].observation_points_changed = True
    update()
