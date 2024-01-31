from delftdashboard.app import app
from delftdashboard.operations import map

from delftdashboard.models.sfincs_hmt.structures.objects.measures_categories import (
    MeasureCategoryFactory,
)
import flood_adapt.api.measures as api_measures
from xugrid.core.wrap import UgridDataArray
from xugrid.ugrid.snapping import snap_to_grid

from pathlib import Path
import geopandas as gpd

from typing import List


class FAMBNameConverter:
    """Class to convert between the names of the measures from the flood adapt names to the names used in the model builder"""

    @staticmethod
    def to_model_builder(flood_adapt_type_name: str) -> str:
        """Method to convert the type of the measure to the type of the model builder"""
        converstion_dict = {
            "floodwall": "weir",
            "thin_dam": "thin_dam",
            "pump": "drainage",
            "culvert": "drainage",
        }
        return converstion_dict[flood_adapt_type_name]

    @staticmethod
    def to_model_builder_short_name(flood_adapt_type_name: str) -> str:
        """Method to convert the type of the measure to the type of the model builder"""
        converstion_dict = {
            "floodwall": "weir",
            "thin_dam": "thd",
            "pump": "drn",
            "culvert": "drn",
        }
        return converstion_dict[flood_adapt_type_name]


def select(*args):
    # reset the map
    map.update()
    app.map.layer["sfincs_hmt"].layer["mask"].activate()

    model = app.model["sfincs_hmt"].domain

    # If no measures layer exists, create it
    if "measures" not in app.map.layer:
        app.map.add_layer("measures")
        layer = app.map.layer["measures"].add_layer("weir")
        layer.line_color_selected = "green"
        layer.line_color = "darkgreen"
        layer = app.map.layer["measures"].add_layer("thd")
        layer.line_color_selected = "orange"
        layer.line_color = "darkorange"
        layer = app.map.layer["measures"].add_layer("drn")
        layer.line_color_selected = "red"
        layer.line_color = "darkred"

    # Add weir measures in the model to the map
    weirs_list = app.gui.getvar("sfincs_hmt", "structure_weir_list")
    if "weir" in model.geoms:
        weirs_list = make_geom_layer(
            "weir", weirs_list, app.map.layer["measures"].layer["weir"]
        )
    if weirs_list:
        app.gui.setvar("sfincs_hmt", "structure_weir_list", weirs_list)
        app.gui.setvar(
            "sfincs_hmt",
            "structure_weir_index",
            weirs_list.index(app.gui.getvar("sfincs_hmt", "active_structure_weir")),
        )

    # Add thin dam measures in the model to the map
    thin_dams_list = app.gui.getvar("sfincs_hmt", "structure_thd_list")
    if "thd" in model.geoms:
        thin_dams_list = make_geom_layer(
            "thd", thin_dams_list, app.map.layer["measures"].layer["thd"]
        )
    if thin_dams_list:
        app.gui.setvar("sfincs_hmt", "structure_thd_list", thin_dams_list)
        app.gui.setvar(
            "sfincs_hmt",
            "structure_thd_index",
            thin_dams_list.index(app.gui.getvar("sfincs_hmt", "active_structure_thd")),
        )

    # Add drainage measures in the model to the map
    drainage_list = app.gui.getvar("sfincs_hmt", "structure_drn_list")
    if "drn" in model.geoms:
        drainage_list = make_geom_layer(
            "drn", drainage_list, app.map.layer["measures"].layer["drn"]
        )
    if drainage_list:
        app.gui.setvar("sfincs_hmt", "structure_drn_list", drainage_list)
        app.gui.setvar(
            "sfincs_hmt",
            "structure_drn_index",
            drainage_list.index(app.gui.getvar("sfincs_hmt", "active_structure_drn")),
        )


def select_struct(*args):
    """Callback method to select a measure from the list"""
    # Split the source in tab, struct_type, name
    tab, struct_type, name = args[0]["source"].split(".")

    # Get selected structure type
    structure_type = app.gui.getvar("measures", "selected_structure_type")

    # Check if the selected structure type is the same as the tab
    if struct_type == structure_type:
        # Get list of possible geoms and index of active geom
        geom_list = app.gui.getvar("sfincs_hmt", f"structure_{structure_type}_list")

        # Get index of selected geom in geom_list
        structure_index = geom_list.index(name)

        # Set active structure
        app.gui.setvar(
            "sfincs_hmt", f"structure_{structure_type}_index", structure_index
        )
        app.gui.setvar("sfincs_hmt", f"active_structure_{structure_type}", name)

        # Update GUI
        app.gui.window.update()


def make_geom_layer(geom_type: str, geom_list: list, layer):
    """Method to create a layer from a geometry"""
    # Get geometry from model
    geoms = app.model["sfincs_hmt"].domain.geoms[geom_type]

    # Get mask from model as xugrid
    if app.model["sfincs_hmt"].domain.reggrid.rotation != 0: # This is a rotated regular grid
        xugrid_mask = UgridDataArray.from_structured(app.model["sfincs_hmt"].domain.mask, 'xc', 'yc')
    else:
        xugrid_mask = UgridDataArray.from_structured(app.model["sfincs_hmt"].domain.mask)

    # Create geodataframe
    for idx, geom in geoms.iterrows():
        if "name" not in geom:
            geom["name"] = geom_type + str(idx)

        if geom["name"] in geom_list:
            continue

        # Create geodataframe
        geom_gdf = gpd.GeoDataFrame(geometry=[geom["geometry"]])

        # Add layer to map
        layer.add_layer(
            str(geom["name"]),
            type="line_selector",
            circle_radius=0,
            line_width = 3,
            line_color=layer.line_color,
            line_style='--',
            line_width_selected = 3,
            line_color_selected=layer.line_color_selected,
            line_style_selected='--',
            hover_param="name",
            select=select_struct,
        )

        layer.add_layer(
            str(geom["name"]) + '_snapped',
            type="line",
            circle_radius=0,
            line_width = 5,
            line_color=layer.line_color,
        )

        # Snap to grid
        _, snapped = snap_to_grid(geom_gdf, xugrid_mask, 1.0)
        geom_gdf["name"] = geom["name"] 
        geom_gdf.crs = app.crs
        snapped["name"] = geom["name"]
        snapped.crs = app.crs
        layer.layer[str(geom["name"])].set_data(geom_gdf, 0)
        layer.layer[str(geom["name"]) + '_snapped'].set_data(snapped)
        geom_list.append(geom["name"])
    return geom_list


def set_variables(*args):
    """Method to set the variables in the gui

    TODO: Is this method still needed?"""

    # All variables will be set
    app.model["sfincs_hmt"].set_model_variables()


def get_win_path(selected_measure_type, model_name):
    """Method to get the path of the window config yaml file"""
    if selected_measure_type == "floodwall":
        yml = "floodwall.yml"
    elif selected_measure_type == "pump":
        yml = "pump.yml"
    elif selected_measure_type == "culvert":
        yml = "culvert.yml"
    elif selected_measure_type == "water_square":
        yml = "water_square.yml"
    elif selected_measure_type == "greening":
        yml = "greening.yml"
    elif selected_measure_type == "total_storage":
        yml = "total_storage.yml"
    elif selected_measure_type == "thin_dam":
        yml = "thin_dam.yml"
    else:
        raise NotImplementedError(
            f"Measure type {selected_measure_type} not implemented"
        )

    # Get window config yaml path
    pop_win_config_path = str(
        Path(app.main_path).joinpath(
            "models", model_name, "config", "measure_templates", yml
        )
    )

    # Return full path
    return pop_win_config_path


def _get_measure_category_and_type():
    """Get measure category and type from gui variables

    Returns
    -------
    tuple
        measure category and type
    """
    # Get selected measure category, type and selection type from measures
    selected_measure_category = app.gui.getvar("measures", "selected_measure_category")
    selected_measure_type = app.gui.getvar("measures", "selected_measure_type")
    selected_measure_selection_type = app.gui.getvar(
        "measures", "selected_measure_selection_type"
    )

    # Get selected measure category factory
    selected_measure_category_factory = (
        MeasureCategoryFactory.get_measure_category_factory(selected_measure_category)
    )

    # Get selected measure type
    selected_measure_type_class = None
    if (
        selected_measure_type
        and selected_measure_type
        in selected_measure_category_factory.get_measure_types()
    ):
        selected_measure_type_class = (
            selected_measure_category_factory.get_measure_type(selected_measure_type)
        )

        # Set app
        selected_measure_type_class.app = app

        # Get selected measure selection type
        if selected_measure_selection_type:
            selected_measure_type_class.selection_class.selection_type = (
                selected_measure_selection_type
            )

    return (selected_measure_category_factory, selected_measure_type_class)


def click_select_structure(*args):
    """Callback method to select a measure from the list"""

    # Get selected structure type
    structure_type = app.gui.getvar("measures", "selected_structure_type")

    # Get list of possible geoms and index of active geom
    geom_list = app.gui.getvar("sfincs_hmt", f"structure_{structure_type}_list")
    structure_index = app.gui.getvar("sfincs_hmt", f"structure_{structure_type}_index")

    # Set active structure
    app.gui.setvar(
        "sfincs_hmt", f"active_structure_{structure_type}", geom_list[structure_index]
    )


def click_add_structure(*args):
    """Callback method to add a measure to the model and map"""

    # TODO: Check where this data should come from for ddb instead of hardcoding
    app.gui.setvar("measure", "elev_ref", 0)

    # Get selected measure category and type
    _, selected_measure_type = _get_measure_category_and_type()

    # Set default values for measure type
    selected_measure_type.set_default_values()

    # Select area to add measure
    if selected_measure_type.selection_class.selection_type == "polygon":
        # First add temporary draw layer with create callback to add measure
        app.map.layer["measures"].add_layer(
            "_TEMP",
            type="draw",
            shape="polygon",
            create=temporary_measure_created,
            polygon_line_color="mediumblue",
            polygon_fill_opacity=0.3,
        )
        app.map.layer["measures"].layer["_TEMP"].draw()

    elif selected_measure_type.selection_class.selection_type == "polyline":
        # First add temporary draw layer with create callback to add measure
        app.map.layer["measures"].add_layer(
            "_TEMP",
            type="draw",
            shape="polyline",
            create=temporary_measure_created,
            polygon_line_color="mediumblue",
            polygon_fill_opacity=0.3,
        )
        app.map.layer["measures"].layer["_TEMP"].draw()

    else:
        # Directly go to add measure
        add_measure()


def add_measure():
    """Method to add a measure to the model and map"""
    # Get selected measure category, type and selection type from measures
    _, selected_measure_type = _get_measure_category_and_type()

    # Set default values for measure type
    pop_win_config_path = get_win_path(
        selected_measure_type.measure_type, app.active_model.name
    )
    okay, data = app.gui.popup(pop_win_config_path)  # Open popup window
    if not okay:
        return

    # Update measure with values from window
    measure = read_measure_window()

    # Check if the name already exists. It cannot exist in any of the measure types (e.g. weir, dam, etc., mostly for clairty)
    if measure["name"] in app.gui.getvar(
        "sfincs_hmt",
        f"structure_{FAMBNameConverter.to_model_builder_short_name(measure['type'])}_list",
    ):
        app.gui.window.dialog_warning(
            text="Name already exists for any of the structures. \nPlease choose another name for the measure"
        )
        # Open popup window again
        add_measure()
        return # Return to prevent that the measure is added twice

    try:
        # Create measure object
        measure_obj = api_measures.create_measure(
            measure, selected_measure_type.measure_type
        )

        # Get geometry based on the selection type
        selection_type = app.gui.getvar("measures", "selected_measure_selection_type")
        if selection_type == "polygon" or selection_type == "polyline":
            gdf = app.gui.getvar("measures", "temp_gdf")
            gdf = gpd.GeoDataFrame(geometry=gdf["geometry"])
        elif selection_type == "import_area":
            path = app.gui.getvar("measure", "geometry_file")
            gdf = gpd.GeoDataFrame.from_file(path)
        else:
            raise NotImplementedError(
                f"Selection type {selection_type} not implemented"
            )

        # Add measure to model
        model = app.model["sfincs_hmt"].domain
        selected_measure_type.add_to_model(measure_obj, model, gdf)

        # Set active measure
        structure_type = app.gui.getvar("measures", "selected_structure_type")
        app.gui.setvar(
            "sfincs_hmt", f"active_structure_{structure_type}", measure["name"]
        )

        # After adding the measure, make sure the data is cleared from the internal storage. This to prevent that if the user adds a measure, closes the window, and then adds another measure, the data from the first measure is still in the internal storage.
        selected_measure_type.delete_window_values()

        # Update the measures window
        select()

    except Exception as e:
        print(e)
        app.gui.window.dialog_warning(
            text=f"There was an error adding the measure: {e}"
        )
        # Open popup window again
        add_measure()


def read_measure_window():
    """Method to parse the values given by the user in the add/edit window"""
    # variables to enable fast allocation with a loop? Or it is more transparent to set one by one?
    _, selected_measure_type = _get_measure_category_and_type()
    return selected_measure_type.get_window_values()


def temporary_measure_created(*args):
    """Callback method to temporarily create a measure while clicking on the map (linestring or polygon)"""

    # Store temporary geometry of this measure (is it best to do this with setvar?)
    app.gui.setvar("measures", "temp_gdf", args[0])
    # Delete temporary draw layer
    app.map.layer["measures"].layer["_TEMP"].delete()
    # Add the measure
    add_measure()
    # Remove temporary geometry
    app.gui.delvar("measures", "temp_gdf")
    # Remove existing measure layers and draw new ones
    app.gui.window.update()


def click_delete_structure(*args):
    """Callback method to delete a measure from the model and map"""

    # Get selected measure category, type and selection type from measures
    _, selected_measure_type = _get_measure_category_and_type()

    # Get selected structure type
    structure_type = app.gui.getvar("measures", "selected_structure_type")

    # Get selected measure and delete it
    selected_measure = app.gui.getvar(
        "sfincs_hmt", "active_structure_" + structure_type
    )
    delete_structure([selected_measure], structure_type)


def click_delete_all_structures(*args):
    """Callback method to delete all measures from the model and map"""

    # Get selected measure category, type and selection type from measures
    _, selected_measure_type = _get_measure_category_and_type()

    # Get selected structure type
    structure_type = app.gui.getvar("measures", "selected_structure_type")

    # Get list of all possible geoms and delete them
    geom_list = app.gui.getvar("sfincs_hmt", f"structure_{structure_type}_list").copy()
    delete_structure(geom_list, structure_type)


def delete_structure(selected_measures: List[str], measure_type: str):
    """Method to delete a measure from the model and map

    Parameters
    ----------
    selected_measures : List[str]
        List of measure names to delete
    measure_type : str
        Type of measure to delete

    Remarks
    -------
    If the last measure is deleted, the active measure is set to None.
    Also, the geom group in the model is not actually deleted, but only the
    geoms are deleted. This is something that SFINCS should be able to handle?
    """

    # Get model
    model = app.model["sfincs_hmt"].domain

    # Check if measure layer exists
    if "measures" not in app.map.layer:
        # Delete measure layer. You can only delete a measure if the layer exists
        raise ValueError("Cannot find measure layer")

    # Check if measure exists in model
    if measure_type not in model.geoms:
        raise ValueError("Cannot find measure in model")

    # Remove measure from model and map
    for selected_measure in selected_measures:
        # Delete measure from model
        if measure_type in model.geoms:
            geoms = model.geoms[measure_type]
            model.geoms[measure_type] = geoms[geoms["name"] != selected_measure]

        # Delete measure from map
        geom_list = app.gui.getvar("sfincs_hmt", f"structure_{measure_type}_list")
        geom_list.remove(selected_measure)
        app.gui.setvar("sfincs_hmt", f"structure_{measure_type}_list", geom_list)

        # Delete layer from map
        if selected_measure in app.map.layer["measures"].layer[measure_type].layer:
            app.map.layer["measures"].layer[measure_type].layer[
                selected_measure
            ].delete()

    # Set active measure
    if len(geom_list) > 0:
        app.gui.setvar("sfincs_hmt", "active_structure_" + measure_type, geom_list[0])
    else:
        app.gui.setvar("sfincs_hmt", "active_structure_" + measure_type, None)

    # Update the measures window
    select()
