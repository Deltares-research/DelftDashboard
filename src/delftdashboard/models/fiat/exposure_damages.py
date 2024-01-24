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


def select_damages_file(*args):
    fn = app.gui.window.dialog_open_file(
        "Select geometry", filter="Geometry (*.shp *.gpkg *.geojson)"
    )
    fn = fn[0]
    fn_value = app.gui.getvar("fiat", "loaded_damages_files_value")
    if fn not in fn_value:
        fn_value.append(Path(fn))
    app.gui.setvar("fiat", "loaded_damages_files_value", fn_value)
    name = Path(fn).name
    current_list_string = app.gui.getvar("fiat", "loaded_damages_files_string")
    if name not in current_list_string:
        current_list_string.append(name)

    app.gui.setvar("fiat", "loaded_damages_files_string", current_list_string)


def load_damages_file(*args):
    index = app.gui.getvar("fiat", "loaded_damages_files")
    file_list = app.gui.getvar("fiat", "loaded_damages_files_value")
    if len(file_list) == 0:
        app.gui.window.dialog_info(
            text="Please load a data source.",
            title="No datasource",
        )
    else:
        path = app.gui.getvar("fiat", "loaded_damages_files_value")[index]
        # Open the data source for reading
        with fiona.open(path) as src:
            # Access the schema to get the column names
            schema = src.schema
            list_columns = list(schema["properties"].keys())
            geometry_type = schema["geometry"].lower()

        if geometry_type == "point":
            app.gui.setvar("fiat", "method_damages", "nearest")
        elif geometry_type in ["polygon", "multipolygon"]:
            app.gui.setvar("fiat", "method_damages", "intersection")
        
        app.gui.setvar("fiat", "damages_file_field_name_value", list_columns)
        app.gui.setvar("fiat", "damages_file_field_name_string", list_columns)


def remove_datasource(*args):
    current_list_string = app.gui.getvar("fiat", "loaded_damages_files_string")
    deselected_aggregation = app.gui.getvar("fiat", "loaded_damages_files")
    if deselected_aggregation > len(
        current_list_string
    ) or deselected_aggregation == len(current_list_string):
        deselected_aggregation = 0
    name = current_list_string[deselected_aggregation]
    current_list_string = app.gui.getvar("fiat", "loaded_damages_files_string")
    current_list_value = app.gui.getvar("fiat", "loaded_damages_files_value")
    current_list_string.remove(name)
    current_list_value = [i for i in current_list_value if name not in str(i)]
    app.gui.setvar("fiat", "loaded_damages_files_string", current_list_string)
    app.gui.setvar("fiat", "loaded_damages_files_value", current_list_value)


def adjust_damage_settings(*args):
    if app.active_model.domain is None:
        app.gui.window.dialog_warning(
            "Please first select a folder for your FIAT model",
            "No FIAT model initiated yet",
        )
        return
    app.active_model.specify_max_potential_damage()


def add_to_model(*args):
    model = "fiat"

    # Get the file path
    idx = app.gui.getvar("fiat", "loaded_damages_files")
    current_list_string = app.gui.getvar("fiat", "loaded_damages_files_string")
    current_list_value = app.gui.getvar(model, "loaded_damages_files_value")
    source_name = current_list_string[idx]
    source_path = str(current_list_value[idx])

    # Get the attribute name
    attribute_name_gfh = app.gui.getvar(model, "damages_file_field_name")

    # Get the method
    method_damages = app.gui.getvar("fiat", "method_damages")

    # Get the max distance
    max_dist_damages = app.gui.getvar("fiat", "max_dist_damages")

    # Get the damage type
    damage_type = app.gui.getvar("fiat", "damage_type")

    app.active_model.domain.exposure_vm.set_damages(
        source=source_path,
        attribute_name=attribute_name_gfh,
        damage_types = damage_type,
        method=method_damages,
        max_dist=max_dist_damages,
    )


    # Set Exposure Model GFH variable
    app.active_model.domain.exposure_vm.exposure_buildings_model.max_potential_damage = source_path
    
    damage_model_user_input()

    # Set the source
    app.gui.setvar(model, "source_max_potential_damage", source_name)

    app.gui.window.dialog_info(
        text="Maximum potential damage data was added to your model",
        title="Added maximum potential damage data",
    )

    # Save model as an dictionary
def damage_model_user_input(*args):
    model = "fiat"

    # Get selected damage type 
    damage_type = app.gui.getvar("fiat", "damage_type")

    # Create dictionary of selected damage type
    damage_model_structure = app.active_model.domain.exposure_vm.exposure_damages_model.dict() if damage_type == "structure" else None
    damage_model_content = app.active_model.domain.exposure_vm.exposure_damages_model.dict() if damage_type == "content" else None
    
    # Set variable 
    app.gui.setvar("fiat", "damage_type_structure",[damage_model_structure]) if damage_model_structure is not None else app.gui.setvar("fiat", "damage_type_content",damage_model_content)
    
    # Create list of both damage type dictionaries
    damages = []
    if app.gui.getvar("fiat", "damage_type_structure") is not None and app.gui.getvar("fiat", "damage_type_content") is None:
       damages.append(app.gui.getvar("fiat", "damage_type_structure"))
    elif app.gui.getvar("fiat", "damage_type_content") is not None and app.gui.getvar("fiat", "damage_type_structure") is None:
       damages.append(app.gui.getvar("fiat", "damage_type_content"))
    elif app.gui.getvar("fiat", "damage_type_structure") is not None and app.gui.getvar("fiat", "damage_type_content") is not None:
       damages.append(app.gui.getvar("fiat", "damage_type_structure"))
       damages.append(app.gui.getvar("fiat", "damage_type_content"))

    return damages
#when running setup function: for i in damages
                                   # if i struct...
                                   # if i cont
    