from delftdashboard.app import app
from delftdashboard.operations import map

import geopandas as gpd
import fiona


def select(*args):
    # De-activate existing layers
    map.update()


def set_variables(*args):
    app.model["fiat"].set_input_variables()


def add_classification_field(*args):
    model = "fiat"
    dlg = app.gui.window.dialog_wait("\nReading classification data...")
    path = app.gui.getvar(model, "classification_source_path")
    attribute_name = app.gui.getvar(model, "classification_file_field_name")
    gdf = gpd.read_file(path)
    list(gdf[attribute_name].unique())

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
    print("Add classification to model")
    # Set the sources
    app.gui.setvar("fiat", "source_classification", "add loaded source")
