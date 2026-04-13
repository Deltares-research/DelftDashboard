"""Polygon I/O for the HurryWave HydroMT Model Maker.

Defines :class:`PolygonsMixin`, mixed into the toolbox ``Toolbox`` so
the ``read_*_polygon`` / ``write_*_polygon`` / ``plot_*_polygon``
methods stay accessible as bound methods (the GUI YAMLs and external
callers expect them there).
"""

from __future__ import annotations

import geopandas as gpd
import pandas as pd

from delftdashboard.app import app
from delftdashboard.misc.gdfutils import mpol2pol


_TB = "modelmaker_hurrywave_hmt"


class PolygonsMixin:
    """Mixin providing polygon read/write/plot methods on the HurryWave HMT Toolbox."""

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

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
        """Load include polygons from file."""
        if not append:
            self.include_polygon = mpol2pol(gpd.read_file(fname)).to_crs(app.crs)
        else:
            gdf = mpol2pol(gpd.read_file(fname)).to_crs(app.crs)
            self.include_polygon = gpd.GeoDataFrame(
                pd.concat([self.include_polygon, gdf], ignore_index=True)
            )

    def read_exclude_polygon(self, fname: str, append: bool) -> None:
        """Load exclude polygons from file."""
        if not append:
            self.exclude_polygon = mpol2pol(gpd.read_file(fname)).to_crs(app.crs)
        else:
            gdf = mpol2pol(gpd.read_file(fname)).to_crs(app.crs)
            self.exclude_polygon = gpd.GeoDataFrame(
                pd.concat([self.exclude_polygon, gdf], ignore_index=True)
            )

    def read_boundary_polygon(self, fname: str, append: bool) -> None:
        """Load boundary polygons from file."""
        if not append:
            self.boundary_polygon = gpd.read_file(fname).to_crs(app.crs)
        else:
            gdf = gpd.read_file(fname).to_crs(app.crs)
            self.boundary_polygon = gpd.GeoDataFrame(
                pd.concat([self.boundary_polygon, gdf], ignore_index=True)
            )

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Plot
    # ------------------------------------------------------------------

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
