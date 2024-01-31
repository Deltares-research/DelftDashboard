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


def select_ground_elevation_file(*args):
    fn = app.gui.window.dialog_open_file("Select raster", filter="Raster (*.tif)")
    fn = fn[0]
    fn_value = app.gui.getvar("fiat", "loaded_ground_elevation_files_value")
    if fn not in fn_value:
        fn_value.append(Path(fn))
    app.gui.setvar("fiat", "loaded_ground_elevation_files_value", fn_value)
    name = Path(fn).name
    current_list_string = app.gui.getvar("fiat", "loaded_ground_elevation_files_string")
    if name not in current_list_string:
        current_list_string.append(name)

    app.gui.setvar("fiat", "loaded_ground_elevation_files_string", current_list_string)


def remove_datasource(*args):
    current_list_string = app.gui.getvar("fiat", "loaded_ground_elevation_files_string")
    deselected_aggregation = app.gui.getvar("fiat", "loaded_ground_elevation_files")
    if deselected_aggregation > len(
        current_list_string
    ) or deselected_aggregation == len(current_list_string):
        deselected_aggregation = 0
    name = current_list_string[deselected_aggregation]
    current_list_string = app.gui.getvar("fiat", "loaded_ground_elevation_files_string")
    current_list_value = app.gui.getvar("fiat", "loaded_ground_elevation_files_value")
    current_list_string.remove(name)
    current_list_value = [i for i in current_list_value if name not in str(i)]
    app.gui.setvar("fiat", "loaded_ground_elevation_files_string", current_list_string)
    app.gui.setvar("fiat", "loaded_ground_elevation_files_value", current_list_value)


def add_to_model(*args):
    model = "fiat"

    # Get the source
    idx = app.gui.getvar(model, "loaded_ground_elevation_files")
    current_list_string = app.gui.getvar(model, "loaded_ground_elevation_files_string")
    current_list_value = app.gui.getvar(model, "loaded_ground_elevation_files_value")
    name_ground_elevation_source = current_list_string[idx]
    path_ground_elevation_source = str(current_list_value[idx])

    # Set the source
    app.gui.setvar(model, "source_ground_elevation", name_ground_elevation_source)

    # Set the settings in HydroMT-FIAT
    app.active_model.domain.exposure_vm.set_ground_elevation(
        source=path_ground_elevation_source
    )

    app.gui.window.dialog_info(
        text="Ground elevation data was added to your model",
        title="Added ground elevation data",
    )
