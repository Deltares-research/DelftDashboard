from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args):
    # De-activate existing layers
    map.update()


def edit(*args):
    app.model["fiat"].set_model_variables()


def select_model_type(*args):
    group = "fiat"
    model_type = app.gui.getvar(group, "model_type")
    if model_type == "Start with NSI":
        app.gui.setvar(group, "selected_asset_locations_string", ["National Structure Inventory (NSI)"])
        app.gui.setvar(group, "selected_asset_locations", 0)
    elif model_type == "Start from scratch":
        app.gui.setvar(group, "selected_asset_locations_string", [])
        app.gui.setvar(group, "selected_asset_locations", 0)


def include_all_road_types(*args):
    group = "fiat"
    if app.gui.getvar(group, "include_all"):
        app.gui.setvar(group, "include_motorways", True)
        app.gui.setvar(group, "include_trunk", True)
        app.gui.setvar(group, "include_primary", True)
        app.gui.setvar(group, "include_secondary", True)
        app.gui.setvar(group, "include_tertiary", True)
    else:
        app.gui.setvar(group, "include_motorways", False)
        app.gui.setvar(group, "include_trunk", False)
        app.gui.setvar(group, "include_primary", False)
        app.gui.setvar(group, "include_secondary", False)
        app.gui.setvar(group, "include_tertiary", False)