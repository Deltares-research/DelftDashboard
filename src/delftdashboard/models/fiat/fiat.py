# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
import os
from PyQt5.QtWidgets import QFileDialog
from pathlib import Path

from delftdashboard.app import app
from delftdashboard.operations.model import GenericModel
from hydromt_fiat.api.hydromt_fiat_vm import HydroMtViewModel


class Model(GenericModel):
    def __init__(self, name):
        super().__init__()

        self.name = name
        self.long_name = "fiat"

        print("Model " + self.name + " added!")
        self.active_domain = 0

        # Set GUI variables
        self.set_gui_variables()

    def add_layers(self):
        # Add main DDB layer
        layer = app.map.add_layer("fiat")

        layer.add_layer(
            "exposure_points",
            type="circle",
            circle_radius=3,
            fill_color="orange",
            line_color="transparent",
        )

    def set_layer_mode(self, mode):
        if mode == "inactive":
            # Everything made visible
            app.map.layer["fiat"].set_mode("inactive")
        elif mode == "invisible":
            # Everything set to invisible
            app.map.layer["fiat"].set_mode("invisible")

    def set_gui_variables(self):
        group = "fiat"
        # Input variables
        app.gui.setvar(
            group,
            "asset_locations_string",
            ["National Structure Inventory (NSI)", "Upload data"],
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
            [
                "*Field 1 from file*",
                "*Field 2 from file*",
                "*Field 3 from file*",
                "*Field 4 from file*",
            ],
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
        app.gui.setvar(
            group,
            "selected_secondary_classification_string",
            [
                "*House*",
                "*Appartment*",
                "*Office*",
                "*School*",
                "*Airport*",
            ],
        )
        app.gui.setvar(
            group,
            "selected_secondary_classification_value",
            ["house", "appartment", "office", "school", "airport"],
        )
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
        app.gui.setvar(group, "created_vulnerability_curves", [""])

    def set_input_variables(self):
        # Update all model input variables
        for var_name in vars(self.domain.input.variables):
            setattr(
                self.domain.input.variables, var_name, app.gui.getvar("fiat", var_name)
            )

    def open(self):
        # Open input file, and change working directory
        fname = app.gui.window.dialog_open_file(
            "Open file", filter="fiat input file;;ini files (*.ini)"
        )
        fname = fname[0]
        if fname:
            dlg = app.gui.window.dialog_wait("Loading fiat model ...")
            path = os.path.dirname(fname)
            self.domain.path = path
            self.domain.read()
            self.set_gui_variables()
            # Change working directory
            os.chdir(path)
            # Change CRS
            app.crs = self.domain.crs
            self.plot()
            dlg.close()

    def save(self):
        # Write fiat.inp
        self.domain.path = os.getcwd()
        self.domain.input.write()
        self.domain.write_batch_file()

    def load(self):
        self.domain.read()

    def set_crs(self, crs):
        self.domain.crs = crs

    def plot(self):
        # Grid
        gdf = self.domain.grid.to_gdf()
        app.map.layer["fiat"].layer["grid"].set_data(gdf)

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

    def create_nsi_assets(self):
        # Set the ini file to the correct variables for creating a FIAT model from NSI
        # data
        hydro_vm = HydroMtViewModel(
            app.config["working_directory"], app.config["data_libs_fiat"][0]
        )
        hydro_vm.exposure_vm.set_asset_locations_source(
            input_source="NSI",
        )
