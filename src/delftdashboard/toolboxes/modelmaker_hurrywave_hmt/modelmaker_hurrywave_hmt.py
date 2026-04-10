"""HurryWave Model Maker toolbox for DelftDashboard.

Provides the ``Toolbox`` class that drives grid generation, bathymetry
interpolation, mask building, wave blocking, and polygon I/O for a
HurryWave (HydroMT) model.
"""

import traceback
from typing import List

import geopandas as gpd
import pandas as pd

from delftdashboard.app import app
from delftdashboard.misc.gdfutils import mpol2pol
from delftdashboard.operations.toolbox import GenericToolbox

_TB = "modelmaker_hurrywave_hmt"
_MODEL = "hurrywave_hmt"


class Toolbox(GenericToolbox):
    """Model Maker toolbox for HurryWave (HydroMT)."""

    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name
        self.long_name = "Model Maker"

    def initialize(self) -> None:
        """Set up default GUI variables and empty polygon state."""
        # Grid outline
        self.grid_outline = gpd.GeoDataFrame()

        # Bathymetry
        self.selected_bathymetry_datasets: List[dict] = []

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

        self.setup_dict: dict = {}

        app.gui.setvar(_TB, "use_waveblocking", True)

        # Domain
        app.gui.setvar(_TB, "x0", 0.0)
        app.gui.setvar(_TB, "y0", 0.0)
        app.gui.setvar(_TB, "nmax", 0)
        app.gui.setvar(_TB, "mmax", 0)
        app.gui.setvar(_TB, "dx", 0.1)
        app.gui.setvar(_TB, "dy", 0.1)
        app.gui.setvar(_TB, "rotation", 0.0)

        # Refinement
        app.gui.setvar(_TB, "refinement_polygon_file", "quadtree.geojson")
        app.gui.setvar(_TB, "refinement_polygon_names", [])
        app.gui.setvar(_TB, "refinement_polygon_index", 0)
        app.gui.setvar(_TB, "refinement_polygon_level", 0)
        app.gui.setvar(_TB, "refinement_polygon_zmin", -99999.0)
        app.gui.setvar(_TB, "refinement_polygon_zmax", 99999.0)
        app.gui.setvar(_TB, "nr_refinement_polygons", 0)
        levstr = [str(i) for i in range(10)]
        app.gui.setvar(_TB, "refinement_polygon_levels", levstr)

        # Bathymetry
        source_names, _sources = app.topography_data_catalog.sources()
        app.gui.setvar(_TB, "bathymetry_source_names", source_names)
        app.gui.setvar(_TB, "active_bathymetry_source", source_names[0])
        dataset_names, _long_names, _src_names = (
            app.topography_data_catalog.dataset_names(source=source_names[0])
        )
        app.gui.setvar(_TB, "bathymetry_dataset_names", dataset_names)
        app.gui.setvar(_TB, "bathymetry_dataset_index", 0)
        app.gui.setvar(_TB, "selected_bathymetry_dataset_names", [])
        app.gui.setvar(_TB, "selected_bathymetry_dataset_index", 0)
        app.gui.setvar(_TB, "selected_bathymetry_dataset_zmin", -99999.0)
        app.gui.setvar(_TB, "selected_bathymetry_dataset_zmax", 99999.0)
        app.gui.setvar(_TB, "nr_selected_bathymetry_datasets", 0)

        # Mask
        app.gui.setvar(_TB, "global_zmax", -2.0)
        app.gui.setvar(_TB, "global_zmin", -99999.0)
        app.gui.setvar(_TB, "include_polygon_names", [])
        app.gui.setvar(_TB, "include_polygon_index", 0)
        app.gui.setvar(_TB, "nr_include_polygons", 0)
        app.gui.setvar(_TB, "include_zmax", 99999.0)
        app.gui.setvar(_TB, "include_zmin", -99999.0)
        app.gui.setvar(_TB, "exclude_polygon_names", [])
        app.gui.setvar(_TB, "exclude_polygon_index", 0)
        app.gui.setvar(_TB, "nr_exclude_polygons", 0)
        app.gui.setvar(_TB, "exclude_zmax", 99999.0)
        app.gui.setvar(_TB, "exclude_zmin", -99999.0)
        app.gui.setvar(_TB, "boundary_polygon_names", [])
        app.gui.setvar(_TB, "boundary_polygon_index", 0)
        app.gui.setvar(_TB, "nr_boundary_polygons", 0)
        app.gui.setvar(_TB, "boundary_zmax", 99999.0)
        app.gui.setvar(_TB, "boundary_zmin", -99999.0)

        # Wave Blocking
        app.gui.setvar(_TB, "waveblocking_nr_dirs", 36)
        app.gui.setvar(_TB, "waveblocking_nr_pixels", 20)
        app.gui.setvar(_TB, "waveblocking_threshold_level", -5.0)

    def set_layer_mode(self, mode: str) -> None:
        """Hide toolbox layers when the toolbox is inactive or invisible.

        Parameters
        ----------
        mode : str
            One of ``'inactive'`` or ``'invisible'``.
        """
        if mode in ("inactive", "invisible"):
            app.map.layer[_TB].hide()

    def set_crs(self) -> None:
        """Update rotation setting when the CRS changes."""
        can_rotate = not app.crs.is_geographic
        layer = app.map.layer.get(_TB)
        if layer and "grid_outline" in layer.layer:
            layer.layer["grid_outline"].set_paint_property("rotate", can_rotate)

    def add_layers(self) -> None:
        """Register all map layers for the Model Maker toolbox."""
        layer = app.map.add_layer(_TB)

        from .domain import grid_outline_created, grid_outline_modified

        layer.add_layer(
            "grid_outline",
            type="draw",
            shape="rectangle",
            create=grid_outline_created,
            modify=grid_outline_modified,
            polygon_line_color="mediumblue",
            polygon_fill_opacity=0.3,
            rotate=not app.crs.is_geographic,
        )

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

        from .mask_active_cells import (
            exclude_polygon_created,
            exclude_polygon_modified,
            exclude_polygon_selected,
            include_polygon_created,
            include_polygon_modified,
            include_polygon_selected,
        )

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

        from .mask_boundary_cells import (
            boundary_polygon_created,
            boundary_polygon_modified,
            boundary_polygon_selected,
        )

        layer.add_layer(
            "mask_boundary",
            type="draw",
            shape="polygon",
            create=boundary_polygon_created,
            modify=boundary_polygon_modified,
            select=boundary_polygon_selected,
            polygon_line_color="deepskyblue",
            polygon_fill_color="deepskyblue",
            polygon_fill_opacity=0.3,
        )

    # ── Grid / bathymetry / mask / wave blocking ─────────────────────

    def generate_grid(self) -> None:
        """Generate the computational grid from domain settings."""
        domain = app.model[_MODEL].domain

        nmax = domain.config.get("nmax") or 0
        if nmax > 0:
            ok = app.gui.window.dialog_ok_cancel(
                "Existing model grid and spatial attributes will be deleted! Continue?",
                title="Warning",
            )
            if not ok:
                return

        app.model[_MODEL].clear_spatial_attributes()

        dlg = app.gui.window.dialog_wait("Generating grid ...")
        try:
            x0 = app.gui.getvar(_TB, "x0")
            y0 = app.gui.getvar(_TB, "y0")
            dx = app.gui.getvar(_TB, "dx")
            dy = app.gui.getvar(_TB, "dy")
            nmax = app.gui.getvar(_TB, "nmax")
            mmax = app.gui.getvar(_TB, "mmax")
            rotation = app.gui.getvar(_TB, "rotation")

            domain.config.set("x0", x0)
            domain.config.set("y0", y0)
            domain.config.set("dx", dx)
            domain.config.set("dy", dy)
            domain.config.set("nmax", nmax)
            domain.config.set("mmax", mmax)
            domain.config.set("rotation", rotation)
            app.model[_MODEL].set_gui_variables()

            refpol = (
                self.refinement_polygon if len(self.refinement_polygon) > 0 else None
            )

            domain.quadtree_grid.create(
                x0,
                y0,
                nmax,
                mmax,
                dx,
                dy,
                rotation,
                epsg=app.crs.to_epsg(),
                refinement_polygons=refpol,
                elevation_list=app.selected_bathymetry_datasets,
            )
            domain.quadtree_grid.write()
            app.map.layer[_MODEL].layer["grid"].set_data(domain.quadtree_grid)
        except Exception as e:
            traceback.print_exc()
            dlg.close()
            app.gui.window.dialog_warning(f"Error generating grid:\n{e}")
            return
        dlg.close()

    def generate_bathymetry(self) -> None:
        """Interpolate bathymetry onto the grid using mean-wet subgrid averaging."""
        dlg = app.gui.window.dialog_wait("Generating bathymetry ...")
        try:
            domain = app.model[_MODEL].domain
            domain.quadtree_elevation.create(
                elevation_list=app.selected_bathymetry_datasets,
                nr_subgrid_pixels=20,
                threshold_level=0.0,
                mean_wet=True,
            )
            domain.quadtree_grid.write()
        except Exception as e:
            traceback.print_exc()
            dlg.close()
            app.gui.window.dialog_warning(f"Error generating bathymetry:\n{e}")
            return
        dlg.close()

    def update_mask(self) -> None:
        """Recompute the mask from current polygon and elevation settings."""
        dlg = app.gui.window.dialog_wait("Updating mask ...")
        try:
            domain = app.model[_MODEL].domain
            domain.quadtree_mask.create(
                zmin=app.gui.getvar(_TB, "global_zmin"),
                zmax=app.gui.getvar(_TB, "global_zmax"),
                include_polygon=self.include_polygon,
                include_zmin=app.gui.getvar(_TB, "include_zmin"),
                include_zmax=app.gui.getvar(_TB, "include_zmax"),
                exclude_polygon=self.exclude_polygon,
                exclude_zmin=app.gui.getvar(_TB, "exclude_zmin"),
                exclude_zmax=app.gui.getvar(_TB, "exclude_zmax"),
                open_boundary_polygon=self.boundary_polygon,
                open_boundary_zmin=app.gui.getvar(_TB, "boundary_zmin"),
                open_boundary_zmax=app.gui.getvar(_TB, "boundary_zmax"),
                update_datashader_dataframe=True,
            )
            domain.quadtree_grid.write()
            app.map.layer[_MODEL].layer["mask"].set_data(domain.quadtree_mask)
        except Exception as e:
            traceback.print_exc()
            dlg.close()
            app.gui.window.dialog_warning(f"Error updating mask:\n{e}")
            return
        dlg.close()

    def cut_inactive_cells(self) -> None:
        """Remove inactive cells from the grid to reduce model size."""
        dlg = app.gui.window.dialog_wait("Cutting Inactive Cells ...")
        try:
            domain = app.model[_MODEL].domain
            domain.quadtree_grid.cut_inactive_cells()
            domain.quadtree_grid.write()
            app.model[_MODEL].plot()
        except Exception as e:
            traceback.print_exc()
            dlg.close()
            app.gui.window.dialog_warning(f"Error cutting inactive cells:\n{e}")
            return
        dlg.close()

    def generate_waveblocking(self) -> None:
        """Generate the wave blocking file from sub-grid bathymetry."""
        filename = app.model[_MODEL].domain.config.get("wblfile")
        if not filename:
            filename = "hurrywave.wbl"
        rsp = app.gui.window.dialog_save_file(
            "Select file ...",
            file_name=filename,
            filter="*.wbl",
            allow_directory_change=False,
        )
        if rsp[0]:
            filename = rsp[2]
        else:
            return

        domain = app.model[_MODEL].domain
        nr_dirs = domain.config.get("ntheta") or 36
        nr_pixels = app.gui.getvar(_TB, "waveblocking_nr_pixels")
        threshold_level = app.gui.getvar(_TB, "waveblocking_threshold_level")

        p = app.gui.window.dialog_progress(
            "               Generating Wave blocking file ...                ", 100
        )
        try:
            domain.wave_blocking.create(
                app.selected_bathymetry_datasets,
                nr_dirs=nr_dirs,
                nr_subgrid_pixels=nr_pixels,
                threshold_level=threshold_level,
                quiet=False,
                progress_bar=p,
            )
        except Exception as e:
            traceback.print_exc()
            p.close()
            app.gui.window.dialog_warning(f"Error generating wave blocking file:\n{e}")
            return
        p.close()

        domain.wave_blocking.write(filename=filename)
        app.gui.setvar(_MODEL, "wblfile", filename)

    def build_model(self) -> None:
        """Run the full model build pipeline."""
        self.generate_grid()
        self.generate_bathymetry()
        self.update_mask()
        self.generate_waveblocking()

    # ── Polygon I/O ──────────────────────────────────────────────────

    def read_refinement_polygon(self, file_name: str, append: bool) -> None:
        """Load refinement polygons from a GeoJSON file.

        Parameters
        ----------
        file_name : str
            Path to the GeoJSON file.
        append : bool
            If True, add to existing polygons; otherwise replace.
        """
        refinement_polygon = gpd.read_file(file_name).to_crs(app.crs)
        if "refinement_level" not in refinement_polygon.columns:
            refinement_polygon["refinement_level"] = 1
        if "zmin" not in refinement_polygon.columns:
            refinement_polygon["zmin"] = -99999.0
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
        """Load include polygons from file.

        Parameters
        ----------
        fname : str
            Path to the GeoJSON file.
        append : bool
            If True, add to existing polygons; otherwise replace.
        """
        if not append:
            self.include_polygon = mpol2pol(gpd.read_file(fname)).to_crs(app.crs)
        else:
            gdf = mpol2pol(gpd.read_file(fname)).to_crs(app.crs)
            self.include_polygon = gpd.GeoDataFrame(
                pd.concat([self.include_polygon, gdf], ignore_index=True)
            )

    def read_exclude_polygon(self, fname: str, append: bool) -> None:
        """Load exclude polygons from file.

        Parameters
        ----------
        fname : str
            Path to the GeoJSON file.
        append : bool
            If True, add to existing polygons; otherwise replace.
        """
        if not append:
            self.exclude_polygon = mpol2pol(gpd.read_file(fname)).to_crs(app.crs)
        else:
            gdf = mpol2pol(gpd.read_file(fname)).to_crs(app.crs)
            self.exclude_polygon = gpd.GeoDataFrame(
                pd.concat([self.exclude_polygon, gdf], ignore_index=True)
            )

    def read_boundary_polygon(self, fname: str, append: bool) -> None:
        """Load boundary polygons from file.

        Parameters
        ----------
        fname : str
            Path to the GeoJSON file.
        append : bool
            If True, add to existing polygons; otherwise replace.
        """
        if not append:
            self.boundary_polygon = gpd.read_file(fname).to_crs(app.crs)
        else:
            gdf = gpd.read_file(fname).to_crs(app.crs)
            self.boundary_polygon = gpd.GeoDataFrame(
                pd.concat([self.boundary_polygon, gdf], ignore_index=True)
            )

    def write_refinement_polygon(self) -> None:
        """Save refinement polygons to a GeoJSON file."""
        if len(self.refinement_polygon) == 0:
            return
        gdf = (
            self.refinement_polygon.drop(columns=["id"])
            if "id" in self.refinement_polygon.columns
            else self.refinement_polygon
        )
        fname = app.gui.getvar(_TB, "refinement_polygon_file")
        gdf.to_file(fname, driver="GeoJSON")

    def write_include_polygon(self) -> None:
        """Save include polygons to include.geojson."""
        if len(self.include_polygon) == 0:
            return
        gpd.GeoDataFrame(geometry=self.include_polygon["geometry"]).to_file(
            self.include_file_name, driver="GeoJSON"
        )

    def write_exclude_polygon(self) -> None:
        """Save exclude polygons to exclude.geojson."""
        if len(self.exclude_polygon) == 0:
            return
        gpd.GeoDataFrame(geometry=self.exclude_polygon["geometry"]).to_file(
            self.exclude_file_name, driver="GeoJSON"
        )

    def write_boundary_polygon(self) -> None:
        """Save boundary polygons to boundary.geojson."""
        if len(self.boundary_polygon) == 0:
            return
        gpd.GeoDataFrame(geometry=self.boundary_polygon["geometry"]).to_file(
            self.boundary_file_name, driver="GeoJSON"
        )

    # ── Plotting ─────────────────────────────────────────────────────

    def plot_refinement_polygon(self) -> None:
        """Plot refinement polygons on the map."""
        app.map.layer[_TB].layer["quadtree_refinement"].set_data(
            self.refinement_polygon
        )

    def plot_include_polygon(self) -> None:
        """Plot include polygons on the map."""
        layer = app.map.layer[_TB].layer["mask_include"]
        layer.clear()
        layer.add_feature(self.include_polygon)

    def plot_exclude_polygon(self) -> None:
        """Plot exclude polygons on the map."""
        layer = app.map.layer[_TB].layer["mask_exclude"]
        layer.clear()
        layer.add_feature(self.exclude_polygon)

    def plot_boundary_polygon(self) -> None:
        """Plot boundary polygons on the map."""
        layer = app.map.layer[_TB].layer["mask_boundary"]
        layer.clear()
        layer.add_feature(self.boundary_polygon)
