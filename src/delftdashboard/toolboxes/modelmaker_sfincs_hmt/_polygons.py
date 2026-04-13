"""Polygon I/O for the SFINCS HydroMT Model Maker.

Defines :class:`PolygonsMixin`, mixed into the toolbox ``Toolbox`` so
the ``read_*_polygon`` / ``write_*_polygon`` / ``plot_*_polygon`` and
``show_mask_polygons`` methods stay accessible as bound methods (the
GUI YAMLs and external callers expect them there).

Many of the per-kind reader/writer/plotter methods are near-identical;
they're kept individually because the GUI YAML configs reference them
by name (e.g. ``method: read_include_polygon``).
"""

from __future__ import annotations

import geopandas as gpd
import pandas as pd

from delftdashboard.app import app
from delftdashboard.misc.gdfutils import mpol2pol


_TB = "modelmaker_sfincs_hmt"


class PolygonsMixin:
    """Mixin providing polygon read/write/plot methods on the SFINCS HMT Toolbox."""

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

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
        """Read include polygons from a file."""
        if not append:
            self.include_polygon = mpol2pol(gpd.read_file(fname)).to_crs(app.crs)
        else:
            gdf = mpol2pol(gpd.read_file(fname)).to_crs(app.crs)
            self.include_polygon = gpd.GeoDataFrame(
                pd.concat([self.include_polygon, gdf], ignore_index=True)
            )

    def read_exclude_polygon(self, fname: str, append: bool) -> None:
        """Read exclude polygons from a file."""
        if not append:
            self.exclude_polygon = mpol2pol(gpd.read_file(fname)).to_crs(app.crs)
        else:
            gdf = mpol2pol(gpd.read_file(fname))
            self.exclude_polygon = gpd.GeoDataFrame(
                pd.concat([self.exclude_polygon, gdf], ignore_index=True)
            )

    def read_open_boundary_polygon(self, fname: str, append: bool) -> None:
        """Read open boundary polygons from a file."""
        if not append:
            self.open_boundary_polygon = mpol2pol(gpd.read_file(fname)).to_crs(app.crs)
        else:
            gdf = mpol2pol(gpd.read_file(fname)).to_crs
            self.open_boundary_polygon = gpd.GeoDataFrame(
                pd.concat([self.open_boundary_polygon, gdf], ignore_index=True)
            )

    def read_downstream_boundary_polygon(self, fname: str, append: bool) -> None:
        """Read downstream boundary polygons from a file."""
        if not append:
            self.downstream_boundary_polygon = mpol2pol(gpd.read_file(fname)).to_crs(
                app.crs
            )
        else:
            gdf = mpol2pol(gpd.read_file(fname)).to_crs(app.crs)
            self.downstream_boundary_polygon = gpd.GeoDataFrame(
                pd.concat([self.downstream_boundary_polygon, gdf], ignore_index=True)
            )

    def read_neumann_boundary_polygon(self, fname: str, append: bool) -> None:
        """Read Neumann boundary polygons from a file."""
        if not append:
            self.neumann_boundary_polygon = mpol2pol(gpd.read_file(fname)).to_crs(
                app.crs
            )
        else:
            gdf = mpol2pol(gpd.read_file(fname)).to_crs(app.crs)
            self.neumann_boundary_polygon = gpd.GeoDataFrame(
                pd.concat([self.neumann_boundary_polygon, gdf], ignore_index=True)
            )

    def read_outflow_boundary_polygon(self, fname: str, append: bool) -> None:
        """Read outflow boundary polygons from a file."""
        if not append:
            self.outflow_boundary_polygon = mpol2pol(gpd.read_file(fname)).to_crs(
                app.crs
            )
        else:
            gdf = mpol2pol(gpd.read_file(fname)).to_crs(app.crs)
            self.outflow_boundary_polygon = gpd.GeoDataFrame(
                pd.concat([self.outflow_boundary_polygon, gdf], ignore_index=True)
            )

    def read_include_polygon_snapwave(self, fname: str, append: bool) -> None:
        """Read SnapWave include polygons from a file."""
        if not append:
            self.include_polygon_snapwave = mpol2pol(gpd.read_file(fname)).to_crs(
                app.crs
            )
        else:
            gdf = mpol2pol(gpd.read_file(fname)).to_crs(app.crs)
            self.include_polygon_snapwave = gpd.GeoDataFrame(
                pd.concat([self.include_polygon_snapwave, gdf], ignore_index=True)
            )

    def read_exclude_polygon_snapwave(self, fname: str, append: bool) -> None:
        """Read SnapWave exclude polygons from a file."""
        if not append:
            self.exclude_polygon_snapwave = mpol2pol(gpd.read_file(fname)).to_crs(
                app.crs
            )
        else:
            gdf = mpol2pol(gpd.read_file(fname)).to_crs(app.crs)
            self.exclude_polygon_snapwave = gpd.GeoDataFrame(
                pd.concat([self.exclude_polygon_snapwave, gdf], ignore_index=True)
            )

    def read_open_boundary_polygon_snapwave(self, fname: str, append: bool) -> None:
        """Read SnapWave open boundary polygons from a file."""
        if not append:
            self.open_boundary_polygon_snapwave = mpol2pol(gpd.read_file(fname)).to_crs(
                app.crs
            )
        else:
            gdf = mpol2pol(gpd.read_file(fname)).to_crs(app.crs)
            self.open_boundary_polygon_snapwave = gpd.GeoDataFrame(
                pd.concat([self.open_boundary_polygon_snapwave, gdf], ignore_index=True)
            )

    def read_neumann_boundary_polygon_snapwave(self, fname: str, append: bool) -> None:
        """Read SnapWave Neumann boundary polygons from a file."""
        if not append:
            self.neumann_boundary_polygon_snapwave = mpol2pol(
                gpd.read_file(fname)
            ).to_crs(app.crs)
        else:
            gdf = mpol2pol(gpd.read_file(fname)).to_crs(app.crs)
            self.neumann_boundary_polygon_snapwave = gpd.GeoDataFrame(
                pd.concat(
                    [self.neumann_boundary_polygon_snapwave, gdf], ignore_index=True
                )
            )

    # ------------------------------------------------------------------
    # Misc
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def write_refinement_polygon(self) -> None:
        """Write refinement polygons to GeoJSON."""
        if len(self.refinement_polygon) == 0:
            return
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

    # ------------------------------------------------------------------
    # Plot
    # ------------------------------------------------------------------

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
