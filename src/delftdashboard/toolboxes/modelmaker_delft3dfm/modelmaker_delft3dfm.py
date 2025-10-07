# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

import numpy as np
import geopandas as gpd
from pyproj import CRS

from delftdashboard.operations.toolbox import GenericToolbox
from delftdashboard.app import app

# from cht_bathymetry.bathymetry_database import bathymetry_database
from cht_utils.misc_tools import dict2yaml
from cht_utils.misc_tools import yaml2dict
from cht_sfincs.quadtree_grid_snapwave import snapwave_quadtree2mesh

class Toolbox(GenericToolbox):
    def __init__(self, name):
        super().__init__()

        self.name = name
        self.long_name = "Model Maker"

    def initialize(self):

        # Set variables

        # Grid outline
        self.grid_outline = gpd.GeoDataFrame()

        # Bathymetry
        self.selected_bathymetry_datasets = []

        # Include polygons
        # self.include_polygon = gpd.GeoDataFrame()
        # Exclude polygons
        self.exclude_polygon = gpd.GeoDataFrame()
        self.exclude_polygon_names = []

        # Boundary polygons
        self.open_boundary_polygon = gpd.GeoDataFrame()
        self.open_boundary_polygon_names = []
        # self.outflow_boundary_polygon = gpd.GeoDataFrame()

        # Refinement
        # self.refinement_levels = []
        self.refinement_polygon = gpd.GeoDataFrame()
        self.refinement_polygon_names = []

        self.refinement_depth = False
        self.min_edge_size = 500

        self.setup_dict = {}

        # Set GUI variable
        group = "modelmaker_delft3dfm"

        # app.gui.setvar(group, "build_grid", True)
        # app.gui.setvar(group, "use_snapwave", False)

        # Domain
        app.gui.setvar(group, "x0", 0.0)
        app.gui.setvar(group, "y0", 0.0)
        app.gui.setvar(group, "nmax", 0)
        app.gui.setvar(group, "mmax", 0)

        if app.crs.is_geographic:
            app.gui.setvar(group, "dx", 0.1)
            app.gui.setvar(group, "dy", 0.1)
        else:
            app.gui.setvar(group, "dx", 1000.0)
            app.gui.setvar(group, "dy", 1000.0)

        # Refinement
        app.gui.setvar(group, "refinement_depth", 0) 
        app.gui.setvar(group, "depth_min_edge_size", 500) 

        # Polygon refinement
        app.gui.setvar(group, "refinement_polygon_file", "refine.geojson")
        app.gui.setvar(group, "refinement_polygon_names", [])
        app.gui.setvar(group, "refinement_polygon_index", 0)
        app.gui.setvar(group, "refinement_polygon_refinement_type", 1) 
        # app.gui.setvar(group, "refinement_polygon_connect_hanging_nodes", 1)
        # app.gui.setvar(group, "refinement_polygon_smoothing", 2)
        # app.gui.setvar(group, "refinement_polygon_max_courant_time", 2)
        app.gui.setvar(group, "nr_refinement_polygons", 0)
        app.gui.setvar(group, "ref_min_edge_size", 500)

        # Mask
        app.gui.setvar(group, "exclude_polygon_file", "exclude.geojson")
        app.gui.setvar(group, "exclude_polygon_names", [])
        app.gui.setvar(group, "exclude_polygon_index", 0)
        app.gui.setvar(group, "nr_exclude_polygons", 0)


        app.gui.setvar(group, "open_boundary_polygon_file", "open_boundary.geojson")
        app.gui.setvar(group, "open_boundary_polygon_names", [])
        app.gui.setvar(group, "open_boundary_polygon_index", 0)
        app.gui.setvar(group, "nr_open_boundary_polygons", 0)
        app.gui.setvar(group, "open_boundary_zmax",  99999.0)
        app.gui.setvar(group, "open_boundary_zmin", -99999.0)
        app.gui.setvar(group, "boundary_dx", 0.05)

        # app.gui.setvar(group, "outflow_boundary_polygon_file", "outflow_boundary.geojson")
        # app.gui.setvar(group, "outflow_boundary_polygon_names", [])
        # app.gui.setvar(group, "outflow_boundary_polygon_index", 0)
        # app.gui.setvar(group, "nr_outflow_boundary_polygons", 0)
        # app.gui.setvar(group, "outflow_boundary_zmax",  99999.0)
        # app.gui.setvar(group, "outflow_boundary_zmin", -99999.0)


        # Bathymetry
        source_names, sources = app.bathymetry_database.sources()
        app.gui.setvar(group, "bathymetry_source_names", source_names)
        app.gui.setvar(group, "active_bathymetry_source", source_names[0])
        dataset_names, dataset_long_names, dataset_source_names = app.bathymetry_database.dataset_names(source=source_names[0])
        app.gui.setvar(group, "bathymetry_dataset_names", dataset_names)
        app.gui.setvar(group, "bathymetry_dataset_index", 0)
        app.gui.setvar(group, "selected_bathymetry_dataset_names", [])
        app.gui.setvar(group, "selected_bathymetry_dataset_index", 0)
        app.gui.setvar(group, "selected_bathymetry_dataset_zmin", -99999.0)
        app.gui.setvar(group, "selected_bathymetry_dataset_zmax", 99999.0)
        app.gui.setvar(group, "nr_selected_bathymetry_datasets", 0)

        # Boundary points
        app.gui.setvar(group, "boundary_dx", 50000.0)

    def set_layer_mode(self, mode):
        if mode == "inactive":
            # Make all layers invisible
            app.map.layer["modelmaker_delft3dfm"].hide()
        if mode == "invisible":
            app.map.layer["modelmaker_delft3dfm"].hide()

    def add_layers(self):
        # Add Mapbox layers
        layer = app.map.add_layer("modelmaker_delft3dfm")

        # Grid outline
        from .domain import grid_outline_created
        from .domain import grid_outline_modified
        layer.add_layer("grid_outline", type="draw",
                             shape="rectangle",
                             create=grid_outline_created,
                             modify=grid_outline_modified,
                             polygon_line_color="mediumblue",
                             polygon_fill_opacity=0.3,
                             rotate=True
                            )

        ### Mask
        # Include
        # from .mask_active_cells import include_polygon_created
        # from .mask_active_cells import include_polygon_modified
        # from .mask_active_cells import include_polygon_selected
        # layer.add_layer("include_polygon", type="draw",
        #                      shape="polygon",
        #                      create=include_polygon_created,
        #                      modify=include_polygon_modified,
        #                      select=include_polygon_selected,
        #                      polygon_line_color="limegreen",
        #                      polygon_fill_color="limegreen",
        #                      polygon_fill_opacity=0.3)
        # Exclude
        from .exclude import exclude_polygon_created
        from .exclude import exclude_polygon_modified
        from .exclude import exclude_polygon_selected
        layer.add_layer("exclude_polygon", type="draw",
                             shape="polygon",
                             create=exclude_polygon_created,
                             modify=exclude_polygon_modified,
                             select=exclude_polygon_selected,
                             polygon_line_color="orangered",
                             polygon_fill_color="orangered",
                             polygon_fill_opacity=0.3)
        # Boundary
        from .boundary import open_boundary_polygon_created
        from .boundary import open_boundary_polygon_modified
        from .boundary import open_boundary_polygon_selected
        layer.add_layer("open_boundary_polygon", type="draw",
                             shape="polygon",
                             create=open_boundary_polygon_created,
                             modify=open_boundary_polygon_modified,
                             select=open_boundary_polygon_selected,
                             polygon_line_color="deepskyblue",
                             polygon_fill_color="deepskyblue",
                             polygon_fill_opacity=0.3)

        # Outflow boundary
        # from .mask_boundary_cells import outflow_boundary_polygon_created
        # from .mask_boundary_cells import outflow_boundary_polygon_modified
        # from .mask_boundary_cells import outflow_boundary_polygon_selected
        # layer.add_layer("outflow_boundary_polygon", type="draw",
        #                      shape="polygon",
        #                      create=outflow_boundary_polygon_created,
        #                      modify=outflow_boundary_polygon_modified,
        #                      select=outflow_boundary_polygon_selected,
        #                      polygon_line_color="red",
        #                      polygon_fill_color="orange",
        #                      polygon_fill_opacity=0.3)

        # Exclude
        # from .mask_active_cells_snapwave import exclude_polygon_created_snapwave
        # from .mask_active_cells_snapwave import exclude_polygon_modified_snapwave
        # from .mask_active_cells_snapwave import exclude_polygon_selected_snapwave
        # layer.add_layer("exclude_polygon_snapwave", type="draw",
        #                      shape="polygon",
        #                      create=exclude_polygon_created_snapwave,
        #                      modify=exclude_polygon_modified_snapwave,
        #                      select=exclude_polygon_selected_snapwave,
        #                      polygon_line_color="orangered",
        #                      polygon_fill_color="orangered",
        #                      polygon_fill_opacity=0.3)

        # Refinement polygons
        from .refinement import refinement_polygon_created
        from .refinement import refinement_polygon_modified
        from .refinement import refinement_polygon_selected
        layer.add_layer("polygon_refinement", type="draw",
                             columns={"min_edge_size": 500},
                             shape="polygon",
                             create=refinement_polygon_created,
                             modify=refinement_polygon_modified,
                             select=refinement_polygon_selected,
                             polygon_line_color="red",
                             polygon_fill_color="orange",
                             polygon_fill_opacity=0.3)

    def set_crs(self):
        # Called when the CRS is changed
        group = "modelmaker_delft3dfm"
        if app.crs.is_geographic:
            app.gui.setvar(group, "dx", 0.1)
            app.gui.setvar(group, "dy", 0.1)
        else:
            app.gui.setvar(group, "dx", 1000.0)
            app.gui.setvar(group, "dy", 1000.0)

        self.initialize()
        self.clear_layers()
        
    def generate_grid(self):
        group = "modelmaker_delft3dfm"
        dlg = app.gui.window.dialog_wait("Generating grid ...")
        # self.clear_layers()
        model = app.model["delft3dfm"].domain
        model.clear_spatial_attributes()    
        x0       = app.gui.getvar(group, "x0")
        y0       = app.gui.getvar(group, "y0")
        dx       = app.gui.getvar(group, "dx")
        dy       = app.gui.getvar(group, "dy")
        nmax     = app.gui.getvar(group, "nmax")
        mmax     = app.gui.getvar(group, "mmax")
        model.input.geometry.netfile.filepath = "flow_net.nc"
        app.gui.setvar("delft3dfm", "netfile", model.input.geometry.netfile.filepath)

        # if len(self.refinement_polygon) == 0:
        #     refpol = None
        # else:
        #     # Make list of separate gdfs for each polygon
        #     refpol = self.refinement_polygon

        # Build grid 
        bathymetry_list = app.toolbox["modelmaker_delft3dfm"].selected_bathymetry_datasets
        model.grid.build(x0, y0, nmax, mmax, dx, dy, bathymetry_list=bathymetry_list, bathymetry_database=app.bathymetry_database)
        # Save grid 
        model.grid.write()

        # Replot everything
        app.model["delft3dfm"].plot()

        dlg.close()

    def generate_depth_refinement(self):
        group = "modelmaker_delft3dfm"
        dlg = app.gui.window.dialog_wait("Generating refinement ...")
        model = app.model["delft3dfm"].domain
        
        bathymetry_list = app.toolbox["modelmaker_delft3dfm"].selected_bathymetry_datasets

        if bathymetry_list:
            model.grid.refine_depth(bathymetry_list, bathymetry_database=app.bathymetry_database)
            
            # Interpolate bathymetry onto the grid (Update: now done only for connect nodes)
            # model.grid.set_bathymetry(bathymetry_list, bathymetry_database=app.bathymetry_database)
        
            # Save grid 
            model.grid.write()

            # Replot everything
            app.model["delft3dfm"].plot()
        else:
            print("No bathymetry selected")

        dlg.close()

    def generate_polygon_depth_refinement(self):
        group = "modelmaker_delft3dfm"
        dlg = app.gui.window.dialog_wait("Generating refinement ...")
        model = app.model["delft3dfm"].domain
        
        bathymetry_list = app.toolbox["modelmaker_delft3dfm"].selected_bathymetry_datasets

        if bathymetry_list:
            model.grid.refine_polygon_depth(bathymetry_list, bathymetry_database=app.bathymetry_database, gdf = self.refinement_polygon)
            
            # Interpolate bathymetry onto the grid (Update: now done only for connect nodes)
            # model.grid.set_bathymetry(bathymetry_list, bathymetry_database=app.bathymetry_database)
        
            # Save grid 
            model.grid.write()

            # Replot everything
            app.model["delft3dfm"].plot()
        else:
            print("No bathymetry selected")

        dlg.close()

    def generate_polygon_refinement(self):
        group = "modelmaker_delft3dfm"
        dlg = app.gui.window.dialog_wait("Generating refinement ...")
        model = app.model["delft3dfm"].domain
        
        model.grid.refine_polygon(gdf = self.refinement_polygon)
        
        # Interpolate bathymetry onto the grid (Update: now done only for connect nodes)
        # bathymetry_list = app.toolbox["modelmaker_delft3dfm"].selected_bathymetry_datasets
        # if bathymetry_list:
        #     model.grid.set_bathymetry(bathymetry_list, bathymetry_database=app.bathymetry_database)
      
        # Save grid 
        model.grid.write()

        # Replot everything
        app.model["delft3dfm"].plot()

        dlg.close()

    def connect_nodes(self):
        group = "modelmaker_delft3dfm"
        dlg = app.gui.window.dialog_wait("Connecting nodes ...")
        model = app.model["delft3dfm"].domain

        bathymetry_list = app.toolbox["modelmaker_delft3dfm"].selected_bathymetry_datasets

        if bathymetry_list:
            model.grid.connect_nodes(bathymetry_list, bathymetry_database=app.bathymetry_database)
            app.model["delft3dfm"].domain.grid.set_bathymetry(bathymetry_list, bathymetry_database=app.bathymetry_database)

            # Save grid 
            model.grid.write()

            # Replot everything
            app.model["delft3dfm"].plot()
        else:
            print("No bathymetry selected")

        dlg.close()

    def generate_bathymetry(self):
        dlg = app.gui.window.dialog_wait("Generating bathymetry ...")
        bathymetry_list = app.toolbox["modelmaker_delft3dfm"].selected_bathymetry_datasets
        app.model["delft3dfm"].domain.grid.set_bathymetry(bathymetry_list, bathymetry_database=app.bathymetry_database)
        app.model["delft3dfm"].domain.grid.write()
        dlg.close()

    def generate_bnd_coastline(self):
        dlg = app.gui.window.dialog_wait("Creating open boundary based on coastline ...")
        res = app.gui.getvar("modelmaker_delft3dfm", "boundary_dx")
        if app.crs.is_geographic:
            res = res / 111111.0
        app.model["delft3dfm"].domain.boundary_conditions.generate_bnd(bnd_withcoastlines = True, resolution = res)
        app.model["delft3dfm"].domain.boundary_conditions.write_bnd()
        # app.model["delft3dfm"].domain.grid.write()
        # Replot everything
        app.model["delft3dfm"].plot()
        dlg.close()

    def generate_bnd_polygon(self):
        dlg = app.gui.window.dialog_wait("Creating open boundary based on polygon ...")
        gdf = self.open_boundary_polygon
        res = app.gui.getvar("modelmaker_delft3dfm", "boundary_dx")
        if app.crs.is_geographic:
            res = res / 111111.0
        app.model["delft3dfm"].domain.boundary_conditions.generate_bnd(bnd_withpolygon = gdf, resolution = res)
        app.model["delft3dfm"].domain.boundary_conditions.write_bnd()
        # app.model["delft3dfm"].domain.grid.write()
        # Replot everything
        app.model["delft3dfm"].plot()
        dlg.close()

    def load_bnd(self, fname):
        dlg = app.gui.window.dialog_wait("Loading boundary ...")
        app.model["delft3dfm"].domain.boundary_conditions.load_bnd(file_name = fname)
        # app.model["delft3dfm"].domain.grid.write()
        # Replot everything
        app.model["delft3dfm"].plot()
        dlg.close()

    def cut_polygon(self):
        dlg = app.gui.window.dialog_wait("Cutting Cells based on polygon ...")
        gdf = self.exclude_polygon
        app.model["delft3dfm"].domain.grid.delete_cells(delete_withpolygon = gdf)
        app.model["delft3dfm"].domain.grid.write()
        # Replot everything
        app.model["delft3dfm"].plot()
        dlg.close()

    def cut_coastline(self):
        dlg = app.gui.window.dialog_wait("Cutting Cells based on coastline ...")
        app.model["delft3dfm"].domain.grid.delete_cells(delete_withcoastlines=True)
        app.model["delft3dfm"].domain.grid.write()
        # Replot everything
        app.model["delft3dfm"].plot()
        dlg.close()

    def build_model(self):
        self.generate_grid()
        self.generate_bathymetry()
        # self.update_mask()
        # self.generate_subgrid()

#    def update_polygons(self): # This should really be moved to the callback modules

        # nrp = len(self.include_polygon)
        # incnames = []
        # for ip in range(nrp):
        #     incnames.append(str(ip + 1))
        # app.gui.setvar("modelmaker_delft3dfm", "nr_include_polygons", nrp)
        # app.gui.setvar("modelmaker_delft3dfm", "include_polygon_names", incnames)
        # app.gui.setvar("modelmaker_delft3dfm", "include_polygon_index", max(nrp, 0))

        # nrp = len(self.exclude_polygon)
        # excnames = []
        # for ip in range(nrp):
        #     excnames.append(str(ip + 1))
        # app.gui.setvar("modelmaker_delft3dfm", "nr_exclude_polygons", nrp)
        # app.gui.setvar("modelmaker_delft3dfm", "exclude_polygon_names", excnames)
        # app.gui.setvar("modelmaker_delft3dfm", "exclude_polygon_index", max(nrp, 0))

        # nrp = len(self.open_boundary_polygon)
        # bndnames = []
        # for ip in range(nrp):
        #     bndnames.append(str(ip + 1))
        # app.gui.setvar("modelmaker_delft3dfm", "nr_open_boundary_polygons", nrp)
        # app.gui.setvar("modelmaker_delft3dfm", "open_boundary_polygon_names", bndnames)

        # nrp = len(self.outflow_boundary_polygon)
        # bndnames = []
        # for ip in range(nrp):
        #     bndnames.append(str(ip + 1))
        # app.gui.setvar("modelmaker_delft3dfm", "nr_outflow_boundary_polygons", nrp)
        # app.gui.setvar("modelmaker_delft3dfm", "outflow_boundary_polygon_names", bndnames)

        # nrp = len(self.include_polygon_snapwave)
        # incnames = []
        # for ip in range(nrp):
        #     incnames.append(str(ip + 1))
        # app.gui.setvar("modelmaker_delft3dfm", "nr_include_polygons_snapwave", nrp)
        # app.gui.setvar("modelmaker_delft3dfm", "include_polygon_names_snapwave", incnames)

        # nrp = len(self.exclude_polygon_snapwave)
        # excnames = []
        # for ip in range(nrp):
        #     excnames.append(str(ip + 1))
        # app.gui.setvar("modelmaker_delft3dfm", "nr_exclude_polygons_snapwave", nrp)
        # app.gui.setvar("modelmaker_delft3dfm", "exclude_polygon_names_snapwave", excnames)

        # app.toolbox["modelmaker_delft3dfm"].write_include_polygon()
        # app.toolbox["modelmaker_delft3dfm"].write_exclude_polygon()
        # app.toolbox["modelmaker_delft3dfm"].write_boundary_polygon()

    # READ

    def read_refinement_polygon(self, file_name=None):
        fname = app.gui.getvar("modelmaker_delft3dfm", "refinement_polygon_file")
        self.refinement_polygon = gpd.read_file(fname)
        # app.toolbox["modelmaker_delft3dfm"].refinement_polygon_names.append(fname)
        # # Loop through rows in geodataframe and set refinement polygon names        
        self.refinement_polygon_names = []
        for i in range(len(self.refinement_polygon)):
            self.refinement_polygon_names.append(self.refinement_polygon["refinement_polygon_name"][i])
        if "min_edge_size" not in self.refinement_polygon.columns:
            self.refinement_polygon["min_edge_size"] = 500

    # def read_include_polygon(self):
    #     fname = app.gui.getvar("modelmaker_delft3dfm", "include_polygon_file")
    #     self.include_polygon = gpd.read_file(fname)

    def read_exclude_polygon(self):
        fname = app.gui.getvar("modelmaker_delft3dfm", "exclude_polygon_file")
        self.exclude_polygon = gpd.read_file(fname)
        self.exclude_polygon_names = []
        for i in range(len(self.exclude_polygon)):
            self.exclude_polygon_names.append(self.exclude_polygon["exclude_polygon_name"][i])

    def read_open_boundary_polygon(self):
        fname = app.gui.getvar("modelmaker_delft3dfm", "open_boundary_polygon_file")
        self.open_boundary_polygon = gpd.read_file(fname)
        self.open_boundary_polygon_names = []
        for i in range(len(self.open_boundary_polygon)):
            self.open_boundary_polygon_names.append(self.open_boundary_polygon["open_boundary_polygon_name"][i])

    # def read_outflow_boundary_polygon(self):
    #     fname = app.gui.getvar("modelmaker_delft3dfm", "outflow_boundary_polygon_file")
    #     self.outflow_boundary_polygon = gpd.read_file(fname)

    # def read_include_polygon_snapwave(self):
    #     fname = app.gui.getvar("modelmaker_delft3dfm", "include_polygon_file_snapwave")
    #     self.include_polygon_snapwave = gpd.read_file(fname)

    # def read_exclude_polygon_snapwave(self):
    #     fname = app.gui.getvar("modelmaker_delft3dfm", "exclude_polygon_file_snapwave")
    #     self.exclude_polygon_snapwave = gpd.read_file(fname)

    # WRITE

    def write_refinement_polygon(self):
        if len(self.refinement_polygon) == 0:
            print("No refinement polygons defined")
            return
        gdf = gpd.GeoDataFrame({"geometry": self.refinement_polygon["geometry"],
                                "refinement_polygon_name": self.refinement_polygon_names,
                                "min_edge_size": self.refinement_polygon["min_edge_size"]})
        # index = app.gui.getvar("modelmaker_delft3dfm", "refinement_polygon_index")
        # fname = app.gui.getvar("modelmaker_delft3dfm", "refinement_polygon_names")
        fname = app.gui.getvar("modelmaker_delft3dfm", "refinement_polygon_file")
        gdf.to_file(fname, driver='GeoJSON')

    # def write_include_polygon(self):
    #     if len(self.include_polygon) == 0:
    #         return
    #     gdf = gpd.GeoDataFrame(geometry=self.include_polygon["geometry"])
    #     fname = app.gui.getvar("modelmaker_delft3dfm", "include_polygon_file")
    #     gdf.to_file(fname, driver='GeoJSON')

    def write_exclude_polygon(self):
        if len(self.exclude_polygon) == 0:
            return
        gdf = gpd.GeoDataFrame({"geometry":self.exclude_polygon["geometry"],
                                "exclude_polygon_name": self.exclude_polygon_names})
        fname = app.gui.getvar("modelmaker_delft3dfm", "exclude_polygon_file")
        gdf.to_file(fname, driver='GeoJSON')

    def write_open_boundary_polygon(self):
        if len(self.open_boundary_polygon) == 0:
            return
        gdf = gpd.GeoDataFrame({"geometry": self.open_boundary_polygon["geometry"],
                                "open_boundary_polygon_name": self.open_boundary_polygon_names})
        fname = app.gui.getvar("modelmaker_delft3dfm", "open_boundary_polygon_file")
        gdf.to_file(fname, driver='GeoJSON')
        # gdf.to_file(fname, driver='ESRI Shapefile')

    # def write_outflow_boundary_polygon(self):
    #     if len(self.outflow_boundary_polygon) == 0:
    #         return
    #     gdf = gpd.GeoDataFrame(geometry=self.outflow_boundary_polygon["geometry"])
    #     fname = app.gui.getvar("modelmaker_delft3dfm", "outflow_boundary_polygon_file")
    #     gdf.to_file(fname, driver='GeoJSON')

    # def write_include_polygon_snapwave(self):
    #     if len(self.include_polygon_snapwave) == 0:
    #         return
    #     gdf = gpd.GeoDataFrame(geometry=self.include_polygon_snapwave["geometry"])
    #     fname = app.gui.getvar("modelmaker_delft3dfm", "include_polygon_file_snapwave")
    #     gdf.to_file(fname, driver='GeoJSON')

    # def write_exclude_polygon_snapwave(self):
    #     if len(self.exclude_polygon_snapwave) == 0:
    #         return
    #     gdf = gpd.GeoDataFrame(geometry=self.exclude_polygon_snapwave["geometry"])
    #     fname = app.gui.getvar("modelmaker_delft3dfm", "exclude_polygon_file_snapwave")
    #     gdf.to_file(fname, driver='GeoJSON')

    # PLOT

    def plot_refinement_polygon(self):
        layer = app.map.layer["modelmaker_delft3dfm"].layer["polygon_refinement"]
        layer.clear()
        layer.add_feature(self.refinement_polygon)

    # def plot_include_polygon(self):
    #     layer = app.map.layer["modelmaker_delft3dfm"].layer["include_polygon"]
    #     layer.clear()
    #     layer.add_feature(self.include_polygon)

    def plot_exclude_polygon(self):
        layer = app.map.layer["modelmaker_delft3dfm"].layer["exclude_polygon"]
        layer.clear()
        layer.add_feature(self.exclude_polygon)

    def plot_open_boundary_polygon(self):
        layer = app.map.layer["modelmaker_delft3dfm"].layer["open_boundary_polygon"]
        layer.clear()
        layer.add_feature(self.open_boundary_polygon)

    # def plot_outflow_boundary_polygon(self):
    #     layer = app.map.layer["modelmaker_delft3dfm"].layer["outflow_boundary_polygon"]
    #     layer.clear()
    #     layer.add_feature(self.outflow_boundary_polygon)

    # def plot_include_polygon_snapwave(self):
    #     layer = app.map.layer["modelmaker_delft3dfm"].layer["include_polygon_snapwave"]
    #     layer.clear()
    #     layer.add_feature(self.include_polygon_snapwave)

    # def plot_exclude_polygon_snapwave(self):
    #     layer = app.map.layer["modelmaker_delft3dfm"].layer["exclude_polygon_snapwave"]
    #     layer.clear()
    #     layer.add_feature(self.exclude_polygon_snapwave)


    def read_setup_yaml(self, file_name):

        # First set some default gui variables
        group = "modelmaker_delft3dfm"
        app.gui.setvar(group, "refinement_polygon_file", "refine.geojson")
        app.gui.setvar(group, "refinement_polygon_index", 0)
        # app.gui.setvar(group, "global_zmin", -99999.0)
        # app.gui.setvar(group, "global_zmax",  99999.0)
        # app.gui.setvar(group, "include_polygon_index", 0)
        # app.gui.setvar(group, "include_zmax",  99999.0)
        # app.gui.setvar(group, "include_zmin", -99999.0)
        # app.gui.setvar(group, "include_polygon_file", "include.geojson")
        app.gui.setvar(group, "exclude_polygon_index", 0)
        # app.gui.setvar(group, "exclude_zmax",  99999.0)
        # app.gui.setvar(group, "exclude_zmin", -99999.0)
        app.gui.setvar(group, "exclude_polygon_file", "exclude.geojson")
        app.gui.setvar(group, "open_boundary_polygon_index", 0)
        # app.gui.setvar(group, "open_boundary_zmax",  99999.0)
        # app.gui.setvar(group, "open_boundary_zmin", -99999.0)
        app.gui.setvar(group, "open_boundary_polygon_file", "open_boundary.geojson")
        # app.gui.setvar(group, "outflow_boundary_polygon_index", 0)
        # app.gui.setvar(group, "outflow_boundary_zmax",  99999.0)
        # app.gui.setvar(group, "outflow_boundary_zmin", -99999.0)
        # app.gui.setvar(group, "outflow_boundary_polygon_file", "outflow_boundary.geojson")
        # app.gui.setvar(group, "global_zmin_snapwave", -99999.0)
        # app.gui.setvar(group, "global_zmax_snapwave",  99999.0)
        # app.gui.setvar(group, "include_polygon_index_snapwave", 0)
        # app.gui.setvar(group, "include_zmax_snapwave",  99999.0)
        # app.gui.setvar(group, "include_zmin_snapwave", -99999.0)
        # app.gui.setvar(group, "include_polygon_file_snapwave", "include_snapwave.geojson")
        # app.gui.setvar(group, "exclude_polygon_index_snapwave", 0)
        # app.gui.setvar(group, "exclude_zmax_snapwave",  99999.0)
        # app.gui.setvar(group, "exclude_zmin_snapwave", -99999.0)
        # app.gui.setvar(group, "exclude_polygon_file_snapwave", "include_snapwave.geojson")

        # Empty geodataframes
        # self.include_polygon = gpd.GeoDataFrame()    
        self.exclude_polygon = gpd.GeoDataFrame()    
        self.open_boundary_polygon = gpd.GeoDataFrame()    
        # self.outflow_boundary_polygon = gpd.GeoDataFrame()    
        # self.snapwave_include_polygon = gpd.GeoDataFrame()    
        # self.snapwave_exclude_polygon = gpd.GeoDataFrame()    
        self.refinement_polygon = gpd.GeoDataFrame()    

        # Read in yaml file
        dct = yaml2dict(file_name)
        self.setup_dict = dct

        group = "modelmaker_delft3dfm"
        # Coordinates
        app.gui.setvar(group, "x0", dct["coordinates"]["x0"])
        app.gui.setvar(group, "y0", dct["coordinates"]["y0"])
        app.gui.setvar(group, "dx", dct["coordinates"]["dx"])
        app.gui.setvar(group, "dy", dct["coordinates"]["dy"])
        app.gui.setvar(group, "nmax", dct["coordinates"]["nmax"])
        app.gui.setvar(group, "mmax", dct["coordinates"]["mmax"])
        app.model["delft3dfm"].domain.crs = CRS(dct["coordinates"]["crs"])

        # Refinement and polygons
        if "refinement" in dct:
            if "polygon_file" in dct["refinement"]:
                app.gui.setvar(group, "refinement_polygon_file", dct["refinement"]["polygon_file"])
                self.read_refinement_polygon()
                self.plot_refinement_polygon()
                # import the function update() from refinement.py
                from .refinement import update as update_refinement
                update_refinement()

                # nrp = len(app.toolbox["modelmaker_delft3dfm"].refinement_polygon)
                # app.gui.setvar("modelmaker_delft3dfm", "nr_refinement_polygons", nrp)
                # refnames = app.toolbox["modelmaker_delft3dfm"].refinement_polygon_names
                # app.gui.setvar("modelmaker_delft3dfm", "refinement_polygon_names", refnames)

        if "exclude" in dct:
            if "polygon_file" in dct["exclude"]:
                app.gui.setvar(group, "exclude_polygon_file", dct["exclude"]["polygon_file"])
                self.read_exclude_polygon()
                self.plot_exclude_polygon()  
                # import the function update() from exclude.py
                from .exclude import update as update_exclude
                update_exclude()

        if "open_boundary" in dct:
            if "polygon_file" in dct["open_boundary"]:
                app.gui.setvar(group, "open_boundary_polygon_file", dct["open_boundary"]["polygon_file"])
                self.read_open_boundary_polygon()
                self.plot_open_boundary_polygon()
                # import the function update() from boundary.py
                from .boundary import update as update_boundary
                update_boundary()

        # Bathymetry
        dataset_names = []
        self.selected_bathymetry_datasets = []
        for ddict in dct["bathymetry"]["dataset"]:
            name = ddict["name"]
            zmin = ddict["zmin"]
            zmax = ddict["zmax"] 
            dataset = {"name": name, "zmin": zmin, "zmax": zmax}
            app.toolbox["modelmaker_delft3dfm"].selected_bathymetry_datasets.append(dataset)
            dataset_names.append(name)
        app.gui.setvar("modelmaker_delft3dfm", "selected_bathymetry_dataset_names", dataset_names)
        app.gui.setvar("modelmaker_delft3dfm", "selected_bathymetry_dataset_index", 0)
        app.gui.setvar("modelmaker_delft3dfm", "nr_selected_bathymetry_datasets", len(dataset_names))

        layer = app.map.layer["modelmaker_delft3dfm"].layer["grid_outline"]
        lenx = dct["coordinates"]["mmax"] * dct["coordinates"]["dx"]
        leny = dct["coordinates"]["nmax"] * dct["coordinates"]["dy"]
        layer.add_rectangle(dct["coordinates"]["x0"],
                            dct["coordinates"]["y0"],
                            lenx, leny,
                            0)

    def write_setup_yaml(self):
        group = "modelmaker_delft3dfm"
        dct = {}
        # Coordinates
        dct["coordinates"] = {}
        dct["coordinates"]["x0"] = float(app.gui.getvar(group, "x0"))
        dct["coordinates"]["y0"] = float(app.gui.getvar(group, "y0"))
        dct["coordinates"]["dx"] = float(app.gui.getvar(group, "dx"))
        dct["coordinates"]["dy"] = float(app.gui.getvar(group, "dy"))
        dct["coordinates"]["nmax"] = int(app.gui.getvar(group, "nmax"))
        dct["coordinates"]["mmax"] = int(app.gui.getvar(group, "mmax"))
        dct["coordinates"]["crs"] = app.model["delft3dfm"].domain.crs.name

        # Refinements
        dct["refinement"] = {}
        if len(app.toolbox["modelmaker_delft3dfm"].refinement_polygon)>0:
            dct["refinement"]["polygon_file"] = app.gui.getvar("modelmaker_delft3dfm", "refinement_polygon_file")
        dct["exclude"] = {}
        if len(app.toolbox["modelmaker_delft3dfm"].exclude_polygon)>0:
            dct["exclude"]["polygon_file"] = app.gui.getvar("modelmaker_delft3dfm", "exclude_polygon_file")
        dct["open_boundary"] = {}
        if len(app.toolbox["modelmaker_delft3dfm"].open_boundary_polygon)>0:
            dct["open_boundary"]["polygon_file"] = app.gui.getvar("modelmaker_delft3dfm", "open_boundary_polygon_file")

        # Bathymetry
        dct["bathymetry"] = {}
        dct["bathymetry"]["dataset"] = []
        for d in app.toolbox["modelmaker_delft3dfm"].selected_bathymetry_datasets:
            dataset = {}
            dataset["name"]   = d["name"]
            dataset["source"] = "delftdashboard"
            dataset["zmin"]   = d["zmin"]
            dataset["zmax"]   = d["zmax"]
            dct["bathymetry"]["dataset"].append(dataset)    

        self.setup_dict = dct

        dict2yaml("model_setup.yml", dct)

        # Write out polygons 
        app.toolbox["modelmaker_delft3dfm"].write_exclude_polygon()
        app.toolbox["modelmaker_delft3dfm"].write_open_boundary_polygon()
        app.toolbox["modelmaker_delft3dfm"].write_refinement_polygon()

def gdf2list(gdf_in):
   gdf_out = []
   for feature in gdf_in.iterfeatures():
      gdf_out.append(gpd.GeoDataFrame.from_features([feature]))
   return gdf_out
