from delftdashboard.app import app
from delftdashboard.operations import map

import geopandas as gpd


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


def load_loaded_classification_source(*args):
    print("Load loaded classification source")


def load_upload_classification_source(*args):
    print("Load upload classification source")
    fn = app.gui.window.dialog_open_file(
        "Select geometry", filter="Geometry (*.shp *.gpkg *.geojson)"
    )
    gdf = gpd.read_file(fn[0])
    list_columns = list(gdf.columns)
    
    app.gui.setvar("fiat", "classification_file_field_name_string", list_columns)
    app.gui.setvar("fiat", "assign_classification_active", True)


def display_primary_classification(*args):
    print("Display primary classification fields")


def display_secondary_classification(*args):
    print("Display secondary classification fields")


def standarize_classification(*args):
    app.model["fiat"].classification_standarize()


def add_classification(*args):
    print("Add classification to model")
