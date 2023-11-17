from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args):
    # De-activate existing layers
    map.update()


def edit(*args):
    app.model["fiat"].set_model_variables()


def select_model_type(*args):
    group = "fiat"
    model_type = app.gui.getvar("fiat", "model_type")
    if model_type == "Start with NSI":
        app.gui.setvar(group, "selected_asset_locations_string", ["National Structure Inventory (NSI)"])
        app.gui.setvar(group, "selected_asset_locations", 0)
