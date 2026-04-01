"""DelftDashboard model interface for HurryWave (HydroMT).

Wraps the ``HurrywaveModel`` from hydromt_hurrywave and connects it to the
DelftDashboard GUI: map layers, configuration panels, and user interactions.
"""

import os
from typing import Optional

import geopandas as gpd
from hydromt_hurrywave import HurrywaveModel

from delftdashboard.app import app
from delftdashboard.operations import map
from delftdashboard.operations.model import GenericModel

_MODEL = "hurrywave_hmt"


class Model(GenericModel):
    """DelftDashboard model wrapper for HurryWave (HydroMT)."""

    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name
        self.long_name = "HurryWave (HydroMT)"

    def initialize(self) -> None:
        """Set up an empty model with default values.

        Called when:
        1. The user clicks "New model" in the menu.
        2. The user changes the CRS, which triggers a re-initialisation.
        """
        self.clear_layers()
        self.domain = HurrywaveModel(root=".", mode="w")
        self.domain.config.set("crs_epsg", app.crs.to_epsg(), skip_validation=True)
        self.set_gui_variables()
        # Switch to r+ so explicit reads work without auto-reading on init
        self.domain.root.mode = "r+"

    def add_layers(self) -> None:
        """Register all map layers for the HurryWave model."""
        layer = app.map.add_layer(_MODEL)

        layer.add_layer("grid", type="raster_image")
        layer.add_layer("mask", type="raster_image")

        from .boundary_conditions import select_boundary_point_from_map

        layer.add_layer(
            "boundary_points",
            type="circle_selector",
            select=select_boundary_point_from_map,
            hover_property="name",
            line_color="white",
            line_opacity=1.0,
            fill_color="blue",
            fill_opacity=1.0,
            circle_radius=4,
            circle_radius_selected=5,
            line_color_selected="white",
            fill_color_selected="red",
            circle_radius_inactive=4,
            line_color_inactive="white",
            fill_color_inactive="lightgrey",
        )

        from .observation_points_regular import (
            select_observation_point_from_map_regular,
        )

        layer.add_layer(
            "observation_points_regular",
            type="circle_selector",
            select=select_observation_point_from_map_regular,
            hover_property="name",
            line_color="white",
            line_opacity=1.0,
            fill_color="blue",
            fill_opacity=1.0,
            circle_radius=3,
            circle_radius_selected=4,
            line_color_selected="white",
            fill_color_selected="red",
        )

        from .observation_points_spectra import (
            select_observation_point_from_map_spectra,
        )

        layer.add_layer(
            "observation_points_spectra",
            type="circle_selector",
            select=select_observation_point_from_map_spectra,
            hover_property="name",
            line_color="white",
            line_opacity=1.0,
            fill_color="orange",
            fill_opacity=1.0,
            circle_radius=3,
            circle_radius_selected=4,
            line_color_selected="white",
            fill_color_selected="red",
        )

    def set_layer_mode(self, mode: str) -> None:
        """Show, hide, or deactivate map layers depending on *mode*.

        Parameters
        ----------
        mode : str
            One of ``'inactive'`` or ``'invisible'``.
        """
        layer = app.map.layer[_MODEL]
        if mode == "inactive":
            layer.layer["grid"].show()
            layer.layer["mask"].hide()
            layer.layer["boundary_points"].deactivate()
            layer.layer["observation_points_regular"].deactivate()
            layer.layer["observation_points_spectra"].deactivate()
        elif mode == "invisible":
            layer.hide()

    def open(self, filename: Optional[str] = None) -> None:
        """Open an existing HurryWave model from disk.

        Parameters
        ----------
        filename : str, optional
            Path to ``hurrywave.inp``.  If *None*, a file dialog is shown.
        """
        if filename is None:
            filename = app.gui.window.dialog_open_file(
                "Open HurryWave input file",
                filter="HurryWave input file (hurrywave.inp)",
            )
            if not filename:
                return
            filename = filename[0]

        if filename:
            dlg = app.gui.window.dialog_wait("Loading HurryWave model ...")
            path = os.path.dirname(filename)
            if not path:
                path = os.getcwd()
            os.chdir(path)
            self.clear_layers()
            self.domain = HurrywaveModel(root=path, mode="r+")
            self.domain.read()
            self.set_gui_variables()
            map.set_crs(self.domain.crs)
            self.plot()
            dlg.close()
            app.gui.window.update()
            self.zoom_to_model()

    def save(self) -> None:
        """Write the current model configuration to disk."""
        self.domain.config.set("crs_epsg", app.crs.to_epsg(), skip_validation=True)
        self.domain.config.write()

    def set_crs(self) -> None:
        """Update the model CRS to match the application CRS and re-plot."""
        crs = app.crs
        old_crs = self.domain.crs
        if old_crs != crs:
            self.domain.config.set("crs_epsg", crs.to_epsg(), skip_validation=True)
            self.plot()

    def plot(self) -> None:
        """Plot all model layers on the map."""
        layer = app.map.layer[_MODEL]
        layer.layer["grid"].set_data(self.domain.quadtree_grid)
        layer.layer["mask"].set_data(self.domain.quadtree_mask)
        layer.layer["boundary_points"].set_data(self.domain.boundary_conditions.gdf, 0)
        layer.layer["observation_points_regular"].set_data(
            self.domain.observation_points.gdf, 0
        )
        layer.layer["observation_points_spectra"].set_data(
            self.domain.observation_points_spectra.gdf, 0
        )

    def zoom_to_model(self, buffer: float = 0.1) -> None:
        """Zoom the map to the model grid extent.

        Parameters
        ----------
        buffer : float, optional
            Fractional buffer around the extent, by default 0.1 (10 %).
        """
        exterior = self.domain.quadtree_grid.exterior
        if len(exterior) == 0:
            return
        crds = exterior.to_crs(crs=4326).total_bounds.tolist()
        dx = crds[2] - crds[0]
        dy = crds[3] - crds[1]
        crds[0] -= buffer * dx
        crds[1] -= buffer * dy
        crds[2] += buffer * dx
        crds[3] += buffer * dy
        app.map.fit_bounds(crds[0], crds[1], crds[2], crds[3])

    def clear_spatial_attributes(self) -> None:
        """Clear all spatial data from the model and reset GUI variables."""
        app.map.layer[_MODEL].clear()
        for comp in [
            self.domain.quadtree_grid,
            self.domain.quadtree_mask,
            self.domain.quadtree_elevation,
            self.domain.wave_blocking,
            self.domain.boundary_conditions,
        ]:
            if hasattr(comp, "clear"):
                comp.clear()
        self.set_gui_variables()

    def set_gui_variables(self) -> None:
        """Copy model config and defaults to GUI variables."""
        group = _MODEL

        # Copy all config variables to GUI
        for key, value in self.domain.config.data.model_dump(
            exclude_none=False
        ).items():
            try:
                app.gui.setvar(group, key, value)
            except Exception:
                pass

        # Extra GUI-only variables
        app.gui.setvar(group, "view_grid", True)
        app.gui.setvar(group, "output_options_text", ["NetCDF", "Binary", "ASCII"])
        app.gui.setvar(group, "output_options_values", ["net", "bin", "asc"])
        app.gui.setvar(group, "wind_type", "uniform")

        # Boundary conditions
        app.gui.setvar(group, "boundary_dx", 50000.0)
        app.gui.setvar(group, "boundary_point_names", [])
        app.gui.setvar(group, "nr_boundary_points", 0)
        app.gui.setvar(group, "active_boundary_point", 0)
        app.gui.setvar(
            group, "boundary_forcing", self.domain.boundary_conditions.forcing
        )
        app.gui.setvar(group, "boundary_hm0", 1.0)
        app.gui.setvar(group, "boundary_tp", 6.0)
        app.gui.setvar(group, "boundary_wd", 0.0)
        app.gui.setvar(group, "boundary_ds", 30.0)

        # Observation points – regular
        app.gui.setvar(group, "observation_point_names_regular", [])
        app.gui.setvar(group, "nr_observation_points_regular", 0)
        app.gui.setvar(group, "active_observation_point_regular", 0)

        # Observation points – spectra
        app.gui.setvar(group, "observation_point_names_spectra", [])
        app.gui.setvar(group, "nr_observation_points_spectra", 0)
        app.gui.setvar(group, "active_observation_point_spectra", 0)

    def set_model_variables(self) -> None:
        """Copy GUI variables back to the HurrywaveModel config."""
        group = _MODEL
        for key in self.domain.config.data.model_dump(exclude_none=False):
            try:
                val = app.gui.getvar(group, key)
                self.domain.config.set(key, val, skip_validation=True)
            except Exception:
                pass

    def add_stations(
        self, gdf_stations_to_add: gpd.GeoDataFrame, naming_option: str = "id"
    ) -> None:
        """Add observation stations to the model.

        Parameters
        ----------
        gdf_stations_to_add : gpd.GeoDataFrame
            GeoDataFrame with station geometries.
        naming_option : str, optional
            Column name used for station names, by default ``'id'``.
        """
        self.domain.observation_points.add_points(
            gdf_stations_to_add, name=naming_option
        )
        gdf = self.domain.observation_points.gdf
        app.map.layer[_MODEL].layer["observation_points_regular"].set_data(gdf, 0)
        self.domain.observation_points.write()

    def get_view_menu(self) -> dict:
        """Return the view menu definition for this model."""
        model_view_menu = {"text": self.long_name, "menu": []}
        model_view_menu["menu"].append(
            {
                "variable_group": self.name,
                "id": f"view.{self.name}.grid",
                "text": "Grid",
                "variable": "view_grid",
                "separator": True,
                "checkable": True,
                "method": self.set_view_menu,
                "option": "grid",
                "dependency": [
                    {
                        "action": "check",
                        "checkfor": "all",
                        "check": [
                            {"variable": "view_grid", "operator": "eq", "value": True}
                        ],
                    }
                ],
            }
        )
        return model_view_menu

    def set_view_menu(self, option: str, checked: bool) -> None:
        """Toggle map layer visibility from the view menu.

        Parameters
        ----------
        option : str
            The view menu option (e.g. ``'grid'``).
        checked : bool
            Whether the option is checked.
        """
        if option == "grid":
            if app.gui.getvar(self.name, "view_grid"):
                app.map.layer[_MODEL].layer["grid"].show()
            else:
                app.map.layer[_MODEL].layer["grid"].hide()
