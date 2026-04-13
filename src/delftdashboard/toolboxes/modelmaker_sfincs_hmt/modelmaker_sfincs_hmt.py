"""Main toolbox class for the SFINCS HMT model-maker in DelftDashboard.

Provides grid generation, bathymetry interpolation, mask creation, sub-grid
table computation, and polygon I/O for the SFINCS model-maker workflow.
"""

from __future__ import annotations

import traceback
from typing import List

import geopandas as gpd
import numpy as np
import pandas as pd
from cht_utils.fileio.yaml import dict2yaml, yaml2dict
from pyproj import CRS

from delftdashboard.app import app
from delftdashboard.misc.gdfutils import mpol2pol
from delftdashboard.operations import map
from delftdashboard.operations.toolbox import GenericToolbox

_TB = "modelmaker_sfincs_hmt"
_MODEL = "sfincs_hmt"


class Toolbox(GenericToolbox):
    """SFINCS HMT model-maker toolbox.

    Manages grid outline, mask polygons, refinement polygons, bathymetry,
    roughness, and sub-grid settings for the SFINCS model-maker workflow.
    """

    def __init__(self, name: str) -> None:
        super().__init__()

        self.name = name
        self.long_name = "Model Maker"

    def initialize(self) -> None:
        """Initialize toolbox state, polygon storage, and GUI variables."""
        # Set variables

        # Grid outline
        self.grid_outline = gpd.GeoDataFrame()

        # Bathymetry
        self.selected_bathymetry_datasets = []

        # Include polygons
        self.include_polygon = gpd.GeoDataFrame()
        self.include_polygon_changed = False

        # Exclude polygons
        self.exclude_polygon = gpd.GeoDataFrame()
        self.exclude_polygon_changed = False

        # Boundary polygons
        self.open_boundary_polygon = gpd.GeoDataFrame()
        self.downstream_boundary_polygon = gpd.GeoDataFrame()
        self.neumann_boundary_polygon = gpd.GeoDataFrame()
        self.outflow_boundary_polygon = gpd.GeoDataFrame()
        self.open_boundary_polygon_changed = False
        self.downstream_boundary_polygon_changed = False
        self.neumann_boundary_polygon_changed = False
        self.outflow_boundary_polygon_changed = False

        # Include polygons SnapWave
        self.include_polygon_snapwave = gpd.GeoDataFrame()
        self.include_polygon_snapwave_changed = False

        # Exclude polygons SnapWave
        self.exclude_polygon_snapwave = gpd.GeoDataFrame()
        self.exclude_polygon_snapwave_changed = False

        # Boundary polygons SnapWave
        self.open_boundary_polygon_snapwave = gpd.GeoDataFrame()
        self.neumann_boundary_polygon_snapwave = gpd.GeoDataFrame()
        self.open_boundary_polygon_snapwave_changed = False
        self.neumann_boundary_polygon_snapwave_changed = False

        # Refinement
        self.refinement_levels = []
        self.refinement_zmin = []
        self.refinement_zmax = []
        self.refinement_polygon = gpd.GeoDataFrame()
        self.refinement_polygon_changed = False

        self.setup_dict = {}

        # Set GUI variable
        group = _TB

        app.gui.setvar(group, "build_quadtree_grid", True)
        app.gui.setvar(group, "use_snapwave", False)
        app.gui.setvar(group, "use_subgrid", False)

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
        self.lenx = 0.0
        self.leny = 0.0

        app.gui.setvar(group, "rotation", 0.0)

        app.gui.setvar(group, "show_mask_polygons_in_domain_tab", False)

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
        app.gui.setvar(_TB, "refinement_polygon_levels", levstr)

        # Mask
        app.gui.setvar(group, "zmax", 100000.0)
        app.gui.setvar(group, "zmin", -100000.0)
        app.gui.setvar(group, "use_mask_global", False)
        app.gui.setvar(group, "global_zmax", 10.0)
        app.gui.setvar(group, "global_zmin", -10.0)
        app.gui.setvar(group, "include_polygon_file", "include.geojson")
        app.gui.setvar(group, "include_polygon_names", [])
        app.gui.setvar(group, "include_polygon_index", 0)
        app.gui.setvar(group, "nr_include_polygons", 0)
        app.gui.setvar(group, "include_zmax", 99999.0)
        app.gui.setvar(group, "include_zmin", -99999.0)
        app.gui.setvar(group, "exclude_polygon_file", "exclude.geojson")
        app.gui.setvar(group, "exclude_polygon_names", [])
        app.gui.setvar(group, "exclude_polygon_index", 0)
        app.gui.setvar(group, "nr_exclude_polygons", 0)
        app.gui.setvar(group, "exclude_zmax", 99999.0)
        app.gui.setvar(group, "exclude_zmin", -99999.0)

        app.gui.setvar(group, "open_boundary_polygon_file", "open_boundary.geojson")
        app.gui.setvar(group, "open_boundary_polygon_names", [])
        app.gui.setvar(group, "open_boundary_polygon_index", 0)
        app.gui.setvar(group, "nr_open_boundary_polygons", 0)
        app.gui.setvar(group, "open_boundary_zmax", 99999.0)
        app.gui.setvar(group, "open_boundary_zmin", -99999.0)

        app.gui.setvar(
            group, "downstream_boundary_polygon_file", "downstream_boundary.geojson"
        )
        app.gui.setvar(group, "downstream_boundary_polygon_names", [])
        app.gui.setvar(group, "downstream_boundary_polygon_index", 0)
        app.gui.setvar(group, "nr_downstream_boundary_polygons", 0)
        app.gui.setvar(group, "downstream_boundary_zmax", 99999.0)
        app.gui.setvar(group, "downstream_boundary_zmin", -99999.0)

        app.gui.setvar(
            group, "neumann_boundary_polygon_file", "neumann_boundary.geojson"
        )
        app.gui.setvar(group, "neumann_boundary_polygon_names", [])
        app.gui.setvar(group, "neumann_boundary_polygon_index", 0)
        app.gui.setvar(group, "nr_neumann_boundary_polygons", 0)
        app.gui.setvar(group, "neumann_boundary_zmax", 99999.0)
        app.gui.setvar(group, "neumann_boundary_zmin", -99999.0)

        app.gui.setvar(
            group, "outflow_boundary_polygon_file", "outflow_boundary.geojson"
        )
        app.gui.setvar(group, "outflow_boundary_polygon_names", [])
        app.gui.setvar(group, "outflow_boundary_polygon_index", 0)
        app.gui.setvar(group, "nr_outflow_boundary_polygons", 0)
        app.gui.setvar(group, "outflow_boundary_zmax", 99999.0)
        app.gui.setvar(group, "outflow_boundary_zmin", -99999.0)

        app.gui.setvar(group, "use_mask_snapwave_global", True)
        app.gui.setvar(group, "global_zmax_snapwave", 2.0)
        app.gui.setvar(group, "global_zmin_snapwave", -99999.0)
        app.gui.setvar(
            group, "include_polygon_file_snapwave", "include_snapwave.geojson"
        )
        app.gui.setvar(group, "include_polygon_names_snapwave", [])
        app.gui.setvar(group, "include_polygon_index_snapwave", 0)
        app.gui.setvar(group, "nr_include_polygons_snapwave", 0)
        app.gui.setvar(group, "include_zmax_snapwave", 99999.0)
        app.gui.setvar(group, "include_zmin_snapwave", -99999.0)
        app.gui.setvar(
            group, "exclude_polygon_file_snapwave", "exclude_snapwave.geojson"
        )
        app.gui.setvar(group, "exclude_polygon_names_snapwave", [])
        app.gui.setvar(group, "exclude_polygon_index_snapwave", 0)
        app.gui.setvar(group, "nr_exclude_polygons_snapwave", 0)
        app.gui.setvar(group, "exclude_zmax_snapwave", 99999.0)
        app.gui.setvar(group, "exclude_zmin_snapwave", -99999.0)

        app.gui.setvar(
            group,
            "open_boundary_polygon_file_snapwave",
            "open_boundary_snapwave.geojson",
        )
        app.gui.setvar(group, "open_boundary_polygon_names_snapwave", [])
        app.gui.setvar(group, "open_boundary_polygon_index_snapwave", 0)
        app.gui.setvar(group, "nr_open_boundary_polygons_snapwave", 0)
        app.gui.setvar(group, "open_boundary_zmax_snapwave", 99999.0)
        app.gui.setvar(group, "open_boundary_zmin_snapwave", -99999.0)

        app.gui.setvar(
            group,
            "neumann_boundary_polygon_file_snapwave",
            "neumann_boundary_snapwave.geojson",
        )
        app.gui.setvar(group, "neumann_boundary_polygon_names_snapwave", [])
        app.gui.setvar(group, "neumann_boundary_polygon_index_snapwave", 0)
        app.gui.setvar(group, "nr_neumann_boundary_polygons_snapwave", 0)
        app.gui.setvar(group, "neumann_boundary_zmax_snapwave", 99999.0)
        app.gui.setvar(group, "neumann_boundary_zmin_snapwave", -99999.0)

        # Roughness
        app.gui.setvar(group, "manning_land", 0.06)
        app.gui.setvar(group, "manning_water", 0.02)
        app.gui.setvar(group, "manning_level", 1.0)

        # Subgrid
        app.gui.setvar(group, "subgrid_nr_levels", 10)
        app.gui.setvar(group, "subgrid_nr_pixels", 20)
        app.gui.setvar(group, "subgrid_max_dzdv", 999.0)
        app.gui.setvar(group, "subgrid_manning_max", 0.024)
        app.gui.setvar(group, "subgrid_manning_z_cutoff", -99999.0)
        app.gui.setvar(group, "subgrid_zmin", -99999.0)

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
        """Register all map layers for this toolbox (grid outline, polygons, etc.)."""
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
            polygon_fill_opacity=0.1,
            rotate=not app.crs.is_geographic,
        )

        ### Mask
        # Include
        from .mask_active_cells import (
            include_polygon_created,
            include_polygon_modified,
            include_polygon_selected,
        )

        layer.add_layer(
            "include_polygon",
            type="draw",
            shape="polygon",
            create=include_polygon_created,
            modify=include_polygon_modified,
            select=include_polygon_selected,
            polygon_line_color="limegreen",
            polygon_fill_color="limegreen",
            polygon_fill_opacity=0.1,
        )
        # Exclude
        from .mask_active_cells import (
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
            polygon_fill_opacity=0.1,
        )
        # Open boundary
        from .mask_boundary_cells import (
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
            polygon_fill_opacity=0.1,
        )
        # Downstream boundary
        from .mask_boundary_cells import (
            downstream_boundary_polygon_created,
            downstream_boundary_polygon_modified,
            downstream_boundary_polygon_selected,
        )

        layer.add_layer(
            "downstream_boundary_polygon",
            type="draw",
            shape="polygon",
            create=downstream_boundary_polygon_created,
            modify=downstream_boundary_polygon_modified,
            select=downstream_boundary_polygon_selected,
            polygon_line_color="purple",
            polygon_fill_color="purple",
            polygon_fill_opacity=0.1,
        )
        # Neumann boundary
        from .mask_boundary_cells import (
            neumann_boundary_polygon_created,
            neumann_boundary_polygon_modified,
            neumann_boundary_polygon_selected,
        )

        layer.add_layer(
            "neumann_boundary_polygon",
            type="draw",
            shape="polygon",
            create=neumann_boundary_polygon_created,
            modify=neumann_boundary_polygon_modified,
            select=neumann_boundary_polygon_selected,
            polygon_line_color="magenta",
            polygon_fill_color="magenta",
            polygon_fill_opacity=0.1,
        )
        # Outflow boundary
        from .mask_boundary_cells import (
            outflow_boundary_polygon_created,
            outflow_boundary_polygon_modified,
            outflow_boundary_polygon_selected,
        )

        layer.add_layer(
            "outflow_boundary_polygon",
            type="draw",
            shape="polygon",
            create=outflow_boundary_polygon_created,
            modify=outflow_boundary_polygon_modified,
            select=outflow_boundary_polygon_selected,
            polygon_line_color="orange",
            polygon_fill_color="orange",
            polygon_fill_opacity=0.1,
        )

        ### Mask SnapWave
        # Include
        from .mask_active_cells_snapwave import (
            include_polygon_created_snapwave,
            include_polygon_modified_snapwave,
            include_polygon_selected_snapwave,
        )

        layer.add_layer(
            "include_polygon_snapwave",
            type="draw",
            shape="polygon",
            create=include_polygon_created_snapwave,
            modify=include_polygon_modified_snapwave,
            select=include_polygon_selected_snapwave,
            polygon_line_color="limegreen",
            polygon_fill_color="limegreen",
            polygon_fill_opacity=0.1,
        )
        # Exclude
        from .mask_active_cells_snapwave import (
            exclude_polygon_created_snapwave,
            exclude_polygon_modified_snapwave,
            exclude_polygon_selected_snapwave,
        )

        layer.add_layer(
            "exclude_polygon_snapwave",
            type="draw",
            shape="polygon",
            create=exclude_polygon_created_snapwave,
            modify=exclude_polygon_modified_snapwave,
            select=exclude_polygon_selected_snapwave,
            polygon_line_color="orangered",
            polygon_fill_color="orangered",
            polygon_fill_opacity=0.1,
        )
        # SnapWave boundaries
        from .mask_boundary_cells_snapwave import (
            open_boundary_polygon_created_snapwave,
            open_boundary_polygon_modified_snapwave,
            open_boundary_polygon_selected_snapwave,
        )

        layer.add_layer(
            "open_boundary_polygon_snapwave",
            type="draw",
            shape="polygon",
            create=open_boundary_polygon_created_snapwave,
            modify=open_boundary_polygon_modified_snapwave,
            select=open_boundary_polygon_selected_snapwave,
            polygon_line_color="deepskyblue",
            polygon_fill_color="deepskyblue",
            polygon_fill_opacity=0.1,
        )
        from .mask_boundary_cells_snapwave import (
            neumann_boundary_polygon_created_snapwave,
            neumann_boundary_polygon_modified_snapwave,
            neumann_boundary_polygon_selected_snapwave,
        )

        layer.add_layer(
            "neumann_boundary_polygon_snapwave",
            type="draw",
            shape="polygon",
            create=neumann_boundary_polygon_created_snapwave,
            modify=neumann_boundary_polygon_modified_snapwave,
            select=neumann_boundary_polygon_selected_snapwave,
            polygon_line_color="red",
            polygon_fill_color="orange",
            polygon_fill_opacity=0.1,
        )

        # Refinement polygons
        from .quadtree import (
            refinement_polygon_created,
            refinement_polygon_modified,
            refinement_polygon_selected,
        )

        layer.add_layer(
            "quadtree_refinement",
            type="draw",
            columns={"refinement_level": 1, "zmin": -99999.0, "zmax": 99999.0},
            shape="polygon",
            create=refinement_polygon_created,
            modify=refinement_polygon_modified,
            select=refinement_polygon_selected,
            polygon_line_color="red",
            polygon_fill_color="orange",
            polygon_fill_opacity=0.1,
        )

    def set_crs(self) -> None:
        """Reset toolbox state and layers when the coordinate reference system changes."""
        # # Called when the CRS is changed
        # # Here we should reset x0, y0, dx, dy etc.
        # # Also clear the grid outline
        # group = _TB
        # app.gui.setvar(group, "x0", 0.0)
        # app.gui.setvar(group, "y0", 0.0)
        # app.gui.setvar(group, "nmax", 0)
        # app.gui.setvar(group, "mmax", 0)
        # if app.crs.is_geographic:
        #     app.gui.setvar(group, "dx", 0.1)
        #     app.gui.setvar(group, "dy", 0.1)
        # else:
        #     app.gui.setvar(group, "dx", 1000.0)
        #     app.gui.setvar(group, "dy", 1000.0)
        # self.lenx = 0.0
        # self.leny = 0.0
        # # Clear the grid outline
        # app.map.layer[_TB].layer["grid_outline"].clear()
        # # Should we also remove all existing polygons? Refinement and mask?
        self.initialize()
        self.clear_layers()
        # Update rotation setting for the grid outline draw layer
        can_rotate = not app.crs.is_geographic
        layer = app.map.layer.get(_TB)
        if layer and "grid_outline" in layer.layer:
            layer.layer["grid_outline"].set_paint_property("rotate", can_rotate)

    def generate_grid(self) -> None:
        """Generate the quadtree grid from current GUI parameters and refinement polygons."""
        group = _TB
        dlg = app.gui.window.dialog_wait("Generating grid ...")
        try:
            model = app.model[_MODEL].domain
            epsg = app.crs.to_epsg()
            x0 = app.gui.getvar(group, "x0")
            y0 = app.gui.getvar(group, "y0")
            dx = app.gui.getvar(group, "dx")
            dy = app.gui.getvar(group, "dy")
            nmax = app.gui.getvar(group, "nmax")
            mmax = app.gui.getvar(group, "mmax")
            rotation = app.gui.getvar(group, "rotation")
            model.config.set("qtrfile", "sfincs.nc")
            app.gui.setvar(_MODEL, "qtrfile", "sfincs.nc")

            if len(self.refinement_polygon) == 0:
                refpol = None
            else:
                refpol = self.refinement_polygon

            model.quadtree_grid.create(
                x0,
                y0,
                nmax,
                mmax,
                dx,
                dy,
                rotation,
                epsg,
                refinement_polygons=refpol,
            )

            model.quadtree_grid.write()
            app.model[_MODEL].plot()
        except Exception as e:
            traceback.print_exc()
            dlg.close()
            app.gui.window.dialog_warning(f"Error generating grid:\n{e}")
            return
        dlg.close()

    def generate_bathymetry(self) -> None:
        """Interpolate bathymetry onto the quadtree grid from selected datasets."""
        dlg = app.gui.window.dialog_wait("Generating bathymetry ...")
        try:
            app.model[_MODEL].domain.quadtree_elevation.create(
                app.selected_bathymetry_datasets,
                zmin=app.gui.getvar(_TB, "zmin"),
                zmax=app.gui.getvar(_TB, "zmax"),
            )
            app.model[_MODEL].domain.quadtree_grid.write()
        except Exception as e:
            traceback.print_exc()
            dlg.close()
            app.gui.window.dialog_warning(f"Error generating bathymetry:\n{e}")
            return
        dlg.close()

    def update_mask(self) -> None:
        """Regenerate the SFINCS active-cell and boundary mask from current settings."""
        # Should improve on this check
        grid = app.model[_MODEL].domain.quadtree_grid
        mask = app.model[_MODEL].domain.quadtree_mask
        z = app.model[_MODEL].domain.quadtree_elevation.data["z"]
        if np.all(np.isnan(z)):
            app.gui.window.dialog_warning("Please first generate a bathymetry !")
            return
        dlg = app.gui.window.dialog_wait("Updating mask ...")
        if app.gui.getvar(_TB, "use_mask_global"):
            global_zmin = app.gui.getvar(_TB, "global_zmin")
            global_zmax = app.gui.getvar(_TB, "global_zmax")
        else:
            # Set zmax lower than zmin to avoid use of global mask
            global_zmin = 10.0
            global_zmax = -10.0

        try:
            mask.create(
                model="sfincs",
                zmin=global_zmin,
                zmax=global_zmax,
                include_polygon=app.toolbox[_TB].include_polygon,
                include_zmin=app.gui.getvar(_TB, "include_zmin"),
                include_zmax=app.gui.getvar(_TB, "include_zmax"),
                exclude_polygon=app.toolbox[_TB].exclude_polygon,
                exclude_zmin=app.gui.getvar(_TB, "exclude_zmin"),
                exclude_zmax=app.gui.getvar(_TB, "exclude_zmax"),
                open_boundary_polygon=app.toolbox[_TB].open_boundary_polygon,
                open_boundary_zmin=app.gui.getvar(_TB, "open_boundary_zmin"),
                open_boundary_zmax=app.gui.getvar(_TB, "open_boundary_zmax"),
                downstream_boundary_polygon=app.toolbox[
                    _TB
                ].downstream_boundary_polygon,
                downstream_boundary_zmin=app.gui.getvar(
                    _TB, "downstream_boundary_zmin"
                ),
                downstream_boundary_zmax=app.gui.getvar(
                    _TB, "downstream_boundary_zmax"
                ),
                neumann_boundary_polygon=app.toolbox[_TB].neumann_boundary_polygon,
                neumann_boundary_zmin=app.gui.getvar(_TB, "neumann_boundary_zmin"),
                neumann_boundary_zmax=app.gui.getvar(_TB, "neumann_boundary_zmax"),
                outflow_boundary_polygon=app.toolbox[_TB].outflow_boundary_polygon,
                outflow_boundary_zmin=app.gui.getvar(_TB, "outflow_boundary_zmin"),
                outflow_boundary_zmax=app.gui.getvar(_TB, "outflow_boundary_zmax"),
            )
        except Exception as e:
            traceback.print_exc()
            dlg.close()
            app.gui.window.dialog_warning(f"Error updating mask:\n{e}")
            return

        app.map.layer[_MODEL].layer["mask"].set_data(mask)

        # if app.model[_MODEL].domain.grid_type == "quadtree":
        grid.write()  # Write new qtr file
        # else:
        #     mask.write() # Write mask, index and depth files

        dlg.close()

    def update_mask_snapwave(self) -> None:
        """Regenerate the SnapWave active-cell mask from current settings."""
        grid = app.model[_MODEL].domain.quadtree_grid
        mask = app.model[_MODEL].domain.quadtree_snapwave_mask
        if np.all(np.isnan(grid.data["z"])):
            app.gui.window.dialog_warning("Please first generate a bathymetry !")
            return

        try:
            dlg = app.gui.window.dialog_wait("Updating SnapWave mask ...")
            if app.gui.getvar(_TB, "use_mask_snapwave_global"):
                global_zmin = app.gui.getvar(_TB, "global_zmin_snapwave")
                global_zmax = app.gui.getvar(_TB, "global_zmax_snapwave")
            else:
                # Set zmax lower than zmin to avoid use of global mask
                global_zmin = 10.0
                global_zmax = -10.0

            mask.build(
                zmin=global_zmin,
                zmax=global_zmax,
                include_polygon=app.toolbox[_TB].include_polygon_snapwave,
                include_zmin=app.gui.getvar(_TB, "include_zmin_snapwave"),
                include_zmax=app.gui.getvar(_TB, "include_zmax_snapwave"),
                exclude_polygon=app.toolbox[_TB].exclude_polygon_snapwave,
                exclude_zmin=app.gui.getvar(_TB, "exclude_zmin_snapwave"),
                exclude_zmax=app.gui.getvar(_TB, "exclude_zmax_snapwave"),
                open_boundary_polygon=app.toolbox[_TB].open_boundary_polygon_snapwave,
                open_boundary_zmin=app.gui.getvar(_TB, "open_boundary_zmin_snapwave"),
                open_boundary_zmax=app.gui.getvar(_TB, "open_boundary_zmax_snapwave"),
                neumann_boundary_polygon=app.toolbox[
                    _TB
                ].neumann_boundary_polygon_snapwave,
                neumann_boundary_zmin=app.gui.getvar(
                    _TB, "neumann_boundary_zmin_snapwave"
                ),
                neumann_boundary_zmax=app.gui.getvar(
                    _TB, "neumann_boundary_zmax_snapwave"
                ),
            )

            app.map.layer[_MODEL].layer["mask_snapwave"].set_data(mask)
            grid.write()

            dlg.close()

        except Exception as e:
            traceback.print_exc()
            dlg.close()
            app.gui.window.dialog_warning(str(e))
            return

    def generate_subgrid(self) -> None:
        """Generate sub-grid tables from high-resolution bathymetry data."""
        group = _TB
        # bathymetry_sets = app.toolbox[_TB].selected_bathymetry_datasets
        bathymetry_sets = app.selected_bathymetry_datasets
        roughness_sets = []
        manning_land = app.gui.getvar(group, "manning_land")
        manning_water = app.gui.getvar(group, "manning_water")
        manning_level = app.gui.getvar(group, "manning_level")
        nr_levels = app.gui.getvar(group, "subgrid_nr_levels")
        nr_pixels = app.gui.getvar(group, "subgrid_nr_pixels")
        max_dzdv = app.gui.getvar(group, "subgrid_max_dzdv")
        manning_max = app.gui.getvar(group, "subgrid_manning_max")
        manning_z_cutoff = app.gui.getvar(group, "subgrid_manning_z_cutoff")
        zmin = app.gui.getvar(group, "zmin")
        zmax = app.gui.getvar(group, "zmax")
        p = app.gui.window.dialog_progress(
            "               Generating Sub-grid Tables ...                ", 100
        )

        try:
            sbgfile = "sfincs_subgrid.nc"

            app.model[_MODEL].domain.quadtree_subgrid.create(
                bathymetry_sets,
                roughness_sets,
                manning_land=manning_land,
                manning_water=manning_water,
                manning_level=manning_level,
                nr_levels=nr_levels,
                nr_subgrid_pixels=nr_pixels,
                max_gradient=max_dzdv,
                zmin=zmin,
                zmax=zmax,
                write_dep_tif=False,
                progress_bar=p,
            )

            # Now write the subgrid tables to a netCDF file
            app.model[_MODEL].domain.quadtree_subgrid.write(sbgfile)

            p.close()

        except Exception as e:
            traceback.print_exc()
            p.close()
            app.gui.window.dialog_critical(
                f"Error generating sub-grid tables: {str(e)}"
            )
            return

        app.model[_MODEL].domain.config.set("sbgfile", sbgfile)
        app.gui.setvar(_MODEL, "sbgfile", sbgfile)
        app.gui.setvar(_MODEL, "bathymetry_type", "subgrid")

    def cut_inactive_cells(self) -> None:
        """Remove inactive cells from the quadtree grid and rewrite grid files."""
        dlg = app.gui.window.dialog_wait("Cutting Inactive Cells ...")
        try:
            app.model[_MODEL].domain.quadtree_grid.cut_inactive_cells()
            app.model[_MODEL].domain.quadtree_grid.write()
            app.model[_MODEL].plot()
        except Exception as e:
            traceback.print_exc()
            dlg.close()
            app.gui.window.dialog_warning(f"Error cutting inactive cells:\n{e}")
            return
        dlg.close()

    def build_model(self) -> None:
        """Build the full SFINCS model: grid, bathymetry, mask, and optionally sub-grid."""
        self.generate_grid()
        self.generate_bathymetry()
        self.update_mask()
        if app.gui.getvar(_TB, "use_snapwave"):
            self.update_mask_snapwave()
        if app.gui.getvar(_TB, "use_subgrid"):
            self.generate_subgrid()

    # READ

    def read_refinement_polygon(self, file_name: str, append: bool) -> None:
        """Read refinement polygons from a GeoJSON file.

        Parameters
        ----------
        file_name : str
            Path to the GeoJSON file containing refinement polygons.
        append : bool
            If True, append to existing polygons; otherwise replace them.
        """
        # Should we make this part of hmt_sfincs?
        # fname = app.gui.getvar(_TB, "refinement_polygon_file")
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
            self.refinement_polygon = gpd.GeoDataFrame(
                pd.concat(
                    [self.refinement_polygon, refinement_polygon], ignore_index=True
                )
            )
        else:
            self.refinement_polygon = refinement_polygon

    def read_include_polygon(self, fname: str, append: bool) -> None:
        """Read include polygons from a file.

        Parameters
        ----------
        fname : str
            Path to the polygon file.
        append : bool
            If True, append to existing polygons; otherwise replace them.
        """
        if not append:
            # New file
            # The include polygon should always be called include.geojson and saved to the
            # current working directory
            self.include_polygon = mpol2pol(gpd.read_file(fname)).to_crs(app.crs)
        else:
            # Append to existing file
            gdf = mpol2pol(gpd.read_file(fname)).to_crs(app.crs)
            self.include_polygon = gpd.GeoDataFrame(
                pd.concat([self.include_polygon, gdf], ignore_index=True)
            )

    def read_exclude_polygon(self, fname: str, append: bool) -> None:
        """Read exclude polygons from a file.

        Parameters
        ----------
        fname : str
            Path to the polygon file.
        append : bool
            If True, append to existing polygons; otherwise replace them.
        """
        if not append:
            # New file
            self.exclude_polygon = mpol2pol(gpd.read_file(fname)).to_crs(app.crs)
        else:
            # Append to existing file
            gdf = mpol2pol(gpd.read_file(fname))
            self.exclude_polygon = gpd.GeoDataFrame(
                pd.concat([self.exclude_polygon, gdf], ignore_index=True)
            )

    def read_open_boundary_polygon(self, fname: str, append: bool) -> None:
        """Read open boundary polygons from a file.

        Parameters
        ----------
        fname : str
            Path to the polygon file.
        append : bool
            If True, append to existing polygons; otherwise replace them.
        """
        if not append:
            # New file
            # app.gui.setvar(_TB, "open_boundary_polygon_file", fname)
            self.open_boundary_polygon = mpol2pol(gpd.read_file(fname)).to_crs(app.crs)
        else:
            # Append to existing file
            gdf = mpol2pol(gpd.read_file(fname)).to_crs
            self.open_boundary_polygon = gpd.GeoDataFrame(
                pd.concat([self.open_boundary_polygon, gdf], ignore_index=True)
            )

    def read_downstream_boundary_polygon(self, fname: str, append: bool) -> None:
        """Read downstream boundary polygons from a file.

        Parameters
        ----------
        fname : str
            Path to the polygon file.
        append : bool
            If True, append to existing polygons; otherwise replace them.
        """
        if not append:
            # New file
            # app.gui.setvar(_TB, "downstream_boundary_polygon_file", fname)
            self.downstream_boundary_polygon = mpol2pol(gpd.read_file(fname)).to_crs(
                app.crs
            )
        else:
            # Append to existing file
            gdf = mpol2pol(gpd.read_file(fname)).to_crs(app.crs)
            self.downstream_boundary_polygon = gpd.GeoDataFrame(
                pd.concat([self.downstream_boundary_polygon, gdf], ignore_index=True)
            )

    def read_neumann_boundary_polygon(self, fname: str, append: bool) -> None:
        """Read Neumann boundary polygons from a file.

        Parameters
        ----------
        fname : str
            Path to the polygon file.
        append : bool
            If True, append to existing polygons; otherwise replace them.
        """
        if not append:
            # New file
            # app.gui.setvar(_TB, "neumann_boundary_polygon_file", fname)
            self.neumann_boundary_polygon = mpol2pol(gpd.read_file(fname)).to_crs(
                app.crs
            )
        else:
            # Append to existing file
            gdf = mpol2pol(gpd.read_file(fname)).to_crs(app.crs)
            self.neumann_boundary_polygon = gpd.GeoDataFrame(
                pd.concat([self.neumann_boundary_polygon, gdf], ignore_index=True)
            )

    def read_outflow_boundary_polygon(self, fname: str, append: bool) -> None:
        """Read outflow boundary polygons from a file.

        Parameters
        ----------
        fname : str
            Path to the polygon file.
        append : bool
            If True, append to existing polygons; otherwise replace them.
        """
        if not append:
            # New file
            # app.gui.setvar(_TB, "outflow_boundary_polygon_file", fname)
            self.outflow_boundary_polygon = mpol2pol(gpd.read_file(fname)).to_crs(
                app.crs
            )
        else:
            # Append to existing file
            gdf = mpol2pol(gpd.read_file(fname)).to_crs(app.crs)
            self.outflow_boundary_polygon = gpd.GeoDataFrame(
                pd.concat([self.outflow_boundary_polygon, gdf], ignore_index=True)
            )

    def read_include_polygon_snapwave(self, fname: str, append: bool) -> None:
        """Read SnapWave include polygons from a file.

        Parameters
        ----------
        fname : str
            Path to the polygon file.
        append : bool
            If True, append to existing polygons; otherwise replace them.
        """
        if not append:
            # New file
            # app.gui.setvar(_TB, "include_polygon_file_snapwave", fname)
            self.include_polygon_snapwave = mpol2pol(gpd.read_file(fname)).to_crs(
                app.crs
            )
        else:
            # Append to existing file
            gdf = mpol2pol(gpd.read_file(fname)).to_crs(app.crs)
            self.include_polygon_snapwave = gpd.GeoDataFrame(
                pd.concat([self.include_polygon_snapwave, gdf], ignore_index=True)
            )

    def read_exclude_polygon_snapwave(self, fname: str, append: bool) -> None:
        """Read SnapWave exclude polygons from a file.

        Parameters
        ----------
        fname : str
            Path to the polygon file.
        append : bool
            If True, append to existing polygons; otherwise replace them.
        """
        if not append:
            # New file
            # app.gui.setvar(_TB, "exclude_polygon_file_snapwave", fname)
            self.exclude_polygon_snapwave = mpol2pol(gpd.read_file(fname)).to_crs(
                app.crs
            )
        else:
            # Append to existing file
            gdf = mpol2pol(gpd.read_file(fname)).to_crs(app.crs)
            self.exclude_polygon_snapwave = gpd.GeoDataFrame(
                pd.concat([self.exclude_polygon_snapwave, gdf], ignore_index=True)
            )

    def read_open_boundary_polygon_snapwave(self, fname: str, append: bool) -> None:
        """Read SnapWave open boundary polygons from a file.

        Parameters
        ----------
        fname : str
            Path to the polygon file.
        append : bool
            If True, append to existing polygons; otherwise replace them.
        """
        if not append:
            # New file
            # app.gui.setvar(_TB, "open_boundary_polygon_file_snapwave", fname)
            self.open_boundary_polygon_snapwave = mpol2pol(gpd.read_file(fname)).to_crs(
                app.crs
            )
        else:
            # Append to existing file
            gdf = mpol2pol(gpd.read_file(fname)).to_crs(app.crs)
            self.open_boundary_polygon_snapwave = gpd.GeoDataFrame(
                pd.concat([self.open_boundary_polygon_snapwave, gdf], ignore_index=True)
            )

    def read_neumann_boundary_polygon_snapwave(self, fname: str, append: bool) -> None:
        """Read SnapWave Neumann boundary polygons from a file.

        Parameters
        ----------
        fname : str
            Path to the polygon file.
        append : bool
            If True, append to existing polygons; otherwise replace them.
        """
        if not append:
            # New file
            # app.gui.setvar(_TB, "neumann_boundary_polygon_file_snapwave", fname)
            self.neumann_boundary_polygon_snapwave = mpol2pol(
                gpd.read_file(fname)
            ).to_crs(app.crs)
        else:
            # Append to existing file
            gdf = mpol2pol(gpd.read_file(fname)).to_crs(app.crs)
            self.neumann_boundary_polygon_snapwave = gpd.GeoDataFrame(
                pd.concat(
                    [self.neumann_boundary_polygon_snapwave, gdf], ignore_index=True
                )
            )

    def show_mask_polygons(self) -> None:
        """Show or hide include/exclude mask polygons on the map."""
        show_polygons = app.gui.getvar(_TB, "show_mask_polygons_in_domain_tab")
        if show_polygons:
            app.map.layer[_TB].layer["include_polygon"].show()
            app.map.layer[_TB].layer["exclude_polygon"].show()
            app.map.layer[_TB].layer["include_polygon"].deactivate()
            app.map.layer[_TB].layer["exclude_polygon"].deactivate()
        else:
            app.map.layer[_TB].layer["include_polygon"].hide()
            app.map.layer[_TB].layer["exclude_polygon"].hide()

    def write_refinement_polygon(self) -> None:
        """Write refinement polygons to GeoJSON."""
        if len(self.refinement_polygon) == 0:
            return
        # Drop the id column (if it exists)
        if "id" in self.refinement_polygon.columns:
            gdf = self.refinement_polygon.drop(columns=["id"])
        else:
            gdf = self.refinement_polygon
        fname = app.gui.getvar(_TB, "refinement_polygon_file")
        gdf.to_file(fname, driver="GeoJSON")

    def write_include_polygon(self) -> None:
        """Write include polygons to GeoJSON."""
        if len(self.include_polygon) == 0:
            return
        gdf = gpd.GeoDataFrame(geometry=self.include_polygon["geometry"])
        fname = app.gui.getvar(_TB, "include_polygon_file")
        gdf.to_file(fname, driver="GeoJSON")

    def write_exclude_polygon(self) -> None:
        """Write exclude polygons to GeoJSON."""
        if len(self.exclude_polygon) == 0:
            return
        gdf = gpd.GeoDataFrame(geometry=self.exclude_polygon["geometry"])
        fname = app.gui.getvar(_TB, "exclude_polygon_file")
        gdf.to_file(fname, driver="GeoJSON")

    def write_open_boundary_polygon(self) -> None:
        """Write open boundary polygons to GeoJSON."""
        if len(self.open_boundary_polygon) == 0:
            return
        gdf = gpd.GeoDataFrame(geometry=self.open_boundary_polygon["geometry"])
        fname = app.gui.getvar(_TB, "open_boundary_polygon_file")
        gdf.to_file(fname, driver="GeoJSON")

    def write_downstream_boundary_polygon(self) -> None:
        """Write downstream boundary polygons to GeoJSON."""
        if len(self.downstream_boundary_polygon) == 0:
            return
        gdf = gpd.GeoDataFrame(geometry=self.downstream_boundary_polygon["geometry"])
        fname = app.gui.getvar(_TB, "downstream_boundary_polygon_file")
        gdf.to_file(fname, driver="GeoJSON")

    def write_neumann_boundary_polygon(self) -> None:
        """Write Neumann boundary polygons to GeoJSON."""
        if len(self.neumann_boundary_polygon) == 0:
            return
        gdf = gpd.GeoDataFrame(geometry=self.neumann_boundary_polygon["geometry"])
        fname = app.gui.getvar(_TB, "neumann_boundary_polygon_file")
        gdf.to_file(fname, driver="GeoJSON")

    def write_outflow_boundary_polygon(self) -> None:
        """Write outflow boundary polygons to GeoJSON."""
        if len(self.outflow_boundary_polygon) == 0:
            return
        gdf = gpd.GeoDataFrame(geometry=self.outflow_boundary_polygon["geometry"])
        fname = app.gui.getvar(_TB, "outflow_boundary_polygon_file")
        gdf.to_file(fname, driver="GeoJSON")

    def write_include_polygon_snapwave(self) -> None:
        """Write SnapWave include polygons to GeoJSON."""
        if len(self.include_polygon_snapwave) == 0:
            return
        gdf = gpd.GeoDataFrame(geometry=self.include_polygon_snapwave["geometry"])
        fname = app.gui.getvar(_TB, "include_polygon_file_snapwave")
        gdf.to_file(fname, driver="GeoJSON")

    def write_exclude_polygon_snapwave(self) -> None:
        """Write SnapWave exclude polygons to GeoJSON."""
        if len(self.exclude_polygon_snapwave) == 0:
            return
        gdf = gpd.GeoDataFrame(geometry=self.exclude_polygon_snapwave["geometry"])
        fname = app.gui.getvar(_TB, "exclude_polygon_file_snapwave")
        gdf.to_file(fname, driver="GeoJSON")

    def write_open_boundary_polygon_snapwave(self) -> None:
        """Write SnapWave open boundary polygons to GeoJSON."""
        if len(self.open_boundary_polygon_snapwave) == 0:
            return
        gdf = gpd.GeoDataFrame(geometry=self.open_boundary_polygon_snapwave["geometry"])
        fname = app.gui.getvar(_TB, "open_boundary_polygon_file_snapwave")
        gdf.to_file(fname, driver="GeoJSON")

    def write_neumann_boundary_polygon_snapwave(self) -> None:
        """Write SnapWave Neumann boundary polygons to GeoJSON."""
        if len(self.neumann_boundary_polygon_snapwave) == 0:
            return
        gdf = gpd.GeoDataFrame(
            geometry=self.neumann_boundary_polygon_snapwave["geometry"]
        )
        fname = app.gui.getvar(_TB, "neumann_boundary_polygon_file_snapwave")
        gdf.to_file(fname, driver="GeoJSON")

    # Plot

    def plot_refinement_polygon(self) -> None:
        """Display refinement polygons on the map."""
        layer = app.map.layer[_TB].layer["quadtree_refinement"]
        layer.set_data(self.refinement_polygon)

    def plot_include_polygon(self) -> None:
        """Display include polygons on the map."""
        layer = app.map.layer[_TB].layer["include_polygon"]
        layer.clear()
        layer.add_feature(self.include_polygon)

    def plot_exclude_polygon(self) -> None:
        """Display exclude polygons on the map."""
        layer = app.map.layer[_TB].layer["exclude_polygon"]
        layer.clear()
        layer.add_feature(self.exclude_polygon)

    def plot_open_boundary_polygon(self) -> None:
        """Display open boundary polygons on the map."""
        layer = app.map.layer[_TB].layer["open_boundary_polygon"]
        layer.clear()
        layer.add_feature(self.open_boundary_polygon)

    def plot_downstream_boundary_polygon(self) -> None:
        """Display downstream boundary polygons on the map."""
        layer = app.map.layer[_TB].layer["downstream_boundary_polygon"]
        layer.clear()
        layer.add_feature(self.downstream_boundary_polygon)

    def plot_neumann_boundary_polygon(self) -> None:
        """Display Neumann boundary polygons on the map."""
        layer = app.map.layer[_TB].layer["neumann_boundary_polygon"]
        layer.clear()
        layer.add_feature(self.neumann_boundary_polygon)

    def plot_outflow_boundary_polygon(self) -> None:
        """Display outflow boundary polygons on the map."""
        layer = app.map.layer[_TB].layer["outflow_boundary_polygon"]
        layer.clear()
        layer.add_feature(self.outflow_boundary_polygon)

    def plot_include_polygon_snapwave(self) -> None:
        """Display SnapWave include polygons on the map."""
        layer = app.map.layer[_TB].layer["include_polygon_snapwave"]
        layer.clear()
        layer.add_feature(self.include_polygon_snapwave)

    def plot_exclude_polygon_snapwave(self) -> None:
        """Display SnapWave exclude polygons on the map."""
        layer = app.map.layer[_TB].layer["exclude_polygon_snapwave"]
        layer.clear()
        layer.add_feature(self.exclude_polygon_snapwave)

    def plot_open_boundary_polygon_snapwave(self) -> None:
        """Display SnapWave open boundary polygons on the map."""
        layer = app.map.layer[_TB].layer["open_boundary_polygon_snapwave"]
        layer.clear()
        layer.add_feature(self.open_boundary_polygon_snapwave)

    def plot_neumann_boundary_polygon_snapwave(self) -> None:
        """Display SnapWave Neumann boundary polygons on the map."""
        layer = app.map.layer[_TB].layer["neumann_boundary_polygon_snapwave"]
        layer.clear()
        layer.add_feature(self.neumann_boundary_polygon_snapwave)

    def read_setup_yaml(self, file_name: str) -> None:
        """Read a model setup YAML file and populate GUI state and polygons.

        Parameters
        ----------
        file_name : str
            Path to the YAML setup file.
        """
        group = _TB

        # Clear layers
        self.clear_layers()

        # Set everything back to defaults
        self.initialize()

        # # First set some default gui variables (should make this a 'clear' function)
        # app.gui.setvar(group, "refinement_polygon_file", "quadtree.geojson")
        # app.gui.setvar(group, "global_zmin", -99999.0)
        # app.gui.setvar(group, "global_zmax",  99999.0)
        # app.gui.setvar(group, "include_polygon_index", 0)
        # app.gui.setvar(group, "include_zmax",  99999.0)
        # app.gui.setvar(group, "include_zmin", -99999.0)
        # app.gui.setvar(group, "include_polygon_file", "include.geojson")
        # app.gui.setvar(group, "exclude_polygon_index", 0)
        # app.gui.setvar(group, "exclude_zmax",  99999.0)
        # app.gui.setvar(group, "exclude_zmin", -99999.0)
        # app.gui.setvar(group, "exclude_polygon_file", "exclude.geojson")
        # app.gui.setvar(group, "open_boundary_polygon_index", 0)
        # app.gui.setvar(group, "open_boundary_zmax",  99999.0)
        # app.gui.setvar(group, "open_boundary_zmin", -99999.0)
        # app.gui.setvar(group, "open_boundary_polygon_file", "open_boundary.geojson")
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
        # app.gui.setvar(group, "open_boundary_polygon_index_snapwave", 0)
        # app.gui.setvar(group, "open_boundary_zmax_snapwave",  99999.0)
        # app.gui.setvar(group, "open_boundary_zmin_snapwave", -99999.0)
        # app.gui.setvar(group, "open_boundary_polygon_file_snapwave", "open_boundary_snapwave.geojson")
        # app.gui.setvar(group, "neumann_boundary_polygon_index_snapwave", 0)
        # app.gui.setvar(group, "neumann_boundary_zmax_snapwave",  99999.0)
        # app.gui.setvar(group, "neumann_boundary_zmin_snapwave", -99999.0)
        # app.gui.setvar(group, "neumann_boundary_polygon_file_snapwave", "neumann_boundary_snapwave.geojson")

        # app.gui.setvar(group, "use_snapwave", False)
        # app.gui.setvar(_MODEL, "snapwave", True)
        # app.model[_MODEL].domain.input.variables.snapwave = False

        # # Empty geodataframes
        # self.include_polygon = gpd.GeoDataFrame()
        # self.exclude_polygon = gpd.GeoDataFrame()
        # self.open_boundary_polygon = gpd.GeoDataFrame()
        # self.outflow_boundary_polygon = gpd.GeoDataFrame()
        # self.include_polygon_snapwave = gpd.GeoDataFrame()
        # self.exclude_polygon_snapwave = gpd.GeoDataFrame()
        # self.open_boundary_polygon_snapwave = gpd.GeoDataFrame()
        # self.neumann_boundary_polygon_snapwave = gpd.GeoDataFrame()
        # self.quadtree_polygon = gpd.GeoDataFrame()

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
        app.gui.setvar(group, "rotation", dct["coordinates"]["rotation"])
        app.model[_MODEL].domain.crs = CRS(dct["coordinates"]["crs"])

        # Change coordinate system
        map.set_crs(app.model[_MODEL].domain.crs)
        # Zoom in to model outline
        x0 = dct["coordinates"]["x0"]
        x1 = x0 + dct["coordinates"]["dx"] * dct["coordinates"]["mmax"]
        y0 = dct["coordinates"]["y0"]
        y1 = y0 + dct["coordinates"]["dy"] * dct["coordinates"]["nmax"]
        dx = x1 - x0
        dy = y1 - y0
        bounds = [x0 - 0.1 * dx, y0 - 0.1 * dy, x1 + 0.1 * dx, y1 + 0.1 * dy]
        app.map.fit_bounds(
            bounds[0], bounds[1], bounds[2], bounds[3], crs=app.model[_MODEL].domain.crs
        )

        # Quadtree refinement
        if "quadtree" in dct:
            if "polygon_file" in dct["quadtree"]:
                app.gui.setvar(
                    group, "refinement_polygon_file", dct["quadtree"]["polygon_file"]
                )
                self.read_refinement_polygon(dct["quadtree"]["polygon_file"], False)
                self.plot_refinement_polygon()
        # Mask
        app.gui.setvar(group, "use_mask_global", False)
        if "global" in dct["mask"]:
            if "zmin" in dct["mask"]["global"]:
                app.gui.setvar(group, "global_zmin", dct["mask"]["global"]["zmin"])
                app.gui.setvar(group, "use_mask_global", True)
            if "zmax" in dct["mask"]["global"]:
                app.gui.setvar(group, "global_zmax", dct["mask"]["global"]["zmax"])
                app.gui.setvar(group, "use_mask_global", True)
        if "include" in dct["mask"]:
            if "zmin" in dct["mask"]["include"]:
                app.gui.setvar(group, "include_zmin", dct["mask"]["include"]["zmin"])
            if "zmax" in dct["mask"]["include"]:
                app.gui.setvar(group, "include_zmax", dct["mask"]["include"]["zmax"])
            if "polygon_file" in dct["mask"]["include"]:
                # Now read in polygons from geojson file (or other file)
                self.read_include_polygon(dct["mask"]["include"]["polygon_file"], False)
                self.plot_include_polygon()
        # Now do the same for exclude polygons
        if "exclude" in dct["mask"]:
            if "zmin" in dct["mask"]["exclude"]:
                app.gui.setvar(group, "exclude_zmin", dct["mask"]["exclude"]["zmin"])
            if "zmax" in dct["mask"]["exclude"]:
                app.gui.setvar(group, "exclude_zmax", dct["mask"]["exclude"]["zmax"])
            if "polygon_file" in dct["mask"]["exclude"]:
                # Now read in polygons from geojson file
                self.read_exclude_polygon(dct["mask"]["exclude"]["polygon_file"], False)
                self.plot_exclude_polygon()
        # Now do the same for open boundary polygons
        if "open_boundary" in dct["mask"]:
            if "zmin" in dct["mask"]["open_boundary"]:
                app.gui.setvar(
                    group, "open_boundary_zmin", dct["mask"]["open_boundary"]["zmin"]
                )
            if "zmax" in dct["mask"]["open_boundary"]:
                app.gui.setvar(
                    group, "open_boundary_zmax", dct["mask"]["open_boundary"]["zmax"]
                )
            if "polygon_file" in dct["mask"]["open_boundary"]:
                # Now read in polygons from geojson file
                self.read_open_boundary_polygon(
                    dct["mask"]["open_boundary"]["polygon_file"], False
                )
                self.plot_open_boundary_polygon()
        # Now do the same for downstream boundary polygons
        if "downstream_boundary" in dct["mask"]:
            if "zmin" in dct["mask"]["downstream_boundary"]:
                app.gui.setvar(
                    group,
                    "downstream_boundary_zmin",
                    dct["mask"]["downstream_boundary"]["zmin"],
                )
            if "zmax" in dct["mask"]["downstream_boundary"]:
                app.gui.setvar(
                    group,
                    "downstream_boundary_zmax",
                    dct["mask"]["downstream_boundary"]["zmax"],
                )
            if "polygon_file" in dct["mask"]["downstream_boundary"]:
                # Now read in polygons from geojson file
                self.read_downstream_boundary_polygon(
                    dct["mask"]["downstream_boundary"]["polygon_file"], False
                )
                self.plot_downstream_boundary_polygon()
        # Now do the same for neumann boundary polygons
        if "neumann_boundary" in dct["mask"]:
            if "zmin" in dct["mask"]["neumann_boundary"]:
                app.gui.setvar(
                    group,
                    "neumann_boundary_zmin",
                    dct["mask"]["neumann_boundary"]["zmin"],
                )
            if "zmax" in dct["mask"]["neumann_boundary"]:
                app.gui.setvar(
                    group,
                    "neumann_boundary_zmax",
                    dct["mask"]["neumann_boundary"]["zmax"],
                )
            if "polygon_file" in dct["mask"]["neumann_boundary"]:
                # Now read in polygons from geojson file
                self.read_neumann_boundary_polygon(
                    dct["mask"]["neumann_boundary"]["polygon_file"], False
                )
                self.plot_neumann_boundary_polygon()
        # Now do the same for outflow boundary polygons
        if "outflow_boundary" in dct["mask"]:
            if "zmin" in dct["mask"]["outflow_boundary"]:
                app.gui.setvar(
                    group,
                    "outflow_boundary_zmin",
                    dct["mask"]["outflow_boundary"]["zmin"],
                )
            if "zmax" in dct["mask"]["outflow_boundary"]:
                app.gui.setvar(
                    group,
                    "outflow_boundary_zmax",
                    dct["mask"]["outflow_boundary"]["zmax"],
                )
            if "polygon_file" in dct["mask"]["outflow_boundary"]:
                # Now read in polygons from geojson file
                self.read_outflow_boundary_polygon(
                    dct["mask"]["outflow_boundary"]["polygon_file"], False
                )
                self.plot_outflow_boundary_polygon()

        if "mask_snapwave" in dct:
            app.gui.setvar(group, "use_snapwave", True)
            # app.gui.setvar(_MODEL, "snapwave", True)
            # app.model[_MODEL].domain.input.variables.snapwave = True
            if "global" in dct["mask_snapwave"]:
                if "zmin" in dct["mask_snapwave"]["global"]:
                    app.gui.setvar(
                        group,
                        "global_zmin_snapwave",
                        dct["mask_snapwave"]["global"]["zmin"],
                    )
                    app.gui.setvar(group, "use_mask_snapwave_global", True)
                if "zmax" in dct["mask_snapwave"]["global"]:
                    app.gui.setvar(
                        group,
                        "global_zmax_snapwave",
                        dct["mask_snapwave"]["global"]["zmax"],
                    )
                    app.gui.setvar(group, "use_mask_snapwave_global", True)
            if "include" in dct["mask_snapwave"]:
                if "zmin" in dct["mask_snapwave"]["include"]:
                    app.gui.setvar(
                        group,
                        "include_zmin_snapwave",
                        dct["mask_snapwave"]["include"]["zmin"],
                    )
                if "zmax" in dct["mask_snapwave"]["include"]:
                    app.gui.setvar(
                        group,
                        "include_zmax_snapwave",
                        dct["mask_snapwave"]["include"]["zmax"],
                    )
                if "polygon_file" in dct["mask_snapwave"]["include"]:
                    # Now read in polygons from geojson file
                    self.read_include_polygon_snapwave(
                        dct["mask_snapwave"]["include"]["polygon_file"], False
                    )
                    self.plot_include_polygon_snapwave()
            if "exclude" in dct["mask_snapwave"]:
                if "zmin" in dct["mask_snapwave"]["exclude"]:
                    app.gui.setvar(
                        group,
                        "exclude_zmin_snapwave",
                        dct["mask_snapwave"]["exclude"]["zmin"],
                    )
                if "zmax" in dct["mask_snapwave"]["exclude"]:
                    app.gui.setvar(
                        group,
                        "exclude_zmax_snapwave",
                        dct["mask_snapwave"]["exclude"]["zmax"],
                    )
                if "polygon_file" in dct["mask_snapwave"]["exclude"]:
                    # Now read in polygons from geojson file
                    self.read_exclude_polygon_snapwave(
                        dct["mask_snapwave"]["exclude"]["polygon_file"], False
                    )
                    self.plot_exclude_polygon_snapwave()
            if "open_boundary" in dct["mask_snapwave"]:
                if "zmin" in dct["mask_snapwave"]["open_boundary"]:
                    app.gui.setvar(
                        group,
                        "open_boundary_zmin_snapwave",
                        dct["mask_snapwave"]["open_boundary"]["zmin"],
                    )
                if "zmax" in dct["mask_snapwave"]["open_boundary"]:
                    app.gui.setvar(
                        group,
                        "open_boundary_zmax_snapwave",
                        dct["mask_snapwave"]["open_boundary"]["zmax"],
                    )
                if "polygon_file" in dct["mask_snapwave"]["open_boundary"]:
                    # Now read in polygons from geojson file
                    self.read_open_boundary_polygon_snapwave(
                        dct["mask_snapwave"]["open_boundary"]["polygon_file"], False
                    )
                    self.plot_open_boundary_polygon_snapwave()
            if "neumann_boundary" in dct["mask_snapwave"]:
                if "zmin" in dct["mask_snapwave"]["neumann_boundary"]:
                    app.gui.setvar(
                        group,
                        "neumann_boundary_zmin_snapwave",
                        dct["mask_snapwave"]["neumann_boundary"]["zmin"],
                    )
                if "zmax" in dct["mask_snapwave"]["neumann_boundary"]:
                    app.gui.setvar(
                        group,
                        "neumann_boundary_zmax_snapwave",
                        dct["mask_snapwave"]["neumann_boundary"]["zmax"],
                    )
                if "polygon_file" in dct["mask_snapwave"]["neumann_boundary"]:
                    # Now read in polygons from geojson file
                    self.read_neumann_boundary_polygon_snapwave(
                        dct["mask_snapwave"]["neumann_boundary"]["polygon_file"], False
                    )
                    self.plot_neumann_boundary_polygon_snapwave()

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
            dct["coordinates"]["x0"],
            dct["coordinates"]["y0"],
            lenx,
            leny,
            dct["coordinates"]["rotation"],
        )

        # Sub grid
        if "subgrid" in dct:
            app.gui.setvar(_TB, "use_subgrid", True)
        else:
            app.gui.setvar(_TB, "use_subgrid", False)

    def write_setup_yaml(self) -> None:
        """Write the current model setup to a YAML file and save all polygons."""
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
        dct["coordinates"]["rotation"] = float(app.gui.getvar(group, "rotation"))
        dct["coordinates"]["crs"] = app.model[_MODEL].domain.crs.name
        # QuadTree
        dct["quadtree"] = {}
        if len(app.toolbox[_TB].refinement_polygon) > 0:
            dct["quadtree"]["polygon_file"] = app.gui.getvar(
                _TB, "refinement_polygon_file"
            )
        # Mask
        dct["mask"] = {}
        if app.gui.getvar(group, "use_mask_global"):
            dct["mask"]["global"] = {}
            dct["mask"]["global"]["zmax"] = app.gui.getvar(group, "global_zmax")
            dct["mask"]["global"]["zmin"] = app.gui.getvar(group, "global_zmin")
        dct["mask"]["include"] = {}
        if len(app.toolbox[_TB].include_polygon) > 0:
            dct["mask"]["include"]["zmax"] = app.gui.getvar(_TB, "include_zmax")
            dct["mask"]["include"]["zmin"] = app.gui.getvar(_TB, "include_zmin")
            dct["mask"]["include"]["polygon_file"] = app.gui.getvar(
                _TB, "include_polygon_file"
            )
        dct["mask"]["exclude"] = {}
        if len(app.toolbox[_TB].exclude_polygon) > 0:
            dct["mask"]["exclude"]["zmax"] = app.gui.getvar(_TB, "exclude_zmax")
            dct["mask"]["exclude"]["zmin"] = app.gui.getvar(_TB, "exclude_zmin")
            dct["mask"]["exclude"]["polygon_file"] = app.gui.getvar(
                _TB, "exclude_polygon_file"
            )
        dct["mask"]["open_boundary"] = {}
        if len(app.toolbox[_TB].open_boundary_polygon) > 0:
            dct["mask"]["open_boundary"]["zmax"] = app.gui.getvar(
                _TB, "open_boundary_zmax"
            )
            dct["mask"]["open_boundary"]["zmin"] = app.gui.getvar(
                _TB, "open_boundary_zmin"
            )
            dct["mask"]["open_boundary"]["polygon_file"] = app.gui.getvar(
                _TB, "open_boundary_polygon_file"
            )
        dct["mask"]["downstream_boundary"] = {}
        if len(app.toolbox[_TB].downstream_boundary_polygon) > 0:
            dct["mask"]["downstream_boundary"]["zmax"] = app.gui.getvar(
                _TB, "downstream_boundary_zmax"
            )
            dct["mask"]["downstream_boundary"]["zmin"] = app.gui.getvar(
                _TB, "downstream_boundary_zmin"
            )
            dct["mask"]["downstream_boundary"]["polygon_file"] = app.gui.getvar(
                _TB, "downstream_boundary_polygon_file"
            )
        dct["mask"]["neumann_boundary"] = {}
        if len(app.toolbox[_TB].neumann_boundary_polygon) > 0:
            dct["mask"]["neumann_boundary"]["zmax"] = app.gui.getvar(
                _TB, "neumann_boundary_zmax"
            )
            dct["mask"]["neumann_boundary"]["zmin"] = app.gui.getvar(
                _TB, "neumann_boundary_zmin"
            )
            dct["mask"]["neumann_boundary"]["polygon_file"] = app.gui.getvar(
                _TB, "neumann_boundary_polygon_file"
            )
        dct["mask"]["outflow_boundary"] = {}
        if len(app.toolbox[_TB].outflow_boundary_polygon) > 0:
            dct["mask"]["outflow_boundary"]["zmax"] = app.gui.getvar(
                _TB, "outflow_boundary_zmax"
            )
            dct["mask"]["outflow_boundary"]["zmin"] = app.gui.getvar(
                _TB, "outflow_boundary_zmin"
            )
            dct["mask"]["outflow_boundary"]["polygon_file"] = app.gui.getvar(
                _TB, "outflow_boundary_polygon_file"
            )
        # SnapWave
        # Check if snapwave is enabled
        if app.model[_MODEL].domain.input.variables.snapwave:
            dct["mask_snapwave"] = {}
            dct["mask_snapwave"]["global"] = {}
            dct["mask_snapwave"]["global"]["zmax"] = app.gui.getvar(
                group, "global_zmax_snapwave"
            )
            dct["mask_snapwave"]["global"]["zmin"] = app.gui.getvar(
                group, "global_zmin_snapwave"
            )
            dct["mask_snapwave"]["include"] = {}
            if len(app.toolbox[_TB].include_polygon_snapwave) > 0:
                dct["mask_snapwave"]["include"]["zmax"] = app.gui.getvar(
                    _TB, "include_zmax_snapwave"
                )
                dct["mask_snapwave"]["include"]["zmin"] = app.gui.getvar(
                    _TB, "include_zmin_snapwave"
                )
                dct["mask_snapwave"]["include"]["polygon_file"] = app.gui.getvar(
                    _TB, "include_polygon_file_snapwave"
                )
            dct["mask_snapwave"]["exclude"] = {}
            if len(app.toolbox[_TB].exclude_polygon_snapwave) > 0:
                dct["mask_snapwave"]["exclude"]["zmax"] = app.gui.getvar(
                    _TB, "exclude_zmax_snapwave"
                )
                dct["mask_snapwave"]["exclude"]["zmin"] = app.gui.getvar(
                    _TB, "exclude_zmin_snapwave"
                )
                dct["mask_snapwave"]["exclude"]["polygon_file"] = app.gui.getvar(
                    _TB, "exclude_polygon_file_snapwave"
                )
            dct["mask_snapwave"]["open_boundary"] = {}
            if len(app.toolbox[_TB].open_boundary_polygon_snapwave) > 0:
                dct["mask_snapwave"]["open_boundary"]["zmax"] = app.gui.getvar(
                    _TB, "open_boundary_zmax_snapwave"
                )
                dct["mask_snapwave"]["open_boundary"]["zmin"] = app.gui.getvar(
                    _TB, "open_boundary_zmin_snapwave"
                )
                dct["mask_snapwave"]["open_boundary"]["polygon_file"] = app.gui.getvar(
                    _TB, "open_boundary_polygon_file_snapwave"
                )
            dct["mask_snapwave"]["neumann_boundary"] = {}
            if len(app.toolbox[_TB].neumann_boundary_polygon_snapwave) > 0:
                dct["mask_snapwave"]["neumann_boundary"]["zmax"] = app.gui.getvar(
                    _TB, "neumann_boundary_zmax_snapwave"
                )
                dct["mask_snapwave"]["neumann_boundary"]["zmin"] = app.gui.getvar(
                    _TB, "neumann_boundary_zmin_snapwave"
                )
                dct["mask_snapwave"]["neumann_boundary"]["polygon_file"] = (
                    app.gui.getvar(_TB, "neumann_boundary_polygon_file_snapwave")
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
        app.toolbox[_TB].write_include_polygon()
        app.toolbox[_TB].write_exclude_polygon()
        app.toolbox[_TB].write_open_boundary_polygon()
        app.toolbox[_TB].write_downstream_boundary_polygon()
        app.toolbox[_TB].write_neumann_boundary_polygon()
        app.toolbox[_TB].write_outflow_boundary_polygon()
        app.toolbox[_TB].write_refinement_polygon()
        app.toolbox[_TB].write_include_polygon_snapwave()
        app.toolbox[_TB].write_exclude_polygon_snapwave()
        app.toolbox[_TB].write_open_boundary_polygon_snapwave()
        app.toolbox[_TB].write_neumann_boundary_polygon_snapwave()


def gdf2list(gdf_in: gpd.GeoDataFrame) -> List[gpd.GeoDataFrame]:
    """Convert a GeoDataFrame into a list of single-feature GeoDataFrames.

    Parameters
    ----------
    gdf_in : gpd.GeoDataFrame
        Input GeoDataFrame with one or more features.

    Returns
    -------
    List[gpd.GeoDataFrame]
        List where each element is a single-feature GeoDataFrame.
    """
    gdf_out = []
    for feature in gdf_in.iterfeatures():
        gdf_out.append(gpd.GeoDataFrame.from_features([feature]))
    return gdf_out
