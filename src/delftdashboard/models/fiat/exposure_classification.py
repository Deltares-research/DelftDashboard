from delftdashboard.app import app
from delftdashboard.operations import map

import fiona


def select(*args):
    # De-activate existing layers
    map.update()


def set_variables(*args):
    app.model["fiat"].set_input_variables()


def add_classification_field(*args):
    print("Add classification field")


def load_nsi_classification_source(*args):
    print("Load NSI classification source")
    app.gui.setvar("fiat", "assign_classification_active", False)


def load_upload_classification_source(*args):
    print("Load upload classification source")
    fn = app.gui.window.dialog_open_file(
        "Select geometry", filter="Geometry (*.shp *.gpkg *.geojson)"
    )
    # Open the data source for reading
    with fiona.open(fn[0]) as src:
        # Access the schema to get the column names
        schema = src.schema
        list_columns = list(schema['properties'].keys())
    
    app.gui.setvar("fiat", "classification_file_field_name_string", list_columns)
    app.gui.setvar("fiat", "assign_classification_active", True)


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
