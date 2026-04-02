"""GUI callbacks for Delft3D-FM regular observation point management."""

from pathlib import Path
from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map

_MODEL = "delft3dfm"


def select(*args: Any) -> None:
    """Activate the observation points layer when the tab is selected."""
    map.update()
    app.map.layer[_MODEL].layer["observation_points"].activate()
    app.map.layer[_MODEL].layer["observation_points"].show()
    update()


def deselect(*args: Any) -> None:
    """Prompt the user to save unsaved observation point changes on tab deselect."""
    if app.model[_MODEL].observation_points_changed:
        ok = app.gui.window.dialog_yes_no(
            "The observation points have changed. Would you like to save the changes?"
        )
        if ok:
            save()
        else:
            app.model[_MODEL].observation_points_changed = False
    app.map.layer[_MODEL].layer["observation_points"].hide()
    update()


def edit(*args: Any) -> None:
    """Apply GUI edits to the domain input variables."""
    app.model[_MODEL].set_input_variables()


def load(*args: Any) -> None:
    """Open observation point files via dialog and load them into the model."""
    map.reset_cursor()
    rsp = app.gui.window.dialog_open_file(
        "Select files ...",
        file_name="delft3dfm.obs",
        filter=None,
        allow_directory_change=False,
        multiple=True,
    )
    if rsp[0]:
        app.model[_MODEL].domain.input.output.obsfile = rsp[0]
        app.model[_MODEL].domain.observation_points.read()
        gdf = app.model[_MODEL].domain.observation_points.gdf
        app.map.layer[_MODEL].layer["observation_points"].set_data(gdf, 0)
        app.gui.setvar(_MODEL, "active_observation_point", 0)
        update()
    app.model[_MODEL].observation_points_changed = False


def save(*args: Any) -> None:
    """Save observation points to a user-selected file."""
    from hydrolib.core.dflowfm.xyn.models import XYNModel

    map.reset_cursor()
    rsp = app.gui.window.dialog_save_file(
        "Select file ...",
        file_name="delft3dfm.obs",
        filter=None,
        allow_directory_change=False,
    )
    if rsp[0]:
        app.model[_MODEL].domain.input.output.obsfile = []
        app.model[_MODEL].domain.input.output.obsfile.append(XYNModel())
        app.model[_MODEL].domain.input.output.obsfile[0].filepath = Path(rsp[2])
        app.model[_MODEL].domain.observation_points.write()


def update() -> None:
    """Refresh observation point names and counts in the GUI."""
    gdf = app.model[_MODEL].domain.observation_points.gdf
    names = []
    for index, row in gdf.iterrows():
        names.append(row["name"])
    app.gui.setvar(_MODEL, "observation_point_names", names)
    app.gui.setvar(_MODEL, "nr_observation_points", len(gdf))
    app.gui.window.update()


def add_observation_point_on_map(*args: Any) -> None:
    """Enable interactive point placement mode on the map."""
    app.map.click_point(point_clicked)


def point_clicked(x: float, y: float) -> None:
    """Handle a map click to add a new observation point.

    Parameters
    ----------
    x : float
        X-coordinate of the clicked location.
    y : float
        Y-coordinate of the clicked location.
    """
    while True:
        name, okay = app.gui.window.dialog_string("Edit name for new observation point")
        if not okay:
            return
        if name in app.gui.getvar(_MODEL, "observation_point_names"):
            app.gui.window.dialog_info(
                "An observation point with this name already exists !"
            )
        else:
            break
    app.model[_MODEL].domain.observation_points.add_point(x, y, name=name)
    index = len(app.model[_MODEL].domain.observation_points.gdf) - 1
    gdf = app.model[_MODEL].domain.observation_points.gdf
    app.map.layer[_MODEL].layer["observation_points"].set_data(gdf, index)
    app.gui.setvar(_MODEL, "active_observation_point", index)
    update()
    app.model[_MODEL].observation_points_changed = True


def select_observation_point_from_list(*args: Any) -> None:
    """Select the observation point chosen in the GUI list on the map."""
    map.reset_cursor()
    index = app.gui.getvar(_MODEL, "active_observation_point")
    app.map.layer[_MODEL].layer["observation_points"].select_by_index(index)


def select_observation_point_from_map(*args: Any) -> None:
    """Handle selection of an observation point by clicking on the map.

    Parameters
    ----------
    *args : Any
        Map callback arguments; ``args[0]["id"]`` holds the feature index.
    """
    map.reset_cursor()
    index = args[0]["id"]
    app.gui.setvar(_MODEL, "active_observation_point", index)
    app.gui.window.update()


def delete_point_from_list(*args: Any) -> None:
    """Delete the currently selected observation point from the model and map."""
    map.reset_cursor()
    index = app.gui.getvar(_MODEL, "active_observation_point")
    app.model[_MODEL].domain.observation_points.delete_point(index)
    gdf = app.model[_MODEL].domain.observation_points.gdf
    index = max(min(index, len(gdf) - 1), 0)
    app.map.layer[_MODEL].layer["observation_points"].set_data(gdf, index)
    app.gui.setvar(_MODEL, "active_observation_point", index)
    app.model[_MODEL].observation_points_changed = True
    update()
