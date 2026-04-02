"""Delft3D-FM model maker toolbox: grid generation, refinement, bathymetry, and boundaries."""

from __future__ import annotations

import traceback
from typing import List, Optional

import geopandas as gpd
from cht_utils.misc_tools import dict2yaml, yaml2dict
from pyproj import CRS

from delftdashboard.app import app
from delftdashboard.operations.toolbox import GenericToolbox

_TB = "modelmaker_delft3dfm"
_MODEL = "delft3dfm"


class Toolbox(GenericToolbox):
    """Toolbox for building Delft3D-FM unstructured grid models."""

    def __init__(self, name: str) -> None:
        super().__init__()

        self.name = name
        self.long_name = "Model Maker"

    def initialize(self) -> None:
        """Initialize GUI variables and empty data containers."""
        # Set variables

        # Grid outline
        self.grid_outline: gpd.GeoDataFrame = gpd.GeoDataFrame()

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
        group = _TB

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
        app.gui.setvar(group, "open_boundary_zmax", 99999.0)
        app.gui.setvar(group, "open_boundary_zmin", -99999.0)
        app.gui.setvar(group, "boundary_dx", 0.05)

        # app.gui.setvar(group, "outflow_boundary_polygon_file", "outflow_boundary.geojson")
        # app.gui.setvar(group, "outflow_boundary_polygon_names", [])
        # app.gui.setvar(group, "outflow_boundary_polygon_index", 0)
        # app.gui.setvar(group, "nr_outflow_boundary_polygons", 0)
        # app.gui.setvar(group, "outflow_boundary_zmax",  99999.0)
        # app.gui.setvar(group, "outflow_boundary_zmin", -99999.0)

        # Bathymetry
        source_names, sources = app.topography_data_catalog.sources()
        app.gui.setvar(group, "bathymetry_source_names", source_names)
        app.gui.setvar(group, "active_bathymetry_source", source_names[0])
        dataset_names, dataset_long_names, dataset_source_names = (
            app.topography_data_catalog.dataset_names(source=source_names[0])
        )
        app.gui.setvar(group, "bathymetry_dataset_names", dataset_names)
        app.gui.setvar(group, "bathymetry_dataset_index", 0)
        app.gui.setvar(group, "selected_bathymetry_dataset_names", [])
        app.gui.setvar(group, "selected_bathymetry_dataset_index", 0)
        app.gui.setvar(group, "selected_bathymetry_dataset_zmin", -99999.0)
        app.gui.setvar(group, "selected_bathymetry_dataset_zmax", 99999.0)
        app.gui.setvar(group, "nr_selected_bathymetry_datasets", 0)

        # Boundary points
        app.gui.setvar(group, "boundary_dx", 50000.0)

    def set_layer_mode(self, mode: str) -> None:
        """Set the visibility mode for all toolbox map layers.

        Parameters
        ----------
        mode : str
            Layer mode, e.g. ``"inactive"`` or ``"invisible"``.
        """
        if mode == "inactive":
            # Make all layers invisible
            app.map.layer[_TB].hide()
        if mode == "invisible":
            app.map.layer[_TB].hide()

    def add_layers(self) -> None:
        """Register all map layers used by this toolbox."""
        # Add Mapbox layers
        layer = app.map.add_layer(_TB)

        # Grid outline
        from .domain import grid_outline_created, grid_outline_modified

        layer.add_layer(
            "grid_outline",
            type="draw",
            shape="rectangle",
            create=grid_outline_created,
            modify=grid_outline_modified,
            polygon_line_color="mediumblue",
            polygon_fill_opacity=0.3,
            rotate=True,
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
        from .exclude import (
            exclude_polygon_created,
            exclude_polygon_modified,
            exclude_polygon_selected,
        )

        layer.add_layer(
            "exclude_polygon",
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
        from .boundary import (
            open_boundary_polygon_created,
            open_boundary_polygon_modified,
            open_boundary_polygon_selected,
        )

        layer.add_layer(
            "open_boundary_polygon",
            type="draw",
            shape="polygon",
            create=open_boundary_polygon_created,
            modify=open_boundary_polygon_modified,
            select=open_boundary_polygon_selected,
            polygon_line_color="deepskyblue",
            polygon_fill_color="deepskyblue",
            polygon_fill_opacity=0.3,
        )

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
        from .refinement import (
            refinement_polygon_created,
            refinement_polygon_modified,
            refinement_polygon_selected,
        )

        layer.add_layer(
            "polygon_refinement",
            type="draw",
            columns={"min_edge_size": 500},
            shape="polygon",
            create=refinement_polygon_created,
            modify=refinement_polygon_modified,
            select=refinement_polygon_selected,
            polygon_line_color="red",
            polygon_fill_color="orange",
            polygon_fill_opacity=0.3,
        )

    def set_crs(self) -> None:
        """Reset grid spacing defaults when the coordinate reference system changes."""
        group = _TB
        if app.crs.is_geographic:
            app.gui.setvar(group, "dx", 0.1)
            app.gui.setvar(group, "dy", 0.1)
        else:
            app.gui.setvar(group, "dx", 1000.0)
            app.gui.setvar(group, "dy", 1000.0)

        self.initialize()
        self.clear_layers()

    def generate_grid(self) -> None:
        """Build the initial structured grid from current GUI parameters."""
        group = _TB
        dlg = app.gui.window.dialog_wait("Generating grid ...")
        try:
            # self.clear_layers()
            model = app.model[_MODEL].domain
            model.clear_spatial_attributes()
            x0 = app.gui.getvar(group, "x0")
            y0 = app.gui.getvar(group, "y0")
            dx = app.gui.getvar(group, "dx")
            dy = app.gui.getvar(group, "dy")
            nmax = app.gui.getvar(group, "nmax")
            mmax = app.gui.getvar(group, "mmax")
            model.input.geometry.netfile.filepath = "flow_net.nc"
            app.gui.setvar(_MODEL, "netfile", model.input.geometry.netfile.filepath)

            # if len(self.refinement_polygon) == 0:
            #     refpol = None
            # else:
            #     # Make list of separate gdfs for each polygon
            #     refpol = self.refinement_polygon

            # Build grid
            bathymetry_list = app.toolbox[_TB].selected_bathymetry_datasets
            model.grid.build(
                x0,
                y0,
                nmax,
                mmax,
                dx,
                dy,
                bathymetry_list=bathymetry_list,
                data_catalog=app.topography_data_catalog.catalog,
            )
            # Save grid
            model.grid.write()

            # Replot everything
            app.model[_MODEL].plot()
        except Exception as e:
            traceback.print_exc()
            dlg.close()
            app.gui.window.dialog_warning(f"Error generating grid:\n{e}")
            return
        dlg.close()

    def generate_depth_refinement(self) -> None:
        """Refine the grid based on bathymetry depth gradients."""
        group = _TB
        dlg = app.gui.window.dialog_wait("Generating refinement ...")
        try:
            model = app.model[_MODEL].domain

            bathymetry_list = app.toolbox[_TB].selected_bathymetry_datasets

            if bathymetry_list:
                model.grid.refine_depth(
                    bathymetry_list, data_catalog=app.topography_data_catalog.catalog
                )

                # Interpolate bathymetry onto the grid (Update: now done only for connect nodes)
                # model.grid.set_bathymetry(bathymetry_list, data_catalog=app.topography_data_catalog.catalog)

                # Save grid
                model.grid.write()

                # Replot everything
                app.model[_MODEL].plot()
            else:
                print("No bathymetry selected")
        except Exception as e:
            traceback.print_exc()
            dlg.close()
            app.gui.window.dialog_warning(f"Error generating depth refinement:\n{e}")
            return
        dlg.close()

    def generate_polygon_depth_refinement(self) -> None:
        """Refine the grid using both polygon extents and depth gradients."""
        group = _TB
        dlg = app.gui.window.dialog_wait("Generating refinement ...")
        try:
            model = app.model[_MODEL].domain

            bathymetry_list = app.toolbox[_TB].selected_bathymetry_datasets

            if bathymetry_list:
                model.grid.refine_polygon_depth(
                    bathymetry_list,
                    data_catalog=app.topography_data_catalog.catalog,
                    gdf=self.refinement_polygon,
                )

                # Interpolate bathymetry onto the grid (Update: now done only for connect nodes)
                # model.grid.set_bathymetry(bathymetry_list, data_catalog=app.topography_data_catalog.catalog)

                # Save grid
                model.grid.write()

                # Replot everything
                app.model[_MODEL].plot()
            else:
                print("No bathymetry selected")
        except Exception as e:
            traceback.print_exc()
            dlg.close()
            app.gui.window.dialog_warning(
                f"Error generating polygon depth refinement:\n{e}"
            )
            return
        dlg.close()

    def generate_polygon_refinement(self) -> None:
        """Refine the grid within user-drawn refinement polygons."""
        group = _TB
        dlg = app.gui.window.dialog_wait("Generating refinement ...")
        try:
            model = app.model[_MODEL].domain

            model.grid.refine_polygon(gdf=self.refinement_polygon)

            # Interpolate bathymetry onto the grid (Update: now done only for connect nodes)
            # bathymetry_list = app.toolbox[_TB].selected_bathymetry_datasets
            # if bathymetry_list:
            #     model.grid.set_bathymetry(bathymetry_list, data_catalog=app.topography_data_catalog.catalog)

            # Save grid
            model.grid.write()

            # Replot everything
            app.model[_MODEL].plot()
        except Exception as e:
            traceback.print_exc()
            dlg.close()
            app.gui.window.dialog_warning(f"Error generating polygon refinement:\n{e}")
            return
        dlg.close()

    def connect_nodes(self) -> None:
        """Connect hanging nodes and interpolate bathymetry onto the grid."""
        group = _TB
        dlg = app.gui.window.dialog_wait("Connecting nodes ...")
        try:
            model = app.model[_MODEL].domain

            bathymetry_list = app.toolbox[_TB].selected_bathymetry_datasets

            if bathymetry_list:
                model.grid.connect_nodes(
                    bathymetry_list, data_catalog=app.topography_data_catalog.catalog
                )
                app.model[_MODEL].domain.grid.set_bathymetry(
                    bathymetry_list, data_catalog=app.topography_data_catalog.catalog
                )

                # Save grid
                model.grid.write()

                # Replot everything
                app.model[_MODEL].plot()
            else:
                print("No bathymetry selected")
        except Exception as e:
            traceback.print_exc()
            dlg.close()
            app.gui.window.dialog_warning(f"Error connecting nodes:\n{e}")
            return
        dlg.close()

    def generate_bathymetry(self) -> None:
        """Interpolate bathymetry onto the grid from selected datasets."""
        dlg = app.gui.window.dialog_wait("Generating bathymetry ...")
        try:
            bathymetry_list = app.toolbox[_TB].selected_bathymetry_datasets
            app.model[_MODEL].domain.grid.set_bathymetry(
                bathymetry_list, data_catalog=app.topography_data_catalog.catalog
            )
            app.model[_MODEL].domain.grid.write()
        except Exception as e:
            traceback.print_exc()
            dlg.close()
            app.gui.window.dialog_warning(f"Error generating bathymetry:\n{e}")
            return
        dlg.close()

    def generate_bnd_coastline(self) -> None:
        """Generate open boundary points along the coastline."""
        dlg = app.gui.window.dialog_wait(
            "Creating open boundary based on coastline ..."
        )
        try:
            res = app.gui.getvar(_TB, "boundary_dx")
            if app.crs.is_geographic:
                res = res / 111111.0
            app.model[_MODEL].domain.boundary_conditions.generate_bnd(
                bnd_withcoastlines=True, resolution=res
            )
            app.model[_MODEL].domain.boundary_conditions.write_bnd()
            # app.model[_MODEL].domain.grid.write()
            # Replot everything
            app.model[_MODEL].plot()
        except Exception as e:
            traceback.print_exc()
            dlg.close()
            app.gui.window.dialog_warning(
                f"Error creating boundary from coastline:\n{e}"
            )
            return
        dlg.close()

    def generate_bnd_polygon(self) -> None:
        """Generate open boundary points within the drawn boundary polygon."""
        dlg = app.gui.window.dialog_wait("Creating open boundary based on polygon ...")
        try:
            gdf = self.open_boundary_polygon
            res = app.gui.getvar(_TB, "boundary_dx")
            if app.crs.is_geographic:
                res = res / 111111.0
            app.model[_MODEL].domain.boundary_conditions.generate_bnd(
                bnd_withpolygon=gdf, resolution=res
            )
            app.model[_MODEL].domain.boundary_conditions.write_bnd()
            # app.model[_MODEL].domain.grid.write()
            # Replot everything
            app.model[_MODEL].plot()
        except Exception as e:
            traceback.print_exc()
            dlg.close()
            app.gui.window.dialog_warning(f"Error creating boundary from polygon:\n{e}")
            return
        dlg.close()

    def load_bnd(self, fname: str) -> None:
        """Load boundary points from a .pli file.

        Parameters
        ----------
        fname : str
            Path to the boundary file.
        """
        dlg = app.gui.window.dialog_wait("Loading boundary ...")
        try:
            app.model[_MODEL].domain.boundary_conditions.load_bnd(file_name=fname)
            # app.model[_MODEL].domain.grid.write()
            # Replot everything
            app.model[_MODEL].plot()
        except Exception as e:
            traceback.print_exc()
            dlg.close()
            app.gui.window.dialog_warning(f"Error loading boundary:\n{e}")
            return
        dlg.close()

    def cut_polygon(self) -> None:
        """Delete grid cells that fall inside the exclude polygons."""
        dlg = app.gui.window.dialog_wait("Cutting Cells based on polygon ...")
        try:
            gdf = self.exclude_polygon
            app.model[_MODEL].domain.grid.delete_cells(delete_withpolygon=gdf)
            app.model[_MODEL].domain.grid.write()
            # Replot everything
            app.model[_MODEL].plot()
        except Exception as e:
            traceback.print_exc()
            dlg.close()
            app.gui.window.dialog_warning(f"Error cutting cells with polygon:\n{e}")
            return
        dlg.close()

    def cut_coastline(self) -> None:
        """Delete grid cells that fall on land based on the coastline."""
        dlg = app.gui.window.dialog_wait("Cutting Cells based on coastline ...")
        try:
            app.model[_MODEL].domain.grid.delete_cells(delete_withcoastlines=True)
            app.model[_MODEL].domain.grid.write()
            # Replot everything
            app.model[_MODEL].plot()
        except Exception as e:
            traceback.print_exc()
            dlg.close()
            app.gui.window.dialog_warning(f"Error cutting cells with coastline:\n{e}")
            return
        dlg.close()

    def build_model(self) -> None:
        """Build the complete model: generate grid and interpolate bathymetry."""
        self.generate_grid()
        self.generate_bathymetry()
        # self.update_mask()
        # self.generate_subgrid()

    #    def update_polygons(self): # This should really be moved to the callback modules

    # nrp = len(self.include_polygon)
    # incnames = []
    # for ip in range(nrp):
    #     incnames.append(str(ip + 1))
    # app.gui.setvar(_TB, "nr_include_polygons", nrp)
    # app.gui.setvar(_TB, "include_polygon_names", incnames)
    # app.gui.setvar(_TB, "include_polygon_index", max(nrp, 0))

    # nrp = len(self.exclude_polygon)
    # excnames = []
    # for ip in range(nrp):
    #     excnames.append(str(ip + 1))
    # app.gui.setvar(_TB, "nr_exclude_polygons", nrp)
    # app.gui.setvar(_TB, "exclude_polygon_names", excnames)
    # app.gui.setvar(_TB, "exclude_polygon_index", max(nrp, 0))

    # nrp = len(self.open_boundary_polygon)
    # bndnames = []
    # for ip in range(nrp):
    #     bndnames.append(str(ip + 1))
    # app.gui.setvar(_TB, "nr_open_boundary_polygons", nrp)
    # app.gui.setvar(_TB, "open_boundary_polygon_names", bndnames)

    # nrp = len(self.outflow_boundary_polygon)
    # bndnames = []
    # for ip in range(nrp):
    #     bndnames.append(str(ip + 1))
    # app.gui.setvar(_TB, "nr_outflow_boundary_polygons", nrp)
    # app.gui.setvar(_TB, "outflow_boundary_polygon_names", bndnames)

    # nrp = len(self.include_polygon_snapwave)
    # incnames = []
    # for ip in range(nrp):
    #     incnames.append(str(ip + 1))
    # app.gui.setvar(_TB, "nr_include_polygons_snapwave", nrp)
    # app.gui.setvar(_TB, "include_polygon_names_snapwave", incnames)

    # nrp = len(self.exclude_polygon_snapwave)
    # excnames = []
    # for ip in range(nrp):
    #     excnames.append(str(ip + 1))
    # app.gui.setvar(_TB, "nr_exclude_polygons_snapwave", nrp)
    # app.gui.setvar(_TB, "exclude_polygon_names_snapwave", excnames)

    # app.toolbox[_TB].write_include_polygon()
    # app.toolbox[_TB].write_exclude_polygon()
    # app.toolbox[_TB].write_boundary_polygon()

    # READ

    def read_refinement_polygon(self, file_name: Optional[str] = None) -> None:
        """Read refinement polygons from a GeoJSON file."""
        fname = app.gui.getvar(_TB, "refinement_polygon_file")
        self.refinement_polygon = gpd.read_file(fname)
        # app.toolbox[_TB].refinement_polygon_names.append(fname)
        # # Loop through rows in geodataframe and set refinement polygon names
        self.refinement_polygon_names = []
        for i in range(len(self.refinement_polygon)):
            self.refinement_polygon_names.append(
                self.refinement_polygon["refinement_polygon_name"][i]
            )
        if "min_edge_size" not in self.refinement_polygon.columns:
            self.refinement_polygon["min_edge_size"] = 500

    # def read_include_polygon(self):
    #     fname = app.gui.getvar(_TB, "include_polygon_file")
    #     self.include_polygon = gpd.read_file(fname)

    def read_exclude_polygon(self) -> None:
        """Read exclude polygons from a GeoJSON file."""
        fname = app.gui.getvar(_TB, "exclude_polygon_file")
        self.exclude_polygon = gpd.read_file(fname)
        self.exclude_polygon_names = []
        for i in range(len(self.exclude_polygon)):
            self.exclude_polygon_names.append(
                self.exclude_polygon["exclude_polygon_name"][i]
            )

    def read_open_boundary_polygon(self) -> None:
        """Read open boundary polygons from a GeoJSON file."""
        fname = app.gui.getvar(_TB, "open_boundary_polygon_file")
        self.open_boundary_polygon = gpd.read_file(fname)
        self.open_boundary_polygon_names = []
        for i in range(len(self.open_boundary_polygon)):
            self.open_boundary_polygon_names.append(
                self.open_boundary_polygon["open_boundary_polygon_name"][i]
            )

    # def read_outflow_boundary_polygon(self):
    #     fname = app.gui.getvar(_TB, "outflow_boundary_polygon_file")
    #     self.outflow_boundary_polygon = gpd.read_file(fname)

    # def read_include_polygon_snapwave(self):
    #     fname = app.gui.getvar(_TB, "include_polygon_file_snapwave")
    #     self.include_polygon_snapwave = gpd.read_file(fname)

    # def read_exclude_polygon_snapwave(self):
    #     fname = app.gui.getvar(_TB, "exclude_polygon_file_snapwave")
    #     self.exclude_polygon_snapwave = gpd.read_file(fname)

    # WRITE

    def write_refinement_polygon(self) -> None:
        """Write refinement polygons to a GeoJSON file."""
        if len(self.refinement_polygon) == 0:
            print("No refinement polygons defined")
            return
        gdf = gpd.GeoDataFrame(
            {
                "geometry": self.refinement_polygon["geometry"],
                "refinement_polygon_name": self.refinement_polygon_names,
                "min_edge_size": self.refinement_polygon["min_edge_size"],
            }
        )
        # index = app.gui.getvar(_TB, "refinement_polygon_index")
        # fname = app.gui.getvar(_TB, "refinement_polygon_names")
        fname = app.gui.getvar(_TB, "refinement_polygon_file")
        gdf.to_file(fname, driver="GeoJSON")

    # def write_include_polygon(self):
    #     if len(self.include_polygon) == 0:
    #         return
    #     gdf = gpd.GeoDataFrame(geometry=self.include_polygon["geometry"])
    #     fname = app.gui.getvar(_TB, "include_polygon_file")
    #     gdf.to_file(fname, driver='GeoJSON')

    def write_exclude_polygon(self) -> None:
        """Write exclude polygons to a GeoJSON file."""
        if len(self.exclude_polygon) == 0:
            return
        gdf = gpd.GeoDataFrame(
            {
                "geometry": self.exclude_polygon["geometry"],
                "exclude_polygon_name": self.exclude_polygon_names,
            }
        )
        fname = app.gui.getvar(_TB, "exclude_polygon_file")
        gdf.to_file(fname, driver="GeoJSON")

    def write_open_boundary_polygon(self) -> None:
        """Write open boundary polygons to a GeoJSON file."""
        if len(self.open_boundary_polygon) == 0:
            return
        gdf = gpd.GeoDataFrame(
            {
                "geometry": self.open_boundary_polygon["geometry"],
                "open_boundary_polygon_name": self.open_boundary_polygon_names,
            }
        )
        fname = app.gui.getvar(_TB, "open_boundary_polygon_file")
        gdf.to_file(fname, driver="GeoJSON")
        # gdf.to_file(fname, driver='ESRI Shapefile')

    # def write_outflow_boundary_polygon(self):
    #     if len(self.outflow_boundary_polygon) == 0:
    #         return
    #     gdf = gpd.GeoDataFrame(geometry=self.outflow_boundary_polygon["geometry"])
    #     fname = app.gui.getvar(_TB, "outflow_boundary_polygon_file")
    #     gdf.to_file(fname, driver='GeoJSON')

    # def write_include_polygon_snapwave(self):
    #     if len(self.include_polygon_snapwave) == 0:
    #         return
    #     gdf = gpd.GeoDataFrame(geometry=self.include_polygon_snapwave["geometry"])
    #     fname = app.gui.getvar(_TB, "include_polygon_file_snapwave")
    #     gdf.to_file(fname, driver='GeoJSON')

    # def write_exclude_polygon_snapwave(self):
    #     if len(self.exclude_polygon_snapwave) == 0:
    #         return
    #     gdf = gpd.GeoDataFrame(geometry=self.exclude_polygon_snapwave["geometry"])
    #     fname = app.gui.getvar(_TB, "exclude_polygon_file_snapwave")
    #     gdf.to_file(fname, driver='GeoJSON')

    # PLOT

    def plot_refinement_polygon(self) -> None:
        """Display the refinement polygons on the map."""
        layer = app.map.layer[_TB].layer["polygon_refinement"]
        layer.clear()
        layer.add_feature(self.refinement_polygon)

    # def plot_include_polygon(self):
    #     layer = app.map.layer[_TB].layer["include_polygon"]
    #     layer.clear()
    #     layer.add_feature(self.include_polygon)

    def plot_exclude_polygon(self) -> None:
        """Display the exclude polygons on the map."""
        layer = app.map.layer[_TB].layer["exclude_polygon"]
        layer.clear()
        layer.add_feature(self.exclude_polygon)

    def plot_open_boundary_polygon(self) -> None:
        """Display the open boundary polygons on the map."""
        layer = app.map.layer[_TB].layer["open_boundary_polygon"]
        layer.clear()
        layer.add_feature(self.open_boundary_polygon)

    # def plot_outflow_boundary_polygon(self):
    #     layer = app.map.layer[_TB].layer["outflow_boundary_polygon"]
    #     layer.clear()
    #     layer.add_feature(self.outflow_boundary_polygon)

    # def plot_include_polygon_snapwave(self):
    #     layer = app.map.layer[_TB].layer["include_polygon_snapwave"]
    #     layer.clear()
    #     layer.add_feature(self.include_polygon_snapwave)

    # def plot_exclude_polygon_snapwave(self):
    #     layer = app.map.layer[_TB].layer["exclude_polygon_snapwave"]
    #     layer.clear()
    #     layer.add_feature(self.exclude_polygon_snapwave)

    def read_setup_yaml(self, file_name: str) -> None:
        """Read a YAML setup file and configure the toolbox accordingly.

        Parameters
        ----------
        file_name : str
            Path to the YAML setup file.
        """
        # First set some default gui variables
        group = _TB
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

        group = _TB
        # Coordinates
        app.gui.setvar(group, "x0", dct["coordinates"]["x0"])
        app.gui.setvar(group, "y0", dct["coordinates"]["y0"])
        app.gui.setvar(group, "dx", dct["coordinates"]["dx"])
        app.gui.setvar(group, "dy", dct["coordinates"]["dy"])
        app.gui.setvar(group, "nmax", dct["coordinates"]["nmax"])
        app.gui.setvar(group, "mmax", dct["coordinates"]["mmax"])
        app.model[_MODEL].domain.crs = CRS(dct["coordinates"]["crs"])

        # Refinement and polygons
        if "refinement" in dct:
            if "polygon_file" in dct["refinement"]:
                app.gui.setvar(
                    group, "refinement_polygon_file", dct["refinement"]["polygon_file"]
                )
                self.read_refinement_polygon()
                self.plot_refinement_polygon()
                # import the function update() from refinement.py
                from .refinement import update as update_refinement

                update_refinement()

                # nrp = len(app.toolbox[_TB].refinement_polygon)
                # app.gui.setvar(_TB, "nr_refinement_polygons", nrp)
                # refnames = app.toolbox[_TB].refinement_polygon_names
                # app.gui.setvar(_TB, "refinement_polygon_names", refnames)

        if "exclude" in dct:
            if "polygon_file" in dct["exclude"]:
                app.gui.setvar(
                    group, "exclude_polygon_file", dct["exclude"]["polygon_file"]
                )
                self.read_exclude_polygon()
                self.plot_exclude_polygon()
                # import the function update() from exclude.py
                from .exclude import update as update_exclude

                update_exclude()

        if "open_boundary" in dct:
            if "polygon_file" in dct["open_boundary"]:
                app.gui.setvar(
                    group,
                    "open_boundary_polygon_file",
                    dct["open_boundary"]["polygon_file"],
                )
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
            app.toolbox[_TB].selected_bathymetry_datasets.append(dataset)
            dataset_names.append(name)
        app.gui.setvar(_TB, "selected_bathymetry_dataset_names", dataset_names)
        app.gui.setvar(_TB, "selected_bathymetry_dataset_index", 0)
        app.gui.setvar(_TB, "nr_selected_bathymetry_datasets", len(dataset_names))

        layer = app.map.layer[_TB].layer["grid_outline"]
        lenx = dct["coordinates"]["mmax"] * dct["coordinates"]["dx"]
        leny = dct["coordinates"]["nmax"] * dct["coordinates"]["dy"]
        layer.add_rectangle(
            dct["coordinates"]["x0"], dct["coordinates"]["y0"], lenx, leny, 0
        )

    def write_setup_yaml(self) -> None:
        """Write the current toolbox configuration to a YAML file."""
        group = _TB
        dct = {}
        # Coordinates
        dct["coordinates"] = {}
        dct["coordinates"]["x0"] = float(app.gui.getvar(group, "x0"))
        dct["coordinates"]["y0"] = float(app.gui.getvar(group, "y0"))
        dct["coordinates"]["dx"] = float(app.gui.getvar(group, "dx"))
        dct["coordinates"]["dy"] = float(app.gui.getvar(group, "dy"))
        dct["coordinates"]["nmax"] = int(app.gui.getvar(group, "nmax"))
        dct["coordinates"]["mmax"] = int(app.gui.getvar(group, "mmax"))
        dct["coordinates"]["crs"] = app.model[_MODEL].domain.crs.name

        # Refinements
        dct["refinement"] = {}
        if len(app.toolbox[_TB].refinement_polygon) > 0:
            dct["refinement"]["polygon_file"] = app.gui.getvar(
                _TB, "refinement_polygon_file"
            )
        dct["exclude"] = {}
        if len(app.toolbox[_TB].exclude_polygon) > 0:
            dct["exclude"]["polygon_file"] = app.gui.getvar(_TB, "exclude_polygon_file")
        dct["open_boundary"] = {}
        if len(app.toolbox[_TB].open_boundary_polygon) > 0:
            dct["open_boundary"]["polygon_file"] = app.gui.getvar(
                _TB, "open_boundary_polygon_file"
            )

        # Bathymetry
        dct["bathymetry"] = {}
        dct["bathymetry"]["dataset"] = []
        for d in app.toolbox[_TB].selected_bathymetry_datasets:
            dataset = {}
            dataset["name"] = d["name"]
            dataset["source"] = "delftdashboard"
            dataset["zmin"] = d["zmin"]
            dataset["zmax"] = d["zmax"]
            dct["bathymetry"]["dataset"].append(dataset)

        self.setup_dict = dct

        dict2yaml("model_setup.yml", dct)

        # Write out polygons
        app.toolbox[_TB].write_exclude_polygon()
        app.toolbox[_TB].write_open_boundary_polygon()
        app.toolbox[_TB].write_refinement_polygon()


def gdf2list(gdf_in: gpd.GeoDataFrame) -> List[gpd.GeoDataFrame]:
    """Split a GeoDataFrame into a list of single-feature GeoDataFrames.

    Parameters
    ----------
    gdf_in : gpd.GeoDataFrame
        Input GeoDataFrame with one or more features.

    Returns
    -------
    list of gpd.GeoDataFrame
        Each element contains a single feature.
    """
    gdf_out = []
    for feature in gdf_in.iterfeatures():
        gdf_out.append(gpd.GeoDataFrame.from_features([feature]))
    return gdf_out
