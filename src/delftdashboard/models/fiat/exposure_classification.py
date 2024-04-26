from delftdashboard.app import app
from delftdashboard.operations import map

import geopandas as gpd
from pathlib import Path
import fiona
import pandas as pd


def select(*args):
    # De-activate existing layers
    map.update()
    if all(values.data is None for key, values in app.map.layer["buildings"].layer.items()):
        app.map.layer["modelmaker_fiat"].layer[app.gui.getvar("modelmaker_fiat", "active_area_of_interest")].show()


def set_variables(*args):
    app.active_model.set_input_variables()


def add_classification_field(*args):
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
        list_columns = list(schema["properties"].keys())

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
    app.active_model.domain.exposure_vm.update_occupancy_types(
        source, attribute_name, object_type
    )

    # Set the source
    source_name = Path(source).name
    app.gui.setvar(model, "source_classification", source_name)

    # Get the new primary and secondary object classifications
    prim, secon = app.active_model.domain.exposure_vm.get_object_types()
    app.active_model.set_object_types(prim, secon)

    # Set the exposure categories to link for the damage functions
    list_types = prim if prim is not None else secon
    list_types.sort()
    df = pd.DataFrame(
        data={
            object_type: list_types,
            "Assigned: Structure": "",
            "Assigned: Content": "",
        }
    )
    ## TODO: add the nr of stories and the basement?
    app.gui.setvar(model, "exposure_categories_to_link", df)

    # TODO: replace the exposure categories in the vulnerability linking table

    app.gui.window.dialog_info(
        text="Standardized classification data was added to your model",
        title="Added standardized classification data",
    )
