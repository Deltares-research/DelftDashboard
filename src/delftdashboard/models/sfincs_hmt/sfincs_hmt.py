# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
# import datetime
import os
from pyproj import CRS

from delftdashboard.operations.model import GenericModel
from delftdashboard.operations import map
from delftdashboard.app import app

from hydromt_sfincs import SfincsModel


class Model(GenericModel):
    def __init__(self, name):
        super().__init__()

        self.name = name
        self.long_name = "SFINCS (HydroMT)"

    def initialize(self):
        self.domain = SfincsModel(root=".", mode="r+")
        self.domain.config.set("epsg", app.crs.to_epsg())
        self.domain.grid_type = "quadtree"
        self.set_gui_variables()
        self.observation_points_changed = False
        self.cross_sections_changed = False
        self.discharge_points_changed = False
        self.boundaries_changed = False
        self.thin_dams_changed = False
        self.wave_boundaries_changed = False

    def get_view_menu(self):
        model_view_menu = {}
        model_view_menu["text"] = self.long_name
        model_view_menu["menu"] = []
        model_view_menu["menu"].append(
            {
                "variable_group": self.name,
                "id": f"view.{self.name}.grid",
                "text": "Grid",
                "variable": "view_grid",
                "separator": True,
                "checkable": True,
                "method": self.set_view_menu,
                "option": "grid",
                "dependency": [
                    {
                        "action": "check",
                        "checkfor": "all",
                        "check": [
                            {"variable": "view_grid", "operator": "eq", "value": True}
                        ],
                    }
                ],
            }
        )
        return model_view_menu

    def set_view_menu(self, option, checked):
        if option == "grid":
            print(f"Checked: {checked}")
            if app.gui.getvar(self.name, "view_grid"):
                app.map.layer["sfincs_hmt"].layer["grid"].show()
                print("Grid is made visible")
            else:
                app.map.layer["sfincs_hmt"].layer["grid"].hide()
                print("Grid is made invisible")

    def add_layers(self):
        layer = app.map.add_layer("sfincs_hmt")

        layer.add_layer("grid", type="image")

        layer.add_layer(
            "grid_exterior", type="line", circle_radius=0, line_color="yellow"
        )

        layer.add_layer("mask", type="image")

        layer.add_layer("mask_snapwave", type="image")

        from .boundary_conditions import select_boundary_point_from_map

        layer.add_layer(
            "boundary_points",
            type="circle_selector",
            select=select_boundary_point_from_map,
            hover_property="name",
            line_color="white",
            line_opacity=1.0,
            fill_color="blue",
            fill_opacity=1.0,
            circle_radius=4,
            circle_radius_selected=5,
            line_color_selected="white",
            fill_color_selected="red",
            circle_radius_inactive=4,
            line_color_inactive="white",
            fill_color_inactive="lightgrey",
        )

        from .structures_thin_dams import thin_dam_created
        from .structures_thin_dams import thin_dam_selected
        from .structures_thin_dams import thin_dam_modified

        thd_layer = layer.add_layer(
            "thin_dams"
        )  # Container layer for thin dams and snapped thin dams
        thd_layer.add_layer(
            "polylines",
            type="draw",
            shape="polyline",
            create=thin_dam_created,
            modify=thin_dam_modified,
            select=thin_dam_selected,
            polyline_line_color="yellow",
            polyline_line_width=2.0,
            polyline_line_opacity=1.0,
        )
        thd_layer.add_layer(
            "snapped",
            type="line",
            line_color="white",
            line_opacity=1.0,
            circle_radius=0,
            line_color_inactive="lightgrey",
        )

        from .observation_points_observation_points import (
            select_observation_point_from_map,
        )

        layer.add_layer(
            "observation_points",
            type="circle_selector",
            select=select_observation_point_from_map,
            hover_property="name",
            line_color="white",
            line_opacity=1.0,
            fill_color="blue",
            fill_opacity=1.0,
            circle_radius=3,
            circle_radius_selected=4,
            line_color_selected="white",
            fill_color_selected="red",
        )

        from .observation_points_cross_sections import cross_section_created
        from .observation_points_cross_sections import cross_section_selected
        from .observation_points_cross_sections import cross_section_modified

        crs_layer = layer.add_layer(
            "cross_sections"
        )  # Container layer for thin dams and snapped thin dams
        crs_layer.add_layer(
            "polylines",
            type="draw",
            shape="polyline",
            create=cross_section_created,
            modify=cross_section_modified,
            select=cross_section_selected,
            polyline_line_color="yellow",
            polyline_line_width=2.0,
            polyline_line_opacity=1.0,
        )
        crs_layer.add_layer(
            "snapped",
            type="line",
            line_color="white",
            line_opacity=1.0,
            circle_radius=0,
            line_color_inactive="lightgrey",
        )

        # Make the layer
        # Create geodataframe with one point at (0,0), crs(4326)
        layer.add_layer(
            "obs_points",
            type="marker",
            hover_property="description",
            click_property="url",
            icon_size=0.5,
            click_popup_width=600,
            click_popup_height=220,
        )

        from .discharge_points import select_discharge_point_from_map

        layer.add_layer(
            "discharge_points",
            type="circle_selector",
            select=select_discharge_point_from_map,
            hover_property="name",
            line_color="white",
            line_opacity=1.0,
            fill_color="blue",
            fill_opacity=1.0,
            circle_radius=3,
            circle_radius_selected=4,
            line_color_selected="white",
            fill_color_selected="red",
        )

        # # Snapwave Boundary Enclosure
        # from .waves_snapwave import boundary_enclosure_created
        # from .waves_snapwave import boundary_enclosure_modified
        # layer.add_layer("snapwave_boundary_enclosure", type="draw",
        #                      shape="polygon",
        #                      create=boundary_enclosure_created,
        #                      modify=boundary_enclosure_modified,
        #                      polygon_line_color="red")
        from .waves_boundary_conditions import select_boundary_point_from_map_snapwave

        layer.add_layer(
            "boundary_points_snapwave",
            type="circle_selector",
            select=select_boundary_point_from_map_snapwave,
            hover_property="name",
            line_color="white",
            line_opacity=1.0,
            fill_color="blue",
            fill_opacity=1.0,
            circle_radius=4,
            circle_radius_selected=5,
            line_color_selected="white",
            fill_color_selected="red",
            circle_radius_inactive=4,
            line_color_inactive="white",
            fill_color_inactive="lightgrey",
        )

        # Wave makers
        from .waves_wave_makers import wave_maker_created
        from .waves_wave_makers import wave_maker_modified
        from .waves_wave_makers import wave_maker_selected

        layer.add_layer(
            "wave_makers",
            type="draw",
            shape="polyline",
            create=wave_maker_created,
            modify=wave_maker_modified,
            select=wave_maker_selected,
            add=wave_maker_modified,
            polygon_line_color="red",
        )

    def set_layer_mode(self, mode):
        layer = app.map.layer["sfincs_hmt"]
        if mode == "inactive":
            # # Make the sfincs_hmt layer visible
            # layer.show()
            # Grid is made visible
            layer.layer["grid"].deactivate()
            # Grid exterior is made visible
            layer.layer["grid_exterior"].deactivate()
            # Mask is made invisible
            layer.layer["mask"].hide()
            layer.layer["mask_snapwave"].hide()
            # Boundary points are made grey
            layer.layer["boundary_points"].deactivate()
            # Observation points are made grey
            layer.layer["observation_points"].deactivate()
            # Cross sections are made grey
            layer.layer["cross_sections"].layer["polylines"].deactivate()
            layer.layer["cross_sections"].layer["snapped"].hide()
            # Discharge points are made grey
            layer.layer["discharge_points"].deactivate()
            # Thin dams are made grey
            layer.layer["thin_dams"].layer["polylines"].deactivate()
            layer.layer["thin_dams"].layer["snapped"].hide()
            # # SnapWave boundary enclosure is made invisible
            # layer.layer["snapwave_boundary_enclosure"].hide()
            layer.layer["boundary_points_snapwave"].deactivate()
            # Wave makers are made invisible
            layer.layer["wave_makers"].hide()
        elif mode == "invisible":
            layer.hide()

    def set_crs(self):
        crs = app.crs
        old_crs = CRS(self.domain.config.get("epsg"))
        if old_crs != crs:
            self.domain.config.set("epsg", crs.to_epsg())
            self.domain.clear_spatial_components()
            self.plot()

    def open(self):
        # Open input file, and change working directory
        fname = app.gui.window.dialog_open_file(
            "Open file", filter="SFINCS input file (sfincs.inp)"
        )
        fname = fname[0]
        if fname:
            dlg = app.gui.window.dialog_wait("Loading SFINCS model ...")
            path = os.path.dirname(fname)
            # Change working directory
            os.chdir(path)
            self.initialize()
            self.domain.path = path
            self.domain.read()
            self.set_gui_variables()
            # Also get mask datashader dataframe (should this not happen when grid is read?)
            self.domain.quadtree_mask.get_datashader_dataframe()
            # TODO: get snapwave mask datashader dataframe
            # self.domain.snapwave.mask.get_datashader_dataframe()
            # Change CRS
            map.set_crs(self.domain.crs)
            self.plot()
            dlg.close()
            app.gui.window.update()
            # Zoom to model extent
            # bounds = self.domain.bounds(crs=4326, buffer=0.1)
            # TODO: add buffer and set crs
            bounds = self.domain.bounds
            app.map.fit_bounds(bounds[0], bounds[1], bounds[2], bounds[3])

    def save(self):
        # Write sfincs.inp
        self.check_times()
        # TODO: set root
        self.domain.path = os.getcwd()
        # self.domain.input.variables.epsg = app.crs.to_epsg()
        self.domain.exe_path = app.config["sfincs_exe_path"]
        self.domain.config.write()
        # TODO: write batch file
        # self.domain.write_batch_file()
        # app.model["sfincs_hmt"].domain.config.write()

    def plot(self):
        # Plot everything
        # app.map.add_layer("sfincs_hmt").clear()
        # Grid
        app.map.layer["sfincs_hmt"].layer["grid"].set_data(
            app.model["sfincs_hmt"].domain.quadtree_grid
        )
        # Grid exterior
        app.map.layer["sfincs_hmt"].layer["grid_exterior"].set_data(
            app.model["sfincs_hmt"].domain.region
        )
        # Mask
        app.map.layer["sfincs_hmt"].layer["mask"].set_data(
            app.model["sfincs_hmt"].domain.quadtree_mask
        )
        # Observation points
        app.map.layer["sfincs_hmt"].layer["observation_points"].set_data(
            app.model["sfincs_hmt"].domain.observation_points.data, 0
        )
        # Cross sections
        app.map.layer["sfincs_hmt"].layer["cross_sections"].layer["polylines"].set_data(
            app.model["sfincs_hmt"].domain.cross_sections.data
        )
        # Thin dams
        app.map.layer["sfincs_hmt"].layer["thin_dams"].layer["polylines"].set_data(
            app.model["sfincs_hmt"].domain.thin_dams.data
        )
        # Boundary points
        app.map.layer["sfincs_hmt"].layer["boundary_points"].set_data(
            app.model["sfincs_hmt"].domain.boundary_conditions.data, 0
        )
        # Discharge points
        app.map.layer["sfincs_hmt"].layer["discharge_points"].set_data(
            app.model["sfincs_hmt"].domain.discharge_points.data, 0
        )
        # Mask SnapWave
        # app.map.layer["sfincs_hmt"].layer["mask_snapwave"].set_data(app.model["sfincs_hmt"].domain.snapwave.mask)
        # SnapWave Boundary points
        # app.map.layer["sfincs_hmt"].layer["boundary_points_snapwave"].set_data(app.model["sfincs_hmt"].domain.snapwave.boundary_conditions.gdf, 0)
        # Wave makers
        # app.map.layer["sfincs_hmt"].layer["wave_makers"].set_data(app.model["sfincs_hmt"].domain.wave_makers.gdf)

    def set_gui_variables(self):
        """Called after reading the input file to set the GUI variables"""

        group = "sfincs_hmt"

        # Copy sfincs input variables to gui variables
        for key, value in self.domain.config.data.model_dump(
            exclude_unset=False
        ).items():
            app.gui.setvar(group, key, value)

        # View
        app.gui.setvar(group, "view_grid", True)

        # Now set some extra variables needed for SFINCS GUI

        app.gui.setvar(group, "grid_type", "regular")
        app.gui.setvar(group, "bathymetry_type", "regular")
        app.gui.setvar(group, "roughness_type", "landsea")
        app.gui.setvar(group, "input_options_text", ["Binary", "ASCII"])
        app.gui.setvar(group, "input_options_values", ["bin", "asc"])
        app.gui.setvar(group, "output_options_text", ["NetCDF", "Binary", "ASCII"])
        app.gui.setvar(group, "output_options_values", ["net", "bin", "asc"])
        app.gui.setvar(group, "meteo_forcing_type", "uniform")
        app.gui.setvar(group, "crs_type", "geographic")

        # Wind drag
        cdwnd = self.domain.config.get("cdwnd", [0.0, 25.0, 50.0])
        app.gui.setvar(group, "wind_speed_1", cdwnd[0])
        app.gui.setvar(group, "wind_speed_2", cdwnd[1])
        app.gui.setvar(group, "wind_speed_3", cdwnd[2])
        cdval = self.domain.config.get("cdval", [0.001, 0.0025, 0.0025])
        app.gui.setvar(group, "cd_1", cdval[0])
        app.gui.setvar(group, "cd_2", cdval[1])
        app.gui.setvar(group, "cd_3", cdval[2])

        # Boundary conditions
        app.gui.setvar(group, "boundary_point_names", [])
        app.gui.setvar(group, "nr_boundary_points", 0)
        app.gui.setvar(group, "active_boundary_point", 0)
        app.gui.setvar(group, "boundary_dx", 10000.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_shape", "constant")
        app.gui.setvar(group, "boundary_conditions_timeseries_time_step", 600.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_offset", 0.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_amplitude", 1.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_phase", 0.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_period", 43200.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_peak", 1.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_tpeak", 86400.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_duration", 43200.0)
        app.gui.setvar(
            group,
            "boundary_conditions_tide_model",
            app.gui.getvar("tide_models", "names")[0],
        )

        # Observation points
        app.gui.setvar(group, "observation_point_names", [])
        app.gui.setvar(group, "nr_observation_points", 0)
        app.gui.setvar(group, "active_observation_point", 0)
        app.gui.setvar(group, "observation_point_name", "")

        # Cross sections
        app.gui.setvar(group, "cross_section_names", [])
        app.gui.setvar(group, "nr_cross_sections", 0)
        app.gui.setvar(group, "active_cross_section", 0)
        app.gui.setvar(group, "cross_section_name", "")

        # Discharge points
        app.gui.setvar(group, "discharge_point_names", [])
        app.gui.setvar(group, "nr_discharge_points", 0)
        app.gui.setvar(group, "active_discharge_point", 0)

        # Thin dams
        app.gui.setvar(group, "thin_dam_names", [])
        app.gui.setvar(group, "nr_thin_dams", 0)
        app.gui.setvar(group, "thin_dam_index", 0)

        # SnapWave
        app.gui.setvar(
            "modelmaker_sfincs_hmt", "use_snapwave", app.gui.getvar(group, "snapwave")
        )
        app.gui.setvar(group, "boundary_point_names_snapwave", [])
        app.gui.setvar(group, "nr_boundary_points_snapwave", 0)
        app.gui.setvar(group, "active_boundary_point_snapwave", 0)
        app.gui.setvar(group, "boundary_dx_snapwave", 10000.0)
        app.gui.setvar(
            group, "boundary_conditions_timeseries_shape_snapwave", "constant"
        )
        app.gui.setvar(
            group, "boundary_conditions_timeseries_time_step_snapwave", 600.0
        )
        app.gui.setvar(group, "boundary_conditions_timeseries_hs_snapwave", 1.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_tp_snapwave", 8.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_wd_snapwave", 0.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_ds_snapwave", 20.0)

        # Wave makers
        app.gui.setvar(group, "wave_maker_names", [])
        app.gui.setvar(group, "nr_wave_makers", 0)
        app.gui.setvar(group, "active_wave_maker", 0)

        app.gui.setvar(group, "wind", False)
        app.gui.setvar(group, "baro", False)
        app.gui.setvar(group, "rain", False)

        # Turning off weirs for now
        app.gui.setvar(group, "enable_weirs", False)

    def set_model_variables(self, varid=None, value=None):
        # Copies gui variables to sfincs input variables
        group = "sfincs_hmt"
        for key, value in self.domain.config.data.model_dump(
            exclude_unset=False
        ).items():
            self.domain.config.set(
                key, app.gui.getvar(group, key), skip_validation=True
            )
        if self.domain.config.get("snapwave"):
            app.gui.setvar("modelmaker_sfincs_hmt", "use_snapwave", True)
        else:
            app.gui.setvar("modelmaker_sfincs_hmt", "use_snapwave", False)
        # Wind drag
        cdwnd = []
        cdwnd.append(app.gui.getvar(group, "wind_speed_1"))
        cdwnd.append(app.gui.getvar(group, "wind_speed_2"))
        cdwnd.append(app.gui.getvar(group, "wind_speed_3"))
        self.domain.config.set("cdwnd", cdwnd)
        cdval = []
        cdval.append(app.gui.getvar(group, "cd_1"))
        cdval.append(app.gui.getvar(group, "cd_2"))
        cdval.append(app.gui.getvar(group, "cd_3"))
        self.domain.config.set("cdval", cdval)

    def set_input_variable(self, gui_variable, value):
        pass

    def add_stations(self, gdf_stations_to_add, naming_option="id"):
        # TODO
        self.domain.observation_points.add_points(
            gdf_stations_to_add, name=naming_option
        )
        gdf = self.domain.observation_points.gdf
        app.map.layer["sfincs_hmt"].layer["observation_points"].set_data(gdf, 0)
        if not self.domain.input.variables.obsfile:
            self.domain.input.variables.obsfile = "sfincs.obs"
            app.gui.setvar("sfincs_hmt", "obsfile", self.domain.input.variables.obsfile)
        self.domain.observation_points.write()

    def check_times(self):
        # TODO
        return
        ok, message_list = self.domain.check_times()
        if not ok:
            messages = ""
            for message in message_list:
                messages = messages + message + "\n"
            app.gui.window.dialog_warning(messages, "Warning")
