from delftdashboard.app import app
from delftdashboard.operations import map
from .vulnerability_damage_curves import update_damage_curves
from hydromt_fiat.api.data_types import Currency, Units,  ExposureRoadsSettings

import pandas as pd
import geopandas as gpd
from pathlib import Path
import os


def select(*args):
    # De-activate existing layers
    map.update()
    if all(
        values.data is None for key, values in app.map.layer["buildings"].layer.items()
    ):
        app.map.layer["modelmaker_fiat"].layer[
            app.gui.getvar("modelmaker_fiat", "active_area_of_interest")
        ].show()
    app.gui.setvar("_main", "show_fiat_checkbox", True)


def edit(*args):
    app.active_model.set_model_variables()


def select_model_type(*args):
    group = "fiat"
    model_type = app.gui.getvar(group, "model_type")
    if model_type == "Start with National Structure Inventory (NSI)":
        app.gui.setvar(
            group,
            "selected_asset_locations_string",
            ["National Structure Inventory (NSI)"],
        )
        app.gui.setvar(group, "osm_roads_threshold_unit", "Threshold value (ft)")
        app.gui.setvar(group, "ground_elevation_unit", "feet")
        app.gui.setvar(group, "selected_asset_locations", 0)
        app.gui.setvar(group, "damage_unit", Currency.dollar.value)
        # For classification the NSI data cannot be used because it is already used, you can only update it with other data.
        app.gui.setvar(group, "classification_source", "nsi_data")
        app.gui.setvar(
            group,
            "classification_source_string",
            ["National Structure Inventory (NSI)", "Upload data"],
        )
        app.gui.setvar(
            group, "classification_source_value", ["nsi_data", "upload_data"]
        )
    elif model_type == "Start with Open Street Map (OSM)":
        # NOTE: This option is currently not implemented
        app.gui.setvar(group, "osm_roads_threshold_unit", "Threshold value (m)")
        app.gui.setvar(group, "ground_elevation_unit", "meters")
        app.gui.setvar(
            group, "selected_asset_locations_string", ["Open Street Map (OSM)"]
        )
        app.gui.setvar(group, "selected_asset_locations", 0)
        app.gui.setvar(group, "damage_unit", Currency.euro.value)
        # When starting from scratch only user-input data can be used for classification
        app.gui.setvar(group, "classification_source", "upload_data")
        app.gui.setvar(
            group,
            "classification_source_string",
            ["Upload data"],
        )
        app.gui.setvar(
            group, "classification_source_value", ["osm_data", "upload_data"]
        )

    #    app.gui.window.dialog_info(
    #        "This option is currently not implemented.",
    #        "Method not implemented",
    #    )


def include_all_road_types(*args):
    group = "fiat"
    if app.gui.getvar(group, "include_all"):
        app.gui.setvar(group, "include_motorways", True)
        app.gui.setvar(group, "include_trunk", True)
        app.gui.setvar(group, "include_primary", True)
        app.gui.setvar(group, "include_secondary", True)
        app.gui.setvar(group, "include_tertiary", True)
    else:
        app.gui.setvar(group, "include_motorways", False)
        app.gui.setvar(group, "include_trunk", False)
        app.gui.setvar(group, "include_primary", False)
        app.gui.setvar(group, "include_secondary", False)
        app.gui.setvar(group, "include_tertiary", False)


def add_exposure_locations_to_model(*args):
    selected_asset_locations = app.gui.getvar("fiat", "selected_asset_locations_string")
    if (
        len(selected_asset_locations) == 1
        and selected_asset_locations[0] == "National Structure Inventory (NSI)"
    ):
        selected_asset_locations = "NSI"
        build_nsi_exposure()
    elif (
        len(selected_asset_locations) == 1
        and selected_asset_locations[0] == "Open Street Map (OSM)"
    ):
        selected_asset_locations = "OSM"

        # Build OSM exposure
        build_osm_exposure()

    elif selected_asset_locations == "User model":
        # Build User exposure
        build_user_exposure()
    else:
        app.gui.window.dialog_info(
            text="The option to have multiple asset location sources is not yet implemented.",
            title="Not yet implemented",
        )
        return

    app.active_model.domain.exposure_vm.set_asset_data_source(selected_asset_locations)

    # Set the unit for Exposure Data for visualization
    view_tab_unit = app.active_model.domain.exposure_vm.exposure_buildings_model.length_unit
    if hasattr(view_tab_unit, "value"):
        view_tab_unit = view_tab_unit.value
    app.gui.setvar("fiat", "view_tab_unit", view_tab_unit)

    # Hide Boundary Box
    if app.map.layer["modelmaker_fiat"].layer[
        app.gui.getvar("modelmaker_fiat", "active_area_of_interest")
    ]:
        app.map.layer["modelmaker_fiat"].layer[
            app.gui.getvar("modelmaker_fiat", "active_area_of_interest")
        ].hide()


def build_nsi_exposure(*args):
    model = "fiat"
    checkbox_group = "_main"
    try:
        dlg = app.gui.window.dialog_wait("\nDownloading NSI data...")
        app.gui.setvar(model, "created_nsi_assets", "nsi")
        app.gui.setvar(
            model, "text_feedback_create_asset_locations", "NSI assets created"
        )

        crs = app.gui.getvar(model, "selected_crs")
        (
            gdf,
            unique_primary_types,
            unique_secondary_types,
        ) = app.active_model.domain.exposure_vm.set_asset_locations_source_and_get_data(
            source="NSI", ground_floor_height="NSI", crs=crs
        )
        gdf.set_crs(crs, inplace=True)

        # Set the buildings attribute to gdf for easy visualization of the buildings
        app.active_model.buildings = gdf

        app.map.layer["buildings"].layer["exposure_points"].crs = crs
        app.map.layer["buildings"].layer["exposure_points"].set_data(gdf)

        unique_primary_types.sort()
        unique_secondary_types.sort()
        app.gui.setvar(
            model, "selected_primary_classification_string", unique_primary_types
        )
        app.gui.setvar(
            model, "selected_secondary_classification_string", unique_secondary_types
        )
        app.gui.setvar(
            model, "selected_primary_classification_value", unique_primary_types
        )
        app.gui.setvar(
            model, "selected_secondary_classification_value", unique_secondary_types
        )

        app.gui.setvar(model, "show_asset_locations", True)
        app.gui.setvar(model, "ground_elevation_unit", "feet")
        app.gui.setvar(model, "OSM_continent", None)
        list_types = list(gdf["Secondary Object Type"].unique())
        list_types.sort()
        df = pd.DataFrame(
            data={
                "Secondary Object Type": list_types,
                "Assigned: Structure": "",
                "Assigned: Content": "",
            }
        )
        ## TODO: add the nr of stories and the basement

        app.gui.setvar(model, "exposure_categories_to_link", df)

        # Set the checkboxes checked
        app.gui.setvar(checkbox_group, "checkbox_asset_locations", True)
        app.gui.setvar(checkbox_group, "checkbox_classification", True)
        app.gui.setvar(checkbox_group, "checkbox_damage_values", True)
        app.gui.setvar(checkbox_group, "checkbox_elevation", True)
        app.gui.setvar(checkbox_group, "checkbox_finished_floor_height", True)

        # Set the sources
        app.gui.setvar(model, "source_asset_locations", "National Structure Inventory")
        app.gui.setvar(model, "source_classification", "National Structure Inventory")
        app.gui.setvar(
            model, "source_finished_floor_height", "National Structure Inventory"
        )
        app.gui.setvar(
            model, "source_max_potential_damage", "National Structure Inventory"
        )
        app.gui.setvar(model, "source_ground_elevation", "National Structure Inventory")

        # Set country
        app.active_model.domain.exposure_vm.set_country("United States")

        update_damage_curves()

        get_roads(model)

        dlg.close()

    except FileNotFoundError:
        app.gui.window.dialog_info(
            text="Please first select a model boundary.",
            title="No model boundary selected",
        )
        dlg.close()


def build_osm_exposure(*args):
    model = "fiat"
    checkbox_group = "_main"
    try:
        dlg = app.gui.window.dialog_wait("\nDownloading OSM data...")

        app.gui.setvar(
            model, "text_feedback_create_asset_locations", "OSM assets created"
        )

        crs = app.gui.getvar(model, "selected_crs")
        bf_conversion = app.gui.getvar(model, "bf_conversion")
        keep_unclassified = app.gui.getvar(model, "classification_unclassified_assets")
        ground_elevation_unit = app.gui.getvar(model, "ground_elevation_unit")
        # Set continent for damage curves
        country, continent = app.active_model.get_continent()
        app.gui.setvar("fiat", "OSM_continent", continent)
        app.gui.setvar("fiat", "OSM_country", country)
        app.gui.setvar(model, "ground_elevation_unit", "meters")

        ground_floor_height = float(app.gui.getvar(model, "osm_ground_floor_height"))
        (
            gdf,
            unique_primary_types,
            unique_secondary_types,
        ) = app.active_model.domain.exposure_vm.set_asset_locations_source_and_get_data(
            source="OSM",
            ground_floor_height=ground_floor_height,
            crs=crs,
            country=country,
            max_potential_damage="jrc_damage_values",
            grnd_elev_unit=ground_elevation_unit,
            bf_conversion=bf_conversion,
            keep_unclassified=keep_unclassified,
        )

        gdf.set_crs(crs, inplace=True)

        # Set the primary and secondary object type lists
        app.active_model.set_object_types(unique_primary_types, unique_secondary_types)

        # Set country
        app.active_model.domain.exposure_vm.set_country(country)

        # Set the buildings attribute to gdf for easy visualization of the buildings
        app.active_model.buildings = gdf

        # Create point data for display
        if not bf_conversion:
            point_buildings = app.active_model.convert_bf_into_centroids(
                app.active_model.buildings, app.gui.getvar("fiat", "selected_crs")
            )

            app.map.layer["buildings"].layer["exposure_points"].crs = crs
            app.map.layer["buildings"].layer["exposure_points"].set_data(
                point_buildings
            )
        else:
            app.map.layer["buildings"].layer["exposure_points"].crs = crs
            app.map.layer["buildings"].layer["exposure_points"].set_data(gdf)

        app.gui.setvar(model, "show_asset_locations", True)

        list_types = list(gdf["Secondary Object Type"].unique())
        list_types.sort()
        df = pd.DataFrame(
            data={
                "Secondary Object Type": list_types,
                "Assigned: Structure": "",
                "Assigned: Content": "",
            }
        )
        ## TODO: add the nr of stories and the basement?
        app.gui.setvar(model, "exposure_categories_to_link", df)

        # Set the checkboxes checked
        app.gui.setvar(checkbox_group, "checkbox_asset_locations", True)
        app.gui.setvar(checkbox_group, "checkbox_classification", True)
        app.gui.setvar(checkbox_group, "checkbox_damage_values", True)
        app.gui.setvar(checkbox_group, "checkbox_elevation", True)
        app.gui.setvar(checkbox_group, "checkbox_finished_floor_height", True)

        # Set the sources
        app.gui.setvar(model, "source_asset_locations", "Open Street Map")
        app.gui.setvar(model, "source_classification", "Open Street Map")
        app.gui.setvar(model, "source_finished_floor_height", "User input")
        app.gui.setvar(model, "source_max_potential_damage", "JRC Damage Values")
        app.gui.setvar(model, "source_ground_elevation", "None")

        # Update the damage curves to JRC Damage Curves
        update_damage_curves()

        # Add OSM roads
        get_roads(model)

        dlg.close()

    except FileNotFoundError:
        app.gui.window.dialog_info(
            text="Please first select a model boundary.",
            title="No model boundary selected",
        )
        dlg.close()


def build_user_exposure(*args):
    model = "fiat"
    checkbox_group = "_main"
    try:
        crs = app.gui.getvar(model, "selected_crs")
        source = app.gui.getvar(model, "source_asset_locations")

        ## TODO: Check if user model uses own data for parameters
        if source == "National Structure Inventory":
            country = "United States"
            max_potential_damage = "NSI"
            ground_floor_height = "NSI"
            source = "NSI"
        elif source == "Open Street Map":
            country = app.gui.getvar(model, "OSM_country")
            max_potential_damage = "jrc_damage_values"
            ground_floor_height = float(
                app.gui.getvar(model, "osm_ground_floor_height")
            )
            source = "OSM"
        else:
            source = "User Model"

        # Set exposure buildings model

        (
            gdf,
            unique_primary_types,
            unique_secondary_types,
        ) = app.active_model.domain.exposure_vm.set_asset_locations_source_and_get_data(
            source=source,
            ground_floor_height=ground_floor_height,
            crs=crs,
            country=country,
            max_potential_damage=max_potential_damage,
            grnd_elev_unit=app.gui.getvar(model, "ground_elevation_unit"),
        )

        # Set the buildings attribute to gdf for easy visualization of the buildings
        app.active_model.buildings = gdf[
            gdf["geometry"].geom_type.isin(["Point", "Polygon", "multiPolygon"])
        ]

        # get roads and set layer
        if (
            Path(os.path.abspath(""))
            / app.active_model.domain.fiat_model.root
            / "exposure"
            / "roads.gpkg"
        ).is_file():
            app.active_model.domain.exposure_vm.exposure_roads_model = ExposureRoadsSettings(
                roads_fn= 'OSM',
                road_types = get_road_types(),
                road_damage=None,
                unit=Units.feet.value,
            )
            get_roads(model)

        app.map.layer["buildings"].layer["exposure_points"].crs = crs
        app.map.layer["buildings"].layer["exposure_points"].set_data(
            app.active_model.buildings
        )

    except FileNotFoundError:
        app.gui.window.dialog_info(
            text="Something went wrong",
            title="Error",
        )


def get_roads(model):
    ## ROADS ##
    if app.gui.getvar(model, "include_osm_roads"):
        road_types = get_road_types()

        try:
            dlg = app.gui.window.dialog_wait("\nDownloading OSM data...")

            # Get the roads to show in the map
            gdf = app.active_model.domain.exposure_vm.get_osm_roads(
                road_types=road_types
            )
            gdf = gdf[gdf["geometry"].geom_type.isin(["MultiLineString", "LineString"])
            ]
            crs = app.gui.getvar("fiat", "selected_crs")
            gdf.set_crs(crs, inplace=True)

            app.map.layer["roads"].layer["exposure_lines"].crs = crs
            app.map.layer["roads"].layer["exposure_lines"].set_data(gdf)

            # Set the road damage threshold
            # road_damage_threshold = app.gui.getvar("fiat", "road_damage_threshold")
            # app.active_model.domain.vulnerability_vm.set_road_damage_threshold(
            #    road_damage_threshold
            # )

            # Show the roads
            app.active_model.show_exposure_roads()
            app.gui.setvar("_main", "checkbox_roads_(optional)", True)

            # Set the checkbox checked
            app.gui.setvar("fiat", "show_roads", True)

            dlg.close()
        except KeyError:
            app.gui.window.dialog_info(
                text="No OSM roads found in this area, try another or a larger area.",
                title="No OSM roads found",
            )
            dlg.close()
          


def get_road_types():
    model = "fiat"
    if app.gui.getvar(model, "include_all"):
        return [
            "motorway",
            "motorway_link",
            "primary",
            "primary_link",
            "secondary",
            "secondary_link",
            "tertiary",
            "tertiary_link",
            "residential",
            "unclassified",
        ]

    list_road_types = []
    if app.gui.getvar(model, "include_motorways"):
        list_road_types.extend(["motorway", "motorway_link"])
    if app.gui.getvar(model, "include_trunk"):
        list_road_types.extend(["trunk", "trunk_link"])
    if app.gui.getvar(model, "include_primary"):
        list_road_types.extend(["primary", "primary_link"])
    if app.gui.getvar(model, "include_secondary"):
        list_road_types.extend(["secondary", "secondary_link"])
    if app.gui.getvar(model, "include_tertiary"):
        list_road_types.extend(["tertiary", "tertiary_link"])

    return list_road_types


def display_roads(*args):
    """Show/hide roads layer"""
    app.gui.setvar("fiat", "show_roads", args[0])
    if args[0]:
        app.active_model.show_exposure_roads()
    else:
        app.active_model.hide_exposure_roads()


def display_asset_locations(*args):
    """Show/hide buildings layer"""
    app.gui.setvar("fiat", "show_asset_locations", args[0])
    if args[0]:
        app.map.layer["buildings"].clear()
        app.gui.setvar("fiat", "show_primary_classification", False)
        app.gui.setvar("fiat", "show_secondary_classification", False)
        app.map.layer["buildings"].layer["exposure_points"].crs = crs = app.gui.getvar(
            "fiat", "selected_crs"
        )
        app.map.layer["buildings"].layer["exposure_points"].set_data(
            app.active_model.buildings
        )

        app.active_model.show_exposure_buildings()
    else:
        app.active_model.hide_exposure_buildings()


def open_info(*args):
    app.gui.window.dialog_info(
        text="The threshold value indicates the water level at which a road is not accessible anymore.",
        title="Threshold value",
    )
