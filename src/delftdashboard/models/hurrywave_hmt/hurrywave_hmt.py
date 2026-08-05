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
        if hasattr(app, "topography_data_catalog"):
            app.topography_data_catalog.add_to_model_catalog(self.domain.data_catalog)
        self._set_crs_config()
        self.set_gui_variables()
        # Switch to r+ so explicit reads work without auto-reading on init
        self.domain.root.mode = "r+"
        self.observation_points_changed = False
        self.observation_points_spectra_changed = False

    def _set_crs_config(self) -> None:
        """Store the application CRS in the config (epsg, name and type)."""
        self.domain.config.set("crs_epsg", app.crs.to_epsg(), skip_validation=True)
        self.domain.config.set("crs_name", app.crs.name, skip_validation=True)
        self.domain.config.set(
            "crs_type",
            "geographic" if app.crs.is_geographic else "projected",
            skip_validation=True,
        )

    def add_layers(self) -> None:
        """Register all map layers for the HurryWave model."""
        layer = app.map.add_layer(_MODEL)
        # Single shared legend for every geometry descendant.
        layer.legend_position = "bottom-right-2"

        layer.add_layer(
            "bathymetry",
            type="raster_image",
            map_overlay_options=self._bathymetry_overlay_options,
        )

        layer.add_layer(
            "mask",
            type="raster_image",
            legend_title="Mask",
            legend_position="bottom-right-2",
            map_overlay_options={
                "colors": {1: "yellow", 2: "red"},
                "labels": {1: "Active", 2: "Boundary"},
            },
        )

        layer.add_layer(
            "grid",
            type="raster_image",
            map_overlay_options={"color": "black"},
        )

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
            legend_label="boundary point",
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
            legend_label="observation point",
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
            legend_label="spectra observation point",
        )

    def _bathymetry_overlay_options(self) -> dict:
        """Return current topography view settings for the bathymetry overlay."""
        try:
            # Get the info from the background topography layer
            return {
                "cmin": app.map.layer["main"].layer["background_topography"].current_cmin,
                "cmax": app.map.layer["main"].layer["background_topography"].current_cmax,
                "cmap": app.map.layer["main"].layer["background_topography"].current_cmap,
            }
        except Exception:
            return {"cmin": -10.0, "cmax": 10.0, "cmap": "gist_earth"}

    def set_layer_mode(self, mode: str) -> None:
        """Show, hide, or deactivate map layers depending on *mode*.

        Parameters
        ----------
        mode : str
            One of ``'inactive'`` or ``'invisible'``.
        """
        layer = app.map.layer[_MODEL]
        if mode == "inactive":
            if app.gui.getvar(self.name, "view_grid"):
                layer.layer["grid"].show()
            else:
                layer.layer["grid"].hide()
            layer.layer["mask"].hide()
            if app.gui.getvar(self.name, "view_bathymetry"):
                layer.layer["bathymetry"].show()
            else:
                layer.layer["bathymetry"].hide()
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
            if hasattr(app, "topography_data_catalog"):
                app.topography_data_catalog.add_to_model_catalog(
                    self.domain.data_catalog
                )
            self.domain.read()

            # DelftDashboard only supports quadtree HurryWave models
            if self.domain.config.get("qtrfile") is None or self.domain.crs is None:
                dlg.close()
                app.gui.window.dialog_warning(
                    "This HurryWave model has no quadtree grid file (qtrfile) "
                    "and cannot be opened."
                )
                self.initialize()
                return

            self.set_gui_variables()
            map.set_crs(self.domain.crs)
            self.plot()
            self.observation_points_changed = False
            self.observation_points_spectra_changed = False
            dlg.close()
            app.gui.window.update()
            self.zoom_to_model()

    def save(self) -> None:
        """Write the current model configuration (and a launcher script) to disk."""
        self._set_crs_config()
        exe_path = app.config.get("hurrywave_exe_path")
        if exe_path:
            self.domain.exe_path = exe_path
        # Write components with unsaved changes before the config write so
        # their file entries (obsfile, ospfile) end up in hurrywave.inp.
        pending = [
            ("observation_points_changed", "observation_points"),
            ("observation_points_spectra_changed", "observation_points_spectra"),
        ]
        for flag, name in pending:
            component = self.domain.components.get(name)
            if component is not None and getattr(self, flag, False):
                try:
                    component.write()
                    setattr(self, flag, False)
                except Exception as e:
                    print(f"Could not write {name}: {e}")
        self.domain.config.write(write_description=True)
        # DDB always wants the launcher; the hydromt default is False so
        # script callers don't get a surprise batch file.
        if exe_path:
            try:
                self.domain.write_batch_file()
            except Exception as e:
                print(f"Could not write run script: {e}")

    def set_crs(self) -> None:
        """Update the model CRS to match the application CRS.

        Existing spatial data (grid, mask, geometries, forcing) is invalid in
        the new CRS and is cleared.
        """
        crs = app.crs
        try:
            old_crs = self.domain.crs
        except (KeyError, AttributeError):
            return
        if old_crs != crs:
            self._set_crs_config()
            self.clear_spatial_attributes()

    def plot(self) -> None:
        """Plot all model layers on the map."""
        layer = app.map.layer[_MODEL]
        layer.layer["grid"].set_data(self.domain.quadtree_grid)
        layer.layer["mask"].set_data(self.domain.quadtree_mask)
        # Bathymetry overlay is only shown when toggled from the View menu
        if app.gui.getvar(_MODEL, "view_bathymetry"):
            layer.layer["bathymetry"].set_data(self.domain.quadtree_elevation)
        layer.layer["boundary_points"].set_data(self.domain.boundary_conditions.gdf, 0)
        layer.layer["observation_points_regular"].set_data(
            self.domain.observation_points.gdf, 0
        )
        layer.layer["observation_points_spectra"].set_data(
            self.domain.observation_points_spectra.gdf, 0
        )
        # Refresh the point-list GUI variables so dependency-gated widgets
        # are correct right after opening a model (set_gui_variables resets
        # the counters to zero before plot() runs)
        self.update_lists()

    def update_lists(self) -> None:
        """Refresh the point-list GUI variables from the model components."""
        group = _MODEL
        nr_bnd = self.domain.boundary_conditions.nr_points
        app.gui.setvar(group, "nr_boundary_points", nr_bnd)
        app.gui.setvar(
            group,
            "boundary_point_names",
            [f"Point {i + 1:03d}" for i in range(nr_bnd)],
        )
        for comp, suffix in [
            (self.domain.observation_points, "regular"),
            (self.domain.observation_points_spectra, "spectra"),
        ]:
            gdf = comp.gdf
            if len(gdf) > 0 and "name" in gdf.columns:
                names = [str(v) for v in gdf["name"].values]
            else:
                names = [f"Point {i + 1:03d}" for i in range(len(gdf))]
            app.gui.setvar(group, f"observation_point_names_{suffix}", names)
            app.gui.setvar(group, f"nr_observation_points_{suffix}", len(gdf))

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
        self.domain.clear_spatial_attributes()
        self.clear_layers()
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
        app.gui.setvar(group, "view_bathymetry", False)
        # Meteo wind source selector (re-derived from the config file
        # entries in meteo.update_sources whenever the Meteo tab is selected)
        app.gui.setvar(group, "wind_source", "none")
        app.gui.setvar(
            group,
            "wind_source_values",
            ["none", "uniform", "gridded", "netcdf", "spiderweb"],
        )
        app.gui.setvar(
            group,
            "wind_source_names",
            ["None", "Uniform", "Gridded (Delft3D)", "Gridded (NetCDF)", "Spiderweb"],
        )

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

        # Domain tab (read-only, filled from the quadtree grid itself)
        app.gui.setvar(group, "refinement_level_index", 0)
        self.update_domain_info()

    def update_domain_info(self) -> None:
        """Fill the Domain-tab variables from the quadtree grid itself.

        The grid attributes (x0, y0, mmax, nmax, dx, dy, rotation) and the
        per-refinement-level active cell counts come straight from the
        quadtree dataset (hurrywave.nc), never from the model-maker GUI.
        """
        import numpy as np

        group = _MODEL
        attrs: dict = {}
        levels = None
        mask = None
        try:
            data = self.domain.quadtree_grid.data
            if data is not None and "level" in data:
                attrs = dict(data.attrs)
                levels = data["level"].to_numpy()
                if "mask" in data:
                    mask = data["mask"].to_numpy()
        except Exception:
            pass

        app.gui.setvar(group, "x0", float(attrs.get("x0", 0.0)))
        app.gui.setvar(group, "y0", float(attrs.get("y0", 0.0)))
        app.gui.setvar(group, "mmax", int(attrs.get("mmax", 0)))
        app.gui.setvar(group, "nmax", int(attrs.get("nmax", 0)))
        app.gui.setvar(group, "dx", float(attrs.get("dx", 0.0)))
        app.gui.setvar(group, "dy", float(attrs.get("dy", 0.0)))
        app.gui.setvar(group, "rotation", float(attrs.get("rotation", 0.0)))

        info = []
        if levels is not None and len(levels) > 0:
            active = levels if mask is None else levels[mask > 0]
            nr_levels = int(attrs.get("nr_levels", int(levels.max())))
            for ilev in range(nr_levels):
                count = int(np.sum(active == ilev + 1))
                info.append(f"Level {ilev + 1}: {count} active cells")
            info.append(f"Total: {len(active)} active cells")
        app.gui.setvar(group, "refinement_level_info", info)

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
        gdf = gdf_stations_to_add.copy()
        # The observation_points component expects a "name" column; fill it
        # from the requested naming column of the stations source.
        if naming_option in gdf.columns:
            gdf["name"] = gdf[naming_option].astype(str)
        elif "name" not in gdf.columns:
            gdf["name"] = [str(i + 1) for i in range(len(gdf))]
        try:
            self.domain.observation_points.add_points(gdf)
        except Exception as e:
            app.gui.window.dialog_warning(f"Cannot add stations:\n{e}")
            return
        gdf = self.domain.observation_points.gdf
        app.map.layer[_MODEL].layer["observation_points_regular"].set_data(gdf, 0)
        self.domain.observation_points.write()
        self.update_lists()
        app.gui.window.update()

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
        model_view_menu["menu"].append(
            {
                "variable_group": self.name,
                "id": f"view.{self.name}.bathymetry",
                "text": "Bathymetry",
                "variable": "view_bathymetry",
                "separator": False,
                "checkable": True,
                "method": self.set_view_menu,
                "option": "bathymetry",
                "dependency": [
                    {
                        "action": "check",
                        "checkfor": "all",
                        "check": [
                            {"variable": "view_bathymetry", "operator": "eq", "value": True}
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
        elif option == "bathymetry":
            if app.gui.getvar(self.name, "view_bathymetry"):
                app.map.layer[_MODEL].layer["bathymetry"].set_data(
                    self.domain.quadtree_elevation
                )
                app.map.layer[_MODEL].layer["bathymetry"].show()
            else:
                app.map.layer[_MODEL].layer["bathymetry"].hide()
