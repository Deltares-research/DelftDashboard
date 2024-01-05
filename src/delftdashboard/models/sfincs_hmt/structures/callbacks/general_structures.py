from delftdashboard.app import app
from delftdashboard.models.sfincs_hmt.structures.objects.measures_categories import (
    MeasureCategoryFactory,
)
import flood_adapt.api.measures as api_measures

from pathlib import Path
import geopandas as gpd

from typing import List


def select(*args):
    model = app.model["sfincs_hmt"].domain

    # If no measures layer exists, create it
    if "measures" not in app.map.layer:
        app.map.add_layer("measures")

    # Add weir measures in the model to the map
    weirs_list = app.gui.getvar("sfincs_hmt", "structure_weir_list")
    if "weir" in model.geoms:
        weirs_list = make_geom_layer("weir", weirs_list, app.map.layer["measures"])
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
            "thd", thin_dams_list, app.map.layer["measures"]
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
        drainage_list = make_geom_layer("drn", drainage_list, app.map.layer["measures"])
    if drainage_list:
        app.gui.setvar("sfincs_hmt", "structure_drn_list", drainage_list)
        app.gui.setvar(
            "sfincs_hmt",
            "structure_drn_index",
            drainage_list.index(app.gui.getvar("sfincs_hmt", "active_structure_drn")),
        )


def make_geom_layer(geom_type: str, geom_list: list, layer):
    """Method to create a layer from a geometry"""
    # Get geometry from model
    geoms = app.model["sfincs_hmt"].domain.geoms[geom_type]

    # Create geodataframe
    for idx, geom in geoms.iterrows():
        if "name" not in geom:
            geom["name"] = geom_type + str(idx)

        if geom["name"] in geom_list:
            continue

        # Create geodataframe
        geom_gdf = gpd.GeoDataFrame(geometry=[geom["geometry"]])
        geom_gdf.crs = app.crs

        # Add layer to map
        layer.add_layer(
            geom["name"],
            type="draw",
            shape="polyline",
            polygon_line_color="green",
            polygon_fill_opacity=0.3,
        )
        layer.layer[geom["name"]].set_data(geom_gdf)
        geom_list.append(geom["name"])
    return geom_list


def set_variables(*args):
    """Method to set the variables in the gui

    TODO: Is this method still needed?"""

    # All variables will be set
    app.model["sfincs_hmt"].set_model_variables()


def get_win_path(selected_measure_type, model_name):
    """Method to get the path of the window config yaml file"""
    if selected_measure_type == "elevate_properties":
        yml = "elevate_properties.yml"
    elif selected_measure_type == "buyout_properties":
        yml = "buyout_properties.yml"
    elif selected_measure_type == "floodproof_properties":
        yml = "floodproof_properties.yml"
    elif selected_measure_type == "floodwall":
        yml = "floodwall.yml"
    elif selected_measure_type == "levee":
        yml = "levee.yml"
    elif selected_measure_type == "pump":
        yml = "pump.yml"
    elif selected_measure_type == "culvert":
        yml = "culvert.yml"
    elif selected_measure_type == "water_square":
        yml = "water_square.yml"
    elif selected_measure_type == "greening":
        yml = "greening.yml"
    elif selected_measure_type == "point_storage":
        yml = "point_storage.yml"
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

    # TODO should the gui variables have the same name as the pydantic ?
    # Update measure with values from window
    measure = read_measure_window()

    # Check if the name already exists. It cannot exist in any of the measure types (e.g. weir, dam, etc., mostly for clairty)
    # TODO: Checking for all measure types is a bit of a shortcut because there is only one measure layer. If you then add multiple measures
    # with the same name for different measure types, only one will be shown on the map. If you give informative names though, this should not be a problem.
    for measure_type in ['weir', 'thd', 'drn']:
        if measure["name"] in app.gui.getvar("sfincs_hmt", f"structure_{measure_type}_list"):
            app.gui.window.dialog_warning(text = "Name already exists for any of the structures. \nPlease choose another name for the measure")
            return

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

        model = app.model["sfincs_hmt"].domain
        # TODO: I dont think it is right that the crs is not yet set? But if I dont do this, i get:
        # Traceback (most recent call last):
        #     File "<string>", line 1, in <module>
        #     File "C:\Users\adrichem\AppData\Local\anaconda3\envs\ddb_fiat\Lib\site-packages\hydromt_sfincs\sfincs.py", line 1458, in setup_structures
        #         ).to_crs(self.crs)
        #         ^^^^^^^^^^^^^^^^
        #     File "C:\Users\adrichem\AppData\Local\anaconda3\envs\ddb_fiat\Lib\site-packages\geopandas\geodataframe.py", line 1425, in to_crs
        #         geom = df.geometry.to_crs(crs=crs, epsg=epsg)
        #             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        #     File "C:\Users\adrichem\AppData\Local\anaconda3\envs\ddb_fiat\Lib\site-packages\geopandas\geoseries.py", line 1157, in to_crs
        #         self.values.to_crs(crs=crs, epsg=epsg), index=self.index, name=self.name
        #         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        #     File "C:\Users\adrichem\AppData\Local\anaconda3\envs\ddb_fiat\Lib\site-packages\geopandas\array.py", line 864, in to_crs
        #         raise ValueError("Must pass either crs or epsg.")
        #     ValueError: Must pass either crs or epsg.
        model.set_crs(app.crs)

        # Add measure to model
        selected_measure_type.add_to_model(measure_obj, model, gdf)

        # Set active measure
        structure_type = app.gui.getvar("measures", "selected_structure_type")
        app.gui.setvar(
            "sfincs_hmt", f"active_structure_{structure_type}", measure["name"]
        )

    except Exception as e:
        print(e)
        # TODO add error popup and reopen edit window to change

    # After adding the measure, make sure the data is cleared from the internal storage. This to prevent that if the user adds a measure, closes the window, and then adds another measure, the data from the first measure is still in the internal storage.
    selected_measure_type.delete_window_values()

    # Update the measures window
    select()


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
        if selected_measure in app.map.layer["measures"].layer:
            app.map.layer["measures"].layer[selected_measure].delete()

    # Set active measure
    if len(geom_list) > 0:
        app.gui.setvar("sfincs_hmt", "active_structure_" + measure_type, geom_list[0])
    else:
        app.gui.setvar("sfincs_hmt", "active_structure_" + measure_type, None)

    # Update the measures window
    select()
