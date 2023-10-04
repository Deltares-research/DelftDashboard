import math
import numpy as np
import geopandas as gpd
import shapely
import json

from delftdashboard.operations.toolbox import GenericToolbox
from delftdashboard.app import app

from cht.bathymetry.bathymetry_database import bathymetry_database

from hydromt.config import configread, configwrite
from hydromt_sfincs.utils import mask2gdf


class Toolbox(GenericToolbox):
    def __init__(self, name):
        super().__init__()

        self.name = name
        self.long_name = "Model Maker"

        # Set variables
        # Area of interest and grid outline
        self.area_of_interest = gpd.GeoDataFrame()
        self.grid_outline = gpd.GeoDataFrame()

        # Bathymetry
        self.selected_bathymetry_datasets = []

        # River bathymetry
        # self.selected_river_datasets = []

        # Manning's n
        self.selected_manning_datasets = []

        # Mask active polygons
        self.mask_init_polygon = gpd.GeoDataFrame()  # initial mask area
        self.mask_include_polygon = gpd.GeoDataFrame()  # explicit include polygons
        self.mask_exclude_polygon = gpd.GeoDataFrame()  # explicit exclude polygons

        # Mask boundary polygons
        self.wlev_include_polygon = gpd.GeoDataFrame()
        # self.wlev_exclude_polygon = gpd.GeoDataFrame()
        self.outflow_include_polygon = gpd.GeoDataFrame()
        # self.outflow_exclude_polygon = gpd.GeoDataFrame()

        self.setup_dict = {}

        # Set GUI variable
        group = "modelmaker_sfincs_hmt"

        # Model extent determination
        app.gui.setvar(group, "grid_outline", 0)
        app.gui.setvar(
            group,
            "setup_grid_methods",
            ["Draw Bounding Box", "Draw polygon", "Load Area of Interest"],
        )
        app.gui.setvar(group, "setup_grid_methods_index", 0)

        # Domain
        app.gui.setvar(group, "x0", 0.0)
        app.gui.setvar(group, "y0", 0.0)
        app.gui.setvar(group, "nmax", 0)
        app.gui.setvar(group, "mmax", 0)
        app.gui.setvar(
            group, "nr_cells", app.gui.getvar(group, "mmax") * app.gui.getvar(group, "nmax")
            )
        if app.crs.is_geographic:
            app.gui.setvar(group, "dx", 0.1)
            app.gui.setvar(group, "dy", 0.1)
            app.gui.setvar(group, "res", 0.1)
        else:
            app.gui.setvar(group, "dx", 500)
            app.gui.setvar(group, "dy", 500)
            app.gui.setvar(group, "res", 500)
        app.gui.setvar(group, "rotation", 0.0)
        app.gui.setvar(group, "lenx", 0.0)
        app.gui.setvar(group, "leny", 0.0)

        # Bathymetry
        source_names = []
        # if app.config["bathymetry_database"] is not None:
        # source_names, sources = bathymetry_database.sources()
        if app.config["data_libs"] is not None:
            for key in app.data_catalog.keys:
                # only keep raster datasets
                if app.data_catalog[key].driver == "raster":
                    # only keep topography datasets
                    if app.data_catalog[key].meta["category"] == "topography":
                        # retrieve source name
                        source= app.data_catalog[key].meta["source"]
                        if source not in source_names:
                            source_names.append(source)

            # source_names.append("hydromt")

        app.gui.setvar(group, "bathymetry_source_names", source_names)
        app.gui.setvar(group, "active_bathymetry_source", source_names[0])

        dataset_names = []
        # if app.config["bathymetry_database"] is not None:
        # dataset_names = bathymetry_database.dataset_names(source=source_names[0])[0]
        if app.config["data_libs"] is not None:
            for key in app.data_catalog.keys:
                if app.data_catalog[key].driver == "raster":
                    if app.data_catalog[key].meta["category"] == "topography":
                        if app.data_catalog[key].meta["source"] == source_names[0]:
                            dataset_names.append(key)

        app.gui.setvar(group, "bathymetry_dataset_names", dataset_names)
        app.gui.setvar(group, "bathymetry_dataset_index", 0)
        app.gui.setvar(group, "selected_bathymetry_dataset_names", [])
        app.gui.setvar(group, "selected_bathymetry_dataset_index", 0)
        app.gui.setvar(group, "selected_bathymetry_dataset_zmin", -99999.0)
        app.gui.setvar(group, "selected_bathymetry_dataset_zmax", 99999.0)
        app.gui.setvar(group, "selected_bathymetry_dataset_offset", 0)
        app.gui.setvar(group, "nr_selected_bathymetry_datasets", 0)
        app.gui.setvar(group, "bathymetry_dataset_buffer_cells", 0)
        app.gui.setvar(group, "bathymetry_dataset_interp_method", "linear")

        # Roughness
        app.gui.setvar(group, "manning_land", 0.06)
        app.gui.setvar(group, "manning_sea", 0.02)
        app.gui.setvar(group, "rgh_lev_land", 0.0)

        roughness_methods = [
            "Constant values",
            "Landuse dataset",
            "Manning dataset",
            "Manning shapes",
        ]
        app.gui.setvar(group, "roughness_methods", roughness_methods)
        app.gui.setvar(group, "roughness_methods_index", 0)

        manning_dataset_names = []
        lulc_dataset_names = []
        cn_dataset_names = []
        qinf_dataset_names = []
        if app.config["data_libs"] is not None:
            for key in app.data_catalog.keys:
                if app.data_catalog[key].driver == "raster":
                    if app.data_catalog[key].meta["category"] == "landuse":
                        lulc_dataset_names.append(key)
                    elif app.data_catalog[key].meta["category"] == "roughness":
                        manning_dataset_names.append(key)
                    elif app.data_catalog[key].meta["category"] == "soil":
                        cn_dataset_names.append(key)
                    elif app.data_catalog[key].meta["category"] == "infiltration":
                        qinf_dataset_names.append(key)

        app.gui.setvar(group, "lulc_dataset_names", lulc_dataset_names)
        app.gui.setvar(group, "lulc_dataset_index", 0)
        app.gui.setvar(group, "lulc_reclass_table", "")
        app.gui.setvar(group, "manning_dataset_names", manning_dataset_names)
        app.gui.setvar(group, "manning_dataset_index", 0)
        app.gui.setvar(group, "manning_polygon_names", [])
        app.gui.setvar(group, "manning_polygon_values", [])
        app.gui.setvar(group, "manning_polygon_index", 0)
        app.gui.setvar(group, "nr_manning_polygons", 0)
        app.gui.setvar(group, "selected_manning_dataset_names", ["Constant values"])
        app.gui.setvar(group, "selected_manning_dataset_index", 0)
        app.gui.setvar(group, "nr_selected_manning_datasets", 0)

        infiltration_methods = ["Constant value", "CN dataset", "Qinf dataset"]
        app.gui.setvar(group, "infiltration_methods", infiltration_methods)
        app.gui.setvar(group, "infiltration_methods_index", 0)

        app.gui.setvar(group, "cn_dataset_names", cn_dataset_names)
        app.gui.setvar(group, "cn_dataset_index", 0)
        app.gui.setvar(group, "cn_antecedent_moisture", "avg")
        app.gui.setvar(group, "qinf_dataset_names", qinf_dataset_names)
        app.gui.setvar(group, "qinf_dataset_index", 0)        

        # Mask active
        mask_polygon_methods = [
            "Load Polygon",
            "Draw Polygon",
            "Delete Polygon",
            "Save Polygon",
        ]

        app.gui.setvar(group, "mask_init_polygon_methods", mask_polygon_methods)
        app.gui.setvar(group, "mask_init_polygon_methods_index", 0)
        app.gui.setvar(group, "nr_mask_init_polygons", 0)
        app.gui.setvar(group, "mask_active_zmax", 10.0)
        app.gui.setvar(group, "mask_active_zmin", -10.0)
        app.gui.setvar(group, "mask_active_drop_area", 0.0)
        app.gui.setvar(group, "mask_active_fill_area", 10.0)
        app.gui.setvar(group, "mask_active_reset", True)
        app.gui.setvar(group, "mask_include_polygon_names", [])
        app.gui.setvar(group, "mask_include_polygon_index", 0)
        app.gui.setvar(group, "nr_mask_include_polygons", 0)
        app.gui.setvar(group, "mask_exclude_polygon_names", [])
        app.gui.setvar(group, "mask_exclude_polygon_index", 0)
        app.gui.setvar(group, "nr_mask_exclude_polygons", 0)

        # Mask bounds
        app.gui.setvar(group, "wlev_include_polygon_names", [])
        app.gui.setvar(group, "wlev_include_polygon_index", 0)
        app.gui.setvar(group, "nr_wlev_include_polygons", 0)
        # app.gui.setvar(group, "wlev_exclude_polygon_names", [])
        # app.gui.setvar(group, "wlev_exclude_polygon_index", 0)
        # app.gui.setvar(group, "nr_wlev_exclude_polygons", 0)
        app.gui.setvar(group, "wlev_zmax", -2.0)
        app.gui.setvar(group, "wlev_zmin", -99999.0)
        app.gui.setvar(group, "wlev_reset", True)

        app.gui.setvar(group, "outflow_include_polygon_names", [])
        app.gui.setvar(group, "outflow_include_polygon_index", 0)
        app.gui.setvar(group, "nr_outflow_include_polygons", 0)
        # app.gui.setvar(group, "outflow_exclude_polygon_names", [])
        # app.gui.setvar(group, "outflow_exclude_polygon_index", 0)
        # app.gui.setvar(group, "nr_outflow_exclude_polygons", 0)
        app.gui.setvar(group, "outflow_zmax", 99999.0)
        app.gui.setvar(group, "outflow_zmin", 2.0)
        app.gui.setvar(group, "outflow_reset", True)

        # subgrid
        app.gui.setvar(group, "nr_subgrid_pixels", 20)
        app.gui.setvar(group, "nbins", 10)
        app.gui.setvar(group, "max_gradient", 5.0)
        app.gui.setvar(group, "nrmax", 2000)
        app.gui.setvar(group, "z_minimum", -99999.0)
        app.gui.setvar(group, "write_dep_tif", True)
        app.gui.setvar(group, "write_man_tif", True)
        app.gui.setvar(group, "extrapolate_values", False)

        subgrid_buffer_cells = app.gui.getvar(
            group, "nr_subgrid_pixels"
        ) * app.gui.getvar(group, "bathymetry_dataset_buffer_cells")
        app.gui.setvar(group, "subgrid_buffer_cells", subgrid_buffer_cells)

    def set_layer_mode(self, mode):
        if mode == "inactive":
            # Make all layers invisible
            app.map.layer["modelmaker_sfincs_hmt"].hide()
        if mode == "invisible":
            app.map.layer["modelmaker_sfincs_hmt"].hide()

    def add_layers(self):
        # Add Mapbox layers
        layer = app.map.add_layer("modelmaker_sfincs_hmt")

        # Area of interest
        from .domain import aio_created
        from .domain import aio_modified

        layer.add_layer(
            "area_of_interest",
            type="draw",
            shape="polygon",
            create=aio_created,
            modify=aio_modified,
            polygon_line_color="grey",
            polygon_fill_opacity=0.3,
        )

        # Grid outline
        from .domain import grid_outline_created
        from .domain import grid_outline_modified

        layer.add_layer(
            "grid_outline",
            type="draw",
            shape="rectangle",
            create=grid_outline_created,
            modify=grid_outline_modified,
            polygon_line_color="mediumblue",
            polygon_fill_opacity=0.3,
        )

        ### Mask
        # Region
        from .mask_active_cells import mask_init_polygon_created
        from .mask_active_cells import mask_init_polygon_modified

        layer.add_layer(
            "mask_init",
            type="draw",
            shape="polygon",
            create=mask_init_polygon_created,
            modify=mask_init_polygon_modified,
            polygon_line_color="grey",
            polygon_fill_color="grey",
            polygon_fill_opacity=0.3,
        )

        # Include
        from .mask_active_cells import include_polygon_created
        from .mask_active_cells import include_polygon_modified
        from .mask_active_cells import include_polygon_selected

        layer.add_layer(
            "mask_include",
            type="draw",
            shape="polygon",
            create=include_polygon_created,
            modify=include_polygon_modified,
            select=include_polygon_selected,
            polygon_line_color="limegreen",
            polygon_fill_color="limegreen",
            polygon_fill_opacity=0.3,
        )
        # Exclude
        from .mask_active_cells import exclude_polygon_created
        from .mask_active_cells import exclude_polygon_modified
        from .mask_active_cells import exclude_polygon_selected

        layer.add_layer(
            "mask_exclude",
            type="draw",
            shape="polygon",
            create=exclude_polygon_created,
            modify=exclude_polygon_modified,
            select=exclude_polygon_selected,
            polygon_line_color="orangered",
            polygon_fill_color="orangered",
            polygon_fill_opacity=0.3,
        )
        # Boundary
        from .mask_boundary_cells import wlev_polygon_created
        from .mask_boundary_cells import wlev_polygon_modified
        from .mask_boundary_cells import wlev_polygon_selected

        layer.add_layer(
            "mask_wlev",
            type="draw",
            shape="polygon",
            create=wlev_polygon_created,
            modify=wlev_polygon_modified,
            select=wlev_polygon_selected,
            polygon_line_color="deepskyblue",
            polygon_fill_color="deepskyblue",
            polygon_fill_opacity=0.3,
        )

        from .mask_boundary_cells import outflow_polygon_created
        from .mask_boundary_cells import outflow_polygon_modified
        from .mask_boundary_cells import outflow_polygon_selected

        layer.add_layer(
            "mask_outflow",
            type="draw",
            shape="polygon",
            create=outflow_polygon_created,
            modify=outflow_polygon_modified,
            select=outflow_polygon_selected,
            polygon_line_color="indianred",
            polygon_fill_color="indianred",
            polygon_fill_opacity=0.3,
        )

    def generate_grid(self):
        model = app.model["sfincs_hmt"].domain

        dlg = app.gui.window.dialog_wait("Generating grid ...")

        group = "modelmaker_sfincs_hmt"
        setup_grid = {
            "x0": float(app.gui.getvar(group, "x0")),
            "y0": float(app.gui.getvar(group, "y0")),
            "dx": float(app.gui.getvar(group, "dx")),
            "dy": float(app.gui.getvar(group, "dy")),
            "nmax": int(app.gui.getvar(group, "nmax")),
            "mmax": int(app.gui.getvar(group, "mmax")),
            "rotation": float(app.gui.getvar(group, "rotation")),
            "epsg": app.crs.to_epsg(),
        }
        model.setup_grid(**setup_grid)
        self.setup_dict.update({"setup_grid": setup_grid})

        group = "sfincs_hmt"
        app.gui.setvar(group, "x0", model.config.get("x0"))
        app.gui.setvar(group, "y0", model.config.get("y0"))
        app.gui.setvar(group, "dx", model.config.get("dx"))
        app.gui.setvar(group, "dy", model.config.get("dy"))
        app.gui.setvar(group, "nmax", model.config.get("nmax"))
        app.gui.setvar(group, "mmax", model.config.get("mmax"))
        app.gui.setvar(group, "rotation", model.config.get("rotation"))
        app.gui.setvar(group, "epsg", model.config.get("epsg"))

        # NOTE this only works for regular grids (quadtee also not implemented)
        gdf = model.reggrid.to_vector_lines()
        app.map.layer["sfincs_hmt"].layer["grid"].set_data(gdf)

        dlg.close()

    def generate_bathymetry(self):
        model = app.model["sfincs_hmt"].domain

        dlg = app.gui.window.dialog_wait("Generating bathymetry ...")

        group = "modelmaker_sfincs_hmt"
        setup_dep = {
            "datasets_dep": app.toolbox[group].selected_bathymetry_datasets,
            "buffer_cells": app.gui.getvar(group, "bathymetry_dataset_buffer_cells"),
            "interp_method": app.gui.getvar(group, "bathymetry_dataset_interp_method"),
        }

        model.setup_dep(**setup_dep)
        self.setup_dict.update({"setup_dep": setup_dep})

        dlg.close()

    def generate_manning(self):
        model = app.model["sfincs_hmt"].domain

        dlg = app.gui.window.dialog_wait("Generating manning roughness ...")

        group = "modelmaker_sfincs_hmt"
        setup_manning_roughness = {
            "datasets_rgh": app.toolbox[group].selected_manning_datasets,
            "manning_land": app.gui.getvar(group, "manning_land"),
            "manning_sea": app.gui.getvar(group, "manning_sea"),
            "rgh_lev_land": app.gui.getvar(group, "rgh_lev_land"),
        }

        # NOTE setup methods parse the dataset-names to xarray datasets
        model.setup_manning_roughness(**setup_manning_roughness)
        self.setup_dict.update({"setup_manning_roughness": setup_manning_roughness})

        dlg.close()

    def update_mask_active(self):
        model = app.model["sfincs_hmt"].domain

        dlg = app.gui.window.dialog_wait("Generating active mask  ...")
        group = "modelmaker_sfincs_hmt"
        setup_mask_active = {
            "mask": app.toolbox[group].mask_init_polygon
            if not app.toolbox[group].mask_init_polygon.empty
            else None,
            "include_mask": app.toolbox[group].mask_include_polygon,
            "exclude_mask": app.toolbox[group].mask_exclude_polygon,
            "zmin": app.gui.getvar(group, "mask_active_zmin"),
            "zmax": app.gui.getvar(group, "mask_active_zmax"),
            "drop_area": app.gui.getvar(group, "mask_active_drop_area"),
            "fill_area": app.gui.getvar(group, "mask_active_fill_area"),
            "reset_mask": app.gui.getvar(group, "mask_active_reset"),
        }

        model.setup_mask_active(**setup_mask_active)
        self.setup_dict.update({"setup_mask_active": setup_mask_active})

        mask = model.mask

        gdf = mask2gdf(mask, option="active")
        if gdf is not None:
            app.map.layer["sfincs_hmt"].layer["mask_active"].set_data(gdf)

        dlg.close()

    def update_mask_bounds(self):
        model = app.model["sfincs_hmt"].domain

        dlg = app.gui.window.dialog_wait("Generating mask boundaries ...")

        group = "modelmaker_sfincs_hmt"
        setup_mask_bounds = {
            "btype": "waterlevel",
            "include_mask": app.toolbox[group].wlev_include_polygon
            if app.gui.getvar(group, "nr_wlev_include_polygons") > 0
            else None,
            "zmin": app.gui.getvar(group, "wlev_zmin"),
            "zmax": app.gui.getvar(group, "wlev_zmax"),
            "reset_bounds": app.gui.getvar(group, "wlev_reset"),
        }

        model.setup_mask_bounds(**setup_mask_bounds)
        self.setup_dict.update({"setup_mask_bounds": setup_mask_bounds})

        setup_mask_bounds2 = {
            "btype": "outflow",
            "include_mask": app.toolbox[group].outflow_include_polygon
            if app.gui.getvar(group, "nr_outflow_include_polygons") > 0
            else None,
            "zmin": app.gui.getvar(group, "outflow_zmin"),
            "zmax": app.gui.getvar(group, "outflow_zmax"),
            "reset_bounds": app.gui.getvar(group, "outflow_reset"),
        }

        app.model["sfincs_hmt"].domain.setup_mask_bounds(**setup_mask_bounds2)
        self.setup_dict.update({"setup_mask_bounds2": setup_mask_bounds2})

        mask = model.mask

        gdf_wlev = mask2gdf(mask, option="wlev")
        if gdf_wlev is not None:
            app.map.layer["sfincs_hmt"].layer["mask_bound_wlev"].set_data(gdf_wlev)

        gdf_outflow = mask2gdf(mask, option="outflow")
        if gdf_wlev is not None:
            app.map.layer["sfincs_hmt"].layer["mask_bound_outflow"].set_data(
                gdf_outflow
            )

        dlg.close()

    def reset_mask_bounds(self):
        model = app.model["sfincs_hmt"].domain

        group = "modelmaker_sfincs_hmt"
        if app.gui.getvar(group, "wlev_reset"):
            model.setup_mask_bounds(reset_bounds=True, btype="waterlevel")
            # remove old waterlevel mask data
            app.map.layer["sfincs_hmt"].layer["mask_bound_wlev"].clear()
            # remove settings from setup_dict
            self.setup_dict.pop("setup_mask_bounds", None)

        if app.gui.getvar(group, "outflow_reset"):
            model.setup_mask_bounds(reset_bounds=True, btype="outflow")
            # remove old outflow mask data
            app.map.layer["sfincs_hmt"].layer["mask_bound_outflow"].clear()
            # remove settings from setup_dict
            self.setup_dict.pop("setup_mask_bounds2", None)

        mask = model.mask
        # possibly mask active has ben changed so, recalculate it
        gdf = mask2gdf(mask, option="active")
        if gdf is not None:
            app.map.layer["sfincs_hmt"].layer["mask_active"].set_data(gdf)

    def generate_subgrid(self):
        model = app.model["sfincs_hmt"].domain

        dlg = app.gui.window.dialog_wait("Generating subgrid ...")

        group = "modelmaker_sfincs_hmt"
        setup_subgrid = {
            "datasets_dep": app.toolbox[group].selected_bathymetry_datasets,
            "datasets_rgh": app.toolbox[group].selected_manning_datasets,
            "manning_land": app.gui.getvar(group, "manning_land"),
            "manning_sea": app.gui.getvar(group, "manning_sea"),
            "rgh_lev_land": app.gui.getvar(group, "rgh_lev_land"),
            "buffer_cells": app.gui.getvar(group, "subgrid_buffer_cells"),
            "nr_subgrid_pixels": app.gui.getvar(group, "nr_subgrid_pixels"),
            "nbins": app.gui.getvar(group, "nbins"),
            "max_gradient": app.gui.getvar(group, "max_gradient"),
            "nrmax": app.gui.getvar(group, "nrmax"),
            "z_minimum": app.gui.getvar(group, "z_minimum"),
            "write_dep_tif": app.gui.getvar(group, "write_dep_tif"),
            "write_man_tif": app.gui.getvar(group, "write_man_tif"),
            "extrapolate_values": app.gui.getvar(group, "extrapolate_values"),
        }

        model.setup_subgrid(**setup_subgrid)
        self.setup_dict.update({"setup_subgrid": setup_subgrid})

        dlg.close()

        dlg = app.gui.window.dialog_wait("Writing SFINCS model ...")
        app.model["sfincs_hmt"].save()
        dlg.close()

    def generate_infiltration(self):
        model = app.model["sfincs_hmt"].domain
        index = app.gui.getvar("modelmaker_sfincs_hmt", "infiltration_methods_index")

        dlg = app.gui.window.dialog_wait("Generating infiltration ...")

        if index == 0: # constant infiltration
            # drop other methods
            model.config.pop("scsfile", None)
            model.config.pop("qinffile", None)
        elif index == 1:
            # drop other methods
            model.config.pop("qinffile", None)
            model.config["qinf"] = 0.0

            # generate CN infiltration
            model.setup_cn_infiltration(
                cn = app.gui.getvar("modelmaker_sfincs_hmt", "cn_dataset_names")[app.gui.getvar("modelmaker_sfincs_hmt", "cn_dataset_index")],
                antecedent_moisture = app.gui.getvar("modelmaker_sfincs_hmt", "cn_antecedent_moisture"),
            )
        elif index == 2:
            # drop other methods
            model.config.pop("scsfile", None)
            model.config["qinf"] = 0.0

            # generate Qinf infiltration
            model.setup_constant_infiltration(
                qinf = app.gui.getvar("modelmaker_sfincs_hmt", "qinf_dataset_names")[app.gui.getvar("modelmaker_sfincs_hmt", "qinf_dataset_index")],
            ) 
        dlg.close()

    def read_setup_yaml(self):
        fname = app.gui.window.dialog_open_file(
            "Select SFINCS setup yaml-file", filter="*.yml *.yaml"
        )
        if fname[0]:
            self.setup_dict = configread(config_fn=fname[0])

    def write_setup_yaml(self):
        _parse_setup_dict(self.setup_dict)
        configwrite(config_fn="sfincs_build.yaml", cfdict=self.setup_dict)

    def build(self):
        model = app.model["sfincs_hmt"].domain

        model.build()


## Helper functions
def _parse_setup_dict(dictionary):
    keys_to_remove = []
    for key, value in dictionary.items():
        if isinstance(value, dict):
            _parse_setup_dict(value)
        elif isinstance(value, gpd.GeoDataFrame):
            # Drop the GeoDataFrame from the dict if empty
            if value.empty:
                keys_to_remove.append(key)
            else:
                # Generate a unique filename based on the key
                filename = key + ".geojson"
                # Write the GeoDataFrame to a GeoJSON file
                value.to_file(filename, driver="GeoJSON")
                # Replace the entry with the filename
                dictionary[key] = filename
        elif value is None:
            keys_to_remove.append(key)

    for key in keys_to_remove:
        dictionary.pop(key)

