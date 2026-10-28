"""GUI callbacks for the flood map view tab.

Handle time selection, color settings, opacity, and flood map display updates.
"""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args: Any) -> None:
    """Activate the view tab and refresh the flood map display."""
    map.update()
    app.toolbox["flood_map"].set_layer_mode("active")
    update()


def select_instantaneous_or_maximum(*args: Any) -> None:
    """Switch between instantaneous and maximum water levels."""
    app.gui.setvar("flood_map", "time_index", 0)
    update()


def select_time(*args: Any) -> None:
    """Update the flood map for the newly selected time step."""
    update()


def export(*args: Any) -> None:
    """Export the current flood map."""
    app.toolbox["flood_map"].export_flood_map()


def select_opacity(*args: Any) -> None:
    """Apply the updated opacity value to the flood map layer."""
    opacity = app.gui.getvar("flood_map", "flood_map_opacity")
    app.map.layer["flood_map"].layer["flood_map"].set_opacity(opacity)


def select_continuous_or_discrete_colors(*args: Any) -> None:
    """Toggle between continuous and discrete color rendering."""
    mode = app.gui.getvar("flood_map", "continuous_or_discrete_colors")
    if mode == "continuous":
        app.toolbox["flood_map"].flood_map.discrete_colors = False
    else:
        app.toolbox["flood_map"].flood_map.discrete_colors = True
    update()


def edit_cmin_cmax(*args: Any) -> None:
    """Apply updated color range and colormap settings."""
    try:
        cmin = float(app.gui.getvar("flood_map", "cmin"))
        cmax = float(app.gui.getvar("flood_map", "cmax"))
        cmap = app.gui.getvar("flood_map", "cmap")

        app.toolbox["flood_map"].flood_map.cmin = cmin
        app.toolbox["flood_map"].flood_map.cmax = cmax
        app.toolbox["flood_map"].flood_map.cmap = cmap
        update()

    except ValueError:
        print("Invalid cmin or cmax value")


def update() -> None:
    """Refresh the flood map layer with the current settings."""
    if app.gui.getvar("flood_map", "instantaneous_or_maximum") == "instantaneous":
        app.gui.setvar(
            "flood_map",
            "available_time_strings",
            app.toolbox["flood_map"].instantaneous_time_strings,
        )
    else:
        app.gui.setvar(
            "flood_map",
            "available_time_strings",
            app.toolbox["flood_map"].maximum_time_strings,
        )
    app.toolbox["flood_map"].update_flood_map()
