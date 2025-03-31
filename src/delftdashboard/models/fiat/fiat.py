import os
from pathlib import Path
import random
import geopandas as gpd
import pandas as pd
import pickle

from delftdashboard.app import app
from delftdashboard.operations.model import GenericModel
from delftdashboard.models.fiat.exposure_start import add_exposure_locations_to_model
from delftdashboard.operations.checklist import zoom_to_boundary
from delftdashboard.operations import update
from delftdashboard.toolboxes.modelmaker_fiat.modelmaker_fiat import (
    generate_boundary,
    set_active_area_file,
)
from hydromt_fiat.api.hydromt_fiat_vm import HydroMtViewModel
from hydromt_fiat.api.data_types import Currency, Units, ExposureRoadsSettings
from hydromt_fiat.api.exposure_vm import ExposureVector, ExposureViewModel
from hydromt_fiat.fiat import FiatModel
from hydromt.log import setuplog

import copy
from .utils import make_labels


class Model(GenericModel):
    def __init__(self, name):
        super().__init__()

        self.name = name
        self.long_name = "FIAT"
        self.buildings = gpd.GeoDataFrame()
        self.roads = gpd.GeoDataFrame()
        self.damage_function_database = pd.DataFrame()
        self.occupancy_to_description = dict()
        self.description_to_occupancy = dict()
        self.default_dict_categories = dict()
        self.updated_dict_categories = dict()
        self.aggregation = gpd.GeoDataFrame()

        print("Model " + self.name + " added!")
        self.active_domain = 0
        self.domain = None

        # Set GUI variables
        self.set_gui_variables()

    def initialize_domain(self, root):
        self.domain = HydroMtViewModel(
            app.config["working_directory"], app.config["data_libs"], root
        )

    def add_layers(self):
        # Add main DDB layer
        layer = app.map.add_layer("buildings")

        layer.add_layer(
            "exposure_points",
            type="circle",
            circle_radius=3,
            legend_position="top-right",
            legend_title="Buildings",
            fill_color="orange",
            line_color="transparent",
            hover_property="secondary_object_type",
            big_data=True,
            min_zoom=10,
        )

        layer.add_layer(
            "primary_classification",
            type="circle",
            circle_radius=5,
            legend_position="top-right",
            legend_title="Buildings",
            fill_color="orange",
            line_color="transparent",
            hover_property="primary_object_type",
            big_data=True,
            min_zoom=10,
        )

        layer.add_layer(
            "secondary_classification",
            type="circle",
            circle_radius=3,
            legend_position="top-right",
            legend_title="Buildings",
            fill_color="orange",
            line_color="transparent",
            hover_property="secondary_object_type",
            big_data=True,
            min_zoom=10,
        )

        layer.add_layer(
            "asset_height",
            type="circle",
            circle_radius=3,
            legend_position="top-right",
            legend_title=f'Ground Floor Height [{app.gui.getvar("fiat", "view_tab_unit")}]',
            # TODO retrieve the unit in the legend title from the data, not hardcoded
            line_color="transparent",
            hover_property="ground_flht",
            big_data=True,
            min_zoom=10,
        )

        layer.add_layer(
            "max_potential_damage_struct",
            type="circle",
            circle_radius=3,
            legend_position="top-right",
            legend_title=f'Max. potential damage: Structure [{app.gui.getvar("fiat", "damage_unit")}]',
            # TODO retrieve the unit in the legend title from the data, not hardcoded
            line_color="transparent",
            hover_property="max_damages_structure",
            big_data=True,
            min_zoom=10,
        )

        layer.add_layer(
            "max_potential_damage_cont",
            type="circle",
            circle_radius=3,
            legend_position="top-right",
            legend_title=f'Max. potential damage: Content [{app.gui.getvar("fiat", "damage_unit")}]',
            # TODO retrieve the unit in the legend title from the data, not hardcoded
            line_color="transparent",
            hover_property="max_damages_content",
            big_data=True,
            min_zoom=10,
        )
        layer.add_layer(
            "ground_elevation",
            type="circle",
            circle_radius=3,
            legend_position="top-right",
            legend_title=f'Ground Elevation [{app.gui.getvar("fiat", "view_tab_unit")}]',
            line_color="transparent",
            hover_property="ground_elevtn",
            big_data=True,
            min_zoom=10,
        )
        layer.add_layer(
            "SVI",
            type="circle",
            circle_radius=3,
            legend_position="top-right",
            legend_title="Social Vulnerability Index",
            fill_color="purple",
            line_color="transparent",
            hover_property="SVI",
            big_data=True,
            min_zoom=10,
        )
        layer = app.map.add_layer("roads")
        layer.add_layer(
            "exposure_lines",
            type="line",
            legend_position="top-right",
            fill_color="purple",
            line_color="purple",
            line_width=3,
            circle_radius=0,
            hover_property="secondary_object_type",
        )

        layer = app.map.add_layer("aggregation")
        layer.add_layer(
            "aggregation_layer",
            type="choropleth",
            legend_position="top-right",
            legend_title="Base Zone",
            hover_property="",
        )

    def set_layer_mode(self, mode):
        if mode == "inactive":
            # Everything made visible
            app.map.layer["buildings"].set_mode("inactive")
            app.map.layer["roads"].set_mode("inactive")
        elif mode == "invisible":
            # Everything set to invisible
            app.map.layer["buildings"].set_mode("invisible")
            app.map.layer["roads"].set_mode("invisible")

    def set_gui_variables(self):
        ## CHECKBOXES ##
        group = "_main"
        app.gui.setvar(group, "checkbox_model_boundary", False)
        app.gui.setvar(group, "checkbox_asset_locations", False)
        app.gui.setvar(group, "checkbox_classification", False)
        app.gui.setvar(group, "checkbox_damage_values", False)
        app.gui.setvar(group, "checkbox_finished_floor_height", False)
        app.gui.setvar(group, "checkbox_attributes_(optional)", False)
        app.gui.setvar(group, "checkbox_vulnerability", False)
        app.gui.setvar(group, "checkbox_equity_(optional)", False)
        app.gui.setvar(group, "checkbox_roads_(optional)", False)
        app.gui.setvar(group, "show_fiat_checkbox", False)

        group = "fiat"

        ## Damage curve tables ##
        app.gui.setvar(group, "OSM_continent", None)
        app.gui.setvar(group, "OSM_country", None)
        default_curves = app.data_catalog.get_dataframe("default_hazus_iwr_linking")
        app.gui.setvar(
            group,
            "damage_curves_table",
            default_curves[["Exposure Link", "Damage Type", "Source", "Description"]],
        )
        app.gui.setvar(
            group, "selected_damage_curve_database", "default_vulnerability_curves"
        )
        app.gui.setvar(
            group, "selected_damage_curve_linking_table", "default_hazus_iwr_linking"
        )

        damage_functions_database = app.data_catalog.get_dataframe(
            "default_vulnerability_curves"
        )
        damage_functions_database_info = damage_functions_database[
            ["Occupancy", "Source", "Description", "Damage Type", "ID"]
        ]
        self.damage_function_database = damage_functions_database_info
        default_curves_table = default_curves[
            ["Occupancy", "Source", "Description", "Damage Type", "ID"]
        ]
        default_curves_table.sort_values("Occupancy", inplace=True, ignore_index=True)

        app.gui.setvar(
            group, "damage_curves_standard_info_static", default_curves_table
        )
        app.gui.setvar(
            group, "damage_curves_standard_info", damage_functions_database_info
        )

        default_occupancy_df = app.data_catalog.get_dataframe(
            "hazus_iwr_occupancy_classes"
        )
        default_occupancy_df.sort_values(
            "Occupancy Class", inplace=True, ignore_index=True
        )
        default_occupancy_df.fillna("", inplace=True)
        default_occupancy_df_adjusted = default_occupancy_df[
            default_occupancy_df["Occupancy Class"] != "RES1"
        ]
        app.gui.setvar(group, "hazus_iwr_occupancy_classes", default_occupancy_df)
        app.gui.setvar(
            group, "hazus_iwr_occupancy_classes_adjusted", default_occupancy_df_adjusted
        )

        cols = [
            "-9",
            "-8",
            "-7",
            "-6",
            "-5",
            "-4",
            "-3",
            "-2",
            "-1",
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "11",
            "12",
            "13",
            "14",
            "15",
            "16",
            "17",
            "18",
            "19",
            "20",
            "21",
            "22",
            "23",
            "24",
        ]
        app.gui.setvar(
            group,
            "damage_curves_standard_curves",
            damage_functions_database[["ID", "Description"] + cols],
        )
        app.gui.setvar(group, "selected_damage_curves", pd.DataFrame(columns=cols))

        # User classification
        app.gui.setvar(group, "old_occupancy_type", "")
        app.gui.setvar(group, "new_occupancy_type", "")
        app.gui.setvar(group, "remove_classification", False)

        ## Standardizing of occupancy categories ##
        self.default_dict_categories = {x: x for x in list(default_curves["Occupancy"])}
        self.updated_dict_categories = self.default_dict_categories

        # Source names #
        app.gui.setvar(group, "source_asset_locations", "")
        app.gui.setvar(group, "source_classification", "")
        app.gui.setvar(group, "source_finished_floor_height", "")
        app.gui.setvar(group, "source_max_potential_damage", "")
        app.gui.setvar(group, "source_ground_elevation", "")

        # Model type #
        app.gui.setvar(
            group, "model_type", "Start with National Structure Inventory (NSI)"
        )
        app.gui.setvar(group, "include_osm_roads", False)
        app.gui.setvar(group, "damage_unit", Currency.euro.value)
        app.gui.setvar(group, "bf_conversion", True)
        app.gui.setvar(group, "classification_unclassified_assets", True)

        # Units
        app.gui.setvar(group, "osm_roads_threshold_unit", "Threshold value (ft)")

        ## ROADS ##
        app.gui.setvar(group, "include_motorways", True)
        app.gui.setvar(group, "include_trunk", True)
        app.gui.setvar(group, "include_primary", True)
        app.gui.setvar(group, "include_secondary", False)
        app.gui.setvar(group, "include_tertiary", False)
        app.gui.setvar(group, "include_all", False)

        ## DISPLAY LAYERS ##
        app.gui.setvar(group, "properties_to_display", None)
        app.gui.setvar(group, "show_asset_locations", False)
        app.gui.setvar(group, "show_classification", False)
        app.gui.setvar(group, "show_asset_heights", False)
        app.gui.setvar(group, "show_max_potential_values", False)
        app.gui.setvar(group, "show_aggregation", False)
        app.gui.setvar(group, "show_damage_curves", False)
        app.gui.setvar(group, "show_roads", False)
        app.gui.setvar(group, "show_attributes", False)
        app.gui.setvar(group, "show_extraction_method", False)

        ## SELECTING VULNERABILITY CURVES ##
        app.gui.setvar(group, "active_damage_function", [0])
        app.gui.setvar(group, "active_exposure_category", [0])

        df = pd.DataFrame(
            columns=[
                "secondary_object_type",
                "Assigned: Structure",
                "Assigned: Content",
            ]
        )
        app.gui.setvar(group, "exposure_categories_to_link", df)

        ## STANDARDIZING EXPOSURE CATEGORIES ##
        df = pd.DataFrame(columns=["primary_object_type", "Assigned"])
        app.gui.setvar(group, "exposure_categories_to_standardize", df)
        app.gui.setvar(group, "active_exposure_category_standardize", [0])
        app.gui.setvar(group, "active_related_occupancy_type", [0])

        ## HAZUS IWR OCCUPANCY CLASSES ##
        self.occupancy_to_description = default_occupancy_df.set_index(
            "Occupancy Class"
        ).to_dict(orient="index")
        self.description_to_occupancy = default_occupancy_df.set_index(
            "Class Description"
        ).to_dict(orient="index")

        app.gui.setvar(group, "dmg_functions_html_filepath", "")

        ## SVI ##
        app.gui.setvar(group, "list_of_census_years", ["2020", "2021"])
        app.gui.setvar(group, "selected_year", "2020")

        app.gui.setvar(group, "use_svi", False)
        app.gui.setvar(group, "use_equity", True)

        app.gui.setvar(group, "extraction_method_string", ["Area", "Centroid"])
        app.gui.setvar(group, "extraction_method_value", ["area", "centroid"])
        app.gui.setvar(group, "extraction_method", "centroid")
        app.gui.setvar(
            group, "extraction_method_exception_string", ["Area", "Centroid"]
        )
        app.gui.setvar(group, "extraction_method_exception_value", ["area", "centroid"])
        app.gui.setvar(group, "extraction_method_exception", None)
        app.gui.setvar(group, "show_secondary_classification", False)
        app.gui.setvar(group, "create_curves", False)
        app.gui.setvar(group, "asset_location_file", "*asset location file path*")
        app.gui.setvar(group, "control_enable", 0)
        app.gui.setvar(group, "area_classification", None)
        app.gui.setvar(group, "classification_display_name", "")
        app.gui.setvar(group, "classification_display_string", [])
        app.gui.setvar(group, "classification_display_value", [])
        app.gui.setvar(group, "classification_source", "nsi_data")
        app.gui.setvar(
            group,
            "classification_source_string",
            ["National Structure Inventory (NSI)", "Upload data"],
        )
        app.gui.setvar(group, "view_tab_unit", "")
        app.gui.setvar(
            group, "classification_source_value", ["nsi_data", "upload_data"]
        )
        app.gui.setvar(group, "classification_source_path", "")
        app.gui.setvar(
            group,
            "object_type_string",
            [
                "Primary Object Type",
                "Secondary_object_type",
            ],  # Make sure these are capitalized
        )
        app.gui.setvar(
            group, "object_type_value", ["primary_object_type", "secondary_object_type"]
        )  # Make sure these are capitalized
        app.gui.setvar(
            group, "object_type", "primary_object_type"
        )  # Make sure this is capitalized
        app.gui.setvar(
            group,
            "classification_file_field_name_string",
            [],
        )
        app.gui.setvar(
            group,
            "classification_file_field_name_value",
            [],
        )
        app.gui.setvar(group, "classification_file_field_name", 0)
        app.gui.setvar(
            group,
            "selected_primary_classification_string",
            [],
        )
        app.gui.setvar(
            group,
            "selected_primary_classification_value",
            [],
        )

        ## Finished Floor Height tab ##
        app.gui.setvar(group, "loaded_asset_heights_files", 0)
        app.gui.setvar(
            group,
            "loaded_asset_heights_files_string",
            [],
        )
        app.gui.setvar(
            group,
            "loaded_asset_heights_files_value",
            [],
        )
        app.gui.setvar(group, "heights_file_field_name", 0)
        app.gui.setvar(group, "heights_file_field_name_string", [])
        app.gui.setvar(
            group,
            "heights_file_field_name_value",
            [],
        )

        # Finished floor height settings popup #
        app.gui.setvar(group, "max_dist_gfh", 10)
        app.gui.setvar(group, "method_gfh", "nearest")
        app.gui.setvar(group, "method_gfh_string", ["nearest", "intersection"])
        app.gui.setvar(group, "method_gfh_value", ["nearest", "intersection"])

        ## Ground Elevation tab ##
        app.gui.setvar("fiat", "update_source_ground_elevation", "sfincs_data")
        app.gui.setvar(group, "loaded_ground_elevation_files", 0)
        app.gui.setvar(
            group,
            "ground_elevation_files_string",
            ["SFINCS Ground Elevation", "Upload data"],
        )
        app.gui.setvar(
            group,
            "ground_elevation_files_value",
            ["sfincs_data", "upload_data"],
        )
        app.gui.setvar(group, "ground_elevation_unit", None),
        app.gui.setvar(group, "ground_elevation_unit_feet", False)
        app.gui.setvar(group, "ground_elevation_unit_meters", False)
        app.gui.setvar(
            group,
            "loaded_ground_elevation_files_string",
            [],
        )
        app.gui.setvar(
            group,
            "loaded_ground_elevation_files_value",
            [],
        )

        ## Damage values tab ##
        app.gui.setvar(group, "loaded_damages_files", 0)
        app.gui.setvar(
            group,
            "loaded_damages_files_string",
            [],
        )
        app.gui.setvar(
            group,
            "loaded_damages_files_value",
            [],
        )
        app.gui.setvar(group, "damages_file_field_name_list", [])
        app.gui.setvar(group, "damages_file_field_name", 0)
        app.gui.setvar(group, "damages_file_field_name_string", [])
        app.gui.setvar(
            group,
            "damages_file_field_name_value",
            [],
        )
        app.gui.setvar(group, "loaded_damages_files_value_list", [])
        app.gui.setvar(group, "loaded_damages_files_string_list", [])
        app.gui.setvar(group, "damage_type", "structure")
        app.gui.setvar(group, "damage_type_list", [])
        app.gui.setvar(group, "damage_type_string", ["structure", "content"])
        app.gui.setvar(group, "damage_type_value", ["structure", "content"])

        # Damages settings popup #
        app.gui.setvar(group, "max_dist_damages", 10)
        app.gui.setvar(group, "max_dist_damages_list", [])
        app.gui.setvar(group, "method_damages", "nearest")
        app.gui.setvar(group, "method_damages_list", [])
        app.gui.setvar(group, "method_damages_string", ["nearest", "intersection"])
        app.gui.setvar(group, "method_damages_value", ["nearest", "intersection"])

        app.gui.setvar(group, "selected_primary_classification_value", 0)
        app.gui.setvar(group, "selected_asset_locations", 0)
        app.gui.setvar(
            group,
            "selected_asset_locations_string",
            ["National Structure Inventory (NSI)"],
        )
        app.gui.setvar(
            group,
            "selected_secondary_classification_string",
            [""],
        )
        app.gui.setvar(
            group,
            "selected_secondary_classification_value",
            [""],
        )
        app.gui.setvar(group, "osm_ground_floor_height", 0.2)
        app.gui.setvar(group, "loaded_aggregation_files", 0)
        app.gui.setvar(
            group,
            "loaded_aggregation_files_string",
            [],
        )
        app.gui.setvar(
            group,
            "loaded_aggregation_files_value",
            [],
        )
        app.gui.setvar(group, "selected_aggregation_files", 0)
        app.gui.setvar(group, "selected_aggregation_files_string", [])
        app.gui.setvar(group, "aggregation_file_field_name", "")
        app.gui.setvar(group, "aggregation_file_field_name_string", [])
        app.gui.setvar(
            group,
            "aggregation_file_field_name_value",
            [],
        )
        app.gui.setvar(group, "aggregation_label_string", "")
        app.gui.setvar(group, "aggregation_label_display_name", "")
        app.gui.setvar(group, "aggregation_label_display_string", [])
        app.gui.setvar(group, "aggregation_label_display_value", [])
        app.gui.setvar(group, "aggregation_table_name", [0])
        app.gui.setvar(
            group,
            "aggregation_table",
            pd.DataFrame(
                columns=["File", "Attribute ID", "Attribute Label", "File Path"]
            ),
        )
        app.gui.setvar(group, "assign_classification_active", False)
        app.gui.setvar(group, "selected_secondary_classification_value", 0)
        app.gui.setvar(group, "show_primary_classification", None)
        app.gui.setvar(group, "show_secondary_classification", None)
        app.gui.setvar(group, "classification_field", None)
        app.gui.setvar(group, "show_aggregation_zone", False)
        app.gui.setvar(group, "selected_crs", "EPSG:4326")
        app.gui.setvar(group, "selected_scenario", "MyScenario")
        app.gui.setvar(group, "created_nsi_assets", None)
        app.gui.setvar(group, "text_feedback_create_asset_locations", "")
        app.gui.setvar(group, "scenario_folder", "")
        app.gui.setvar(group, "apply_extraction_method", None)
        app.gui.setvar(group, "extraction_method_exception_apply", None)
        app.gui.setvar(
            group,
            "vulnerability_source_input_string",
            [
                "Hazus",
                "JRC",
                "Manual Input",
            ],
        )
        app.gui.setvar(
            group,
            "vulnerability_source_input_value",
            ["hazus", "jrc", "manual"],
        )
        app.gui.setvar(group, "vulnerability_source_input", "hazus")
        app.gui.setvar(group, "created_vulnerability_curves_string", [""])
        app.gui.setvar(group, "created_vulnerability_curves_value", [""])
        app.gui.setvar(
            group,
            "curve_classification_string",
            [
                "",
            ],
        )
        app.gui.setvar(
            group,
            "curve_classification_value",
            [""],
        )
        app.gui.setvar(group, "selected_vulnerability_curve", "")
        app.gui.setvar(group, "selected_secondary_classification_type", "")
        app.gui.setvar(group, "text_feedback_vulnerability_source_input", "")
        app.gui.setvar(group, "show_vulnerability_curves", "")
        app.gui.setvar(group, "nr_selected_bathymetry_datasets", 0)
        app.gui.setvar(group, "show_damage_values", 0)
        app.gui.setvar(group, "created_vulnerability_curves", 0)
        app.gui.setvar(group, "linking_object_type", 0)
        # app.gui.setvar(group, "road_damage_threshold", 1)

        app.gui.setvar(group, "max_potential_damage_name", "")
        app.gui.setvar(group, "max_potential_damage_string", [])
        app.gui.setvar(group, "max_potential_damage_value", [])
        app.gui.setvar(group, "view_svi_value", pd.DataFrame)
        app.gui.setvar(
            group,
            "view_exposure_value",
            pd.DataFrame(
                columns=[
                    "object_id",
                    "object_name",
                    "primary_object_type",
                    "secondary_object_type",
                    "max_damages_structure",
                    "max_damages_content",
                    "ground_flht",
                    "ground_elevtn",
                    "extract_method",
                    "fn_damages_structure",
                    "fn_damages_content",
                    "lanes",
                    "Segment Length [m]",
                    "SVI_key_domain",
                    "SVI",
                ]
            ),
        )

    @staticmethod
    def set_dict_inverted(dictionary):
        return {value: key for key, value in dictionary.items()}

    def set_input_variables(self):
        # Update all model input variables
        for var_name in vars(self.domain.input.variables):
            setattr(
                self.domain.input.variables, var_name, app.gui.getvar("fiat", var_name)
            )

    def select_working_directory(self, path=None):
        root = path or os.getcwd()
        app.gui.setvar("fiat", "selected_scenario", Path(root).stem)
        app.gui.setvar("fiat", "scenario_folder", Path(root))
        self.initialize_domain(root)
        if self.domain.fiat_model.root != root:
            self.domain.fiat_model.set_root(root, mode="w+")

    def open(self):
        # Open input file, and change working directory
        fname = app.gui.window.dialog_select_path("Select an existing model folder")
        if fname:
            dlg = app.gui.window.dialog_wait("Loading fiat model ...")

            # Reading in model
            self.domain = HydroMtViewModel(
                app.config["working_directory"],
                app.config["data_libs"],
                fname,
            )
            self.domain.read()

            # Get region
            fpath = str(
                Path(os.path.abspath(""))
                / self.domain.fiat_model.root
                / "geoms"
                / "region.geojson"
            )

            # Set variables from existing model
            with open(
                Path(os.path.abspath(""))
                / self.domain.fiat_model.root
                / "variables.pkl",
                "rb",
            ) as f:
                variables = pickle.load(f)
            app.gui.variables["_main"] = variables["main"]
            app.gui.variables["fiat"] = variables["fiat"]
            app.gui.variables["modelmaker_fiat"] = variables["modelmaker_fiat"]

            # Get variables sources and parameters
            max_source = app.gui.getvar("fiat", "source_max_potential_damage")
            gfh_source = app.gui.getvar("fiat", "source_finished_floor_height")
            ground_elevation_source = app.gui.getvar("fiat", "source_ground_elevation")
            additional_attr = app.gui.getvar("fiat", "loaded_aggregation_files_string")

            # Set area of interest
            app.gui.setvar("fiat", "selected_asset_locations_string", "User model")
            app.gui.setvar(
                "modelmaker_fiat",
                "active_area_of_interest",
                "area_of_interest_from_file",
            )
            app.gui.setvar("modelmaker_fiat", "fn_model_boundary_file_list", fpath)

            # Select filepath through self.domain output exposure
            self.domain.exposure_vm.create_interest_area(fpath=fpath)
            gdf = gpd.read_file(fpath)
            gdf.to_crs(app.crs, inplace=True)
            layer = app.map.layer["modelmaker_fiat"].layer["area_of_interest_from_file"]
            layer.set_data(gdf)
            app.active_toolbox.area_of_interest = gdf.set_crs(app.crs)

            # exposure_buildings_model
            add_exposure_locations_to_model()
            # set fiat model to vm
            self.domain.fiat_model.exposure.exposure_db = (
                self.domain.exposure_vm.exposure.exposure_db
            )
            self.domain.fiat_model.exposure.exposure_geoms = (
                self.domain.exposure_vm.exposure.exposure_geoms
            )

            # Update exposure
            # Re-setting variables from existing model
            with open(
                Path(os.path.abspath(""))
                / self.domain.fiat_model.root
                / "variables.pkl",
                "rb",
            ) as f:
                variables = pickle.load(f)
            app.gui.variables["_main"] = variables["main"]
            app.gui.variables["fiat"] = variables["fiat"]
            app.gui.variables["modelmaker_fiat"] = variables["modelmaker_fiat"]

            ## Max potential Damages
            if max_source not in ["National Structure Inventory", "JRC Damage Values"]:
                idx = app.gui.getvar("fiat", "loaded_damages_files")
                self.domain.exposure_vm.set_damages(
                    source=(app.gui.getvar("fiat", "loaded_damages_files_value_list")),
                    attribute_name=app.gui.getvar(
                        "fiat", "damages_file_field_name_list"
                    ),
                    method_damages=app.gui.getvar("fiat", "method_damages_list"),
                    max_dist=app.gui.getvar("fiat", "max_dist_damages_list"),
                    damage_types=app.gui.getvar("fiat", "damage_type_list"),
                )
                update.update_parameters("Max Potential Damages")

            ## Finished Floor Height
            if gfh_source not in ["National Structure Inventory", "User input"]:
                idx = app.gui.getvar("fiat", "loaded_asset_heights_files")
                idx_attr = app.gui.getvar("fiat", "heights_file_field_name")
                self.domain.exposure_vm.set_ground_floor_height(
                    source=str(
                        app.gui.getvar("fiat", "loaded_asset_heights_files_value")[idx]
                    ),
                    gfh_attribute_name=str(
                        app.gui.getvar("fiat", "heights_file_field_name_value")[
                            idx_attr
                        ]
                    ),
                    gfh_method=app.gui.getvar("fiat", "method_gfh"),
                    max_dist=app.gui.getvar("fiat", "max_dist_gfh"),
                )
                update.update_parameters("ground_flht")

            ## Ground Elevation
            if ground_elevation_source not in ["National Structure Inventory", "None"]:
                idx = app.gui.getvar("fiat", "loaded_ground_elevation_files")
                unit = app.gui.getvar("fiat", "ground_elevation_unit")
                self.domain.exposure_vm.set_ground_elevation(
                    source=str(
                        app.gui.getvar("fiat", "loaded_ground_elevation_files_value")[
                            idx
                        ]
                    ),
                    unit=unit,
                )
                update.update_parameters("ground_elevtn")

            ## Additional Atrributes
            if len(additional_attr) > 0:
                table = app.gui.getvar("fiat", "aggregation_table")
                source = [str(item) for item in table["File Path"].to_list()]
                attribute_name = table["Attribute ID"].to_list()
                label_names = table["Attribute Label"].to_list()
                self.domain.exposure_vm.set_aggregation_areas_config(
                    files=source,
                    attribute_names=attribute_name,
                    label_names=label_names,
                )
                self.domain.fiat_model.setup_additional_attributes(
                    source, attribute_name, label_names
                )

            # vulnerability_buildings_model
            selected_damage_curve_database = app.gui.getvar(
                "fiat", "selected_damage_curve_database"
            )
            selected_link_table = app.gui.getvar(
                "fiat", "selected_damage_curve_linking_table"
            )
            self.domain.vulnerability_vm.add_vulnerability_curves_to_model(
                selected_damage_curve_database, selected_link_table
            )

            # Change working directory
            os.chdir(fname)

            # Change CRS
            app.crs = self.domain.fiat_model.config["global"]["crs"]

            zoom_to_boundary()

            # Show exposure buildings
            self.show_exposure_buildings()

            dlg.close()

    def save(self):
        self.domain.write()

    def load(self):
        self.domain.read()

    def set_crs(self, crs):
        self.domain.crs = crs

    def get_filtered_damage_function_database(
        self, filter: str, col: str = "Occupancy"
    ):
        df = copy.deepcopy(self.damage_function_database)
        filter_occtype = self.updated_dict_categories[filter]
        return df.loc[df[col].str.startswith(filter_occtype)]

    @staticmethod
    def generate_random_colors(n):
        return ["#%06x" % random.randint(0, 0xFFFFFF) for _ in range(n)]

    def create_paint_properties(self, gdf, attribute, type="circle", opacity=1):
        unique_types = list(gdf[attribute].unique())
        color_properties = [
            "match",
            ["get", attribute],
        ]
        colors = self.generate_random_colors(len(unique_types))
        attr_color_list = [item for pair in zip(unique_types, colors) for item in pair]
        color_properties.extend(attr_color_list)
        color_properties.append("#000000")

        if type == "circle":
            paint_properties = {
                "circle-color": color_properties,
                "circle-stroke-width": 2,
                "circle-stroke-color": "black",
                "circle-stroke-opacity": 0,
                "circle-radius": 3,
                "circle-opacity": opacity,
            }
        elif type == "polygon":
            paint_properties = {
                "fill-color": color_properties,
                "fill-opacity": opacity,
            }
        return paint_properties

    def get_paint_properties(self, type="secondary") -> dict:
        """Get's NSI-specific paint properties to visualize NSI data

        Parameters
        ----------
        type : str, optional
            Type of occupancy, "primary" or "secondary", by default "secondary"

        Returns
        -------
        dict
            The paint properties for mapbox
        """
        if type == "primary":
            circle_color = [
                "match",
                ["get", "primary_object_type"],
                "AGR",
                "#009c99",
                "COM",
                "#6590bb",
                "EDU",
                "#7665b1",
                "GOV",
                "#710b60",
                "IND",
                "#10f276",
                "REL",
                "#4cf6ce",
                "RES",
                "#f55243",
                "#000000",
            ]

        if type == "secondary":
            circle_color = [
                "match",
                ["get", "secondary_object_type"],
                "AGR1",
                "#009c99",
                "COM1",
                "#6590bb",
                "COM10",
                "#5b6d47",
                "COM2",
                "#b63f1d",
                "COM3",
                "#70d073",
                "COM4",
                "#f2facd",
                "COM5",
                "#f4428d",
                "COM6",
                "#2f5770",
                "COM7",
                "#472d9c",
                "COM8",
                "#816035",
                "COM9",
                "#f9917f",
                "EDU1",
                "#7665b1",
                "EDU2",
                "#c85dcf",
                "GOV1",
                "#710b60",
                "GOV2",
                "#fd32f1",
                "IND1",
                "#10f276",
                "IND2",
                "#bc2db1",
                "IND3",
                "#09459b",
                "IND4",
                "#2c3d14",
                "IND5",
                "#90f27d",
                "IND6",
                "#388bb3",
                "REL1",
                "#4cf6ce",
                "RES1-1SNB",
                "#f55243",
                "RES1-1SWB",
                "#1f520d",
                "RES1-2SNB",
                "#143523",
                "RES1-2SWB",
                "#301eb1",
                "RES1-3SNB",
                "#80f304",
                "RES1-3SWB",
                "#4aab4e",
                "RES2",
                "#7e0309",
                "RES3A",
                "#c6a083",
                "RES3B",
                "#919900",
                "RES3C",
                "#337adc",
                "RES3D",
                "#571950",
                "RES3E",
                "#a2863a",
                "RES3F",
                "#330b34",
                "RES4",
                "#37d6c8",
                "RES5",
                "#939b8f",
                "RES6",
                "#665435",
                "#000000",
            ]

        if type == "osm_primary":
            circle_color = [
                "match",
                ["get", "primary_object_type"],
                "commercial",
                "#6590bb",
                "infrastructure",
                "#7665b1",
                "transport",
                "#710b60",
                "industrial",
                "#10f276",
                "agriculture",
                "#4cf6ce",
                "residential",
                "#f55243",
                "building averaged",
                "#80f304",
                "roads",
                "#4aab4e",
                "#000000",
            ]

        if type == "osm_secondary":
            circle_color = [
                "match",
                ["get", "secondary_object_type"],
                "retail",
                "#009c99",
                "commercial",
                "#6590bb",
                "infrastructure",
                "#7665b1",
                "transport",
                "#710b60",
                "industrial",
                "#10f276",
                "agriculture",
                "#4cf6ce",
                "residential",
                "#f55243",
                "building averaged",
                "#80f304",
                "roads",
                "#4aab4e",
                "#000000",
            ]

        if type == "asset_height":
            circle_color = [
                "step",
                ["get", "ground_flht"],
                "#FFFFFF",
                0,
                "#EBF0FC",
                0.5,
                "#D6E1F8",
                1.0,
                "#A4C4F2",
                1.5,
                "#6C95E1",
                2.0,
                "#3750B2",
                2.5,
                "#1A237E",
            ]
        if type == "damage_struct":
            circle_color = [
                "step",
                ["get", "max_damages_structure"],
                "#FFFFFF",
                0,
                "#FFF4E7",
                15000.0,
                "#FEE9CE",
                50000.0,
                "#FDBB84",
                100000.0,
                "#FC844E",
                250000.0,
                "#E03720",
                500000.0,
                "#860000",
            ]
        if type == "damage_cont":
            circle_color = [
                "step",
                ["get", "max_damages_content"],
                "#FFFFFF",
                0,
                "#FFF4E7",
                15000.0,
                "#FEE9CE",
                50000.0,
                "#FDBB84",
                100000.0,
                "#FC844E",
                250000.0,
                "#E03720",
                500000.0,
                "#860000",
            ]
        if type == "ground_elevation":
            circle_color = [
                "step",
                ["get", "ground_elevtn"],
                "#FFFFFF",
                0,
                "#F7FFF6",
                1,
                "#E1FCE4",
                2,
                "#CDEA88",
                3,
                "#A8E496",
                4,
                "#74CC9C",
                5,
                "#4BAF7A",
                6,
                "#3F9E6F",
                7,
                "#359364",
                8,
                "#2C7B5A",
                9,
                "#236B50",
                10,
                "#1A5A45",
                11,
                "#124A3A",
                12,
                "#093931",
                13,
                "#032C27",
                14,
                "#00211D",
                15,
                "#001615",
            ]
        if type == "SVI_key_domain":
            circle_color = [
                "match",
                ["get", "SVI_key_domain"],
                "Age",
                "#009c99",
                "Dependence",
                "#6590bb",
                "Education",
                "#5b6d47",
                "Employment",
                "#b63f1d",
                "Ethnicity",
                "#70d073",
                "Family structure",
                "#00211D",
                "Gender",
                "#7665b1",
                "Health",
                "#c85dcf",
                "Housing",
                "#710b60",
                "Income",
                "#fd32f1",
                "Language",
                "#10f276",
                "Mobility",
                "#bc2db1",
                "Race",
                "#09459b",
                "Wealth",
                "#4cf6ce",
                "#000000",
            ]
        if type == "SVI":
            circle_color = [
                "step",
                ["get", "SVI"],
                "#000080 ",
                -2,
                "#0000FF",
                -1.5,
                "#0080FF",
                -1,
                "#00FFFF",
                -0.5,
                "#80FF80",
                0,
                "#FFFF00",
                0.5,
                "#FFD700",
                1,
                "#FFA500",
                1.5,
                "#FF4500",
                2.0,
                "#FF0000",
                2.5,
                "#800000",
                3,
                "#8B0000",
            ]

        paint_properties = {
            "circle-color": circle_color,
            "circle-stroke-width": 2,
            "circle-stroke-color": "black",
            "circle-stroke-opacity": 0,
            "circle-radius": 3,
            "circle-opacity": 1,
        }
        return paint_properties

    def show_classification(self, type="secondary"):
        """Show exposure layer(s)"""
        source = app.gui.getvar("fiat", "source_asset_locations")
        if type == "primary" and source == "Open Street Map":
            type = "osm_primary"
        elif type == "secondary" and source == "Open Street Map":
            type = "osm_secondary"
        if not self.buildings.empty:
            paint_properties = self.get_paint_properties(
                type=type
            )  # always paint according to primary
            color_items = paint_properties["circle-color"][2:-1]
            color_items.append("other")
            color_items.append(paint_properties["circle-color"][-1])
            legend = [
                {"style": color_items[i + 1], "label": color_items[i]}
                for i in range(0, len(color_items), 2)
            ]
            if type == "primary" or type == "osm_primary":
                app.map.layer["buildings"].layer["primary_classification"].set_data(
                    self.buildings, paint_properties, legend
                )
                self.show_exposure_buildings_primary()
            else:
                app.map.layer["buildings"].layer["secondary_classification"].set_data(
                    self.buildings, paint_properties, legend
                )
                self.show_exposure_buildings_secondary()

    def show_asset_height(self, type="asset_height"):
        if not self.buildings.empty:
            paint_properties = self.get_paint_properties(type=type)
            color_items = paint_properties["circle-color"][2:]

            colors = [color_items[i] for i in range(0, len(color_items), 2)]
            labels = make_labels(
                [color_items[i + 1] for i in range(0, len(color_items) - 1, 2)],
                decimals=1,
            )

            legend = [
                {"style": color, "label": label} for color, label in zip(colors, labels)
            ]
            app.map.layer["buildings"].layer["asset_height"].fill_color = (
                paint_properties["circle-color"]
            )
            app.map.layer["buildings"].layer["asset_height"].unit = app.gui.getvar(
                "fiat", "view_tab_unit"
            )
            app.map.layer["buildings"].layer[
                "asset_height"
            ].legend_title = (
                f'Finished Floor Height [{app.gui.getvar("fiat", "view_tab_unit")}]'
            )
            app.map.layer["buildings"].layer["asset_height"].set_data(
                self.buildings, paint_properties, legend
            )
            self.show_asset_heights()

    def show_max_potential_damage_struct(self, type="damage_struct"):
        """Show maximum potential damage: structure layer(s)"""
        if not self.buildings.empty:
            paint_properties = self.get_paint_properties(type=type)
            color_items = paint_properties["circle-color"][2:]

            colors = [color_items[i] for i in range(0, len(color_items), 2)]
            labels = make_labels(
                [color_items[i + 1] for i in range(0, len(color_items) - 1, 2)],
                decimals=1,
            )

            legend = [
                {"style": color, "label": label} for color, label in zip(colors, labels)
            ]
            app.map.layer["buildings"].layer[
                "max_potential_damage_struct"
            ].fill_color = paint_properties["circle-color"]
            app.map.layer["buildings"].layer[
                "max_potential_damage_struct"
            ].unit = self.domain.exposure_vm.exposure_buildings_model.damage_unit
            app.map.layer["buildings"].layer[
                "max_potential_damage_struct"
            ].legend_title = f"Max. potential damage: Structure [{self.domain.exposure_vm.exposure_buildings_model.damage_unit}]"
            app.map.layer["buildings"].layer["max_potential_damage_struct"].set_data(
                self.buildings, paint_properties, legend
            )
            self.show_max_potential_damage_structure()

    def show_max_potential_damage_cont(self, type="damage_cont"):
        """Show maximum potential damage: content layer(s)"""
        if not self.buildings.empty:
            paint_properties = self.get_paint_properties(type=type)
            color_items = paint_properties["circle-color"][2:]

            colors = [color_items[i] for i in range(0, len(color_items), 2)]
            labels = make_labels(
                [color_items[i + 1] for i in range(0, len(color_items) - 1, 2)],
                decimals=1,
            )

            legend = [
                {"style": color, "label": label} for color, label in zip(colors, labels)
            ]
            app.map.layer["buildings"].layer["max_potential_damage_cont"].fill_color = (
                paint_properties["circle-color"]
            )
            app.map.layer["buildings"].layer[
                "max_potential_damage_cont"
            ].unit = self.domain.exposure_vm.exposure_buildings_model.damage_unit
            app.map.layer["buildings"].layer[
                "max_potential_damage_cont"
            ].legend_title = f"Max. potential damage: Content [{self.domain.exposure_vm.exposure_buildings_model.damage_unit}]"
            app.map.layer["buildings"].layer["max_potential_damage_cont"].set_data(
                self.buildings,
                paint_properties,
                legend,
            )
            self.show_max_potential_damage_content()

    def show_ground_elevation(self, type="ground_elevation"):
        """Show Ground Elevation"""
        if not self.buildings.empty:
            paint_properties = self.get_paint_properties(type=type)
            color_items = paint_properties["circle-color"][2:]

            colors = [color_items[i] for i in range(0, len(color_items), 2)]
            labels = make_labels(
                [color_items[i + 1] for i in range(0, len(color_items) - 1, 2)],
                decimals=1,
            )

            legend = [
                {"style": color, "label": label} for color, label in zip(colors, labels)
            ]
            app.map.layer["buildings"].layer["ground_elevation"].fill_color = (
                paint_properties["circle-color"]
            )
            app.map.layer["buildings"].layer["ground_elevation"].unit = app.gui.getvar(
                "fiat", "view_tab_unit"
            )
            app.map.layer["buildings"].layer[
                "ground_elevation"
            ].legend_title = (
                f'Ground Elevation [{app.gui.getvar("fiat", "view_tab_unit")}]'
            )
            app.map.layer["buildings"].layer["ground_elevation"].set_data(
                self.buildings, paint_properties, legend
            )
            self.show_ground_elevations()

    def show_svi(self, type="SVI"):
        """Show SVI Index"""  # str(Path(self.root) / "exposure" / "SVI")
        if not self.buildings.empty and "SVI" in self.buildings.columns:
            paint_properties = self.get_paint_properties(type=type)
            color_items = paint_properties["circle-color"][2:]
            colors = [color_items[i] for i in range(0, len(color_items), 2)]
            labels = make_labels(
                [color_items[i + 1] for i in range(0, len(color_items) - 1, 2)],
                decimals=1,
            )
            legend = [
                {"style": color, "label": label} for color, label in zip(colors, labels)
            ]
            app.map.layer["buildings"].layer["SVI"].fill_color = paint_properties[
                "circle-color"
            ]
            app.map.layer["buildings"].layer["SVI"].legend_title = "SVI"
            app.map.layer["buildings"].layer["SVI"].set_data(
                self.buildings, paint_properties, legend
            )
            self.show_SVI_index()
        else:
            app.gui.window.dialog_info(
                text="There are no SVI data in your model. Please add SVI data when you set up your model.",
                title="Additional attributes not found.",
            )

    def show_svi_key_domain(self, type="SVI_key_domain"):
        """Show SVI Key Domain"""  # str(Path(self.root) / "exposure" / "SVI")
        if not self.buildings.empty and "SVI_key_domain" in self.buildings.columns:
            paint_properties = self.get_paint_properties(type=type)
            color_items = paint_properties["circle-color"][2:-1]
            color_items.append("other")
            color_items.append(paint_properties["circle-color"][-1])
            legend = [
                {"style": color_items[i + 1], "label": color_items[i]}
                for i in range(0, len(color_items), 2)
            ]
            app.map.layer["buildings"].layer["SVI"].set_data(
                self.buildings, paint_properties, legend
            )
            self.show_SVI_index()
        else:
            app.gui.window.dialog_info(
                text="There are no SVI data in your model. Please add SVI data when you set up your model.",
                title="Additional attributes not found.",
            )

    def show_exposure_buildings(self):
        app.map.layer["buildings"].layer["exposure_points"].show()

    def show_exposure_buildings_primary(self):
        app.map.layer["buildings"].layer["primary_classification"].show()

    def show_exposure_buildings_secondary(self):
        app.map.layer["buildings"].layer["secondary_classification"].show()

    def show_asset_heights(self):
        app.map.layer["buildings"].layer["asset_height"].show()

    def show_max_potential_damage_content(self):
        app.map.layer["buildings"].layer["max_potential_damage_cont"].show()

    def show_max_potential_damage_structure(self):
        app.map.layer["buildings"].layer["max_potential_damage_struct"].show()

    def show_ground_elevations(self):
        app.map.layer["buildings"].layer["ground_elevation"].show()

    def show_SVI_index(self):
        app.map.layer["buildings"].layer["SVI"].show()

    def hide_exposure_buildings(self):
        app.map.layer["buildings"].layer["exposure_points"].hide()

    def show_exposure_roads(self):
        app.map.layer["roads"].layer["exposure_lines"].show()

    def hide_exposure_roads(self):
        app.map.layer["roads"].layer["exposure_lines"].hide()

    def damage_curves_specify(self):
        # get window config yaml path
        pop_win_config_path = str(
            Path(
                app.gui.config_path
            ).parent  # TODO: replace with a variables config_path for the fiat model
            / "models"
            / self.name
            / "config"
            / "vulnerability_specify_damage_curves.yml"
        )
        # Create pop-up and only continue if user presses ok
        okay, data = app.gui.popup(
            pop_win_config_path, data=None, id="specify_damage_curves"
        )
        if not okay:
            return

    def classification_standarize(self):
        # get window config yaml path
        pop_win_config_path = str(
            Path(
                app.gui.config_path
            ).parent  # TODO: replace with a variables config_path for the fiat model
            / "models"
            / self.name
            / "config"
            / "exposure_classification_standarize.yml"
        )
        # Create pop-up and only continue if user presses ok
        okay, data = app.gui.popup(pop_win_config_path, None)
        if not okay:
            return

    def specify_finished_floor_height(self):
        # get window config yaml path
        pop_win_config_path = str(
            Path(
                app.gui.config_path
            ).parent  # TODO: replace with a variables config_path for the fiat model
            / "models"
            / self.name
            / "config"
            / "exposure_finished_floor_height_settings.yml"
        )
        # Create pop-up and only continue if user presses ok
        okay, data = app.gui.popup(pop_win_config_path, data=None)
        if not okay:
            return

    def specify_max_potential_damage(self):
        # get window config yaml path
        pop_win_config_path = str(
            Path(
                app.gui.config_path
            ).parent  # TODO: replace with a variables config_path for the fiat model
            / "models"
            / self.name
            / "config"
            / "exposure_damages_settings.yml"
        )
        # Create pop-up and only continue if user presses ok
        okay, data = app.gui.popup(pop_win_config_path, data=None)
        if not okay:
            return

    def overwrite_classification(self):
        pop_win_config_path = str(
            Path(
                app.gui.config_path
            ).parent  # TODO: replace with a variables config_path for the fiat model
            / "models"
            / self.name
            / "config"
            / "exposure_classification_settings_2.yml"
        )
        okay, data = app.gui.popup(pop_win_config_path, data=None)
        if not okay:
            raise ValueError("The classification data will not be overwritten")

    def overwrite_damages(self):
        # get window config yaml path
        pop_win_config_path = str(
            Path(
                app.gui.config_path
            ).parent  # TODO: replace with a variables config_path for the fiat model
            / "models"
            / self.name
            / "config"
            / "exposure_damages_settings_2.yml"
        )
        okay, data = app.gui.popup(pop_win_config_path, data=None)
        if not okay:
            raise ValueError("The data will not be overwritten")

    def overwrite_model(self):
        # get window config yaml path
        pop_win_config_path = str(
            Path(
                app.gui.config_path
            ).parent  # TODO: replace with a variables config_path for the fiat model
            / "models"
            / self.name
            / "config"
            / "create_model_settings.yml"
        )
        okay, data = app.gui.popup(pop_win_config_path, data=None)
        if not okay:
            raise ValueError("The data will not be overwritten")

    def view_exposure(self):
        # get window config yaml path
        pop_win_config_path = str(
            Path(
                app.gui.config_path
            ).parent  # TODO: replace with a variables config_path for the fiat model
            / "models"
            / self.name
            / "config"
            / "view_tab_exposure_table.yml"
        )
        # Create pop-up and only continue if user presses ok
        okay, data = app.gui.popup(pop_win_config_path, data=None)
        if not okay:
            return

    def view_svi(self):
        # get window config yaml path
        pop_win_config_path = str(
            Path(
                app.gui.config_path
            ).parent  # TODO: replace with a variables config_path for the fiat model
            / "models"
            / self.name
            / "config"
            / "view_tab_svi_table.yml"
        )
        # Create pop-up and only continue if user presses ok
        okay, data = app.gui.popup(pop_win_config_path, data=None)
        if not okay:
            return

    def view_equity(self):
        # get window config yaml path
        pop_win_config_path = str(
            Path(
                app.gui.config_path
            ).parent  # TODO: replace with a variables config_path for the fiat model
            / "models"
            / self.names
            / "config"
            / "view_tab_equity_table.yml"
        )
        # Create pop-up and only continue if user presses ok
        okay, data = app.gui.popup(pop_win_config_path, data=None)
        if not okay:
            return

    def set_object_types(self, unique_primary_types, unique_secondary_types):

        model = "fiat"
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

    def get_continent(self):
        self.exposure = ExposureVector(
            data_catalog=self.domain.data_catalog,
            logger=self.domain.fiat_model.logger,
            region=self.domain.fiat_model.region,
            crs=self.domain.fiat_model.crs,
        )
        country, continent = self.exposure.get_continent()
        return country, continent

    def convert_bf_into_centroids(self, gdf_bf, crs):
        list_centroid = []
        list_object_id = []
        for index, row in gdf_bf.iterrows():
            centroid = row["geometry"].centroid
            list_centroid.append(centroid)
            list_object_id.append(row["object_id"])
        data = {"object_id": list_object_id, "geometry": list_centroid}
        gdf_centroid = gpd.GeoDataFrame(data, columns=["object_id", "geometry"])
        gdf = gdf_bf.merge(gdf_centroid, on="object_id", suffixes=("_gdf1", "_gdf2"))
        gdf.drop(columns="geometry_gdf1", inplace=True)
        gdf.rename(columns={"geometry_gdf2": "geometry"}, inplace=True)
        gdf.drop_duplicates(inplace=True)
        gdf = gpd.GeoDataFrame(gdf, geometry=gdf["geometry"])
        gdf.crs = crs

        return gdf

    def save_gui_variables(self):
        # Save model variables
        dic_variables_main = app.gui.variables["_main"]
        dic_variables_fiat = app.gui.variables["fiat"]
        dic_variables_model_maker = app.gui.variables["modelmaker_fiat"]

        dic_variables = {
            "main": dic_variables_main,
            "fiat": dic_variables_fiat,
            "modelmaker_fiat": dic_variables_model_maker,
        }
        with open(
            Path(os.path.abspath("")) / self.domain.fiat_model.root / "variables.pkl",
            "wb",
        ) as f:
            pickle.dump(dic_variables, f)
