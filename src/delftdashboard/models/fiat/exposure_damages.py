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
    
    # Remove empty string if in list 
    fn_value = [item for item in fn_value if item != Path('.')]
    app.gui.setvar("fiat", "loaded_damages_files_value", fn_value)

    name = Path(fn).name
    current_list_string = app.gui.getvar("fiat", "loaded_damages_files_string")
    if name not in current_list_string:
        current_list_string.append(name)

    # Remove empty string if in list
    current_list_string  = [item for item in current_list_string  if item != '']
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

    # Get the damage type
    damage_type = app.gui.getvar("fiat", "damage_type")

    if damage_type in app.gui.getvar(model, "damage_type_list"):
        # app.gui.window.dialog_warning(
        #    "You already added that damage type to your model. Do you want to overwrite it?",
        #    "Damage type was already added",
        # )
        # return
        damage_index = app.gui.getvar(model, "damage_type_list").index(damage_type)

        # Create pop-up and only continue if user presses ok
        try:
            app.active_model.overwrite_damages()
        except ValueError as e:
            return
        replace_damage(damage_index)
    else:
        add_damages()


def add_damages():
    model = "fiat"

    # Get the damage type
    damage_type = app.gui.getvar("fiat", "damage_type")
    app.gui.getvar(model, "damage_type_list").append(damage_type)
    damage_types = app.gui.getvar(model, "damage_type_list")
    app.gui.setvar(model, "damage_type_list", damage_types)
    damage_types = app.gui.getvar(model, "damage_type_list")

    # Get the file path
    idx = app.gui.getvar(model, "loaded_damages_files")
    current_list_value = app.gui.getvar(model, "loaded_damages_files_value")[idx]
    current_list_string = app.gui.getvar(model, "loaded_damages_files_string")[idx]

    app.gui.getvar(model, "loaded_damages_files_value_list").append(
        str(current_list_value)
    )
    fn_damages = app.gui.getvar(model, "loaded_damages_files_value_list")
    app.gui.setvar(model, "loaded_damages_files_value_list", fn_damages)
    source_path = app.gui.getvar(model, "loaded_damages_files_value_list")

    app.gui.getvar(model, "loaded_damages_files_string_list").append(
        current_list_string
    )
    name_damages = app.gui.getvar(model, "loaded_damages_files_string_list")
    app.gui.setvar(model, "loaded_damages_files_string_list", name_damages)

    source_name = app.gui.getvar(model, "loaded_damages_files_string_list")

    # Get the attribute name
    attribute_name_damage = app.gui.getvar(model, "damages_file_field_name")

    app.gui.getvar(model, "damages_file_field_name_list").append(attribute_name_damage)
    attribute_name_damages = app.gui.getvar(model, "damages_file_field_name_list")
    app.gui.setvar(model, "damages_file_field_name_list", attribute_name_damages)
    attribute_name_damages = app.gui.getvar(model, "damages_file_field_name_list")

    # Empty field name parameter
    app.gui.setvar(model, "damages_file_field_name", 0)

    # Get the method
    method_damages = app.gui.getvar("fiat", "method_damages")

    app.gui.getvar(model, "method_damages_list").append(method_damages)
    method_damages = app.gui.getvar(model, "method_damages_list")
    app.gui.setvar("fiat", "method_damages_list", method_damages)
    method_damages = app.gui.getvar(model, "method_damages_list")

    # Get the max distance
    max_dist_damages = app.gui.getvar("fiat", "max_dist_damages")

    app.gui.getvar(model, "max_dist_damages_list").append(max_dist_damages)
    max_dist_damages = app.gui.getvar(model, "max_dist_damages_list")
    app.gui.setvar(model, "max_dist_damages_list", max_dist_damages)
    max_dist_damages = app.gui.getvar(model, "max_dist_damages_list")

    app.active_model.domain.exposure_vm.set_damages(
        source=source_path,
        attribute_name=attribute_name_damages,
        method_damages=method_damages,
        max_dist=max_dist_damages,
        damage_types=damage_types,
    )

    # Set the source
    app.gui.setvar(model, "source_max_potential_damage", source_name)

    app.gui.window.dialog_info(
        text="Maximum potential damage data was added to your model",
        title="Added maximum potential damage data",
    )


def replace_damage(damage_index):
    model = "fiat"

    # Replace Damage_type
    damage_type = app.gui.getvar("fiat", "damage_type")
    damage_type_list = app.gui.getvar(model, "damage_type_list")
    damage_type_list[damage_index] = damage_type

    app.gui.setvar(model, "damage_type_list", damage_type_list)
    damage_types = app.gui.getvar(model, "damage_type_list")

    # Replace file path
    idx = app.gui.getvar(model, "loaded_damages_files")
    current_list_value = app.gui.getvar(model, "loaded_damages_files_value")[idx]

    damage_values_list = app.gui.getvar(model, "loaded_damages_files_value_list")

    damage_values_list[damage_index] = str(current_list_value)
    app.gui.setvar(model, "loaded_damages_files_value_list", damage_values_list)
    source_path = app.gui.getvar(model, "loaded_damages_files_value_list")

    # Replace file name
    current_list_string = app.gui.getvar(model, "loaded_damages_files_string")[idx]

    damage_string_list = app.gui.getvar(model, "loaded_damages_files_string_list")
    damage_string_list[damage_index] = current_list_string
    app.gui.setvar(model, "loaded_damages_files_string_list", damage_string_list)

    source_name = app.gui.getvar(model, "loaded_damages_files_string_list")

    # Get the attribute name
    attribute_name_damage = app.gui.getvar(model, "damages_file_field_name")

    damages_attribute_list = app.gui.getvar(model, "damages_file_field_name_list")
    damages_attribute_list[damage_index] = attribute_name_damage

    app.gui.setvar(model, "damages_file_field_name_list", damages_attribute_list)
    attribute_name_damages = app.gui.getvar(model, "damages_file_field_name_list")
    
    # Empty field name parameter
    app.gui.setvar(model, "damages_file_field_name", 0)

    # Get the method
    method_damages = app.gui.getvar("fiat", "method_damages")

    method_damages_list = app.gui.getvar(model, "method_damages_list")
    method_damages_list[damage_index] = method_damages

    app.gui.setvar("fiat", "method_damages_list", method_damages_list)
    method_damages = app.gui.getvar(model, "method_damages_list")

    # Get the max distance
    max_dist_damages = app.gui.getvar("fiat", "max_dist_damages")

    max_dist_list = app.gui.getvar(model, "max_dist_damages_list")
    max_dist_list[damage_index] = max_dist_damages
    app.gui.setvar(model, "max_dist_damages_list", max_dist_list)
    max_dist_damages = app.gui.getvar(model, "max_dist_damages_list")

    app.active_model.domain.exposure_vm.set_damages(
        source=source_path,
        attribute_name=attribute_name_damages,
        method_damages=method_damages,
        max_dist=max_dist_damages,
        damage_types=damage_types,
    )

    # Set the source
    app.gui.setvar(model, "source_max_potential_damage", source_name)

    app.gui.window.dialog_info(
        text="Maximum potential damage data was added to your model",
        title="Added maximum potential damage data",
    )
