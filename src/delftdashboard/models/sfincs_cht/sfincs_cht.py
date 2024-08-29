# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
# import datetime
import os

from delftdashboard.operations.model import GenericModel
from delftdashboard.app import app

from cht_sfincs.sfincs import SFINCS

#from hydromt_sfincs import SfincsModel

class Model(GenericModel):
    def __init__(self, name):
        super().__init__()

        self.name = name
        self.long_name = "SFINCS (CHT)"

        print("Model " + self.name + " added!")
        self.active_domain = 0

        self.initialize_domain()
        self.set_gui_variables()

    def add_layers(self):
        layer = app.map.add_layer("sfincs_cht")

        layer.add_layer("grid", type="image")

        layer.add_layer("grid_exterior",
                        type="line",
                        circle_radius=0,
                        line_color="yellow")

        layer.add_layer("mask_include",
                        type="circle",
                        circle_radius=3,
                        fill_color="yellow",
                        line_color="transparent")

        layer.add_layer("mask_open_boundary",
                        type="circle",
                        circle_radius=3,
                        fill_color="red",
                        line_color="transparent")

        layer.add_layer("mask_outflow_boundary",
                        type="circle",
                        circle_radius=3,
                        fill_color="green",
                        line_color="transparent")

        layer.add_layer("mask_include_snapwave",
                        type="circle",
                        circle_radius=3,
                        fill_color="yellow",
                        line_color="transparent")

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

        from .observation_points import select_observation_point_from_map
        layer.add_layer("observation_points",
                        type="circle_selector",
                        select=select_observation_point_from_map,
                        line_color="white",
                        line_opacity=1.0,
                        fill_color="blue",
                        fill_opacity=1.0,
                        circle_radius=3,
                        circle_radius_selected=4,
                        line_color_selected="white",
                        fill_color_selected="red")


        # Snapwave Boundary Enclosure
        from .waves_snapwave import boundary_enclosure_created
        from .waves_snapwave import boundary_enclosure_modified
        layer.add_layer("snapwave_boundary_enclosure", type="draw",
                             shape="polygon",
                             create=boundary_enclosure_created,
                             modify=boundary_enclosure_modified,
#                             add=boundary_enclosure_created,
                             polygon_line_color="red")

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
        layer = app.map.layer["sfincs_cht"]
        if mode == "inactive":
            # Grid is made visible
            layer.layer["grid"].deactivate()
            # Grid exterior is made visible
            layer.layer["grid_exterior"].deactivate()
            # Mask is made invisible
            layer.layer["mask_include"].hide()
            layer.layer["mask_open_boundary"].hide()
            layer.layer["mask_outflow_boundary"].hide()
            layer.layer["mask_include_snapwave"].hide()
            # Boundary points are made grey
            layer.layer["boundary_points"].deactivate()
            # Observation points are made grey
            layer.layer["observation_points"].deactivate()
            # Thin dams are made grey
            layer.layer["thin_dams"].layer["polylines"].deactivate()
            layer.layer["thin_dams"].layer["snapped"].hide()
            # SnapWave boundary enclosure is made invisible
            layer.layer["snapwave_boundary_enclosure"].hide()
            # Wave makers are made invisible
            layer.layer["wave_makers"].hide()
        if mode == "invisible":
           layer.hide()

    def set_crs(self):
        crs = app.crs
        old_crs = self.domain.crs
        if old_crs != crs:
            self.domain.crs = crs
            self.domain.clear_spatial_attributes()
            self.plot()

    def open(self):
        # Open input file, and change working directory
        fname = app.gui.window.dialog_open_file("Open file", filter="SFINCS input file (sfincs.inp)")
        fname = fname[0]
        if fname:
            dlg = app.gui.window.dialog_wait("Loading SFINCS model ...")
            self.initialize_domain()
            path = os.path.dirname(fname)
            self.domain.path = path
            self.domain.read()
            self.set_gui_variables()
            # Change working directory
            os.chdir(path)
            # Change CRS
            old_crs = app.crs
            app.crs = self.domain.crs
            app.map.crs = self.domain.crs
            self.plot()
            if old_crs != app.crs:
                app.map.fly_to(-80.0, 30.0, 6)
            dlg.close()

    def save(self):
        # Write sfincs.inp
        self.domain.path = os.getcwd()        
        self.domain.input.variables.epsg = app.crs.to_epsg()
        self.domain.exe_path = self.exe_path
        self.domain.input.write()
        self.domain.write_batch_file()
        app.model["sfincs_cht"].domain.input.write()

    def plot(self):
        # Plot everything
#        app.map.add_layer("sfincs_cht").clear()
        # Grid
        app.map.layer["sfincs_cht"].layer["grid"].set_data(app.model["sfincs_cht"].domain.grid)
        # Grid exterior
        app.map.layer["sfincs_cht"].layer["grid_exterior"].set_data(app.model["sfincs_cht"].domain.grid.exterior)
        # Mask
        app.map.layer["sfincs_cht"].layer["mask_include"].set_data(app.model["sfincs_cht"].domain.mask.to_gdf(option="include"))
        app.map.layer["sfincs_cht"].layer["mask_open_boundary"].set_data(app.model["sfincs_cht"].domain.mask.to_gdf(option="open"))
        app.map.layer["sfincs_cht"].layer["mask_outflow_boundary"].set_data(app.model["sfincs_cht"].domain.mask.to_gdf(option="outflow"))
        # Observation points
        app.map.layer["sfincs_cht"].layer["observation_points"].set_data(app.model["sfincs_cht"].domain.observation_points.gdf, 0)
        # Boundary points
        app.map.layer["sfincs_cht"].layer["boundary_points"].set_data(app.model["sfincs_cht"].domain.boundary_conditions.gdf, 0)
        # SnapWave boundary enclosure
        app.map.layer["sfincs_cht"].layer["snapwave_boundary_enclosure"].set_data(app.model["sfincs_cht"].domain.snapwave.boundary_enclosure.gdf)
        # Wave makers
        app.map.layer["sfincs_cht"].layer["wave_makers"].set_data(app.model["sfincs_cht"].domain.wave_makers.gdf)

    def plot_wave_makers(self):
        layer = app.map.layer["sfincs_cht"].layer["wave_makers"]
        layer.clear()
        layer.add_feature(self.domain.wave_makers.gdf)

    def set_gui_variables(self):

        group = "sfincs_cht"

        # Copy sfincs input variables to gui variables
        for var_name in vars(self.domain.input.variables):
            app.gui.setvar(group, var_name, getattr(self.domain.input.variables, var_name))

        # Now set some extra variables needed for SFINCS GUI

        app.gui.setvar(group, "grid_type", "regular")
        app.gui.setvar(group, "bathymetry_type", "regular")

        app.gui.setvar(group, "snapwave", False)

        app.gui.setvar(group, "roughness_type", "landsea")

        app.gui.setvar(group, "input_options_text", ["Binary", "ASCII"])
        app.gui.setvar(group, "input_options_values", ["bin", "asc"])

        app.gui.setvar(group, "output_options_text", ["NetCDF", "Binary", "ASCII"])
        app.gui.setvar(group, "output_options_values", ["net", "bin", "asc"])

        app.gui.setvar(group, "meteo_forcing_type", "uniform")

        app.gui.setvar(group, "crs_type", "geographic")

        # Boundary conditions
        app.gui.setvar(group, "boundary_point_names", [])
        app.gui.setvar(group, "nr_boundary_points", 0)
        app.gui.setvar(group, "active_boundary_point", 0)
        app.gui.setvar(group, "boundary_wl", 0.0)
        app.gui.setvar(group, "boundary_dx", 10000.0)
         
        # Observation points 
        app.gui.setvar(group, "observation_point_names", [])
        app.gui.setvar(group, "nr_observation_points", 0)
        app.gui.setvar(group, "active_observation_point", 0)

        # Thin dams
        app.gui.setvar(group, "thin_dam_names", [])
        app.gui.setvar(group, "nr_thin_dams", 0)
        app.gui.setvar(group, "thin_dam_index", 0)

        # Wave makers  
        app.gui.setvar(group, "wave_maker_names", [])
        app.gui.setvar(group, "nr_wave_makers", 0)
        app.gui.setvar(group, "active_wave_maker", 0)

        app.gui.setvar(group, "wind", True)
        app.gui.setvar(group, "rain", True)


    def set_model_variables(self, varid=None, value=None):
        # Copies gui variables to sfincs input variables
        group = "sfincs_cht"
        for var_name in vars(self.domain.input.variables):
            setattr(self.domain.input.variables, var_name, app.gui.getvar(group, var_name))
        if self.domain.input.variables.snapwave:
            app.gui.setvar("modelmaker_sfincs_cht", "use_snapwave", True)
        else:
            app.gui.setvar("modelmaker_sfincs_cht", "use_snapwave", False)


    def initialize_domain(self):
        self.domain = SFINCS(crs=app.crs)

    def set_input_variable(self, gui_variable, value):
        pass

