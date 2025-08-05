# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
import pandas as pd
import geopandas as gpd
from pyproj import CRS

from delftdashboard.operations.toolbox import GenericToolbox
from delftdashboard.app import app

# from cht_bathymetry.bathymetry_database import bathymetry_database
from cht_utils.misc_tools import dict2yaml
from cht_utils.misc_tools import yaml2dict

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
        self.include_polygon = gpd.GeoDataFrame()
        self.include_file_name = "include.geojson"
        # Exclude polygons
        self.exclude_polygon = gpd.GeoDataFrame()
        self.exclude_file_name = "exclude.geojson"
        # Boundary polygons
        self.boundary_polygon = gpd.GeoDataFrame()
        self.boundary_file_name = "boundary.geojson"
        # Refinement
        self.refinement_levels = []
        self.refinement_zmin = []
        self.refinement_zmax = []
        self.refinement_polygon = gpd.GeoDataFrame()

        self.setup_dict = {}

        # Set GUI variable
        group = "modelmaker_hurrywave"

        app.gui.setvar(group, "use_waveblocking", True)

        # Domain
        app.gui.setvar(group, "x0", 0.0)
        app.gui.setvar(group, "y0", 0.0)
        app.gui.setvar(group, "nmax", 0)
        app.gui.setvar(group, "mmax", 0)
        app.gui.setvar(group, "dx", 0.1)
        app.gui.setvar(group, "dy", 0.1)
        app.gui.setvar(group, "rotation", 0.0)

        # Refinement
        app.gui.setvar(group, "refinement_polygon_file", "quadtree.geojson")
        app.gui.setvar(group, "refinement_polygon_names", [])
        app.gui.setvar(group, "refinement_polygon_index", 0)
        app.gui.setvar(group, "refinement_polygon_level", 0)
        app.gui.setvar(group, "refinement_polygon_zmin", -99999.0)
        app.gui.setvar(group, "refinement_polygon_zmax", 99999.0)
        app.gui.setvar(group, "nr_refinement_polygons", 0)
        # Strings for refinement levels
        levstr = []
        for i in range(10):
            levstr.append(str(i))
        app.gui.setvar("modelmaker_hurrywave", "refinement_polygon_levels", levstr)    

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

        # Mask
        app.gui.setvar(group, "global_zmax",     -2.0)
        app.gui.setvar(group, "global_zmin", -99999.0)
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
        app.gui.setvar(group, "boundary_polygon_names", [])
        app.gui.setvar(group, "boundary_polygon_index", 0)
        app.gui.setvar(group, "nr_boundary_polygons", 0)
        app.gui.setvar(group, "boundary_zmax",  99999.0)
        app.gui.setvar(group, "boundary_zmin", -99999.0)

        # Wave Blocking
        app.gui.setvar(group, "waveblocking_nr_dirs", 36)
        app.gui.setvar(group, "waveblocking_nr_pixels", 20)
        app.gui.setvar(group, "waveblocking_threshold_level", -5.0)

    def set_layer_mode(self, mode):
        if mode == "inactive":
            # Make all layers invisible
            app.map.layer["modelmaker_hurrywave"].hide()
        if mode == "invisible":
            app.map.layer["modelmaker_hurrywave"].hide()

    def add_layers(self):
        # Add Mapbox layers
        layer = app.map.add_layer("modelmaker_hurrywave")

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

        # Refinement polygons
        from .quadtree import refinement_polygon_created
        from .quadtree import refinement_polygon_modified
        from .quadtree import refinement_polygon_selected
        layer.add_layer("quadtree_refinement", type="draw",
                        columns={"refinement_level": 1, "zmin": -99999.0, "zmax": 99999.0},
                        shape="polygon",
                        create=refinement_polygon_created,
                        modify=refinement_polygon_modified,
                        select=refinement_polygon_selected,
                        polygon_line_color="red",
                        polygon_fill_color="orange",
                        polygon_fill_opacity=0.1)

        ### Mask
        # Include
        from .mask_active_cells import include_polygon_created
        from .mask_active_cells import include_polygon_modified
        from .mask_active_cells import include_polygon_selected
        layer.add_layer("mask_include", type="draw",
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
        layer.add_layer("mask_exclude", type="draw",
                             shape="polygon",
                             create=exclude_polygon_created,
                             modify=exclude_polygon_modified,
                             select=exclude_polygon_selected,
                             polygon_line_color="orangered",
                             polygon_fill_color="orangered",
                             polygon_fill_opacity=0.3)
        # Boundary
        from .mask_boundary_cells import boundary_polygon_created
        from .mask_boundary_cells import boundary_polygon_modified
        from .mask_boundary_cells import boundary_polygon_selected
        layer.add_layer("mask_boundary", type="draw",
                             shape="polygon",
                             create=boundary_polygon_created,
                             modify=boundary_polygon_modified,
                             select=boundary_polygon_selected,
                             polygon_line_color="deepskyblue",
                             polygon_fill_color="deepskyblue",
                             polygon_fill_opacity=0.3)

    def generate_grid(self):

        model = app.model["hurrywave"].domain

        # Check if there is already a grid. If so, ask if it should be overwritten.

        if model.input.variables.nmax > 0:
            ok = app.gui.window.dialog_ok_cancel("Existing model grid and spatial attributes will be deleted! Continue?",
                                       title="Warning")
            if not ok:
                return

        # Clear all spatial attributes (grid, mask, boundaries, etc.)
        app.model["hurrywave"].clear_spatial_attributes()

        dlg = app.gui.window.dialog_wait("Generating grid ...")

        # Get bbox coords from toolbox, and set them in the model input variables (do we actually need them for the model when using quadtree?)
        group = "modelmaker_hurrywave"
        model.input.variables.x0       = app.gui.getvar(group, "x0")
        model.input.variables.y0       = app.gui.getvar(group, "y0")
        model.input.variables.dx       = app.gui.getvar(group, "dx")
        model.input.variables.dy       = app.gui.getvar(group, "dy")
        model.input.variables.nmax     = app.gui.getvar(group, "nmax")
        model.input.variables.mmax     = app.gui.getvar(group, "mmax")
        model.input.variables.rotation = app.gui.getvar(group, "rotation")
               
        app.model["hurrywave"].set_gui_variables()
        # group = "hurrywave"
        # app.gui.setvar(group, "x0", model.input.variables.x0)
        # app.gui.setvar(group, "y0", model.input.variables.y0)
        # app.gui.setvar(group, "dx", model.input.variables.dx)
        # app.gui.setvar(group, "dy", model.input.variables.dy)
        # app.gui.setvar(group, "nmax", model.input.variables.nmax)
        # app.gui.setvar(group, "mmax", model.input.variables.mmax)
        # app.gui.setvar(group, "rotation", model.input.variables.rotation)

        x0 = model.input.variables.x0
        y0 = model.input.variables.y0
        dx = model.input.variables.dx
        dy = model.input.variables.dy
        nmax = model.input.variables.nmax
        mmax = model.input.variables.mmax
        rotation = model.input.variables.rotation

        if len(self.refinement_polygon) == 0:
            refpol = None
        else:
            # Make list of separate gdfs for each polygon
            refpol = self.refinement_polygon

        model.grid.build(x0, y0, nmax, mmax, dx, dy, rotation,
                         refinement_polygons=refpol,
                         bathymetry_sets=app.selected_bathymetry_datasets,
                         bathymetry_database=app.bathymetry_database)

        app.model["hurrywave"].domain.grid.write()

        app.map.layer["hurrywave"].layer["grid"].set_data(model.grid)

        dlg.close()

    def generate_bathymetry(self):
        dlg = app.gui.window.dialog_wait("Generating bathymetry ...")
        app.model["hurrywave"].domain.grid.set_bathymetry(app.selected_bathymetry_datasets,
                                                          bathymetry_database=app.bathymetry_database)
        app.model["hurrywave"].domain.grid.write()
        dlg.close()

    def update_mask(self):

        dlg = app.gui.window.dialog_wait("Updating mask ...")

        grid = app.model["hurrywave"].domain.grid
        mask = app.model["hurrywave"].domain.mask
        mask.build(zmin=app.gui.getvar("modelmaker_hurrywave", "global_zmin"),
                   zmax=app.gui.getvar("modelmaker_hurrywave", "global_zmax"),
                   include_polygon=app.toolbox["modelmaker_hurrywave"].include_polygon,
                   include_zmin=app.gui.getvar("modelmaker_hurrywave", "include_zmin"),
                   include_zmax=app.gui.getvar("modelmaker_hurrywave", "include_zmax"),
                   exclude_polygon=app.toolbox["modelmaker_hurrywave"].exclude_polygon,
                   exclude_zmin=app.gui.getvar("modelmaker_hurrywave", "exclude_zmin"),
                   exclude_zmax=app.gui.getvar("modelmaker_hurrywave", "exclude_zmax"),
                   boundary_polygon=app.toolbox["modelmaker_hurrywave"].boundary_polygon,
                   boundary_zmin=app.gui.getvar("modelmaker_hurrywave", "boundary_zmin"),
                   boundary_zmax=app.gui.getvar("modelmaker_hurrywave", "boundary_zmax"),
                   update_datashader_dataframe=True
                  )
        # app.map.layer["hurrywave"].layer["mask_include"].set_data(mask.to_gdf(option="include"))
        # app.map.layer["hurrywave"].layer["mask_boundary"].set_data(mask.to_gdf(option="boundary"))
        app.map.layer["hurrywave"].layer["mask"].set_data(mask)
        # app.map.layer["hurrywave"].layer["mask_boundary"].set_data(mask.to_gdf(option="boundary"))
        grid.write()
        # if not app.model["hurrywave"].domain.input.variables.mskfile:
        #     app.model["hurrywave"].domain.input.variables.mskfile = "hurrywave.msk"
        # grid.write_msk_file()
        # # GUI variables
        # app.gui.setvar("hurrywave", "mskfile", app.model["hurrywave"].domain.input.variables.mskfile)

        dlg.close()

    def cut_inactive_cells(self):
        dlg = app.gui.window.dialog_wait("Cutting Inactive Cells ...")
        app.model["hurrywave"].domain.grid.cut_inactive_cells()
        app.model["hurrywave"].domain.grid.write()
        # Replot everything
        app.model["hurrywave"].plot()
        dlg.close()

    def generate_waveblocking(self):
        """Generate wave blocking file"""
        group = "modelmaker_hurrywave"
        filename = app.model["hurrywave"].domain.input.variables.wblfile
        if not filename:
            filename = "hurrywave.wbl"
        rsp = app.gui.window.dialog_save_file("Select file ...",
                                            file_name=filename,
                                            filter="*.wbl",
                                            allow_directory_change=False)
        if rsp[0]:
            filename = rsp[2] # file name without path
        else:
            return
        bathymetry_sets = app.toolbox["modelmaker_hurrywave"].selected_bathymetry_datasets
        # Set ndirs same as in hurrywave model
        # nr_dirs = app.gui.getvar(group, "waveblocking_nr_directions")
        nr_dirs = app.model["hurrywave"].domain.input.variables.ntheta
        nr_pixels = app.gui.getvar(group, "waveblocking_nr_pixels")
        threshold_level = app.gui.getvar(group, "waveblocking_threshold_level")
        p = app.gui.window.dialog_progress("               Generating Wave blocking file ...                ", 100)
        ds_wbl = app.model["hurrywave"].domain.waveblocking.build(bathymetry_sets,
                                                                  bathymetry_database=app.bathymetry_database,
                                                                  nr_dirs=nr_dirs,
                                                                  nr_subgrid_pixels=nr_pixels,
                                                                  threshold_level=threshold_level,
                                                                  quiet=False, 
                                                                  progress_bar=p)
        p.close()
        if ds_wbl:
            app.model["hurrywave"].domain.input.variables.wblfile = filename
            app.gui.setvar("hurrywave", "wblfile", filename)

    def build_model(self):
        self.generate_grid()
        self.generate_bathymetry()
        self.update_mask()
        self.generate_waveblocking()

    def update_polygons(self):

        nrp = len(self.include_polygon)
        incnames = []
        for ip in range(nrp):
            incnames.append(str(ip + 1))
        app.gui.setvar("modelmaker_hurrywave", "nr_include_polygons", nrp)
        app.gui.setvar("modelmaker_hurrywave", "include_polygon_names", incnames)

        nrp = len(self.exclude_polygon)
        excnames = []
        for ip in range(nrp):
            excnames.append(str(ip + 1))
        app.gui.setvar("modelmaker_hurrywave", "nr_exclude_polygons", nrp)
        app.gui.setvar("modelmaker_hurrywave", "exclude_polygon_names", excnames)

        nrp = len(self.boundary_polygon)
        bndnames = []
        for ip in range(nrp):
            bndnames.append(str(ip + 1))
        app.gui.setvar("modelmaker_hurrywave", "nr_boundary_polygons", nrp)
        app.gui.setvar("modelmaker_hurrywave", "boundary_polygon_names", bndnames)

        # app.toolbox["modelmaker_hurrywave"].write_include_polygon()
        # app.toolbox["modelmaker_hurrywave"].write_exclude_polygon()
        # app.toolbox["modelmaker_hurrywave"].write_boundary_polygon()

    def read_refinement_polygon(self, file_name, append):
        # Should we make this part of cht_hurrywave? Yes, but for now it is in the modelmaker_hurrywave toolbox.
        refinement_polygon = gpd.read_file(file_name).to_crs(app.crs)
        # Check if the file contains a column "refinement_level"
        if "refinement_level" not in refinement_polygon.columns:
            refinement_polygon["refinement_level"] = 1
        # Check if the file contains a column "zmin"
        if "zmin" not in refinement_polygon.columns:
            refinement_polygon["zmin"] = -99999.0
        # Check if the file contains a column "zmax"
        if "zmax" not in refinement_polygon.columns:
            refinement_polygon["zmax"] = 99999.0
        if append:
            self.refinement_polygon = gpd.GeoDataFrame(pd.concat([self.refinement_polygon, refinement_polygon], ignore_index=True))
        else:
            self.refinement_polygon = refinement_polygon

    def read_include_polygon(self):
        self.include_polygon = gpd.read_file(self.include_file_name)
        self.update_polygons()

    def read_exclude_polygon(self):
        self.exclude_polygon = gpd.read_file(self.exclude_file_name)
        self.update_polygons()

    def read_boundary_polygon(self):
        self.boundary_polygon = gpd.read_file(self.boundary_file_name)
        self.update_polygons()

    def write_refinement_polygon(self):
        if len(self.refinement_polygon) == 0:
            print("No refinement polygons defined")
            return
        # Drop the id column
        gdf = self.refinement_polygon.drop(columns=["id"])
        fname = app.gui.getvar("modelmaker_hurrywave", "refinement_polygon_file")
        gdf.to_file(fname, driver='GeoJSON')

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

    def write_boundary_polygon(self):
        if len(self.boundary_polygon) == 0:
            return
        gdf = gpd.GeoDataFrame(geometry=self.boundary_polygon["geometry"])
        gdf.to_file(self.boundary_file_name, driver='GeoJSON')

    # Plot

    def plot_refinement_polygon(self):
        layer = app.map.layer["modelmaker_hurrywave"].layer["quadtree_refinement"]
        layer.set_data(self.refinement_polygon)

    def plot_include_polygon(self):
        layer = app.map.layer["modelmaker_hurrywave"].layer["mask_include"]
        layer.clear()
        layer.add_feature(self.include_polygon)

    def plot_exclude_polygon(self):
        layer = app.map.layer["modelmaker_hurrywave"].layer["mask_exclude"]
        layer.clear()
        layer.add_feature(self.exclude_polygon)

    def plot_boundary_polygon(self):
        layer = app.map.layer["modelmaker_hurrywave"].layer["mask_boundary"]
        layer.clear()
        layer.add_feature(self.boundary_polygon)

    def read_setup_yaml(self, file_name):

        dct = yaml2dict(file_name)
        self.setup_dict = dct

        group = "modelmaker_hurrywave"
        # Coordinates
        app.gui.setvar(group, "x0", dct["coordinates"]["x0"])
        app.gui.setvar(group, "y0", dct["coordinates"]["y0"])
        app.gui.setvar(group, "dx", dct["coordinates"]["dx"])
        app.gui.setvar(group, "dy", dct["coordinates"]["dy"])
        app.gui.setvar(group, "nmax", dct["coordinates"]["nmax"])
        app.gui.setvar(group, "mmax", dct["coordinates"]["mmax"])
        app.gui.setvar(group, "rotation", dct["coordinates"]["rotation"])
        app.model["hurrywave"].domain.crs = CRS(dct["coordinates"]["crs"])

        # Quadtree refinement
        if "quadtree" in dct:
            if "polygon_file" in dct["quadtree"]:
                app.gui.setvar(group, "refinement_polygon_file", dct["quadtree"]["polygon_file"])
                self.read_refinement_polygon()
                self.plot_refinement_polygon()

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

        # Bathymetry
        dataset_names = []
        self.selected_bathymetry_datasets = []
        for ddict in dct["bathymetry"]["dataset"]:
            name = ddict["name"]
            zmin = ddict["zmin"]
            zmax = ddict["zmax"] 
            # d = app.bathymetry_database.get_dataset(name)
            dataset = {"dataset": name, "zmin": zmin, "zmax": zmax}
            app.toolbox["modelmaker_hurrywave"].selected_bathymetry_datasets.append(dataset)
            dataset_names.append(name)
        app.gui.setvar("modelmaker_hurrywave", "selected_bathymetry_dataset_names", dataset_names)
        app.gui.setvar("modelmaker_hurrywave", "selected_bathymetry_dataset_index", 0)
        app.gui.setvar("modelmaker_hurrywave", "nr_selected_bathymetry_datasets", len(dataset_names))

        self.update_polygons()

        layer = app.map.layer["modelmaker_hurrywave"].layer["grid_outline"]
        lenx = dct["coordinates"]["mmax"] * dct["coordinates"]["dx"]
        leny = dct["coordinates"]["nmax"] * dct["coordinates"]["dy"]
        layer.add_rectangle(dct["coordinates"]["x0"],
                            dct["coordinates"]["y0"],
                            lenx, leny,
                            dct["coordinates"]["rotation"])


    def write_setup_yaml(self):
        group = "modelmaker_hurrywave"
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
        dct["coordinates"]["crs"] = app.model["hurrywave"].domain.crs.name

        # QuadTree
        dct["quadtree"] = {}
        if len(app.toolbox["modelmaker_sfincs_cht"].refinement_polygon)>0:
            dct["quadtree"]["polygon_file"] = app.gui.getvar("modelmaker_sfincs_cht", "refinement_polygon_file")

        # Mask
        dct["mask"] = {}
        dct["mask"]["zmin"] = app.gui.getvar(group, "global_zmin")
        dct["mask"]["zmax"] = app.gui.getvar(group, "global_zmax")
        dct["mask"]["include_polygon"] = []
        if len(app.toolbox["modelmaker_hurrywave"].include_polygon)>0:
            pol = {}
            pol["file_name"] = self.include_file_name
            pol["zmin"] = app.gui.getvar("modelmaker_hurrywave", "include_zmin")
            pol["zmax"] = app.gui.getvar("modelmaker_hurrywave", "include_zmax")
            dct["mask"]["include_polygon"].append(pol)
        dct["mask"]["exclude_polygon"] = []
        if len(app.toolbox["modelmaker_hurrywave"].exclude_polygon)>0:
            pol = {}
            pol["file_name"] = self.exclude_file_name
            pol["zmin"] = app.gui.getvar("modelmaker_hurrywave", "exclude_zmin")
            pol["zmax"] = app.gui.getvar("modelmaker_hurrywave", "exclude_zmax")
            dct["mask"]["exclude_polygon"].append(pol)
        dct["mask"]["open_boundary_polygon"] = []
        if len(app.toolbox["modelmaker_hurrywave"].boundary_polygon)>0:
            pol = {}
            pol["file_name"] = self.boundary_file_name
            pol["zmin"] = app.gui.getvar("modelmaker_hurrywave", "boundary_zmin")
            pol["zmax"] = app.gui.getvar("modelmaker_hurrywave", "boundary_zmax")
            dct["mask"]["open_boundary_polygon"].append(pol)
        # Bathymetry
        dct["bathymetry"] = {}
        dct["bathymetry"]["dataset"] = []
        dataset = {}
        for d in app.toolbox["modelmaker_hurrywave"].selected_bathymetry_datasets:
            dataset["name"]   = d["dataset"].name
            dataset["source"] = "delftdashboard"
            dataset["zmin"]   = d["zmin"]
            dataset["zmax"]   = d["zmax"]
        dct["bathymetry"]["dataset"].append(dataset)    

        self.setup_dict = dct

        dict2yaml("model_setup.yml", dct)

