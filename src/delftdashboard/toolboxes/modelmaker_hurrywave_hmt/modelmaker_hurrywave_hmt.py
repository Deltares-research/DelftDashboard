import pandas as pd
import geopandas as gpd

from delftdashboard.operations.toolbox import GenericToolbox
from delftdashboard.app import app
from delftdashboard.misc.gdfutils import mpol2pol


class Toolbox(GenericToolbox):
    def __init__(self, name):
        super().__init__()

        self.name = name
        self.long_name = "Model Maker"

    def initialize(self):

        # Grid outline
        self.grid_outline = gpd.GeoDataFrame()

        # Bathymetry
        self.selected_bathymetry_datasets = []

        # Include polygons
        self.include_polygon = gpd.GeoDataFrame()
        self.include_file_name = "include.geojson"
        self.include_polygon_changed = False
        # Exclude polygons
        self.exclude_polygon = gpd.GeoDataFrame()
        self.exclude_file_name = "exclude.geojson"
        self.exclude_polygon_changed = False
        # Boundary polygons
        self.boundary_polygon = gpd.GeoDataFrame()
        self.boundary_file_name = "boundary.geojson"
        self.boundary_polygon_changed = False
        # Refinement
        self.refinement_polygon = gpd.GeoDataFrame()
        self.refinement_polygons_changed = False

        self.setup_dict = {}

        group = "modelmaker_hurrywave_hmt"

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
        levstr = [str(i) for i in range(10)]
        app.gui.setvar(group, "refinement_polygon_levels", levstr)

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
        if mode in ("inactive", "invisible"):
            app.map.layer["modelmaker_hurrywave_hmt"].hide()

    def add_layers(self):
        layer = app.map.add_layer("modelmaker_hurrywave_hmt")

        from .domain import grid_outline_created
        from .domain import grid_outline_modified
        layer.add_layer("grid_outline", type="draw",
                        shape="rectangle",
                        create=grid_outline_created,
                        modify=grid_outline_modified,
                        polygon_line_color="mediumblue",
                        polygon_fill_opacity=0.3,
                        rotate=True)

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
        domain = app.model["hurrywave_hmt"].domain

        nmax = domain.config.get("nmax") or 0
        if nmax > 0:
            ok = app.gui.window.dialog_ok_cancel(
                "Existing model grid and spatial attributes will be deleted! Continue?",
                title="Warning")
            if not ok:
                return

        app.model["hurrywave_hmt"].clear_spatial_attributes()

        dlg = app.gui.window.dialog_wait("Generating grid ...")

        group = "modelmaker_hurrywave_hmt"
        x0       = app.gui.getvar(group, "x0")
        y0       = app.gui.getvar(group, "y0")
        dx       = app.gui.getvar(group, "dx")
        dy       = app.gui.getvar(group, "dy")
        nmax     = app.gui.getvar(group, "nmax")
        mmax     = app.gui.getvar(group, "mmax")
        rotation = app.gui.getvar(group, "rotation")

        domain.config.set("x0", x0)
        domain.config.set("y0", y0)
        domain.config.set("dx", dx)
        domain.config.set("dy", dy)
        domain.config.set("nmax", nmax)
        domain.config.set("mmax", mmax)
        domain.config.set("rotation", rotation)
        app.model["hurrywave_hmt"].set_gui_variables()

        refpol = self.refinement_polygon if len(self.refinement_polygon) > 0 else None

        domain.quadtree_grid.create(
            x0, y0, nmax, mmax, dx, dy, rotation,
            epsg=app.crs.to_epsg(),
            refinement_polygons=refpol,
            elevation_list=app.selected_bathymetry_datasets,
            bathymetry_database=app.bathymetry_database)
        domain.quadtree_grid.write()
        app.map.layer["hurrywave_hmt"].layer["grid"].set_data(domain.quadtree_grid)

        dlg.close()

    def generate_bathymetry(self):
        dlg = app.gui.window.dialog_wait("Generating bathymetry ...")

        domain = app.model["hurrywave_hmt"].domain
        domain.quadtree_elevation.create(
            elevation_list=app.selected_bathymetry_datasets,
            bathymetry_database=app.bathymetry_database,
            nr_subgrid_pixels=20,
            threshold_level=0.0,
            mean_wet=True)
        domain.quadtree_grid.write()

        dlg.close()

    def update_mask(self):
        dlg = app.gui.window.dialog_wait("Updating mask ...")

        domain = app.model["hurrywave_hmt"].domain
        group = "modelmaker_hurrywave_hmt"
        domain.quadtree_mask.create(
            zmin=app.gui.getvar(group, "global_zmin"),
            zmax=app.gui.getvar(group, "global_zmax"),
            include_polygon=self.include_polygon,
            include_zmin=app.gui.getvar(group, "include_zmin"),
            include_zmax=app.gui.getvar(group, "include_zmax"),
            exclude_polygon=self.exclude_polygon,
            exclude_zmin=app.gui.getvar(group, "exclude_zmin"),
            exclude_zmax=app.gui.getvar(group, "exclude_zmax"),
            open_boundary_polygon=self.boundary_polygon,
            open_boundary_zmin=app.gui.getvar(group, "boundary_zmin"),
            open_boundary_zmax=app.gui.getvar(group, "boundary_zmax"),
            update_datashader_dataframe=True)
        domain.quadtree_grid.write()
        app.map.layer["hurrywave_hmt"].layer["mask"].set_data(domain.quadtree_mask)

        dlg.close()

    def cut_inactive_cells(self):
        dlg = app.gui.window.dialog_wait("Cutting Inactive Cells ...")

        domain = app.model["hurrywave_hmt"].domain
        domain.quadtree_grid.cut_inactive_cells()
        domain.quadtree_grid.write()
        app.model["hurrywave_hmt"].plot()

        dlg.close()

    def generate_waveblocking(self):
        group = "modelmaker_hurrywave_hmt"
        filename = app.model["hurrywave_hmt"].domain.config.get("wblfile")
        if not filename:
            filename = "hurrywave.wbl"
        rsp = app.gui.window.dialog_save_file("Select file ...",
                                              file_name=filename,
                                              filter="*.wbl",
                                              allow_directory_change=False)
        if rsp[0]:
            filename = rsp[2]
        else:
            return

        domain = app.model["hurrywave_hmt"].domain
        nr_dirs = domain.config.get("ntheta") or 36
        nr_pixels = app.gui.getvar(group, "waveblocking_nr_pixels")
        threshold_level = app.gui.getvar(group, "waveblocking_threshold_level")

        p = app.gui.window.dialog_progress(
            "               Generating Wave blocking file ...                ", 100)

        domain.wave_blocking.create(
            app.selected_bathymetry_datasets,
            bathymetry_database=app.bathymetry_database,
            nr_dirs=nr_dirs,
            nr_subgrid_pixels=nr_pixels,
            threshold_level=threshold_level,
            quiet=False,
            progress_bar=p)
        p.close()

        domain.wave_blocking.write(filename=filename)
        app.gui.setvar("hurrywave_hmt", "wblfile", filename)

    def build_model(self):
        self.generate_grid()
        self.generate_bathymetry()
        self.update_mask()
        self.generate_waveblocking()

    def read_refinement_polygon(self, file_name, append):
        refinement_polygon = gpd.read_file(file_name).to_crs(app.crs)
        if "refinement_level" not in refinement_polygon.columns:
            refinement_polygon["refinement_level"] = 1
        if "zmin" not in refinement_polygon.columns:
            refinement_polygon["zmin"] = -99999.0
        if "zmax" not in refinement_polygon.columns:
            refinement_polygon["zmax"] = 99999.0
        if append:
            self.refinement_polygon = gpd.GeoDataFrame(
                pd.concat([self.refinement_polygon, refinement_polygon], ignore_index=True))
        else:
            self.refinement_polygon = refinement_polygon

    def read_include_polygon(self, fname, append):
        if not append:
            self.include_polygon = mpol2pol(gpd.read_file(fname)).to_crs(app.crs)
        else:
            gdf = mpol2pol(gpd.read_file(fname)).to_crs(app.crs)
            self.include_polygon = gpd.GeoDataFrame(
                pd.concat([self.include_polygon, gdf], ignore_index=True))

    def read_exclude_polygon(self, fname, append):
        if not append:
            self.exclude_polygon = mpol2pol(gpd.read_file(fname)).to_crs(app.crs)
        else:
            gdf = mpol2pol(gpd.read_file(fname)).to_crs(app.crs)
            self.exclude_polygon = gpd.GeoDataFrame(
                pd.concat([self.exclude_polygon, gdf], ignore_index=True))

    def read_boundary_polygon(self, fname, append):
        if not append:
            self.boundary_polygon = gpd.read_file(fname).to_crs(app.crs)
        else:
            gdf = gpd.read_file(fname).to_crs(app.crs)
            self.boundary_polygon = gpd.GeoDataFrame(
                pd.concat([self.boundary_polygon, gdf], ignore_index=True))

    def write_refinement_polygon(self):
        if len(self.refinement_polygon) == 0:
            return
        gdf = self.refinement_polygon.drop(columns=["id"]) if "id" in self.refinement_polygon.columns else self.refinement_polygon
        fname = app.gui.getvar("modelmaker_hurrywave_hmt", "refinement_polygon_file")
        gdf.to_file(fname, driver="GeoJSON")

    def write_include_polygon(self):
        if len(self.include_polygon) == 0:
            return
        gpd.GeoDataFrame(geometry=self.include_polygon["geometry"]).to_file(
            self.include_file_name, driver="GeoJSON")

    def write_exclude_polygon(self):
        if len(self.exclude_polygon) == 0:
            return
        gpd.GeoDataFrame(geometry=self.exclude_polygon["geometry"]).to_file(
            self.exclude_file_name, driver="GeoJSON")

    def write_boundary_polygon(self):
        if len(self.boundary_polygon) == 0:
            return
        gpd.GeoDataFrame(geometry=self.boundary_polygon["geometry"]).to_file(
            self.boundary_file_name, driver="GeoJSON")

    def plot_refinement_polygon(self):
        app.map.layer["modelmaker_hurrywave_hmt"].layer["quadtree_refinement"].set_data(
            self.refinement_polygon)

    def plot_include_polygon(self):
        layer = app.map.layer["modelmaker_hurrywave_hmt"].layer["mask_include"]
        layer.clear()
        layer.add_feature(self.include_polygon)

    def plot_exclude_polygon(self):
        layer = app.map.layer["modelmaker_hurrywave_hmt"].layer["mask_exclude"]
        layer.clear()
        layer.add_feature(self.exclude_polygon)

    def plot_boundary_polygon(self):
        layer = app.map.layer["modelmaker_hurrywave_hmt"].layer["mask_boundary"]
        layer.clear()
        layer.add_feature(self.boundary_polygon)
