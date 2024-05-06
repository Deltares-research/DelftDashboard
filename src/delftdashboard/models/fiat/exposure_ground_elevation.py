# -*- coding: utf-8 -*-
from delftdashboard.app import app
from delftdashboard.operations import map
from delftdashboard.operations import  update
from pathlib import Path
import fiona


def select(*args):
    # De-activate existing layers
    map.update()
    if all(values.data is None for key, values in app.map.layer["buildings"].layer.items()):
        app.map.layer["modelmaker_fiat"].layer[app.gui.getvar("modelmaker_fiat", "active_area_of_interest")].show()
    


def set_variables(*args):
    app.active_model.set_input_variables()

def select_ground_elevation_unit_feet(*args):
    if app.gui.getvar("fiat", "ground_elevation_unit_feet"):
        app.gui.setvar("fiat", "ground_elevation_unit_meters", False)
        app.gui.setvar("fiat", "ground_elevation_unit", "feet")
def select_ground_elevation_unit_meters(*args):
    if app.gui.getvar("fiat", "ground_elevation_unit_meters"):
        app.gui.setvar("fiat", "ground_elevation_unit_feet", False)
        app.gui.setvar("fiat", "ground_elevation_unit", "meters")
        
def select_ground_elevation_file(*args):
    if app.gui.getvar("fiat", "update_source_ground_elevation") == "sfincs_data":
        unit = app.gui.setvar("fiat", "ground_elevation_unit", "meters")
        load_sfincs_ground_elevation(unit)
    elif app.gui.getvar("fiat", "update_source_ground_elevation") == "upload_data":
        unit = app.gui.getvar("fiat", "ground_elevation_unit")
        fn = app.gui.window.dialog_open_file(
            "Select raster", filter="Raster (*.tif)"
        )
        fn = fn[0]
        fn_value = app.gui.getvar("fiat", "loaded_ground_elevation_files_value")
        if fn not in fn_value:
            fn_value.append(Path(fn))
        app.gui.setvar("fiat", "loaded_ground_elevation_files_value", fn_value)
        name = Path(fn).name
        current_list_string = app.gui.getvar("fiat", "loaded_ground_elevation_files_string")
        if name not in current_list_string:
            current_list_string.append(name)

        current_list_string = [item for item in current_list_string if item != '']
        app.gui.setvar("fiat", "loaded_ground_elevation_files_string", current_list_string)

def load_sfincs_ground_elevation(unit: str, *args):
    fname = app.gui.window.dialog_select_path("Select the SFINCS model folder")
    app.gui.setvar("fiat", "ground_elevation_unit", "meters")
    if fname:
        path_to_sfincs_domain = Path(fname) / "subgrid" / "dep_subgrid.tif"
        if path_to_sfincs_domain.exists():
            fn = Path(path_to_sfincs_domain)
            fn_value = app.gui.getvar("fiat", "loaded_ground_elevation_files_value")
            if fn not in fn_value:
                fn_value.append(fn)
            app.gui.setvar("fiat", "loaded_ground_elevation_files_value", fn_value)

            name = Path(fn).name
            current_list_string = app.gui.getvar("fiat", "loaded_ground_elevation_files_string")
            if name not in current_list_string:
                current_list_string.append(name)

            current_list_string = [item for item in current_list_string if item != '']
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
    unit = app.gui.getvar(model, "ground_elevation_unit")

    # Set the source
    app.gui.setvar(model, "source_ground_elevation", name_ground_elevation_source)

    # Set the settings in HydroMT-FIAT
    app.active_model.domain.exposure_vm.set_ground_elevation(
        source=path_ground_elevation_source, unit = unit
    )

    # If model already create, re-run the model to add additional attributes afterwards without aving to "create model" manually
    if app.active_model.domain.fiat_model.exposure is not None:
        dlg = app.gui.window.dialog_wait("\nUpdating Ground Elevation in your FIAT model...")
        update.update_parameters("Ground Elevation")
        dlg.close()

    app.gui.window.dialog_info(
        text="Ground elevation data was added to your model",
        title="Added ground elevation data",
    )