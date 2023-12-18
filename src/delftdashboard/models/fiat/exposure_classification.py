from delftdashboard.app import app
from delftdashboard.operations import map

import geopandas as gpd
from pathlib import Path
import fiona


def select(*args):
    # De-activate existing layers
    map.update()


def set_variables(*args):
    app.active_model.set_input_variables()


def add_classification_field(*args):
    model = "fiat"
    dlg = app.gui.window.dialog_wait("\nReading classification data...")
    path = app.gui.getvar(model, "classification_source_path")
    object_type = app.gui.getvar(model, "object_type")
    attribute_name = app.gui.getvar(model, "classification_file_field_name")

    # Read the vector file and update the table for standardization
    gdf = gpd.read_file(path)
    df = app.gui.getvar(model, "exposure_categories_to_standardize")
    df[object_type] = list(gdf[attribute_name].unique())
    df = df[[object_type, "Assigned"]]
    df.fillna("", inplace=True)
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
        list_columns = list(schema['properties'].keys())
    
    app.gui.setvar(model, "classification_file_field_name_string", list_columns)
    app.gui.setvar(model, "classification_file_field_name_value", list_columns)
    app.gui.setvar(model, "assign_classification_active", True)  # This variable needs to be set to False when NSI is used


def display_primary_classification(*args):
    """Show/hide buildings layer"""
    app.gui.setvar("fiat", "show_primary_classification", args[0])
    if args[0]:
        app.active_model.show_classification(type="primary")
        app.gui.setvar("fiat", "show_secondary_classification", False)
        map.update()
    else:
        if not app.gui.getvar("fiat", "show_secondary_classification"):
            app.active_model.hide_exposure_buildings()


def display_secondary_classification(*args):
    """Show/hide buildings layer"""
    app.gui.setvar("fiat", "show_secondary_classification", args[0])
    if args[0]:
        app.active_model.show_classification(type="secondary")
        app.gui.setvar("fiat", "show_primary_classification", False)
        map.update()
    else:
        if not app.gui.getvar("fiat", "show_primary_classification"):
            app.active_model.hide_exposure_buildings()


def standarize_classification(*args):
    app.active_model.classification_standarize()


def add_classification(*args):
    model = "fiat"

    # TODO: remove the exposure objects that are not linked to any 
    # occupancy class

    # Set the source
    source = app.gui.getvar(model, "classification_source_path")
    source_name = Path(source).name
    app.gui.setvar(model, "source_classification", source_name)
