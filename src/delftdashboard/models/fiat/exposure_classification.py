from delftdashboard.app import app
from delftdashboard.operations import map

import geopandas as gpd
from pathlib import Path
import fiona
import pandas as pd


def select(*args):
    # De-activate existing layers
    map.update()
    if all(
        values.data is None for key, values in app.map.layer["buildings"].layer.items()
    ):
        app.map.layer["modelmaker_fiat"].layer[
            app.gui.getvar("modelmaker_fiat", "active_area_of_interest")
        ].show()


def set_variables(*args):
    app.active_model.set_input_variables()


def add_classification_field(*args):
    model = "fiat"
    existing_exposure_cat = app.gui.getvar(model, "exposure_categories_to_standardize")
    if existing_exposure_cat.values.any():
        try:
            app.active_model.overwrite_classification()
        except ValueError as e:
            # show dialog
            return
    read_classification()


def read_classification(*args):
    model = "fiat"
    dlg = app.gui.window.dialog_wait("\nReading classification data...")
    path = app.gui.getvar(model, "classification_source_path")
    object_type = app.gui.getvar(model, "object_type")
    attribute_name = app.gui.getvar(model, "classification_file_field_name")

    # Reset the self.updated_dict_categories dict
    app.active_model.updated_dict_categories = app.active_model.default_dict_categories

    # Read the vector file and update the table for standardization
    gdf = gpd.read_file(path)
    df = pd.DataFrame({object_type: list(gdf[attribute_name].unique()), "Assigned": ""})
    df.sort_values(object_type, inplace=True, ignore_index=True)
    app.gui.setvar(model, "exposure_categories_to_standardize", df)
    dlg.close()
    if object_type == "Primary Object Type":
        app.gui.window.dialog_info(
            f"Updating the primary classification, will cause the secondary classification to automatically be updated, too. This ensures that primary and secondary classification are consistent. If you wish to only update the name of the primary classification, and not the damage curve, please do so manually.<br><p>Please standardize your classification so the correct damage curves can be assigned.</p>",
            "Please standardize",
        )
    elif object_type == "Secondary Object Type":
        app.gui.window.dialog_info(
            f"Please standardize your classification so the correct damage curves can be assigned.",
            "Please standardize",
        )
    standarize_classification()


def load_upload_classification_source(*args):
    model = "fiat"
    fn = app.gui.window.dialog_open_file(
        "Select geometry", filter="Geometry (*.shp *.gpkg *.geojson)"
    )
    app.gui.setvar(model, "classification_source_path", str(fn[0]))
    # Open the data source for reading
    with fiona.open(fn[0]) as src:
        # Access the schema to get the column names
        schema = src.schema
        list_columns = ["Select"]
        for i in list(schema["properties"].keys()):
            list_columns.append(i)

    app.gui.setvar(model, "classification_file_field_name_string", list_columns)
    app.gui.setvar(model, "classification_file_field_name_value", list_columns)
    app.gui.setvar(
        model, "assign_classification_active", True
    )  # This variable needs to be set to False when NSI is used


def display_primary_classification(*args):
    """Show/hide buildings layer"""
    # TODO: ensure that the correct classification is shown
    # if user-input data is used
    app.gui.setvar("fiat", "show_primary_classification", args[0])
    if args[0]:
        app.map.layer["buildings"].clear()
        app.gui.setvar("fiat", "show_asset_locations", False)
        app.gui.setvar("fiat", "show_secondary_classification", False)
        app.active_model.show_classification(type="primary")
        map.update()
    else:
        if not app.gui.getvar("fiat", "show_secondary_classification"):
            app.active_model.hide_exposure_buildings()


def display_secondary_classification(*args):
    """Show/hide buildings layer"""
    # TODO: ensure that the correct classification is shown
    # if user-input data is used
    app.gui.setvar("fiat", "show_secondary_classification", args[0])
    if args[0]:
        app.map.layer["buildings"].clear()
        app.gui.setvar("fiat", "show_asset_locations", False)
        app.gui.setvar("fiat", "show_primary_classification", False)
        app.active_model.show_classification(type="secondary")
        map.update()
    else:
        if not app.gui.getvar("fiat", "show_primary_classification"):
            app.active_model.hide_exposure_buildings()


def standarize_classification(*args):
    app.active_model.classification_standarize()


def add_classification(*args):

    model = "fiat"

    # Get the source, object type and attribute name
    source = app.gui.getvar(model, "classification_source_path")
    object_type = app.gui.getvar(model, "object_type")
    attribute_name = app.gui.getvar(model, "classification_file_field_name")
    remove_object_type = app.gui.getvar(model, "remove_classification")

    # Set the source
    source_name = Path(source).name
    app.gui.setvar(model, "source_classification", source_name)

    # TODO: ge the variables that are changed!
    new_occupancy_value = app.gui.getvar(model, "new_occupancy_type")

    old_occupancy_value = app.gui.getvar(model, "old_occupancy_type")

    if not new_occupancy_value:
        app.gui.window.dialog_info(
            f"You need to standardize your classification before you can proceed.",
            "Please standardize",
        )
        exit()

    # Initiate classification model
    app.active_model.domain.exposure_vm.set_classification_config(
        source=source,
        attribute=attribute_name,
        type_add=object_type,
        old_values=old_occupancy_value,
        new_values=new_occupancy_value,
        damage_types=["structure", "content"],
        remove_object_type=remove_object_type,
    )

    # Reset variables
    app.gui.setvar(model, "classification_file_field_name", 0)

    app.gui.window.dialog_info(
        text="Standardized classification data was added to your model",
        title="Added standardized classification data",
    )
