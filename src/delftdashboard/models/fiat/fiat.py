# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
import os
from pathlib import Path

from delftdashboard.app import app
from delftdashboard.operations.model import GenericModel
from hydromt_fiat.api.hydromt_fiat_vm import HydroMtViewModel


class Model(GenericModel):
    def __init__(self, name):
        super().__init__()

        self.name = name
        self.long_name = "FIAT"

        print("Model " + self.name + " added!")
        self.active_domain = 0
        self.domain = None

        # Set GUI variables
        self.set_gui_variables()

    def add_layers(self):
        # Add main DDB layer
        layer = app.map.add_layer("fiat")

        # Add colors as dictionary per attribute

        layer.add_layer(
            "exposure_points",
            type="circle",
            circle_radius=3,
            legend_position="top-right",
            fill_color="orange",
            line_color="transparent",
            color_property="Secondary Object Type",
            hover_property="Secondary Object Type",
            legend_title="Asset locations"
        )

        layer.add_layer(
            "exposure_lines",
            type="line",
            legend_position="top-right",
            fill_color="purple",
            line_color="purple",
            line_width=3,
            circle_radius=0,
            color_property="Secondary Object Type",
            hover_property="Secondary Object Type",
            legend_title="Roads"
        )

    def set_layer_mode(self, mode):
        if mode == "inactive":
            # Everything made visible
            app.map.layer["fiat"].set_mode("inactive")
        elif mode == "invisible":
            # Everything set to invisible
            app.map.layer["fiat"].set_mode("invisible")

    def set_gui_variables(self):
        ## CHECKBOXES ##
        group = "_main"
        app.gui.setvar(group, "checkbox_model_boundary", False)
        app.gui.setvar(group, "checkbox_asset_locations", False)
        app.gui.setvar(group, "checkbox_classification", False)
        app.gui.setvar(group, "checkbox_damage_values", False)
        app.gui.setvar(group, "checkbox_elevation", False)
        app.gui.setvar(group, "checkbox_aggregation_(optional)", False)
        app.gui.setvar(group, "checkbox_vulnerability", False)
        app.gui.setvar(group, "checkbox_svi_(optional)", False)

        group = "fiat"
        
        ## TO BE DESCRIBED ##
        default_curves = app.data_catalog.get_dataframe("default_hazus_iwr_linking")
        default_curves = default_curves[["Exposure Link", "Damage Type", "Source", "Description"]]
        app.gui.setvar(group, "damage_curves_table", default_curves)
        app.gui.setvar(group, "selected_damage_curve_database", "default_vulnerability_curves")
        app.gui.setvar(group, "selected_damage_curve_linking_table", "default_hazus_iwr_linking")
        
        app.gui.setvar(group, "display_asset_locations", None)
        app.gui.setvar(group, "display_classification", None)
        app.gui.setvar(group, "display_asset_heights", None)
        app.gui.setvar(group, "display_max_potential_values", None)
        app.gui.setvar(group, "display_aggregation", None)
        app.gui.setvar(group, "display_damage_curves", None)
        
        app.gui.setvar(
            group,
            "asset_locations_string",
            ["National Structure Inventory (NSI)", "Upload file"],
        )
        app.gui.setvar(group, "asset_locations_value", ["nsi", "file"])
        app.gui.setvar(group, "asset_locations", "nsi")
        app.gui.setvar(group, "damages_source_string", ["NSI", "Hazus", "Create"])
        app.gui.setvar(group, "damages_source_value", ["nsi", "hazus", "create"])
        app.gui.setvar(group, "damages_source", "nsi")
        app.gui.setvar(
            group,
            "curve_join_type_string",
            ["Primary object type", "Secondary object type"],
        )
        app.gui.setvar(group, "curve_join_type_value", ["primary", "secondary"])
        app.gui.setvar(group, "curve_join_type", "Secondary object type")
        app.gui.setvar(
            group,
            "fiat_fields_string",
            [
                "Object ID",
                "Object Name",
                "Primary Object Type",
                "Secondary Object Type",
            ],
        )
        app.gui.setvar(
            group,
            "fiat_fields_value",
            ["objectid", "objectname", "primaryobject", "secondaryobject"],
        )
        app.gui.setvar(group, "fiat_field_name_1", None)
        app.gui.setvar(group, "fiat_field_name_2", None)
        app.gui.setvar(group, "fiat_field_name_3", None)
        app.gui.setvar(group, "fiat_field_name_4", None)
        app.gui.setvar(
            group,
            "data_fields_string",
            ["data field 1", "data field 2", "data field 3"],
        )
        app.gui.setvar(
            group, "data_fields_value", ["data_field_1", "data_field_2", "data_field_3"]
        )
        app.gui.setvar(group, "data_field_name_1", None)
        app.gui.setvar(group, "data_field_name_2", None)
        app.gui.setvar(group, "data_field_name_3", None)
        app.gui.setvar(group, "data_field_name_4", None)
        app.gui.setvar(group, "show_asset_locations", False)
        app.gui.setvar(group, "show_extraction_method", False)
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
        app.gui.setvar(group, "classification_source", "nsi_data")
        app.gui.setvar(
            group,
            "classification_source_string",
            ["National Structure Inventory (NSI)", "Any previously loaded data", "Upload data"],
        )
        app.gui.setvar(group, "classification_source_value", ["nsi_data", "loaded_data", "upload_data"])
        app.gui.setvar(group, "upload_classification", None)
        app.gui.setvar(
            group,
            "object_type_string",
            ["Primary object type", "Secondary object type"],
        )
        app.gui.setvar(group, "object_type_value", ["pot", "sot"])
        app.gui.setvar(group, "object_type", None)
        app.gui.setvar(
            group,
            "classification_file_field_name_string",
            [],
        )
        app.gui.setvar(
            group,
            "classification_file_field_name_value",
            ["field1", "field2", "field3", "field4"],
        )
        app.gui.setvar(group, "classification_file_field_name", None)
        app.gui.setvar(
            group,
            "selected_primary_classification_string",
            [
                "*Residential*",
                "*Commercial*",
                "*Industrial*",
            ],
        )
        app.gui.setvar(
            group,
            "selected_primary_classification_value",
            [
                "residential",
                "commercial",
                "industrial",
            ],
        )
        app.gui.setvar(group, "selected_primary_classification_value", 0)
        app.gui.setvar(group, "selected_asset_locations", 0)
        app.gui.setvar(
            group,
            "selected_asset_locations_string",
            [],
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
        app.gui.setvar(group, "loaded_aggregation_files", 0)
        app.gui.setvar(
            group,
            "loaded_aggregation_files_string",
            [],
        )
        app.gui.setvar(group, "selected_aggregation_files", 0)
        app.gui.setvar(group, "selected_aggregation_files_string", [])
        app.gui.setvar(group, "assign_classification_active", False)
        app.gui.setvar(group, "selected_secondary_classification_value", 0)
        app.gui.setvar(group, "show_primary_classification", None)
        app.gui.setvar(group, "show_secondary_classification", None)
        app.gui.setvar(group, "classification_field", None)
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
        app.gui.setvar(group, "text_feedback_damage_values", "empty")
        app.gui.setvar(group, "nr_selected_bathymetry_datasets", 0)
        app.gui.setvar(group, "show_damage_values", 0)
        app.gui.setvar(group, "created_vulnerability_curves", 0)
        app.gui.setvar(group, "linking_object_type", 0)
        app.gui.setvar(group, "road_damage_threshold", 1)
        

    def set_input_variables(self):
        # Update all model input variables
        for var_name in vars(self.domain.input.variables):
            setattr(
                self.domain.input.variables, var_name, app.gui.getvar("fiat", var_name)
            )

    def new(self):
        fname = app.gui.window.dialog_select_path(
            "Select an empty folder"
        )
        if fname:
            app.gui.setvar("fiat", "selected_scenario", Path(fname).stem)
            app.gui.setvar("fiat", "scenario_folder", fname)
            self.domain = HydroMtViewModel(
                app.config["working_directory"],
                app.config["data_libs"],
                fname,
            )

    def open(self):
        # Open input file, and change working directory
        fname = app.gui.window.dialog_select_path(
            "Select an existing model folder"
        )
        if fname:
            dlg = app.gui.window.dialog_wait("Loading fiat model ...")
            self.domain = HydroMtViewModel(
                app.config["working_directory"],
                app.config["data_libs"],
                fname,
            )
            self.domain.read()
            self.set_gui_variables()
            # Change working directory
            os.chdir(fname)
            # Change CRS
            app.crs = self.domain.crs
            self.plot()
            dlg.close()

    def save(self):
        self.domain.write()

    def load(self):
        self.domain.read()

    def set_crs(self, crs):
        self.domain.crs = crs

    def plot(self):
        # Grid
        gdf = self.domain.grid.to_gdf()
        app.map.layer["fiat"].layer["grid"].set_data(gdf)

    def show_exposure_layers(self):
        app.map.layer["fiat"].layer["exposure_points"].show()
        app.map.layer["fiat"].layer["exposure_lines"].show()

    def hide_exposure_layers(self):
        app.map.layer["fiat"].layer["exposure_points"].hide()
        app.map.layer["fiat"].layer["exposure_lines"].hide()

    def set_asset_locations_field(self):
        # get window config yaml path
        pop_win_config_path = str(
            Path(
                app.gui.config_path
            ).parent  # TODO: replace with a variables config_path for the fiat model
            / "models"
            / self.name
            / "config"
            / "exposure_asset_locations_fields.yml"
        )
        # Create pop-up and only continue if user presses ok
        okay, data = app.gui.popup(pop_win_config_path, None)
        if not okay:
            return

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
        okay, data = app.gui.popup(pop_win_config_path, None)
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
