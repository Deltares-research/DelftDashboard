# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
# import datetime
import os

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
        # self.domain = SfincsModel(root=".", mode="r+")
        self.domain.config.set("epsg", app.crs.to_epsg())
        self.set_gui_variables()
        self.observation_points_changed = False
        self.cross_sections_changed = False
        self.discharge_points_changed = False
        self.boundaries_changed = False
        self.thin_dams_changed = False
        self.weirs_changed = False
        self.drainage_structures_changed = False
        self.wave_boundaries_changed = False
        self.wave_makers_changed = False

    def get_view_menu(self):
        model_view_menu = {}
        model_view_menu["text"] = self.long_name
        model_view_menu["menu"] = []
        model_view_menu["menu"].append({"variable_group": self.name,
                                        "id": f"view.{self.name}.grid",
                                        "text": "Grid",
                                        "variable": "view_grid",
                                        "separator": True,
                                        "checkable": True,
                                        "method": self.set_view_menu,
                                        "option": "grid",
                                        "dependency": [{"action": "check", "checkfor": "all", "check": [{"variable": "view_grid", "operator": "eq", "value": True}]}]})
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

        layer.add_layer("grid", type="raster_image")

        layer.add_layer("grid_exterior",
                        type="line",
                        circle_radius=0,
                        line_color="yellow")

        layer.add_layer("mask",
                        type="raster_image")
        
        layer.add_layer("mask_snapwave",
                        type="raster_image")

        from .boundary_conditions import select_boundary_point_from_map
        layer.add_layer("boundary_points",
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
                        fill_color_inactive="lightgrey"
                       )

        from .structures_thin_dams import thin_dam_created
        from .structures_thin_dams import thin_dam_selected
        from .structures_thin_dams import thin_dam_modified
        thd_layer = layer.add_layer("thin_dams") # Container layer for thin dams and snapped thin dams
        thd_layer.add_layer("polylines",
                            type="draw",
                            shape="polyline",
                            create=thin_dam_created,
                            modify=thin_dam_modified,
                            select=thin_dam_selected,
                            polyline_line_color="yellow",
                            polyline_line_width=2.0,
                            polyline_line_opacity=1.0)
        thd_layer.add_layer("snapped",
                            type="line",
                            line_color="white",
                            line_opacity=1.0,
                            circle_radius=0,
                            line_color_inactive="lightgrey")

        from .structures_weirs import weir_created
        from .structures_weirs import weir_selected
        from .structures_weirs import weir_modified
        weir_layer = layer.add_layer("weirs") # Container layer for weirs and snapped weirs
        weir_layer.add_layer("polylines",
                            type="draw",
                            shape="polyline",
                            create=weir_created,
                            modify=weir_modified,
                            select=weir_selected,
                            polyline_line_color="yellow",
                            polyline_line_width=2.0,
                            polyline_line_opacity=1.0)
        weir_layer.add_layer("snapped",
                            type="line",
                            line_color="white",
                            line_opacity=1.0,
                            circle_radius=0,
                            line_color_inactive="lightgrey")

        from .structures_drainage_structures import drainage_structure_created
        from .structures_drainage_structures import drainage_structure_selected
        from .structures_drainage_structures import drainage_structure_modified
        layer.add_layer("drainage_structures",
                         type="draw",
                         shape="polyline",
                         create=drainage_structure_created,
                         modify=drainage_structure_modified,
                         select=drainage_structure_selected,
                         polyline_line_color="yellow",
                         polyline_line_width=2.0,
                         polyline_line_opacity=1.0)

        from .observation_points_observation_points import select_observation_point_from_map
        layer.add_layer("observation_points",
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
                        fill_color_selected="red")

        from .observation_points_cross_sections import cross_section_created
        from .observation_points_cross_sections import cross_section_selected
        from .observation_points_cross_sections import cross_section_modified
        crs_layer = layer.add_layer("cross_sections") # Container layer for cross sections and snapped cross sections
        crs_layer.add_layer("polylines",
                            type="draw",
                            shape="polyline",
                            create=cross_section_created,
                            modify=cross_section_modified,
                            select=cross_section_selected,
                            polyline_line_color="yellow",
                            polyline_line_width=2.0,
                            polyline_line_opacity=1.0)
        crs_layer.add_layer("snapped",
                            type="line",
                            line_color="white",
                            line_opacity=1.0,
                            circle_radius=0,
                            line_color_inactive="lightgrey")

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
        layer.add_layer("discharge_points",
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
                        fill_color_selected="red")

        from .waves_boundary_conditions import select_boundary_point_from_map_snapwave
        layer.add_layer("boundary_points_snapwave",
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
                        fill_color_inactive="lightgrey"
                       )

        # Wave makers
        from .waves_wave_makers import wave_maker_created
        from .waves_wave_makers import wave_maker_modified
        from .waves_wave_makers import wave_maker_selected
        layer.add_layer("wave_makers", type="draw",
                             shape="polyline",
                             create=wave_maker_created,
                             modify=wave_maker_modified,
                             select=wave_maker_selected,
                             add=wave_maker_modified,
                             polygon_line_color="red")
        
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
            # Drainage structures are made grey
            layer.layer["drainage_structures"].deactivate()
            # # SnapWave boundary enclosure is made invisible
            # layer.layer["snapwave_boundary_enclosure"].hide()
            layer.layer["boundary_points_snapwave"].deactivate()
            # Wave makers are made invisible
            layer.layer["wave_makers"].hide()
        elif mode == "invisible":
           layer.hide()

    def set_crs(self):
        crs = app.crs
        old_crs = self.domain.crs
        if old_crs != crs:
            self.domain.crs = crs
            self.domain.clear_spatial_attributes()
            self.plot()

    def open(self, filename=None):
        # Open input file, and change working directory
        if filename is None:
            # Open file dialog to select input file
            filename = app.gui.window.dialog_open_file("Open file", filter="SFINCS input file (sfincs.inp)")
            filename = filename[0]

        if filename:
            dlg = app.gui.window.dialog_wait("Loading SFINCS model ...")
            path = os.path.dirname(filename)
            # if path is and empty string, use current working directory
            if not path:
                path = os.getcwd()
            os.chdir(path)
            self.initialize()
            self.domain = SfincsModel(root=".", mode="r+")
            self.set_gui_variables()
            # Change CRS
            map.set_crs(self.domain.crs)
            self.plot()
            dlg.close()
            app.gui.window.update()

            # Zoom to model extent (cht_sfincs has a nice function for this...)
            buffer = 0.1
            crds = self.domain.quadtree_grid.exterior.to_crs(crs=4326).total_bounds.tolist()
            dx = crds[2] - crds[0]
            dy = crds[3] - crds[1]
            crds[0] = crds[0] - buffer * dx
            crds[1] = crds[1] - buffer * dy
            crds[2] = crds[2] + buffer * dx
            crds[3] = crds[3] + buffer * dy
            app.map.fit_bounds(crds[0], crds[1], crds[2], crds[3])

    def save(self):        
        # Write sfincs.inp
        self.check_times()
        # self.domain.path = os.getcwd()
        # self.domain.input.variables.epsg = app.crs.to_epsg()
        # self.domain.exe_path = app.config["sfincs_exe_path"]
        # self.domain.write_batch_file()
        app.model["sfincs_hmt"].domain.config.write()

    def plot(self):
        # Plot everything
        # app.map.add_layer("sfincs_hmt").clear()
        # Grid
        app.map.layer["sfincs_hmt"].layer["grid"].set_data(app.model["sfincs_hmt"].domain.quadtree_grid)
        # Grid exterior
        app.map.layer["sfincs_hmt"].layer["grid_exterior"].set_data(app.model["sfincs_hmt"].domain.quadtree_grid.exterior)
        # Mask
        app.map.layer["sfincs_hmt"].layer["mask"].set_data(app.model["sfincs_hmt"].domain.quadtree_mask)
        # Thin dams
        app.map.layer["sfincs_hmt"].layer["thin_dams"].layer["polylines"].set_data(app.model["sfincs_hmt"].domain.thin_dams.gdf)
        # Weirs
        app.map.layer["sfincs_hmt"].layer["weirs"].layer["polylines"].set_data(app.model["sfincs_hmt"].domain.weirs.gdf)
        # Drainage structures
        app.map.layer["sfincs_hmt"].layer["drainage_structures"].set_data(app.model["sfincs_hmt"].domain.drainage_structures.gdf)
        # Observation points
        app.map.layer["sfincs_hmt"].layer["observation_points"].set_data(app.model["sfincs_hmt"].domain.observation_points.gdf, 0)
        # Cross sections
        app.map.layer["sfincs_hmt"].layer["cross_sections"].layer["polylines"].set_data(app.model["sfincs_hmt"].domain.cross_sections.gdf)
        # Boundary points
        app.map.layer["sfincs_hmt"].layer["boundary_points"].set_data(app.model["sfincs_hmt"].domain.water_level.gdf, 0)
        # Discharge points
        app.map.layer["sfincs_hmt"].layer["discharge_points"].set_data(app.model["sfincs_hmt"].domain.discharge_points.gdf, 0)
        # Mask SnapWave
        app.map.layer["sfincs_hmt"].layer["mask_snapwave"].set_data(app.model["sfincs_hmt"].domain.quadtree_snapwave_mask)
        # SnapWave Boundary points
        app.map.layer["sfincs_hmt"].layer["boundary_points_snapwave"].set_data(app.model["sfincs_hmt"].domain.snapwave_boundary_conditions.gdf, 0)
        # Wave makers
        app.map.layer["sfincs_hmt"].layer["wave_makers"].set_data(app.model["sfincs_hmt"].domain.wave_makers.data)

    def set_gui_variables(self):
        """Called after reading the input file to set the GUI variables"""

        group = "sfincs_hmt"

        # Copy sfincs input variables to gui variables
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
        cdval = self.domain.config.get("cdval", [0.0, 0.0, 0.0])
        app.gui.setvar(group, "cd_1", cdval[0])
        app.gui.setvar(group, "cd_2", cdval[1])
        app.gui.setvar(group, "cd_3", cdval[2])

        # Boundary conditions
        app.gui.setvar(group, "boundary_point_names", [])
        app.gui.setvar(group, "nr_boundary_points", 0)
        app.gui.setvar(group, "active_boundary_point", 0)
        app.gui.setvar(group, "boundary_dx", 10000.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_or_astro", "timeseries")
        app.gui.setvar(group, "boundary_conditions_timeseries_shape", "constant")
        app.gui.setvar(group, "boundary_conditions_timeseries_time_step", 600.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_offset", 0.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_amplitude", 1.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_phase", 0.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_period", 43200.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_peak", 1.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_tpeak", 86400.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_duration", 43200.0)
        app.gui.setvar(group, "boundary_conditions_tide_model", app.gui.getvar("tide_models", "names")[0])
                 
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

        # Weirs
        app.gui.setvar(group, "weir_names", [])
        app.gui.setvar(group, "nr_weirs", 0)
        app.gui.setvar(group, "weir_index", 0)
        app.gui.setvar(group, "weir_elevation", 0.0)
        app.gui.setvar(group, "weir_par1", 0.5)
        app.gui.setvar(group, "weir_elevation", 0.0)
        app.gui.setvar(group, "weir_enable_editing_elevation", False)
        app.gui.setvar(group, "weir_enable_editing_par1", False)

        # Drainage
        app.gui.setvar(group, "drainage_structure_names", [])
        app.gui.setvar(group, "nr_drainage_structures", 0)
        app.gui.setvar(group, "drainage_structure_index", 0)
        app.gui.setvar(group, "drainage_structure_alpha", 0.6)
        app.gui.setvar(group, "drainage_structure_discharge", 1.0)
        app.gui.setvar(group, "drainage_structure_width", 100.0)
        app.gui.setvar(group, "drainage_structure_sill_elevation", 0.0)
        app.gui.setvar(group, "drainage_structure_manning_n", 0.024)
        app.gui.setvar(group, "drainage_structure_zmin", 0.0)
        app.gui.setvar(group, "drainage_structure_zmax", 1.0)
        app.gui.setvar(group, "drainage_structure_closing_time", 600.0)
        app.gui.setvar(group, "drainage_structure_type", 1)
        app.gui.setvar(group, "drainage_structure_types", [1, 2, 3, 4])
        app.gui.setvar(group, "drainage_structure_type_names", ["Pump", "Culvert", "Check Valve", "Gate"])

        # SnapWave
        app.gui.setvar("modelmaker_sfincs_hmt", "use_snapwave", app.gui.getvar(group, "snapwave"))
        app.gui.setvar(group, "boundary_point_names_snapwave", [])
        app.gui.setvar(group, "nr_boundary_points_snapwave", 0)
        app.gui.setvar(group, "active_boundary_point_snapwave", 0)
        app.gui.setvar(group, "boundary_dx_snapwave", 10000.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_shape_snapwave", "constant")
        app.gui.setvar(group, "boundary_conditions_timeseries_time_step_snapwave", 600.0)
        # app.gui.setvar(group, "boundary_conditions_timeseries_offset", 0.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_hm0_snapwave", 1.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_tp_snapwave", 8.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_wd_snapwave", 0.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_ds_snapwave", 20.0)
        # app.gui.setvar(group, "boundary_conditions_timeseries_phase", 0.0)
        # app.gui.setvar(group, "boundary_conditions_timeseries_period", 43200.0)
        # app.gui.setvar(group, "boundary_conditions_timeseries_peak", 1.0)
        # app.gui.setvar(group, "boundary_conditions_timeseries_tpeak", 86400.0)
        # app.gui.setvar(group, "boundary_conditions_timeseries_duration", 43200.0)

        # Wave makers  
        app.gui.setvar(group, "wave_maker_names", [])
        app.gui.setvar(group, "nr_wave_makers", 0)
        app.gui.setvar(group, "active_wave_maker", 0)

        app.gui.setvar(group, "wind", False)
        app.gui.setvar(group, "baro", False)
        app.gui.setvar(group, "rain", False)

        # Turning off weirs for now
        app.gui.setvar(group, "enable_weirs", True)

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

        # group = "sfincs_hmt"
        # for var_name in vars(self.domain.input.variables):
        #     setattr(self.domain.input.variables, var_name, app.gui.getvar(group, var_name))
        # if self.domain.input.variables.snapwave:
        #     app.gui.setvar("modelmaker_sfincs_hmt", "use_snapwave", True)
        # else:
        #     app.gui.setvar("modelmaker_sfincs_hmt", "use_snapwave", False)
        # # Wind drag    
        # self.domain.input.variables.cdwnd[0] = app.gui.getvar(group, "wind_speed_1")
        # self.domain.input.variables.cdwnd[1] = app.gui.getvar(group, "wind_speed_2")
        # self.domain.input.variables.cdwnd[2] = app.gui.getvar(group, "wind_speed_3")
        # self.domain.input.variables.cdval[0] = app.gui.getvar(group, "cd_1")
        # self.domain.input.variables.cdval[1] = app.gui.getvar(group, "cd_2")
        # self.domain.input.variables.cdval[2] = app.gui.getvar(group, "cd_3")

    # def initialize_domain(self):
    #     self.domain = SFINCS(crs=app.crs)
    #     # Also add some other attributes needed for the GUI
    #     self.observation_points_changed = False
    #     self.discharge_points_changed = False
    #     self.boundaries_changed = False
    #     self.thin_dams_changed = False

    def set_input_variable(self, gui_variable, value):
        pass

    def add_stations(self, gdf_stations_to_add, naming_option="id"):
        self.domain.observation_points.add_points(gdf_stations_to_add, name=naming_option)
        gdf = self.domain.observation_points.gdf
        app.map.layer["sfincs_hmt"].layer["observation_points"].set_data(gdf, 0)
        if not self.domain.input.variables.obsfile:
            self.domain.input.variables.obsfile = "sfincs.obs"
            app.gui.setvar("sfincs_hmt", "obsfile", self.domain.input.variables.obsfile)
        self.domain.observation_points.write()

    def check_times(self):
        # This does not yet exist for HydroMT-SFINCS
        return
        ok, message_list = self.domain.check_times()
        if not ok:
            messages = ""
            for message in message_list:
                messages = messages + message + "\n"
            app.gui.window.dialog_warning(messages, "Warning")

