# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
import os
#from PyQt5.QtWidgets import QFileDialog
from pathlib import Path

from delftdashboard.operations.model import GenericModel
from delftdashboard.operations import map
from delftdashboard.app import app

# from cht_delft3dfm.delft3dfm import Delft3DFM
from cht_delft3dfm import Delft3DFM
import datetime
import ast

class Model(GenericModel):
    def __init__(self, name):
        super().__init__()

        self.name = name
        self.long_name = "Delft3D-FM"

    def initialize(self):
        # self.active_domain = 0
        self.domain = Delft3DFM(crs = app.crs)
        self.domain.fname = 'flow.mdu'
        self.set_gui_variables()
        self.observation_points_changed = False
        self.observation_lines_changed = False
        self.discharge_points_changed = False
        self.boundaries_changed = False
        self.thin_dams_changed = False

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
                app.map.layer["delft3dfm"].layer["grid"].show()
                print("Grid is made visible")
            else:
                app.map.layer["delft3dfm"].layer["grid"].hide()
                print("Grid is made invisible")

    def add_layers(self):
        # Add main DDB layer
        layer = app.map.add_layer("delft3dfm")

        # layer.add_layer("grid", type="deck_geojson",
        #                 file_name="delft3dfm_grid.geojson",
        #                 line_color="black")
        layer.add_layer("grid", type="image")

        # layer.add_layer("mask_include",
        #                 type="circle",
        #                 file_name="delft3dfm_mask_include.geojson",
        #                 circle_radius=3,
        #                 fill_color="yellow",
        #                 line_color="transparent")

        # layer.add_layer("mask_boundary",
        #                 type="circle",
        #                 file_name="delft3dfm_mask_boundary.geojson",
        #                 circle_radius=3,
        #                 fill_color="red",
        #                 line_color="transparent")

        # Move this to delft3dfm.py
        # from .boundary_conditions import select_boundary_point_from_map
        layer.add_layer("boundary_line",
                        type="line",
                        hover_property="name",
                        line_color="red",
                        line_width= 3,
                        line_opacity=1.0,
                        fill_color="red",
                        fill_opacity=1.0,
                       )

        from .observation_points_regular import select_observation_point_from_map
        layer.add_layer("observation_points",
                        type="circle_selector",
                        hover_property="name",
                        select=select_observation_point_from_map,
                        line_color="white",
                        line_opacity=1.0,
                        fill_color="blue",
                        fill_opacity=1.0,
                        circle_radius=3,
                        circle_radius_selected=4,
                        line_color_selected="white",
                        fill_color_selected="red")

        from .observation_points_crs import obs_lines_created
        from .observation_points_crs import obs_lines_selected
        from .observation_points_crs import obs_lines_modified
        layer.add_layer("observation_lines",
                        type="draw",
                        shape="polyline",
                        create=obs_lines_created,
                        modify=obs_lines_modified,
                        select=obs_lines_selected,
                        polyline_line_color="yellow",
                        polyline_line_width=2.0,
                        polyline_line_opacity=1.0)
        
        # from .observation_points_spectra import select_observation_point_from_map_spectra
        # layer.add_layer("observation_points_spectra",
        #                 type="circle_selector",
        #                 select=select_observation_point_from_map_spectra,
        #                 line_color="white",
        #                 line_opacity=1.0,
        #                 fill_color="orange",
        #                 fill_opacity=1.0,
        #                 circle_radius=3,
        #                 circle_radius_selected=4,
        #                 line_color_selected="white",
        #                 fill_color_selected="red")

    def set_layer_mode(self, mode):
        if mode == "inactive":
            # Grid is made visible
            app.map.layer["delft3dfm"].layer["grid"].deactivate()
            # Mask is made invisible
            # app.map.layer["delft3dfm"].layer["mask_include"].hide()
            # app.map.layer["delft3dfm"].layer["mask_boundary"].hide()
            # Boundary points are made grey
            app.map.layer["delft3dfm"].layer["boundary_line"].deactivate()
            # Observation points are made grey
            app.map.layer["delft3dfm"].layer["observation_points"].deactivate()
            app.map.layer["delft3dfm"].layer["observation_lines"].deactivate()
            # app.map.layer["delft3dfm"].layer["observation_points_spectra"].deactivate()
        elif mode == "invisible":
            # Everything set to invisible
            app.map.layer["delft3dfm"].hide()

    def set_crs(self):
        crs = app.crs
        old_crs = self.domain.crs
        if old_crs != crs:
            self.domain.crs = crs
            self.domain.clear_spatial_attributes()
            self.plot()

    def set_gui_variables(self):
        group = "delft3dfm"
        subgroups = ['numerics', 'physics', 'output', 'geometry','wind',]

        # View  
        app.gui.setvar(group, "view_grid", True)

        # Input variables
        for groupname in subgroups:
            subgroup = getattr(self.domain.input, groupname)

            for var_name, var_value in vars(subgroup).items():
                if var_name == 'comments':
                    continue  # Skip 'comments' variable

                # if isinstance(var_value, list):  # Handle lists
                #     app.gui.setvar(group, f'{groupname}.{var_name}', var_value)

                    # for i, item in enumerate(var_value):
                    #     app.gui.setvar(group, f'{groupname}.{var_name}', item)
                if hasattr(var_value, '__dict__'): 
                    for subvar_name, subvar_value in vars(var_value).items():
                        # if isinstance(subvar_value, Path): # Convert Path object to string if it's a filepath
                        #     subvar_value = str(subvar_value)
                        # Set the nested variable
                        app.gui.setvar("delft3dfm", f'{groupname}.{var_name}.{subvar_name}', subvar_value)
                else:
                    # if isinstance(var_value, Path):   # Convert Path object to string if it's a filepath
                    #     var_value = str(var_value)
                    app.gui.setvar(group, f'{groupname}.{var_name}', var_value)

        # Overwrite time variables to set them to datetime objects
        tnow = datetime.datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        app.gui.setvar(group, "time.refdate", tnow)
        app.gui.setvar(group, "time.tstart", tnow)
        app.gui.setvar(group, "time.tstop", tnow + datetime.timedelta(days=1))

        app.gui.setvar(group, "setup.x0", 0)
        app.gui.setvar(group, "setup.y0", 1)
        app.gui.setvar(group, "setup.nmax", 0)
        app.gui.setvar(group, "setup.mmax", 0)
        app.gui.setvar(group, "setup.dx", 0.01)
        app.gui.setvar(group, "setup.dy", 0.01)

        app.gui.setvar(group, "boundary_point_names", []) 
        app.gui.setvar(group, "active_boundary_point", 0)
        app.gui.setvar(group, "boundary_forcing", self.domain.boundary_conditions.forcing)
        app.gui.setvar(group, "boundary_hm0", 1.0)
        app.gui.setvar(group, "boundary_tp", 6.0)
        app.gui.setvar(group, "boundary_wd", 0.0)
        app.gui.setvar(group, "boundary_ds", 30.0)

        app.gui.setvar(group, "observation_point_names", [])
        app.gui.setvar(group, "nr_observation_points", 0)
        app.gui.setvar(group, "active_observation_point", 0)

        app.gui.setvar(group, "observation_line_names", [])
        app.gui.setvar(group, "nr_observation_lines", 0)
        app.gui.setvar(group, "active_observation_line", 0)
        app.gui.setvar(group, "observation_line_index", 0)

        app.gui.setvar(group, "boundary_line_active", 0)
        app.gui.setvar(group, "boundary_conditions_tide_model", [])

        # Boundary conditions
        # app.gui.setvar(group, "boundary_point_names", [])
        # app.gui.setvar(group, "nr_boundary_points", 0)
        # app.gui.setvar(group, "active_boundary_point", 0)
        # app.gui.setvar(group, "boundary_dx", 10000.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_shape", "constant")
        app.gui.setvar(group, "boundary_conditions_timeseries_time_step", 600.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_offset", 0.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_offset_custom", 0.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_amplitude", 1.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_phase", 0.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_period", 43200.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_peak", 1.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_tpeak", 86400.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_duration", 43200.0)
        # app.gui.setvar(group, "boundary_conditions_tide_model", [])

    # def set_model_variables(self, varid=None, value=None):
    #     # Copies gui variables to delft3dfm input variables
    #     group = "delft3dfm"
    #     subgroups = ['numerics', 'physics', 'time', 'output', ]
                     
    #     # Input variables
    #     for groupname in subgroups:
    #         subgroup = getattr(self.domain.input, groupname)
    #         for var_name, var_value in vars(subgroup).items():
    #             setattr(f'{groupname}.{var_name}', var_name, app.gui.getvar(group, f'{groupname}.{var_name}'))

    #     group = "delft3dfm"
    #     for var_name in vars(self.domain.input.variables):
    #         setattr(self.domain.input.variables, var_name, app.gui.getvar(group, var_name))


    def set_input_variables(self):
        # Update all model input variables
        subgroups = ['numerics', 'physics', 'geometry', 'wind', ]

        for groupname in subgroups:
            subgroup = getattr(self.domain.input, groupname)

            for var_name, var_value in vars(subgroup).items():
                if var_name in ['comments', 'landboundaryfile']:
                    continue  # Skip 'comments' variable
        
                # if isinstance(var_value, list):  # Handle lists
                #     val = app.gui.getvar(f'delft3dfm', f'{groupname}.{var_name}')
                #     for i, item in enumerate(var_value):
                #         value[i] = Path(val) if isinstance(item, Path) else val
                #     setattr(subgroup, var_name, value)
                if hasattr(var_value, '__dict__'): # Handle dictionaries
                    for subvar_name in vars(var_value):
                        value = app.gui.getvar(f'delft3dfm', f'{groupname}.{var_name}.{subvar_name}')
                        if 'filepath' in subvar_name.lower() and value is not None:  # Check if it's a filepath
                            value = Path(value)  # Parse to Path
                        setattr(var_value, subvar_name, value)
                else:
                    value = app.gui.getvar("delft3dfm", f'{groupname}.{var_name}')
                    if 'filepath' in var_name.lower() and value is not None:  # Check if it's a filepath
                        value = Path(value)  # Parse to Path
                    setattr(subgroup, var_name, value)
        # Set timeframe of domain using set_timeframe
        self.set_timeframe()
        
        # Set output variables
        hisinterval = app.gui.getvar("delft3dfm", "output.hisinterval")
        if isinstance(hisinterval, str):
            hisinterval = ast.literal_eval(hisinterval)
        setattr(self.domain.input.output, "hisinterval", hisinterval)
        mapinterval = app.gui.getvar("delft3dfm", "output.mapinterval")
        if isinstance(mapinterval, str):
            mapinterval = ast.literal_eval(mapinterval)
        setattr(self.domain.input.output, "mapinterval", mapinterval)
        rstinterval = app.gui.getvar("delft3dfm", "output.rstinterval")
        if isinstance(rstinterval, str):
            rstinterval = ast.literal_eval(rstinterval)
        setattr(self.domain.input.output, "rstinterval", rstinterval)

    def set_timeframe(self):
        refdate = app.gui.getvar("delft3dfm", "time.refdate")
        refdate = refdate.strftime("%Y%m%d")
        setattr(self.domain.input.time, "refdate", refdate)

        start_time = app.gui.getvar("delft3dfm", "time.tstart")
        start_time = start_time.strftime("%Y%m%d%H%M%S")
        setattr(self.domain.input.time, "startdatetime", start_time)

        stop_time = app.gui.getvar("delft3dfm", "time.tstop")
        stop_time = stop_time.strftime("%Y%m%d%H%M%S")
        setattr(self.domain.input.time, "stopdatetime", stop_time)
     
    def open(self):
        # Open input file, and change working directory
        fname = app.gui.window.dialog_open_file("Open file", filter="Delft3D-FM input file (flow.mdu)")
        fname = fname[0]
        if fname:
            dlg = app.gui.window.dialog_wait("Loading Delft3D-FM model ...")
            path = os.path.dirname(fname)
            self.domain.path = path
            self.domain.fname = fname
            self.domain.read_input_file(fname)
            self.domain.read_attribute_files()
            self.set_gui_variables()
            # Change working directory
            os.chdir(path)
            # Change CRS
            app.crs = self.domain.crs
            self.plot()
            dlg.close()

    def save(self):
        # Write flow.mdu
        self.domain.path = os.getcwd()
        self.domain.write_input_file(input_file=os.path.join(self.domain.path, self.domain.fname))        
        # self.domain.write_batch_file()

    def load(self):
        self.domain.read_input_file(input_file=os.path.join(self.domain.path, self.domain.fname))

    def plot(self):
        # Grid
        app.map.layer["delft3dfm"].layer["grid"].set_data(self.domain.grid)
        # # Mask
        # app.map.layer["delft3dfm"].layer["mask_include"].set_data(self.domain.grid.mask_to_gdf(option="include"))
        # app.map.layer["delft3dfm"].layer["mask_boundary"].set_data(self.domain.grid.mask_to_gdf(option="boundary"))
        # Boundary points
        app.map.layer["delft3dfm"].layer["boundary_line"].clear()
        app.map.layer["delft3dfm"].layer["boundary_line"].set_data(self.domain.boundary_conditions.gdf)

        # Observation points
        # app.map.layer["delft3dfm"].layer["observation_points"].set_data(app.model["delft3dfm"].domain.observation_point_gdf, 0)
        app.map.layer["delft3dfm"].layer["observation_points"].set_data(app.model["delft3dfm"].domain.observation_points.gdf, 0)

        # Observation cross sections
        # app.map.layer["delft3dfm"].layer["observation_lines"].set_data(app.model["delft3dfm"].domain.observation_line_gdf)

        # # Boundary points
        # gdf = self.domain.boundary_conditions.gdf
        # app.map.layer["delft3dfm"].layer["boundary_points"].set_data(gdf, 0)
        # # Observation points
        # gdf = self.domain.observation_points_regular.gdf
        # app.map.layer["delft3dfm"].layer["observation_points_regular"].set_data(gdf, 0)
        # gdf = self.domain.observation_points_sp2.gdf
        # app.map.layer["delft3dfm"].layer["observation_points_spectra"].set_data(gdf, 0)

    def add_stations(self, gdf_stations_to_add, naming_option="id"):
        self.domain.observation_points.add_points(gdf_stations_to_add, name=naming_option)
        gdf = self.domain.observation_points.gdf
        app.map.layer["delft3dfm"].layer["observation_points"].set_data(gdf, 0)
        if not self.domain.input.variables.obsfile:
            self.domain.input.variables.obsfile = "delft3dfm.obs"
        self.domain.observation_points.write()
