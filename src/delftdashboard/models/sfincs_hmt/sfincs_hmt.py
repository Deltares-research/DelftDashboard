
from delftdashboard.operations.model import GenericModel
from delftdashboard.app import app
import os

# from cht.sfincs.sfincs import SFINCS

from hydromt_sfincs import SfincsModel


class Model(GenericModel):
    def __init__(self, name):
        super().__init__()

        self.name = name
        self.long_name = "HydroMT SFINCS"

        print("Model " + self.name + " added!")
        self.active_domain = 0

        self.initialize_domain()
        self.set_gui_variables()

    def initialize_domain(self):
        root = os.getcwd()
        self.domain = SfincsModel(data_libs=app.config["data_libs"], root=root, mode="w+")

    def add_layers(self):
        # Add main app layer
        layer = app.map.add_layer("sfincs_hmt")

        layer.add_layer(
            "grid",
            type="deck_geojson",
            file_name="sfincs_grid.geojson",
            line_color="black",
        )

        layer.add_layer(
            "mask_active",
            type="circle",
            file_name="sfincs_mask_active.geojson",
            circle_radius=3,
            fill_color="yellow",
            line_color="transparent",
        )

        layer.add_layer(
            "mask_bound_wlev",
            type="circle",
            file_name="sfincs_mask_bound_wlev.geojson",
            circle_radius=3,
            fill_color="blue",
            line_color="transparent",
        )

        layer.add_layer(
            "mask_bound_outflow",
            type="circle",
            file_name="sfincs_mask_bound_outflow.geojson",
            circle_radius=3,
            fill_color="red",
            line_color="transparent",
        )

        # Move this to hurrywave.py
        from .boundary_conditions import select_boundary_point_from_map

        layer.add_layer(
            "boundary_points",
            type="circle_selector",
            select=select_boundary_point_from_map,
            line_color="white",
            line_opacity=1.0,
            fill_color="blue",
            fill_opacity=1.0,
            circle_radius=3,
            circle_radius_selected=4,
            line_color_selected="white",
            fill_color_selected="red",
        )

        layer.add_layer(
            "observation_points",
            type="circle_selector",
            line_color="white",
            line_opacity=1.0,
            fill_color="blue",
            fill_opacity=1.0,
            circle_radius=3,
            circle_radius_selected=4,
            line_color_selected="white",
            fill_color_selected="red",
        )

    def set_layer_mode(self, mode):
        if mode == "inactive":
            # Mask is made invisible
            app.map.layer["sfincs_hmt"].layer["grid"].set_mode("invisible")
            app.map.layer["sfincs_hmt"].layer["mask_active"].set_mode("invisible")
            app.map.layer["sfincs_hmt"].layer["mask_bound_wlev"].set_mode("invisible")
            app.map.layer["sfincs_hmt"].layer["mask_bound_outflow"].set_mode("invisible")

            # Boundary points are made grey
            app.map.layer["sfincs_hmt"].layer["boundary_points"].set_mode("inactive")
            # Observation points are made grey
            app.map.layer["sfincs_hmt"].layer["observation_points"].set_mode("inactive")
        if mode == "invisible":
            app.map.layer["sfincs_hmt"].set_mode("invisible")

    def set_gui_variables(self):
        # Copies sfincs input to gui variables
        group = "sfincs_hmt"

        for var_name in self.domain.config:
            app.gui.setvar(group, var_name, self.domain.config.get(var_name))

        app.gui.setvar(group, "roughness_type", "landsea")

        # Now set some extra variables needed for SFINCS GUI
        app.gui.setvar(group, "input_options_text", ["Binary", "ASCII"])
        app.gui.setvar(group, "input_options_values", ["bin", "asc"])

        app.gui.setvar(group, "output_options_text", ["NetCDF", "Binary", "ASCII"])
        app.gui.setvar(group, "output_options_values", ["net", "bin", "asc"])

        app.gui.setvar(group, "meteo_forcing_type", "uniform")

        app.gui.setvar(group, "depthcontour_value", 0.0)
        app.gui.setvar(group, "flowboundarypoints_length", 0)
        app.gui.setvar(group, "boundaryspline_length", 0)
        app.gui.setvar(group, "boundaryspline_filename", "")
        app.gui.setvar(group, "boundaryspline_flowdx", 0.0)
        app.gui.setvar(group, "boundaryconditions_zs", 0.0)
        app.gui.setvar(group, "wind", True)
        app.gui.setvar(group, "rain", True)

    def set_input_variables(self, varid=None, value=None):
        # Copies gui variables to sfincs input
        group = "sfincs_hmt"

        for var_name in self.domain.config:
            self.domain.set_config(
                var_name, app.gui.variables[group][var_name]["value"]
            )

    def open(self):
        # Open input file, and change working directory
        fname = app.gui.open_file_name(
            "Open file", "SFINCS input file (sfincs.inp)"
        )
        if fname:
            path = os.path.dirname(fname)
            self.domain.set_root(root=path, mode="r")
            self.domain.read()
            # Change working directory
            os.chdir(path)
            # Change CRS
            app.crs = self.domain.crs


    def save(self):
        # Save sfincs input
        mode = (
            "r+"
            if self.domain._write and self.domain._read
            else ("w" if self.domain._write else "r")
        )
        if mode == "r":
            fname = app.gui.select_path(
                "Select model directory", "Select the directory where you want to store your model",
            )
            self.domain.set_root(root=fname, mode="w+")

        # Write sfincs model
        self.domain.write()

        # self.domain.write_batch_file()

    def load(self):
        self.domain.read()

    def set_crs(self, crs):
        self.domain.set_crs(crs)

    def plot(self):
        pass