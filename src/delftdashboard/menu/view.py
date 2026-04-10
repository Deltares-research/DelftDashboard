"""Menu callbacks for View menu actions (topography, terrain, settings)."""

import os
from copy import deepcopy

from delftdashboard.app import app

# def globe(option):
#     if app.gui.getvar("view_settings", "projection") != "globe":
#         app.gui.setvar("view_settings", "projection", "globe")
#         app.map.set_projection("globe")
#         app.gui.window.update()

# def mercator(option):
#     # if app.view["projection"] != "mercator":
#     if app.gui.getvar("view_settings", "projection") != "mercator":
#         app.gui.setvar("view_settings", "projection", "mercator")
#         app.map.set_projection("mercator")
#         app.gui.window.update()


def topography(option: str) -> None:
    """Toggle visibility of the background topography layer.

    Parameters
    ----------
    option : str
        Menu option identifier (unused).
    """
    if not app.gui.getvar("view_settings", "topography_visible"):
        app.gui.setvar("view_settings", "topography_visible", True)
        app.map.layer["main"].layer["background_topography"].show()
    else:
        app.gui.setvar("view_settings", "topography_visible", False)
        app.map.layer["main"].layer["background_topography"].hide()
    # app.map.layer["main"].layer["background_topography"].set_visibility(app.gui.getvar("view_settings", "topography_visible"))
    app.gui.window.update()


# def layer_style(option):
#     if app.gui.getvar("view_settings", "layer_style") != option:
#         app.gui.setvar("view_settings", "layer_style", option)
#         app.map.set_layer_style(option)
#     app.gui.window.update()


def terrain(option: str) -> None:
    """Toggle 3-D terrain rendering on the map.

    Parameters
    ----------
    option : str
        Menu option identifier (unused).
    """
    if not app.gui.getvar("view_settings", "terrain_visible"):
        app.gui.setvar("view_settings", "terrain_visible", True)
    else:
        app.gui.setvar("view_settings", "terrain_visible", False)
    app.map.set_terrain(
        app.gui.getvar("view_settings", "terrain_visible"),
        app.gui.getvar("view_settings", "terrain_exaggeration"),
    )


def model_view(option: str) -> None:
    """Activate the current model's view.

    Parameters
    ----------
    option : str
        Menu option identifier (unused).
    """
    # Get the model name (first string before . in option)
    # model_name = option.split(".")[0]
    app.active_model.select()


def edit_settings(option: str) -> None:
    """Open the view-settings popup and apply changes on confirmation.

    Parameters
    ----------
    option : str
        Menu option identifier (unused).
    """
    # This opens the popup window for the view settings

    # We first make a copy of the gui variable group "view_settings" for editing. This will allow us to cancel the settings.
    app.gui.variables["edit_view_settings"] = deepcopy(
        app.gui.variables["view_settings"]
    )

    # Open settings window
    okay, data = app.gui.popup(
        os.path.join(app.main_path, "misc", "view_settings", "view_settings.yml"),
        id="view_settings",
    )
    if not okay:
        return

    # Okay was pressed, so update view settings
    original_view_settings = app.gui.variables["view_settings"]
    edited_view_settings = app.gui.variables["edit_view_settings"]

    # Perhaps we need to make some changes

    # # Change projection
    # if edited_view_settings["projection"]["value"] != original_view_settings["projection"]["value"]:
    #     app.map.set_projection(edited_view_settings["projection"]["value"])

    # Terrain
    if (
        edited_view_settings["terrain_exaggeration"]["value"]
        != original_view_settings["terrain_exaggeration"]["value"]
    ):
        if original_view_settings["terrain_visible"]["value"]:
            app.map.set_terrain(
                True, edited_view_settings["terrain_exaggeration"]["value"]
            )
        else:
            app.map.set_terrain(
                False, edited_view_settings["terrain_exaggeration"]["value"]
            )

    # Background topography
    update_background_topography = False
    vars_to_check = [
        "topography_dataset",
        "topography_auto_update",
        "topography_zmin",
        "topography_zmax",
        "topography_autoscaling",
        "topography_opacity",
        "topography_colormap",
        "topography_hillshading",
        "topography_interp_method",
        "topography_quality",
    ]
    for var in vars_to_check:
        if edited_view_settings[var]["value"] != original_view_settings[var]["value"]:
            update_background_topography = True

    # Copy edited settings to view_settings
    app.gui.variables["view_settings"] = deepcopy(edited_view_settings)

    if update_background_topography:
        app.map.layer["main"].layer["background_topography"].update()
