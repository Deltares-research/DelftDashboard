# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

#import math
import numpy as np
import geopandas as gpd
#import shapely
#import json
from pyproj import CRS

from delftdashboard.operations.toolbox import GenericToolbox
from delftdashboard.app import app

from cht.bathymetry.bathymetry_database import bathymetry_database
from cht.misc.misc_tools import dict2yaml
from cht.misc.misc_tools import yaml2dict

class Toolbox(GenericToolbox):
    def __init__(self, name):
        super().__init__()

        self.name = name
        self.long_name = "Model Maker"

        # Set variables

        # Grid outline
        self.grid_outline = gpd.GeoDataFrame()

        # Bathymetry
        self.selected_bathymetry_datasets = []

        # Include polygons
        self.include_polygon = gpd.GeoDataFrame()
        self.include_file_name = "include.geojson"
        # Exclude polygons
        self.exclude_polygon = gpd.GeoDataFrame()
        self.exclude_file_name = "exclude.geojson"
        # Boundary polygons
        self.open_boundary_polygon = gpd.GeoDataFrame()
        self.open_boundary_file_name = "open_boundary.geojson"
        self.outflow_boundary_polygon = gpd.GeoDataFrame()
        self.outflow_boundary_file_name = "outflow_boundary.geojson"
        # Include polygons
        self.include_polygon_snapwave = gpd.GeoDataFrame()
        self.include_file_name_snapwave = "include_snapwave.geojson"
        # Exclude polygons
        self.exclude_polygon_snapwave = gpd.GeoDataFrame()
        self.exclude_file_name_snapwave = "exclude_snapwave.geojson"
        # Refinement
        self.refinement_levels = []
        self.refinement_polygon = gpd.GeoDataFrame()

        self.setup_dict = {}

        # Set GUI variable
        group = "modelmaker_sfincs_cht"

        app.gui.setvar(group, "build_quadtree_grid", True)
        app.gui.setvar(group, "use_snapwave", False)

        # Domain
        app.gui.setvar(group, "x0", 0.0)
        app.gui.setvar(group, "y0", 0.0)
        app.gui.setvar(group, "nmax", 0)
        app.gui.setvar(group, "mmax", 0)
        app.gui.setvar(group, "dx", 0.1)
        app.gui.setvar(group, "dy", 0.1)
        app.gui.setvar(group, "rotation", 0.0)

        # Bathymetry
        source_names, sources = bathymetry_database.sources()
        app.gui.setvar(group, "bathymetry_source_names", source_names)
        app.gui.setvar(group, "active_bathymetry_source", source_names[0])
        dataset_names, dataset_long_names, dataset_source_names = bathymetry_database.dataset_names(source=source_names[0])
        app.gui.setvar(group, "bathymetry_dataset_names", dataset_names)
        app.gui.setvar(group, "bathymetry_dataset_index", 0)
        app.gui.setvar(group, "selected_bathymetry_dataset_names", [])
        app.gui.setvar(group, "selected_bathymetry_dataset_index", 0)
        app.gui.setvar(group, "selected_bathymetry_dataset_zmin", -99999.0)
        app.gui.setvar(group, "selected_bathymetry_dataset_zmax", 99999.0)
        app.gui.setvar(group, "nr_selected_bathymetry_datasets", 0)

        # Mask
        app.gui.setvar(group, "global_zmax",  10.0)
        app.gui.setvar(group, "global_zmin",  -10.0)
        app.gui.setvar(group, "include_polygon_names", [])
        app.gui.setvar(group, "include_polygon_index", 0)
        app.gui.setvar(group, "nr_include_polygons", 0)
        app.gui.setvar(group, "include_zmax",  99999.0)
        app.gui.setvar(group, "include_zmin", -99999.0)
        app.gui.setvar(group, "exclude_polygon_names", [])
        app.gui.setvar(group, "exclude_polygon_index", 0)
        app.gui.setvar(group, "nr_exclude_polygons", 0)
        app.gui.setvar(group, "exclude_zmax",  99999.0)
        app.gui.setvar(group, "exclude_zmin", -99999.0)

        app.gui.setvar(group, "open_boundary_polygon_names", [])
        app.gui.setvar(group, "open_boundary_polygon_index", 0)
        app.gui.setvar(group, "nr_open_boundary_polygons", 0)
        app.gui.setvar(group, "open_boundary_zmax",  99999.0)
        app.gui.setvar(group, "open_boundary_zmin", -99999.0)

        app.gui.setvar(group, "outflow_boundary_polygon_names", [])
        app.gui.setvar(group, "outflow_boundary_polygon_index", 0)
        app.gui.setvar(group, "nr_outflow_boundary_polygons", 0)
        app.gui.setvar(group, "outflow_boundary_zmax",  99999.0)
        app.gui.setvar(group, "outflow_boundary_zmin", -99999.0)


        app.gui.setvar(group, "global_zmax_snapwave",     -2.0)
        app.gui.setvar(group, "global_zmin_snapwave", -99999.0)
        app.gui.setvar(group, "include_polygon_names_snapwave", [])
        app.gui.setvar(group, "include_polygon_index_snapwave", 0)
        app.gui.setvar(group, "nr_include_polygons_snapwave", 0)
        app.gui.setvar(group, "include_zmax_snapwave",  99999.0)
        app.gui.setvar(group, "include_zmin_snapwave", -99999.0)
        app.gui.setvar(group, "exclude_polygon_names_snapwave", [])
        app.gui.setvar(group, "exclude_polygon_index_snapwave", 0)
        app.gui.setvar(group, "nr_exclude_polygons_snapwave", 0)
        app.gui.setvar(group, "exclude_zmax_snapwave",  99999.0)
        app.gui.setvar(group, "exclude_zmin_snapwave", -99999.0)


        # Refinement
        app.gui.setvar(group, "refinement_polygon_names", [])
        app.gui.setvar(group, "refinement_polygon_index", 0)
        app.gui.setvar(group, "refinement_polygon_level", 0)
        app.gui.setvar(group, "nr_refinement_polygons", 0)
        # Strings for refinement levels
        levstr = []
        for i in range(10):
            levstr.append(str(i))
        app.gui.setvar("modelmaker_sfincs_cht", "refinement_polygon_levels", levstr)    

        # Subgrid
        app.gui.setvar(group, "subgrid_nr_bins", 10)
        app.gui.setvar(group, "subgrid_nr_pixels", 20)
        app.gui.setvar(group, "subgrid_max_dzdv", 5.0)
        app.gui.setvar(group, "subgrid_manning_max", 0.024)
        app.gui.setvar(group, "subgrid_manning_z_cutoff", 0.024)
        app.gui.setvar(group, "subgrid_zmin", -99999.0)

#        app.gui.setvar(group, "refinement_polygons", 0)


        # Boundary points
        app.gui.setvar(group, "boundary_dx", 50000.0)

    def set_layer_mode(self, mode):
        if mode == "inactive":
            # Make all layers invisible
            app.map.layer["modelmaker_sfincs_cht"].set_mode("invisible")
        if mode == "invisible":
            app.map.layer["modelmaker_sfincs_cht"].set_mode("invisible")

    def add_layers(self):
        # Add Mapbox layers
        layer = app.map.add_layer("modelmaker_sfincs_cht")

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
        from .mask_active_cells import include_polygon_created
        from .mask_active_cells import include_polygon_modified
        from .mask_active_cells import include_polygon_selected
        layer.add_layer("include_polygon", type="draw",
                             shape="polygon",
                             create=include_polygon_created,
                             modify=include_polygon_modified,
                             select=include_polygon_selected,
                             polygon_line_color="limegreen",
                             polygon_fill_color="limegreen",
                             polygon_fill_opacity=0.3)
        # Exclude
        from .mask_active_cells import exclude_polygon_created
        from .mask_active_cells import exclude_polygon_modified
        from .mask_active_cells import exclude_polygon_selected
        layer.add_layer("exclude_polygon", type="draw",
                             shape="polygon",
                             create=exclude_polygon_created,
                             modify=exclude_polygon_modified,
                             select=exclude_polygon_selected,
                             polygon_line_color="orangered",
                             polygon_fill_color="orangered",
                             polygon_fill_opacity=0.3)
        # Boundary
        from .mask_boundary_cells import open_boundary_polygon_created
        from .mask_boundary_cells import open_boundary_polygon_modified
        from .mask_boundary_cells import open_boundary_polygon_selected
        layer.add_layer("open_boundary_polygon", type="draw",
                             shape="polygon",
                             create=open_boundary_polygon_created,
                             modify=open_boundary_polygon_modified,
                             select=open_boundary_polygon_selected,
                             polygon_line_color="deepskyblue",
                             polygon_fill_color="deepskyblue",
                             polygon_fill_opacity=0.3)

        # Outflow boundary
        from .mask_boundary_cells import outflow_boundary_polygon_created
        from .mask_boundary_cells import outflow_boundary_polygon_modified
        from .mask_boundary_cells import outflow_boundary_polygon_selected
        layer.add_layer("outflow_boundary_polygon", type="draw",
                             shape="polygon",
                             create=outflow_boundary_polygon_created,
                             modify=outflow_boundary_polygon_modified,
                             select=outflow_boundary_polygon_selected,
                             polygon_line_color="red",
                             polygon_fill_color="orange",
                             polygon_fill_opacity=0.3)

        ### Mask SnapWave
        # Include
        from .mask_active_cells_snapwave import include_polygon_created_snapwave
        from .mask_active_cells_snapwave import include_polygon_modified_snapwave
        from .mask_active_cells_snapwave import include_polygon_selected_snapwave
        layer.add_layer("include_polygon_snapwave", type="draw",
                             shape="polygon",
                             create=include_polygon_created_snapwave,
                             modify=include_polygon_modified_snapwave,
                             select=include_polygon_selected_snapwave,
                             polygon_line_color="limegreen",
                             polygon_fill_color="limegreen",
                             polygon_fill_opacity=0.3)
        # Exclude
        from .mask_active_cells_snapwave import exclude_polygon_created_snapwave
        from .mask_active_cells_snapwave import exclude_polygon_modified_snapwave
        from .mask_active_cells_snapwave import exclude_polygon_selected_snapwave
        layer.add_layer("exclude_polygon_snapwave", type="draw",
                             shape="polygon",
                             create=exclude_polygon_created_snapwave,
                             modify=exclude_polygon_modified_snapwave,
                             select=exclude_polygon_selected_snapwave,
                             polygon_line_color="orangered",
                             polygon_fill_color="orangered",
                             polygon_fill_opacity=0.3)

        # Refinement polygons
        from .quadtree import refinement_polygon_created
        from .quadtree import refinement_polygon_modified
        from .quadtree import refinement_polygon_selected
        layer.add_layer("quadtree_refinement", type="draw",
                             shape="polygon",
                             create=refinement_polygon_created,
                             modify=refinement_polygon_modified,
                             select=refinement_polygon_selected,
                             polygon_line_color="red",
                             polygon_fill_color="orange",
                             polygon_fill_opacity=0.3)


    def generate_grid(self):

        group = "modelmaker_sfincs_cht"

        dlg = app.gui.window.dialog_wait("Generating grid ...")

        model = app.model["sfincs_cht"].domain

        x0       = app.gui.getvar(group, "x0")
        y0       = app.gui.getvar(group, "y0")
        dx       = app.gui.getvar(group, "dx")
        dy       = app.gui.getvar(group, "dy")
        nmax     = app.gui.getvar(group, "nmax")
        mmax     = app.gui.getvar(group, "mmax")
        rotation = app.gui.getvar(group, "rotation")

#        if app.gui.getvar(group, "build_quadtree_grid"):

#            model.set_grid_type("quadtree")

        model.input.variables.qtrfile = "sfincs.qtr"
        app.gui.setvar(group, "qtrfile", model.input.variables.qtrfile)

        if len(self.refinement_polygon) == 0:
            refpol = None
            reflev = None
        else:
            # Make list of separate gdfs for each polygon
            refpol = gdf2list(self.refinement_polygon)
            reflev = []
            for ipol in range(app.gui.getvar(group, "nr_refinement_polygons")):
                reflev.append(self.refinement_levels[ipol] + 1) 

        model.grid.build(x0, y0, nmax, mmax, dx, dy, rotation, refinement_polygons=refpol, refinement_levels=reflev)
        model.grid.write()

        # else:

        #     model.set_grid_type("regular")

        #     model.input.variables.x0       = x0
        #     model.input.variables.y0       = y0
        #     model.input.variables.dx       = dx
        #     model.input.variables.dy       = dy
        #     model.input.variables.nmax     = nmax
        #     model.input.variables.mmax     = mmax
        #     model.input.variables.rotation = rotation

        #     group = "sfincs_cht"
        #     app.gui.setvar(group, "x0", model.input.variables.x0)
        #     app.gui.setvar(group, "y0", model.input.variables.y0)
        #     app.gui.setvar(group, "dx", model.input.variables.dx)
        #     app.gui.setvar(group, "dy", model.input.variables.dy)
        #     app.gui.setvar(group, "nmax", model.input.variables.nmax)
        #     app.gui.setvar(group, "mmax", model.input.variables.mmax)
        #     app.gui.setvar(group, "rotation", model.input.variables.rotation)

        #     model.grid.build()

        # Clear mask from map
        app.map.layer["sfincs_cht"].layer["mask_include"].clear()
        app.map.layer["sfincs_cht"].layer["mask_open_boundary"].clear()
        app.map.layer["sfincs_cht"].layer["mask_outflow_boundary"].clear()

        app.map.layer["sfincs_cht"].layer["grid"].set_data(model.grid, 
                                                          xlim=[app.gui.getvar(group, "x0"),
                                                                app.gui.getvar(group, "x0")],                                                                
                                                          ylim=[app.gui.getvar(group, "y0"),
                                                                 app.gui.getvar(group, "y0")])

        dlg.close()

    def generate_bathymetry(self):
        dlg = app.gui.window.dialog_wait("Generating bathymetry ...")
        bathymetry_list = app.toolbox["modelmaker_sfincs_cht"].selected_bathymetry_datasets
        # if not app.model["sfincs_cht"].domain.input.variables.depfile:
        #     app.model["sfincs_cht"].domain.input.variables.depfile = "sfincs.dep"
        app.model["sfincs_cht"].domain.grid.set_bathymetry(bathymetry_list)
        # if app.model["sfincs_cht"].domain.grid_type == "regular":
        #     app.model["sfincs_cht"].domain.grid.write_dep_file()
        #     app.gui.setvar("sfincs_cht", "depfile", app.model["sfincs_cht"].domain.input.variables.depfile)
        # else:
        app.model["sfincs_cht"].domain.grid.write()
        dlg.close()

    def update_mask(self):

        # Should improve on this check
        grid = app.model["sfincs_cht"].domain.grid
        mask = app.model["sfincs_cht"].domain.mask
        z    = app.model["sfincs_cht"].domain.grid.data["z"]
        if np.all(np.isnan(z)):
            app.gui.window.dialog_warning("Please first generate a bathymetry !")
            return

        dlg = app.gui.window.dialog_wait("Updating mask ...")

        mask.build(zmin=app.gui.getvar("modelmaker_sfincs_cht", "global_zmin"),
                   zmax=app.gui.getvar("modelmaker_sfincs_cht", "global_zmax"),
                   include_polygon=app.toolbox["modelmaker_sfincs_cht"].include_polygon,
                   include_zmin=app.gui.getvar("modelmaker_sfincs_cht", "include_zmin"),
                   include_zmax=app.gui.getvar("modelmaker_sfincs_cht", "include_zmax"),
                   exclude_polygon=app.toolbox["modelmaker_sfincs_cht"].exclude_polygon,
                   exclude_zmin=app.gui.getvar("modelmaker_sfincs_cht", "exclude_zmin"),
                   exclude_zmax=app.gui.getvar("modelmaker_sfincs_cht", "exclude_zmax"),
                   open_boundary_polygon=app.toolbox["modelmaker_sfincs_cht"].open_boundary_polygon,
                   open_boundary_zmin=app.gui.getvar("modelmaker_sfincs_cht", "open_boundary_zmin"),
                   open_boundary_zmax=app.gui.getvar("modelmaker_sfincs_cht", "open_boundary_zmax"),
                   outflow_boundary_polygon=app.toolbox["modelmaker_sfincs_cht"].outflow_boundary_polygon,
                   outflow_boundary_zmin=app.gui.getvar("modelmaker_sfincs_cht", "outflow_boundary_zmin"),
                   outflow_boundary_zmax=app.gui.getvar("modelmaker_sfincs_cht", "outflow_boundary_zmax")
                   )
        app.map.layer["sfincs_cht"].layer["mask_include"].set_data(mask.to_gdf(option="include"))
        app.map.layer["sfincs_cht"].layer["mask_open_boundary"].set_data(mask.to_gdf(option="open"))
        app.map.layer["sfincs_cht"].layer["mask_outflow_boundary"].set_data(mask.to_gdf(option="outflow"))
        # if not app.model["sfincs_cht"].domain.input.variables.mskfile:
        #     app.model["sfincs_cht"].domain.input.variables.mskfile = "sfincs.msk"
        grid.write()
        # # GUI variables
        # app.gui.setvar("sfincs_cht", "mskfile", app.model["sfincs_cht"].domain.input.variables.mskfile)

        dlg.close()

    def update_mask_snapwave(self):

        grid = app.model["sfincs_cht"].domain.grid
        mask = app.model["sfincs_cht"].domain.snapwave.mask
        if np.all(np.isnan(grid.data["z"])):
            app.gui.window.dialog_warning("Please first generate a bathymetry !")
            return

        dlg = app.gui.window.dialog_wait("Updating SnapWave mask ...")

        mask.build(zmin=app.gui.getvar("modelmaker_sfincs_cht", "global_zmin_snapwave"),
                   zmax=app.gui.getvar("modelmaker_sfincs_cht", "global_zmax_snapwave"),
                   include_polygon=app.toolbox["modelmaker_sfincs_cht"].include_polygon_snapwave,
                   include_zmin=app.gui.getvar("modelmaker_sfincs_cht", "include_zmin_snapwave"),
                   include_zmax=app.gui.getvar("modelmaker_sfincs_cht", "include_zmax_snapwave"),
                   exclude_polygon=app.toolbox["modelmaker_sfincs_cht"].exclude_polygon_snapwave,
                   exclude_zmin=app.gui.getvar("modelmaker_sfincs_cht", "exclude_zmin_snapwave"),
                   exclude_zmax=app.gui.getvar("modelmaker_sfincs_cht", "exclude_zmax_snapwave")
                   )
        app.map.layer["sfincs_cht"].layer["mask_include_snapwave"].set_data(mask.to_gdf(option="include"))
        if not app.model["sfincs_cht"].domain.input.variables.snapwave_mskfile:
            app.model["sfincs_cht"].domain.input.variables.snapwave_mskfile = "snapwave.msk"
        grid.write()
        # GUI variables
        app.gui.setvar("sfincs_cht", "snapwave_mskfile", app.model["sfincs_cht"].domain.input.variables.snapwave_mskfile)

        dlg.close()

    def generate_subgrid(self):
        group = "modelmaker_sfincs_cht"
        bathymetry_sets = app.toolbox["modelmaker_sfincs_cht"].selected_bathymetry_datasets
        roughness_sets = []
        nr_bins = app.gui.getvar(group, "subgrid_nr_bins")
        nr_pixels = app.gui.getvar(group, "subgrid_nr_pixels")
        max_dzdv = app.gui.getvar(group, "subgrid_max_dzdv")
        manning_max = app.gui.getvar(group, "subgrid_manning_max")
        manning_z_cutoff = app.gui.getvar(group, "subgrid_manning_z_cutoff")
        zmin = app.gui.getvar(group, "subgrid_zmin")
        p = app.gui.window.dialog_progress("               Generating Sub-grid Tables ...                ", 100)
        app.model["sfincs_cht"].domain.subgrid.build(bathymetry_sets,
                                                     roughness_sets,
                                                     nr_bins=nr_bins,
                                                     nr_subgrid_pixels=nr_pixels,
                                                     max_gradient=max_dzdv,
                                                     zmin=zmin,
                                                     progress_bar=p)
        app.model["sfincs_cht"].domain.input.variables.sbgfile = "sfincs.sbg"
        app.gui.setvar("sfincs_cht", "sbgfile", app.model["sfincs_cht"].domain.input.variables.sbgfile)
        app.gui.setvar("sfincs_cht", "bathymetry_type", "subgrid")
    # def create_boundary_points(self):

    #     dlg = app.gui.window.dialog_wait("Making boundary points ...")

    #     # First check if there are already boundary points
    #     if len(app.model["sfincs_cht"].domain.boundary_conditions.gdf.index)>0:
    #         ok = app.gui.window.dialog_ok_cancel("Existing boundary points will be overwritten! Continue?",                                
    #                                    title="Warning")
    #         if not ok:
    #             return
    #     # Create points from mask
    #     bnd_dist = app.gui.getvar("modelmaker_sfincs_cht", "boundary_dx")
    #     app.model["sfincs_cht"].domain.boundary_conditions.get_boundary_points_from_mask(bnd_dist=bnd_dist)
    #     # Drop time series (MapBox doesn't like it)
    #     gdf = app.model["sfincs_cht"].domain.boundary_conditions.gdf.drop(["timeseries"], axis=1)
    #     app.map.layer["sfincs_cht"].layer["boundary_points"].set_data(gdf, 0)
    #     # Save points to bnd file
    #     app.model["sfincs_cht"].domain.boundary_conditions.write_boundary_points()
    #     # Set all boundary conditions to constant values
    #     app.model["sfincs_cht"].domain.boundary_conditions.set_timeseries_uniform(1.0, 8.0, 45.0, 20.0)
    #     # Save points to bhs, etc. files
    #     app.model["sfincs_cht"].domain.boundary_conditions.write_boundary_conditions_timeseries()

    #     dlg.close()

    def build_model(self):
        self.generate_grid()
        self.generate_bathymetry()
        self.update_mask()
        self.generate_subgrid()

    def update_polygons(self):

        nrp = len(self.include_polygon)
        incnames = []
        for ip in range(nrp):
            incnames.append(str(ip + 1))
        app.gui.setvar("modelmaker_sfincs_cht", "nr_include_polygons", nrp)
        app.gui.setvar("modelmaker_sfincs_cht", "include_polygon_names", incnames)

        nrp = len(self.exclude_polygon)
        excnames = []
        for ip in range(nrp):
            excnames.append(str(ip + 1))
        app.gui.setvar("modelmaker_sfincs_cht", "nr_exclude_polygons", nrp)
        app.gui.setvar("modelmaker_sfincs_cht", "exclude_polygon_names", excnames)

        nrp = len(self.open_boundary_polygon)
        bndnames = []
        for ip in range(nrp):
            bndnames.append(str(ip + 1))
        app.gui.setvar("modelmaker_sfincs_cht", "nr_open_boundary_polygons", nrp)
        app.gui.setvar("modelmaker_sfincs_cht", "open_boundary_polygon_names", bndnames)

        nrp = len(self.outflow_boundary_polygon)
        bndnames = []
        for ip in range(nrp):
            bndnames.append(str(ip + 1))
        app.gui.setvar("modelmaker_sfincs_cht", "nr_outflow_boundary_polygons", nrp)
        app.gui.setvar("modelmaker_sfincs_cht", "outflow_boundary_polygon_names", bndnames)

        nrp = len(self.include_polygon_snapwave)
        incnames = []
        for ip in range(nrp):
            incnames.append(str(ip + 1))
        app.gui.setvar("modelmaker_sfincs_cht", "nr_include_polygons_snapwave", nrp)
        app.gui.setvar("modelmaker_sfincs_cht", "include_polygon_names_snapwave", incnames)

        nrp = len(self.exclude_polygon_snapwave)
        excnames = []
        for ip in range(nrp):
            excnames.append(str(ip + 1))
        app.gui.setvar("modelmaker_sfincs_cht", "nr_exclude_polygons_snapwave", nrp)
        app.gui.setvar("modelmaker_sfincs_cht", "exclude_polygon_names_snapwave", excnames)

        # app.toolbox["modelmaker_sfincs_cht"].write_include_polygon()
        # app.toolbox["modelmaker_sfincs_cht"].write_exclude_polygon()
        # app.toolbox["modelmaker_sfincs_cht"].write_boundary_polygon()

    def read_include_polygon(self):
        self.include_polygon = gpd.read_file(self.include_file_name)
        self.update_polygons()

    def read_exclude_polygon(self):
        self.exclude_polygon = gpd.read_file(self.exclude_file_name)
        self.update_polygons()

    def read_open_boundary_polygon(self):
        self.open_boundary_polygon = gpd.read_file(self.open_boundary_file_name)
        self.update_polygons()

    def read_outflow_boundary_polygon(self):
        self.outflow_boundary_polygon = gpd.read_file(self.outflow_boundary_file_name)
        self.update_polygons()

    def read_include_polygon_snapwave(self):
        self.include_polygon_snapwave = gpd.read_file(self.include_file_name_snapwave)
        self.update_polygons()

    def read_exclude_polygon_snapwave(self):
        self.exclude_polygon_snapwave = gpd.read_file(self.exclude_file_name_snapwave)
        self.update_polygons()


    def write_include_polygon(self):
        if len(self.include_polygon) == 0:
            return
        gdf = gpd.GeoDataFrame(geometry=self.include_polygon["geometry"])
        gdf.to_file(self.include_file_name, driver='GeoJSON')

    def write_exclude_polygon(self):
        if len(self.exclude_polygon) == 0:
            return
        gdf = gpd.GeoDataFrame(geometry=self.exclude_polygon["geometry"])
        gdf.to_file(self.exclude_file_name, driver='GeoJSON')

    def write_open_boundary_polygon(self):
        if len(self.open_boundary_polygon) == 0:
            return
        gdf = gpd.GeoDataFrame(geometry=self.open_boundary_polygon["geometry"])
        gdf.to_file(self.open_boundary_file_name, driver='GeoJSON')

    def write_outflow_boundary_polygon(self):
        if len(self.outflow_boundary_polygon) == 0:
            return
        gdf = gpd.GeoDataFrame(geometry=self.outflow_boundary_polygon["geometry"])
        gdf.to_file(self.outflow_boundary_file_name, driver='GeoJSON')

    def write_include_polygon_snapwave(self):
        if len(self.include_polygon_snapwave) == 0:
            return
        gdf = gpd.GeoDataFrame(geometry=self.include_polygon_snapwave["geometry"])
        gdf.to_file(self.include_file_name_snapwave, driver='GeoJSON')

    def write_exclude_polygon_snapwave(self):
        if len(self.exclude_polygon_snapwave) == 0:
            return
        gdf = gpd.GeoDataFrame(geometry=self.exclude_polygon_snapwave["geometry"])
        gdf.to_file(self.exclude_file_name_snapwave, driver='GeoJSON')



    def plot_include_polygon(self):
        layer = app.map.layer["modelmaker_sfincs_cht"].layer["include_polygon"]
        layer.clear()
        layer.add_feature(self.include_polygon)

    def plot_exclude_polygon(self):
        layer = app.map.layer["modelmaker_sfincs_cht"].layer["exclude_polygon"]
        layer.clear()
        layer.add_feature(self.exclude_polygon)

    def plot_open_boundary_polygon(self):
        layer = app.map.layer["modelmaker_sfincs_cht"].layer["open_boundary_polygon"]
        layer.clear()
        layer.add_feature(self.open_boundary_polygon)

    def plot_outflow_boundary_polygon(self):
        layer = app.map.layer["modelmaker_sfincs_cht"].layer["outflow_boundary_polygon"]
        layer.clear()
        layer.add_feature(self.outflow_boundary_polygon)

    def plot_include_polygon_snapwave(self):
        layer = app.map.layer["modelmaker_sfincs_cht"].layer["include_polygon_snapwave"]
        layer.clear()
        layer.add_feature(self.include_polygon_snapwave)

    def plot_exclude_polygon_snapwave(self):
        layer = app.map.layer["modelmaker_sfincs_cht"].layer["exclude_polygon_snapwave"]
        layer.clear()
        layer.add_feature(self.exclude_polygon_snapwave)


    def read_setup_yaml(self, file_name):

        dct = yaml2dict(file_name)
        self.setup_dict = dct

        group = "modelmaker_sfincs_cht"
        # Coordinates
        app.gui.setvar(group, "x0", dct["coordinates"]["x0"])
        app.gui.setvar(group, "y0", dct["coordinates"]["y0"])
        app.gui.setvar(group, "dx", dct["coordinates"]["dx"])
        app.gui.setvar(group, "dy", dct["coordinates"]["dy"])
        app.gui.setvar(group, "nmax", dct["coordinates"]["nmax"])
        app.gui.setvar(group, "mmax", dct["coordinates"]["mmax"])
        app.gui.setvar(group, "rotation", dct["coordinates"]["rotation"])
        app.model["sfincs_cht"].domain.crs = CRS(dct["coordinates"]["crs"])
        # Mask
        app.gui.setvar(group, "global_zmin", dct["mask"]["zmin"])
        app.gui.setvar(group, "global_zmax", dct["mask"]["zmax"])

        if len(dct["mask"]["include_polygon"])>0:
            self.include_file_name = dct["mask"]["include_polygon"][0]["file_name"]
            app.gui.setvar(group, "include_zmin", dct["mask"]["include_polygon"][0]["zmin"])
            app.gui.setvar(group, "include_zmax", dct["mask"]["include_polygon"][0]["zmax"])
            # Now read in polygons from geojson file (or other file)
            self.read_include_polygon()
            self.plot_include_polygon()
        else:
            self.include_polygon = gpd.GeoDataFrame()    

        if len(dct["mask"]["exclude_polygon"])>0:
            self.exclude_file_name = dct["mask"]["exclude_polygon"][0]["file_name"]
            app.gui.setvar(group, "exclude_zmin", dct["mask"]["exclude_polygon"][0]["zmin"])
            app.gui.setvar(group, "exclude_zmax", dct["mask"]["exclude_polygon"][0]["zmax"])
            # Now read in polygons from geojson file (or other file)
            self.read_exclude_polygon()
            self.plot_exclude_polygon()
        else:
            self.exclude_polygon = gpd.GeoDataFrame()    

        if len(dct["mask"]["open_boundary_polygon"])>0:
            self.boundary_file_name = dct["mask"]["open_boundary_polygon"][0]["file_name"]
            app.gui.setvar(group, "boundary_zmin", dct["mask"]["open_boundary_polygon"][0]["zmin"])
            app.gui.setvar(group, "boundary_zmax", dct["mask"]["open_boundary_polygon"][0]["zmax"])
            # Now read in polygons from geojson file (or other file)
            self.read_boundary_polygon()
            self.plot_boundary_polygon()
        else:
            self.boundary_polygon = gpd.GeoDataFrame()    

        if len(dct["mask"]["outflow_boundary_polygon"])>0:
            self.boundary_file_name = dct["mask"]["outflow_boundary_polygon"][0]["file_name"]
            app.gui.setvar(group, "outflow_boundary_zmin", dct["mask"]["outflow_boundary_polygon"][0]["zmin"])
            app.gui.setvar(group, "outflow_boundary_zmax", dct["mask"]["outflow_boundary_polygon"][0]["zmax"])
            # Now read in polygons from geojson file (or other file)
            self.read_outflow_boundary_polygon()
            self.plot_outflow_boundary_polygon()
        else:
            self.outflow_boundary_polygon = gpd.GeoDataFrame()    

        # Bathymetry
        dataset_names = []
        self.selected_bathymetry_datasets = []
        for ddict in dct["bathymetry"]["dataset"]:
            name = ddict["name"]
            zmin = ddict["zmin"]
            zmax = ddict["zmax"] 
            d = bathymetry_database.get_dataset(name)
            dataset = {"dataset": d, "zmin": zmin, "zmax": zmax}
            app.toolbox["modelmaker_sfincs_cht"].selected_bathymetry_datasets.append(dataset)
            dataset_names.append(name)
        app.gui.setvar("modelmaker_sfincs_cht", "selected_bathymetry_dataset_names", dataset_names)
        app.gui.setvar("modelmaker_sfincs_cht", "selected_bathymetry_dataset_index", 0)

        self.update_polygons()

        layer = app.map.layer["modelmaker_sfincs_cht"].layer["grid_outline"]
        lenx = dct["coordinates"]["mmax"] * dct["coordinates"]["dx"]
        leny = dct["coordinates"]["nmax"] * dct["coordinates"]["dy"]
        layer.add_rectangle(dct["coordinates"]["x0"],
                            dct["coordinates"]["y0"],
                            lenx, leny,
                            dct["coordinates"]["rotation"])


    def write_setup_yaml(self):
        group = "modelmaker_sfincs_cht"
        dct = {}
        # Coordinates
        dct["coordinates"] = {}
        dct["coordinates"]["x0"] = float(app.gui.getvar(group, "x0"))
        dct["coordinates"]["y0"] = float(app.gui.getvar(group, "y0"))
        dct["coordinates"]["dx"] = float(app.gui.getvar(group, "dx"))
        dct["coordinates"]["dy"] = float(app.gui.getvar(group, "dy"))
        dct["coordinates"]["nmax"] = int(app.gui.getvar(group, "nmax"))
        dct["coordinates"]["mmax"] = int(app.gui.getvar(group, "mmax"))
        dct["coordinates"]["rotation"] = float(app.gui.getvar(group, "rotation"))
        dct["coordinates"]["crs"] = app.model["sfincs_cht"].domain.crs.name
        # Mask
        dct["mask"] = {}
        dct["mask"]["zmin"] = app.gui.getvar(group, "global_zmin")
        dct["mask"]["zmax"] = app.gui.getvar(group, "global_zmax")
        dct["mask"]["include_polygon"] = []
        if len(app.toolbox["modelmaker_sfincs_cht"].include_polygon)>0:
            pol = {}
            pol["file_name"] = self.include_file_name
            pol["zmin"] = app.gui.getvar("modelmaker_sfincs_cht", "include_zmin")
            pol["zmax"] = app.gui.getvar("modelmaker_sfincs_cht", "include_zmax")
            dct["mask"]["include_polygon"].append(pol)
        dct["mask"]["exclude_polygon"] = []
        if len(app.toolbox["modelmaker_sfincs_cht"].exclude_polygon)>0:
            pol = {}
            pol["file_name"] = self.exclude_file_name
            pol["zmin"] = app.gui.getvar("modelmaker_sfincs_cht", "exclude_zmin")
            pol["zmax"] = app.gui.getvar("modelmaker_sfincs_cht", "exclude_zmax")
            dct["mask"]["exclude_polygon"].append(pol)
        dct["mask"]["open_boundary_polygon"] = []
        if len(app.toolbox["modelmaker_sfincs_cht"].open_boundary_polygon)>0:
            pol = {}
            pol["file_name"] = self.open_boundary_file_name
            pol["zmin"] = app.gui.getvar("modelmaker_sfincs_cht", "open_boundary_zmin")
            pol["zmax"] = app.gui.getvar("modelmaker_sfincs_cht", "open_boundary_zmax")
            dct["mask"]["open_boundary_polygon"].append(pol)
        dct["mask"]["outflow_boundary_polygon"] = []
        if len(app.toolbox["modelmaker_sfincs_cht"].outflow_boundary_polygon)>0:
            pol = {}
            pol["file_name"] = self.outflow_boundary_file_name
            pol["zmin"] = app.gui.getvar("modelmaker_sfincs_cht", "outflow_boundary_zmin")
            pol["zmax"] = app.gui.getvar("modelmaker_sfincs_cht", "outflow_boundary_zmax")
            dct["mask"]["outflow_boundary_polygon"].append(pol)
        # Bathymetry
        dct["bathymetry"] = {}
        dct["bathymetry"]["dataset"] = []
        dataset = {}
        for d in app.toolbox["modelmaker_sfincs_cht"].selected_bathymetry_datasets:
            dataset["name"]   = d["dataset"].name
            dataset["source"] = "delftdashboard"
            dataset["zmin"]   = d["zmin"]
            dataset["zmax"]   = d["zmax"]
        dct["bathymetry"]["dataset"].append(dataset)    

        self.setup_dict = dct

        dict2yaml("model_setup.yml", dct)

def gdf2list(gdf_in):
   gdf_out = []
   for feature in gdf_in.iterfeatures():
      gdf_out.append(gpd.GeoDataFrame.from_features([feature]))
   return gdf_out
