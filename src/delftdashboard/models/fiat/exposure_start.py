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

        # For classification the NSI data cannot be used because it is already used, you can only update it with other data.
        app.gui.setvar(group, "classification_source", "nsi_data")
        app.gui.setvar(
            group,
            "classification_source_string",
            ["National Structure Inventory (NSI)", "Upload data"],
        )
        app.gui.setvar(group, "classification_source_value", ["nsi_data", "upload_data"])
    elif model_type == "Start from scratch":
        app.gui.setvar(group, "selected_asset_locations_string", [])
        app.gui.setvar(group, "selected_asset_locations", 0)

        # When starting from scratch only user-input data can be used for classification
        app.gui.setvar(group, "classification_source", "upload_data")
        app.gui.setvar(
            group,
            "classification_source_string",
            ["Upload data"],
        )
        app.gui.setvar(group, "classification_source_value", ["upload_data"])


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