# -*- coding: utf-8 -*-
from delftdashboard.app import app
from delftdashboard.operations import map
from pathlib import Path
import fiona


def select(*args):
    # De-activate existing layers
    map.update()


def set_variables(*args):
    app.active_model.set_input_variables()


def select_asset_heights_file(*args):
    fn = app.gui.window.dialog_open_file(
        "Select geometry", filter="Geometry (*.shp *.gpkg *.geojson)"
    )
    fn = fn[0]
    fn_value = app.gui.getvar("fiat", "loaded_asset_heights_files_value")
    if fn not in fn_value:
        fn_value.append(Path(fn))
    app.gui.setvar("fiat", "loaded_asset_heights_files_value", fn_value)
    name = Path(fn).name
    current_list_string = app.gui.getvar("fiat", "loaded_asset_heights_files_string")
    if name not in current_list_string:
        current_list_string.append(name)

    app.gui.setvar("fiat", "loaded_asset_heights_files_string", current_list_string)


def load_asset_heights_file(*args):
    index = app.gui.getvar("fiat", "loaded_asset_heights_files")
    file_list = app.gui.getvar("fiat", "loaded_asset_heights_files_value")
    if len(file_list) == 0:
        app.gui.window.dialog_info(
            text="Please load a data source.",
            title="No datasource",
        )
    else:
        path = app.gui.getvar("fiat", "loaded_asset_heights_files_value")[index]
        # Open the data source for reading
        with fiona.open(path) as src:
            # Access the schema to get the column names
            schema = src.schema
            list_columns = list(schema['properties'].keys())
        
        app.gui.setvar("fiat", "heights_file_field_name_value", list_columns)
        app.gui.setvar("fiat", "heights_file_field_name_string", list_columns)


def remove_datasource(*args):
    current_list_string = app.gui.getvar("fiat", "loaded_asset_heights_files_string")
    deselected_aggregation = app.gui.getvar("fiat", "loaded_asset_heights_files")
    if deselected_aggregation > len(
        current_list_string
    ) or deselected_aggregation == len(current_list_string):
        deselected_aggregation = 0
    name = current_list_string[deselected_aggregation]
    current_list_string = app.gui.getvar("fiat", "loaded_asset_heights_files_string")
    current_list_value = app.gui.getvar("fiat", "loaded_asset_heights_files_value")
    current_list_string.remove(name)
    current_list_value = [i for i in current_list_value if name not in str(i)]
    app.gui.setvar("fiat", "loaded_asset_heights_files_string", current_list_string)
    app.gui.setvar("fiat", "loaded_asset_heights_files_value", current_list_value)


def adjust_ffe_settings(*args):
    print("Adjust settings")


def add_to_model(*args):
    print("Add to model")

    # Set the source
    idx = app.gui.getvar("fiat", "loaded_asset_heights_files")
    current_list_string = app.gui.getvar("fiat", "loaded_asset_heights_files_string")
    app.gui.setvar("fiat", "source_finished_floor_elevation", current_list_string[idx])