"""Main toolbox class for the SFINCS HMT model-maker in DelftDashboard.

Provides grid generation, bathymetry interpolation, mask creation, sub-grid
table computation, and polygon I/O for the SFINCS model-maker workflow.
"""

from __future__ import annotations

import traceback
from typing import List

import geopandas as gpd
import numpy as np

from delftdashboard.app import app
from delftdashboard.operations import map
from delftdashboard.operations.toolbox import GenericToolbox
from delftdashboard.operations.topography import to_hydromt_elevation_list

from ._polygons import PolygonsMixin
from ._setup_yaml import SetupYamlMixin

_TB = "modelmaker_sfincs_hmt"
_MODEL = "sfincs_hmt"


class Toolbox(PolygonsMixin, SetupYamlMixin, GenericToolbox):
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
        self.refinement_polygons_changed = False

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
                to_hydromt_elevation_list(app.selected_bathymetry_datasets),
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
        bathymetry_sets = to_hydromt_elevation_list(app.selected_bathymetry_datasets)
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
