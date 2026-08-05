"""SFINCS (HydroMT) model plugin for DelftDashboard.

Provides the ``Model`` class that wraps a HydroMT-SFINCS domain,
registers map layers, and synchronizes GUI state with the model
configuration for the SFINCS coastal flooding model.
"""

import os
from typing import Any, Optional

from hydromt_sfincs import SfincsModel

from delftdashboard.app import app
from delftdashboard.operations import map
from delftdashboard.operations.model import GenericModel

_MODEL = "sfincs_hmt"
_GROUP = "sfincs_hmt"


class Model(GenericModel):
    """DelftDashboard model wrapper for SFINCS via HydroMT-SFINCS."""

    def __init__(self, name: str) -> None:
        """Initialize the SFINCS model plugin.

        Parameters
        ----------
        name : str
            Identifier for this model instance (typically ``"sfincs_hmt"``).
        """
        super().__init__()

        self.name = name
        self.long_name = "SFINCS (HydroMT)"

    def initialize(self) -> None:
        """Create a fresh SfincsModel domain and set default GUI variables."""
        # Drop any features left over from a previously-loaded model so
        # a "New Model" or a second "Open Model" doesn't leak stale
        # polygons / points onto the map.
        self.clear_layers()
        self.domain = SfincsModel(root=".", mode="w", write_gis=False)
        if hasattr(app, "topography_data_catalog"):
            app.topography_data_catalog.add_to_model_catalog(self.domain.data_catalog)
        self.domain.config.set("epsg", app.crs.to_epsg())
        # Establish the grid type now (while still in write mode) so that the
        # grid_type getter never tries to read a (possibly absent or stale)
        # sfincs.inp from the working directory later on.
        self.domain.config.update_grid_from_config()
        # Set to "r+" to allow explicit reads without auto-reading on init
        self.domain.root.mode = "r+"
        self.set_gui_variables()
        self.observation_points_changed = False
        self.cross_sections_changed = False
        self.discharge_points_changed = False
        self.boundaries_changed = False
        self.thin_dams_changed = False
        self.weirs_changed = False
        self.drainage_structures_changed = False
        self.urban_drainage_changed = False
        self.wave_boundaries_changed = False
        self.wave_makers_changed = False

    def get_view_menu(self) -> dict:
        """Build the View menu entries for this model.

        Returns
        -------
        dict
            Menu definition dict with text, sub-items, and callbacks.
        """
        model_view_menu = {}
        model_view_menu["text"] = self.long_name
        model_view_menu["menu"] = []
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
                            {
                                "variable": "view_bathymetry",
                                "operator": "eq",
                                "value": True,
                            }
                        ],
                    }
                ],
            }
        )
        return model_view_menu

    def set_view_menu(self, option: str, checked: bool) -> None:
        """Handle View menu toggling for model layers.

        Parameters
        ----------
        option : str
            The menu option toggled (e.g. ``"grid"``).
        checked : bool
            Whether the option is now checked.
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

    def _bathymetry_overlay_options(self) -> dict:
        """Return current topography view settings for the bathymetry overlay."""
        try:
            topo = app.map.layer["main"].layer["background_topography"]
            return {
                "cmin": topo.current_cmin,
                "cmax": topo.current_cmax,
                "cmap": topo.current_cmap,
                "legend": False,
            }
        except Exception:
            return {"cmin": -10.0, "cmax": 10.0, "cmap": "gist_earth", "legend": False}

    def add_layers(self) -> None:
        """Register all map layers for the SFINCS model."""
        layer = app.map.add_layer(_MODEL)
        # Single shared legend for every geometry descendant. Leaves
        # that declare ``legend_label`` contribute a swatch; layers
        # that don't, stay out.
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
                "colors": {1: "yellow", 2: "red", 3: "pink", 5: "orange", 6: "limegreen"},
                "labels": {
                    1: "Active",
                    2: "Water level",
                    3: "Outflow",
                    5: "Downstream",
                    6: "Neumann",
                },
            },
        )

        layer.add_layer(
            "mask_snapwave",
            type="raster_image",
            legend_title="SnapWave Mask",
            legend_position="bottom-right-2",
            map_overlay_options={
                "colors": {1: "yellow", 2: "red", 3: "green"},
                "labels": {1: "Active", 2: "Boundary", 3: "Neumann"},
            },
        )

        layer.add_layer(
            "grid",
            type="raster_image",
            map_overlay_options={"color": "black"},
        )

        layer.add_layer(
            "grid_exterior", type="line", circle_radius=0, line_color="yellow"
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

        from .structures_thin_dams import (
            thin_dam_created,
            thin_dam_modified,
            thin_dam_selected,
        )

        thd_layer = layer.add_layer("thin_dams")
        thd_layer.add_layer(
            "polylines",
            type="draw",
            shape="polyline",
            create=thin_dam_created,
            modify=thin_dam_modified,
            select=thin_dam_selected,
            polyline_line_color="yellow",
            polyline_line_width=2.0,
            polyline_line_opacity=1.0,
            legend_label="thin dam",
        )
        thd_layer.add_layer(
            "snapped",
            type="line",
            line_color="white",
            line_opacity=1.0,
            circle_radius=0,
            line_color_inactive="lightgrey",
            legend_label="thin dam (snapped)",
        )

        from .structures_weirs import weir_created, weir_modified, weir_selected

        weir_layer = layer.add_layer("weirs")
        weir_layer.add_layer(
            "polylines",
            type="draw",
            shape="polyline",
            create=weir_created,
            modify=weir_modified,
            select=weir_selected,
            polyline_line_color="yellow",
            polyline_line_width=2.0,
            polyline_line_opacity=1.0,
            legend_label="weir",
        )
        weir_layer.add_layer(
            "snapped",
            type="line",
            line_color="white",
            line_opacity=1.0,
            circle_radius=0,
            line_color_inactive="lightgrey",
            legend_label="weir (snapped)",
        )

        from .structures_drainage_structures import (
            drainage_structure_created,
            drainage_structure_modified,
            drainage_structure_selected,
        )

        layer.add_layer(
            "drainage_structures",
            type="draw",
            shape="polyline",
            create=drainage_structure_created,
            modify=drainage_structure_modified,
            select=drainage_structure_selected,
            polyline_line_color="yellow",
            polyline_line_width=2.0,
            polyline_line_opacity=1.0,
            legend_label="drainage structure",
        )

        from .urban_drainage import (
            urban_drainage_area_created,
            urban_drainage_area_modified,
            urban_drainage_area_selected,
        )

        # Container grouping the two urban-drainage sub-layers. The
        # legend is owned by the top-level SFINCS container, so no
        # per-sub-container ``legend_position`` is needed here.
        urban_drainage_layer = layer.add_layer("urban_drainage")

        urban_drainage_layer.add_layer(
            "urban_drainage_areas",
            type="draw",
            shape="polygon",
            create=urban_drainage_area_created,
            modify=urban_drainage_area_modified,
            select=urban_drainage_area_selected,
            polygon_line_color="orange",
            polygon_line_width=2.0,
            polygon_line_opacity=1.0,
            polygon_fill_color="orange",
            polygon_fill_opacity=0.2,
            legend_label="urban drainage area",
        )

        urban_drainage_layer.add_layer(
            "outfall_locations",
            type="circle",
            hover_property="name",
            line_color="white",
            line_opacity=1.0,
            fill_color="orange",
            fill_opacity=1.0,
            circle_radius=5,
            legend_label="outfall location",
        )

        from .observation_points_observation_points import (
            select_observation_point_from_map,
        )

        layer.add_layer(
            "observation_points",
            type="circle_selector",
            select=select_observation_point_from_map,
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

        from .observation_points_cross_sections import (
            cross_section_created,
            cross_section_modified,
            cross_section_selected,
        )

        crs_layer = layer.add_layer("cross_sections")
        crs_layer.add_layer(
            "polylines",
            type="draw",
            shape="polyline",
            create=cross_section_created,
            modify=cross_section_modified,
            select=cross_section_selected,
            polyline_line_color="yellow",
            polyline_line_width=2.0,
            polyline_line_opacity=1.0,
            legend_label="cross section",
        )
        crs_layer.add_layer(
            "snapped",
            type="line",
            line_color="white",
            line_opacity=1.0,
            circle_radius=0,
            line_color_inactive="lightgrey",
            legend_label="cross section (snapped)",
        )

        from .discharge_points import select_discharge_point_from_map

        layer.add_layer(
            "discharge_points",
            type="circle_selector",
            select=select_discharge_point_from_map,
            hover_property="name",
            line_color="white",
            line_opacity=1.0,
            fill_color="blue",
            fill_opacity=1.0,
            circle_radius=3,
            circle_radius_selected=4,
            line_color_selected="white",
            fill_color_selected="red",
            legend_label="discharge point",
        )

        from .waves_boundary_conditions import select_boundary_point_from_map_snapwave

        layer.add_layer(
            "boundary_points_snapwave",
            type="circle_selector",
            select=select_boundary_point_from_map_snapwave,
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
            legend_label="SnapWave boundary point",
        )

        # Wave makers
        from .waves_wave_makers import (
            wave_maker_created,
            wave_maker_modified,
            wave_maker_selected,
        )

        layer.add_layer(
            "wave_makers",
            type="draw",
            shape="polyline",
            create=wave_maker_created,
            modify=wave_maker_modified,
            select=wave_maker_selected,
            add=wave_maker_modified,
            polygon_line_color="red",
            show_endpoints=True,
            legend_label="wave maker",
        )
        layer.add_layer(
            "wave_makers_snapped",
            type="line",
            line_color="white",
            line_opacity=1.0,
            circle_radius=0,
            line_color_inactive="lightgrey",
            legend_label="wave maker (snapped)",
        )

    def set_layer_mode(self, mode: str) -> None:
        """Set the visibility/activation mode for all model layers.

        Parameters
        ----------
        mode : str
            Either ``"inactive"`` (grey out) or ``"invisible"`` (hide all).
        """
        layer = app.map.layer[_MODEL]
        if mode == "inactive":
            if app.gui.getvar(self.name, "view_grid"):
                layer.layer["grid"].show()
            else:
                layer.layer["grid"].hide()
            layer.layer["grid_exterior"].deactivate()
            layer.layer["mask"].hide()
            layer.layer["mask_snapwave"].hide()
            if app.gui.getvar(self.name, "view_bathymetry"):
                layer.layer["bathymetry"].show()
            else:
                layer.layer["bathymetry"].hide()
            layer.layer["boundary_points"].deactivate()
            layer.layer["observation_points"].deactivate()
            layer.layer["cross_sections"].layer["polylines"].deactivate()
            layer.layer["cross_sections"].layer["snapped"].hide()
            layer.layer["discharge_points"].deactivate()
            layer.layer["thin_dams"].layer["polylines"].deactivate()
            layer.layer["thin_dams"].layer["snapped"].hide()
            layer.layer["weirs"].layer["polylines"].deactivate()
            layer.layer["weirs"].layer["snapped"].hide()
            layer.layer["drainage_structures"].deactivate()
            # Grey out the drawn areas like the other geometry layers; only
            # the derived outfall circles are hidden (like the snapped layers)
            layer.layer["urban_drainage"].layer["urban_drainage_areas"].deactivate()
            layer.layer["urban_drainage"].layer["outfall_locations"].hide()
            layer.layer["boundary_points_snapwave"].deactivate()
            layer.layer["wave_makers"].deactivate()
            layer.layer["wave_makers_snapped"].hide()
        elif mode == "invisible":
            layer.hide()

    def set_crs(self) -> None:
        """Update the model CRS to match the application CRS.

        Existing spatial data (grid, mask, geometries, forcing) is invalid in
        the new CRS and is cleared. The model CRS itself is derived from the
        ``epsg`` entry in the SFINCS config (``SfincsModel.crs`` is
        read-only), so store the new EPSG code there.
        """
        crs = app.crs
        try:
            old_crs = self.domain.crs
        except (KeyError, AttributeError, ValueError, FileNotFoundError):
            # Model not yet initialized — no CRS to update
            return
        if old_crs != crs:
            # Set the new EPSG first: clearing re-derives the grid properties
            # from the config, so it must already hold the new CRS.
            self.domain.config.set("epsg", crs.to_epsg(), skip_validation=True)
            self.clear_spatial_attributes()
            self.set_gui_variables()

    def clear_spatial_attributes(self) -> None:
        """Clear all spatial model data and its map layers, keeping the config."""
        self.domain.clear_spatial_attributes()
        self.clear_layers()
        self.observation_points_changed = False
        self.cross_sections_changed = False
        self.discharge_points_changed = False
        self.boundaries_changed = False
        self.thin_dams_changed = False
        self.weirs_changed = False
        self.drainage_structures_changed = False
        self.urban_drainage_changed = False
        self.wave_boundaries_changed = False
        self.wave_makers_changed = False

    def open(self, filename: Optional[str] = None) -> None:
        """Open an existing SFINCS model from an input file.

        Parameters
        ----------
        filename : str or None
            Path to ``sfincs.inp``. If ``None``, a file dialog is shown.
        """
        if filename is None:
            # Open file dialog to select input file
            filename = app.gui.window.dialog_open_file(
                "Open file", filter="SFINCS input file (sfincs.inp)"
            )
            filename = filename[0]

        if filename:
            dlg = app.gui.window.dialog_wait("Loading SFINCS model ...")
            path = os.path.dirname(filename)
            # if path is and empty string, use current working directory
            if not path:
                path = os.getcwd()
            os.chdir(path)
            self.initialize()
            self.domain = SfincsModel(root=".", mode="r+", write_gis=False)
            if hasattr(app, "topography_data_catalog"):
                app.topography_data_catalog.add_to_model_catalog(self.domain.data_catalog)

            # DelftDashboard only supports quadtree SFINCS models
            if self.domain.config.get("qtrfile") is None:    
                dlg.close()
                app.gui.window.dialog_warning(
                    "DelftDashboard only supports SFINCS models with a "
                    "quadtree grid. This model uses a regular grid and "
                    "cannot be opened."
                )
                self.initialize()
                return

            self.set_gui_variables()
            # Change CRS
            map.set_crs(self.domain.crs)
            self.plot()
            dlg.close()
            app.gui.window.update()

            # Zoom to model extent (cht_sfincs has a nice function for this...)
            buffer = 0.1
            crds = self.domain.quadtree_grid.exterior.to_crs(
                crs=4326
            ).total_bounds.tolist()
            dx = crds[2] - crds[0]
            dy = crds[3] - crds[1]
            crds[0] = crds[0] - buffer * dx
            crds[1] = crds[1] - buffer * dy
            crds[2] = crds[2] + buffer * dx
            crds[3] = crds[3] + buffer * dy
            app.map.fit_bounds(crds[0], crds[1], crds[2], crds[3])

    def save(self) -> None:
        """Write the SFINCS configuration (and a launcher script) to disk."""
        self.check_times()
        domain = app.model[_MODEL].domain
        exe_path = app.config.get("sfincs_exe_path")
        if exe_path:
            domain.exe_path = exe_path
        # Write every component with unsaved changes, so that File > Save
        # captures everything without requiring a separate save from each
        # tab. Must happen before the config write so the file entries
        # (obsfile, thdfile, urbfile, ...) end up in sfincs.inp. Each
        # component's write() is a no-op when it holds no data.
        pending = [
            ("observation_points_changed", "observation_points"),
            ("cross_sections_changed", "cross_sections"),
            ("discharge_points_changed", "discharge_points"),
            ("boundaries_changed", "water_level"),
            ("thin_dams_changed", "thin_dams"),
            ("weirs_changed", "weirs"),
            ("drainage_structures_changed", "drainage_structures"),
            ("urban_drainage_changed", "urban_drainage_areas"),
            ("wave_boundaries_changed", "snapwave_boundary_conditions"),
            ("wave_makers_changed", "wave_makers"),
        ]
        for flag, name in pending:
            component = domain.components.get(name)
            if component is not None and getattr(self, flag, False):
                try:
                    component.write()
                    setattr(self, flag, False)
                except Exception as e:
                    print(f"Could not write {name}: {e}")
        # DDB always wants the launcher; the hydromt default is False so
        # script callers don't get a surprise batch file.
        domain.config.write(write_description=True)
        if exe_path:
            try:
                domain.write_batch_file()
            except Exception as e:
                print(f"Could not write run script: {e}")

    def plot(self) -> None:
        """Plot all model features on the map."""
        # Bathymetry (only shown when toggled from the View menu)
        if app.gui.getvar(_GROUP, "view_bathymetry"):
            app.map.layer[_MODEL].layer["bathymetry"].set_data(
                app.model[_MODEL].domain.quadtree_elevation
            )
        # Grid
        app.map.layer[_MODEL].layer["grid"].set_data(
            app.model[_MODEL].domain.quadtree_grid
        )
        # Grid exterior
        app.map.layer[_MODEL].layer["grid_exterior"].set_data(
            app.model[_MODEL].domain.quadtree_grid.exterior
        )
        # Mask
        app.map.layer[_MODEL].layer["mask"].set_data(
            app.model[_MODEL].domain.quadtree_mask
        )
        # Thin dams
        app.map.layer[_MODEL].layer["thin_dams"].layer["polylines"].set_data(
            app.model[_MODEL].domain.thin_dams.gdf
        )
        # Weirs
        app.map.layer[_MODEL].layer["weirs"].layer["polylines"].set_data(
            app.model[_MODEL].domain.weirs.gdf
        )
        # Drainage structures
        app.map.layer[_MODEL].layer["drainage_structures"].set_data(
            app.model[_MODEL].domain.drainage_structures.gdf
        )


        # Urban drainage areas (under the urban_drainage container) and
        # their derived outfall-location circles. Only available on the
        # urban_drainage branch of hydromt_sfincs.
        if "urban_drainage_areas" in app.model[_MODEL].domain.components:
            app.map.layer[_MODEL].layer["urban_drainage"].layer[
                "urban_drainage_areas"
            ].set_data(app.model[_MODEL].domain.urban_drainage_areas.gdf)
            from .urban_drainage import plot_outfall_layer
            plot_outfall_layer()

        # Observation points
        app.map.layer[_MODEL].layer["observation_points"].set_data(
            app.model[_MODEL].domain.observation_points.gdf, 0
        )


        # Cross sections
        app.map.layer[_MODEL].layer["cross_sections"].layer["polylines"].set_data(
            app.model[_MODEL].domain.cross_sections.gdf
        )
        # Boundary points
        app.map.layer[_MODEL].layer["boundary_points"].set_data(
            app.model[_MODEL].domain.water_level.gdf, 0
        )
        # Discharge points
        app.map.layer[_MODEL].layer["discharge_points"].set_data(
            app.model[_MODEL].domain.discharge_points.gdf, 0
        )
        # Mask SnapWave
        app.map.layer[_MODEL].layer["mask_snapwave"].set_data(
            app.model[_MODEL].domain.quadtree_snapwave_mask
        )
        # SnapWave Boundary points
        app.map.layer[_MODEL].layer["boundary_points_snapwave"].set_data(
            app.model[_MODEL].domain.snapwave_boundary_conditions.gdf, 0
        )
        # Wave makers
        app.map.layer[_MODEL].layer["wave_makers"].set_data(
            app.model[_MODEL].domain.wave_makers.data
        )
        # Snapped-to-grid overlays. Normally refreshed on tab select, but
        # fill them here too so they are correct right after opening a model.
        from .observation_points_cross_sections import (
            update_grid_snapper as update_cross_section_snapper,
        )
        from .structures_thin_dams import (
            update_grid_snapper as update_thin_dam_snapper,
        )
        from .structures_weirs import update_grid_snapper as update_weir_snapper
        from .waves_wave_makers import (
            update_grid_snapper as update_wave_maker_snapper,
        )
        update_thin_dam_snapper()
        update_weir_snapper()
        update_cross_section_snapper()
        update_wave_maker_snapper()

    def set_gui_variables(self) -> None:
        """Populate GUI variables from the current model configuration."""
        group = _GROUP

        # Copy sfincs input variables to gui variables
        for key, value in self.domain.config.data.model_dump(
            exclude_unset=False
        ).items():
            app.gui.setvar(group, key, value)

        # View
        app.gui.setvar(group, "view_grid", True)
        app.gui.setvar(group, "view_bathymetry", False)

        # Now set some extra variables needed for SFINCS GUI

        # Subgrid models get their own dependency branches in the GUI
        # (wiggle suppression, roughness tab)
        app.gui.setvar(
            group,
            "bathymetry_type",
            "subgrid" if self.domain.config.get("sbgfile") else "regular",
        )
        app.gui.setvar(group, "roughness_type", "landsea")
        app.gui.setvar(group, "output_options_text", ["NetCDF", "Binary", "ASCII"])
        app.gui.setvar(group, "output_options_values", ["net", "bin", "asc"])
        # Meteo source selectors (re-derived from the config file entries in
        # meteo.update_sources whenever the Meteo tab is selected)
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
        app.gui.setvar(group, "pressure_source", "none")
        app.gui.setvar(
            group,
            "pressure_source_values",
            ["none", "gridded", "netcdf", "spiderweb"],
        )
        app.gui.setvar(
            group,
            "pressure_source_names",
            ["None", "Gridded (Delft3D)", "Gridded (NetCDF)", "Spiderweb"],
        )
        app.gui.setvar(group, "rain_source", "none")
        app.gui.setvar(
            group,
            "rain_source_values",
            ["none", "uniform", "gridded", "netcdf", "spiderweb"],
        )
        app.gui.setvar(
            group,
            "rain_source_names",
            ["None", "Uniform", "Gridded (Delft3D)", "Gridded (NetCDF)", "Spiderweb"],
        )
        app.gui.setvar(
            group,
            "crs_type",
            "geographic" if app.crs.is_geographic else "projected",
        )

        # Wind drag. Fallbacks match the config-model defaults (the
        # built-in Smith & Banke 3-point curve); pad short lists so a
        # 2-breakpoint model does not crash the GUI.
        cdwnd = list(self.domain.config.get("cdwnd") or [0.0, 28.0, 50.0])
        cdval = list(self.domain.config.get("cdval") or [0.001, 0.0025, 0.0025])
        while len(cdwnd) < 3:
            cdwnd.append(cdwnd[-1] if cdwnd else 0.0)
        while len(cdval) < 3:
            cdval.append(cdval[-1] if cdval else 0.0)
        app.gui.setvar(group, "wind_speed_1", cdwnd[0])
        app.gui.setvar(group, "wind_speed_2", cdwnd[1])
        app.gui.setvar(group, "wind_speed_3", cdwnd[2])
        app.gui.setvar(group, "cd_1", cdval[0])
        app.gui.setvar(group, "cd_2", cdval[1])
        app.gui.setvar(group, "cd_3", cdval[2])

        # Boundary conditions
        app.gui.setvar(group, "boundary_point_names", [])
        app.gui.setvar(group, "nr_boundary_points", 0)
        app.gui.setvar(group, "active_boundary_point", 0)
        app.gui.setvar(group, "boundary_dx", 10000.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_or_astro", "timeseries")
        app.gui.setvar(group, "boundary_conditions_timeseries_shape", "constant")
        app.gui.setvar(group, "boundary_conditions_timeseries_time_step", 600.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_offset", 0.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_amplitude", 1.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_phase", 0.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_period", 43200.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_peak", 1.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_tpeak", 86400.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_duration", 43200.0)
        tide_model_names = app.gui.getvar("tide_models", "names")
        app.gui.setvar(
            group,
            "boundary_conditions_tide_model",
            tide_model_names[0] if tide_model_names else "",
        )

        # Observation points
        app.gui.setvar(group, "observation_point_names", [])
        app.gui.setvar(group, "nr_observation_points", 0)
        app.gui.setvar(group, "active_observation_point", 0)
        app.gui.setvar(group, "observation_point_name", "")

        # Cross sections
        app.gui.setvar(group, "cross_section_names", [])
        app.gui.setvar(group, "nr_cross_sections", 0)
        app.gui.setvar(group, "active_cross_section", 0)
        app.gui.setvar(group, "cross_section_name", "")

        # Discharge points
        app.gui.setvar(group, "discharge_point_names", [])
        app.gui.setvar(group, "nr_discharge_points", 0)
        app.gui.setvar(group, "active_discharge_point", 0)

        # Thin dams
        app.gui.setvar(group, "thin_dam_names", [])
        app.gui.setvar(group, "nr_thin_dams", 0)
        app.gui.setvar(group, "thin_dam_index", 0)

        # Weirs
        app.gui.setvar(group, "weir_names", [])
        app.gui.setvar(group, "nr_weirs", 0)
        app.gui.setvar(group, "weir_index", 0)
        app.gui.setvar(group, "weir_elevation", 0.0)
        app.gui.setvar(group, "weir_par1", 0.5)
        app.gui.setvar(group, "weir_enable_editing_elevation", False)
        app.gui.setvar(group, "weir_enable_editing_par1", False)

        # Drainage
        app.gui.setvar(group, "drainage_structure_names", [])
        app.gui.setvar(group, "nr_drainage_structures", 0)
        app.gui.setvar(group, "drainage_structure_index", 0)
        app.gui.setvar(group, "drainage_structure_alpha", 0.6)
        app.gui.setvar(group, "drainage_structure_discharge", 1.0)
        app.gui.setvar(group, "drainage_structure_width", 100.0)
        app.gui.setvar(group, "drainage_structure_sill_elevation", 0.0)
        app.gui.setvar(group, "drainage_structure_manning_n", 0.024)
        app.gui.setvar(group, "drainage_structure_closing_time", 600.0)
        # Detailed culvert (type 5) parameters
        app.gui.setvar(group, "drainage_structure_height", 2.0)
        app.gui.setvar(group, "drainage_structure_invert_1", 0.0)
        app.gui.setvar(group, "drainage_structure_invert_2", 0.0)
        app.gui.setvar(group, "drainage_structure_submergence_ratio", 0.67)
        # Gate control rules: ordered list of (operation, when) per structure
        app.gui.setvar(group, "drainage_structure_rule_strings", [])
        app.gui.setvar(group, "nr_drainage_structure_rules", 0)
        app.gui.setvar(group, "drainage_structure_rule_index", 0)
        app.gui.setvar(group, "drainage_structure_rule_operation", "open")
        app.gui.setvar(
            group, "drainage_structure_rule_operations", ["open", "close", "hold"]
        )
        app.gui.setvar(
            group,
            "drainage_structure_rule_operation_names",
            ["Open", "Close", "Hold"],
        )
        app.gui.setvar(group, "drainage_structure_rule_when", "")
        app.gui.setvar(group, "drainage_structure_type", 1)
        app.gui.setvar(group, "drainage_structure_type_to_add", 1)
        app.gui.setvar(group, "drainage_structure_direction", "both")
        app.gui.setvar(
            group, "drainage_structure_directions", ["both", "positive", "negative"]
        )
        app.gui.setvar(
            group,
            "drainage_structure_direction_names",
            ["Both", "Positive", "Negative"],
        )
        # Integer codes used internally: 1=pump, 2=culvert_simple,
        # 5=culvert (detailed), 4=gate.
        app.gui.setvar(group, "drainage_structure_types", [1, 2, 5, 4])
        app.gui.setvar(
            group,
            "drainage_structure_type_names",
            ["Pump", "Culvert Simple", "Culvert", "Gate"],
        )

        # Urban drainage areas
        app.gui.setvar(group, "urban_drainage_area_names", [])
        app.gui.setvar(group, "nr_urban_drainage_areas", 0)
        app.gui.setvar(group, "urban_drainage_area_index", 0)
        app.gui.setvar(group, "selected_urban_drainage_area_name", "")
        app.gui.setvar(group, "urban_drainage_area_type", "piped_drainage")
        app.gui.setvar(
            group,
            "urban_drainage_area_types",
            ["piped_drainage", "injection_well"],
        )
        app.gui.setvar(
            group,
            "urban_drainage_area_type_names",
            ["Piped Drainage", "Injection Well"],
        )
        app.gui.setvar(
            group, "urban_drainage_area_type_to_add", "piped_drainage"
        )
        app.gui.setvar(group, "urban_drainage_area_h_threshold", 0.0)
        app.gui.setvar(group, "urban_drainage_area_outfall_x", 0.0)
        app.gui.setvar(group, "urban_drainage_area_outfall_y", 0.0)
        app.gui.setvar(group, "urban_drainage_area_capacity_mode", "design_precip")
        app.gui.setvar(
            group,
            "urban_drainage_area_capacity_modes",
            ["design_precip", "max_outfall_rate"],
        )
        app.gui.setvar(
            group,
            "urban_drainage_area_capacity_mode_names",
            ["Design precipitation", "Max outfall rate"],
        )
        app.gui.setvar(group, "urban_drainage_area_design_precip", 20.0)
        app.gui.setvar(group, "urban_drainage_area_max_outfall_rate", 1.0)
        app.gui.setvar(group, "urban_drainage_area_dh_design_min", 0.1)
        app.gui.setvar(group, "urban_drainage_area_include_outfall", True)
        app.gui.setvar(group, "urban_drainage_area_check_valve", False)
        app.gui.setvar(group, "urban_drainage_area_injection_rate", 0.5)
        app.gui.setvar(group, "urban_drainage_area_maximum_capacity", 1000.0)

        # SnapWave
        app.gui.setvar(
            "modelmaker_sfincs_hmt", "use_snapwave", app.gui.getvar(group, "snapwave")
        )
        app.gui.setvar(group, "boundary_point_names_snapwave", [])
        app.gui.setvar(group, "nr_boundary_points_snapwave", 0)
        app.gui.setvar(group, "active_boundary_point_snapwave", 0)
        app.gui.setvar(group, "boundary_dx_snapwave", 10000.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_hm0_snapwave", 1.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_tp_snapwave", 8.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_wd_snapwave", 0.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_ds_snapwave", 20.0)

        # Wave makers
        app.gui.setvar(group, "wave_maker_names", [])
        app.gui.setvar(group, "nr_wave_makers", 0)
        app.gui.setvar(group, "active_wave_maker", 0)

        # NOTE: "baro" must NOT be set here — it is a real SFINCS config key
        # already copied from the config in the loop above; overwriting it
        # would silently reset baro=1 models to 0 on the next edit.

        app.gui.setvar(group, "enable_weirs", True)

        # Domain tab (read-only, filled from the quadtree grid itself)
        app.gui.setvar(group, "refinement_level_index", 0)
        self.update_domain_info()

    def update_domain_info(self) -> None:
        """Fill the Domain-tab variables from the quadtree grid itself.

        The grid attributes (x0, y0, mmax, nmax, dx, dy, rotation) and the
        per-refinement-level active cell counts come straight from the
        quadtree dataset (sfincs.nc), never from the model-maker GUI.
        """
        import numpy as np

        group = _GROUP
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

    def set_model_variables(
        self, varid: Optional[str] = None, value: Any = None
    ) -> None:
        """Copy GUI variables back to the SFINCS model configuration.

        Parameters
        ----------
        varid : str or None
            Specific variable identifier to update (unused, all are copied).
        value : Any
            Value to set (unused, read from GUI).
        """
        group = _GROUP
        for key, value in self.domain.config.data.model_dump(
            exclude_unset=False
        ).items():
            self.domain.config.set(
                key, app.gui.getvar(group, key), skip_validation=True
            )
        if self.domain.config.get("snapwave"):
            app.gui.setvar("modelmaker_sfincs_hmt", "use_snapwave", True)
        else:
            app.gui.setvar("modelmaker_sfincs_hmt", "use_snapwave", False)
        # Wind drag
        cdwnd = []
        cdwnd.append(app.gui.getvar(group, "wind_speed_1"))
        cdwnd.append(app.gui.getvar(group, "wind_speed_2"))
        cdwnd.append(app.gui.getvar(group, "wind_speed_3"))
        cdval = []
        cdval.append(app.gui.getvar(group, "cd_1"))
        cdval.append(app.gui.getvar(group, "cd_2"))
        cdval.append(app.gui.getvar(group, "cd_3"))
        # Honour the number of breakpoints selected in the GUI (2 or 3)
        nrb = int(app.gui.getvar(group, "cdnrb") or 3)
        nrb = max(min(nrb, 3), 2)
        self.domain.config.set("cdwnd", cdwnd[:nrb])
        self.domain.config.set("cdval", cdval[:nrb])

    def set_input_variable(self, gui_variable: str, value: Any) -> None:
        """Set a single input variable (currently a no-op placeholder).

        Parameters
        ----------
        gui_variable : str
            The GUI variable name.
        value : Any
            The value to set.
        """
        pass

    def add_stations(self, gdf_stations_to_add: Any, naming_option: str = "id") -> None:
        """Add observation stations from a GeoDataFrame.

        Parameters
        ----------
        gdf_stations_to_add : GeoDataFrame
            Station locations to add.
        naming_option : str
            Column to use for station names (default ``"id"``).
        """
        gdf = gdf_stations_to_add.copy()
        # The observation_points component expects a "name" column; fill it
        # from the requested naming column of the stations source.
        if naming_option in gdf.columns:
            gdf["name"] = gdf[naming_option].astype(str)
        elif "name" not in gdf.columns:
            gdf["name"] = [str(i + 1) for i in range(len(gdf))]
        try:
            # create() reprojects to the model CRS, clips to the model
            # region, merges with existing points and sets obsfile in the
            # config.
            self.domain.observation_points.create(gdf, merge=True)
        except ValueError as e:
            app.gui.window.dialog_warning(f"Cannot add stations:\n{e}")
            return
        gdf = self.domain.observation_points.gdf
        app.map.layer[_MODEL].layer["observation_points"].set_data(gdf, 0)
        app.gui.setvar(_GROUP, "obsfile", self.domain.config.get("obsfile"))
        self.domain.observation_points.write()

    def check_times(self) -> None:
        """Validate that forcing covers the full simulation period (not yet implemented)."""
        # This does not yet exist for HydroMT-SFINCS
        return
        ok, message_list = self.domain.check_times()
        if not ok:
            messages = ""
            for message in message_list:
                messages = messages + message + "\n"
            app.gui.window.dialog_warning(messages, "Warning")
