"""Delft3D-FM model plugin for DelftDashboard.

Provides the ``Model`` class that wraps a cht_delft3dfm domain, registers
map layers, and synchronizes GUI state with the model configuration.
"""

import ast
import datetime
import os
from pathlib import Path
from typing import Any, Dict

import geopandas as gpd
from cht_delft3dfm import Delft3DFM

from delftdashboard.app import app
from delftdashboard.operations.model import GenericModel

_MODEL = "delft3dfm"


class Model(GenericModel):
    """DelftDashboard model wrapper for Delft3D-FM."""

    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name
        self.long_name = "Delft3D-FM"

    def initialize(self) -> None:
        """Create a fresh Delft3DFM domain and set default GUI variables."""
        self.domain = Delft3DFM(crs=app.crs)
        self.domain.fname = "flow.mdu"
        self.set_gui_variables()
        self.observation_points_changed = False
        self.cross_sections_changed = False
        self.boundaries_changed = False
        self.thin_dams_changed = False

    def get_view_menu(self) -> Dict[str, Any]:
        """Build the View menu entries for this model.

        Returns
        -------
        dict
            Menu definition dict with text, sub-items, and callbacks.
        """
        model_view_menu: Dict[str, Any] = {}
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
        return model_view_menu

    def set_view_menu(self, option: str, checked: bool) -> None:
        """Toggle map layer visibility from the view menu.

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

    def add_layers(self) -> None:
        """Register all map layers for the Delft3D-FM model."""
        layer = app.map.add_layer(_MODEL)

        layer.add_layer("grid", type="raster_image")

        layer.add_layer(
            "grid_exterior",
            type="line",
            circle_radius=0,
            line_color="yellow",
        )

        layer.add_layer(
            "boundary_line",
            type="line",
            hover_property="name",
            line_color="red",
            line_width=3,
            line_opacity=1.0,
            fill_color="red",
            fill_opacity=1.0,
        )

        from .observation_points_regular import select_observation_point_from_map

        layer.add_layer(
            "observation_points",
            type="circle_selector",
            hover_property="name",
            select=select_observation_point_from_map,
            line_color="white",
            line_opacity=1.0,
            fill_color="blue",
            fill_opacity=1.0,
            circle_radius=3,
            circle_radius_selected=4,
            line_color_selected="white",
            fill_color_selected="red",
        )

        from .structures_thin_dams import (
            thin_dam_created,
            thin_dam_modified,
            thin_dam_selected,
        )

        layer.add_layer(
            "thin_dams",
            type="draw",
            shape="polyline",
            create=thin_dam_created,
            modify=thin_dam_modified,
            select=thin_dam_selected,
            polyline_line_color="yellow",
            polyline_line_width=2.0,
            polyline_line_opacity=1.0,
        )

        from .observation_points_crs import (
            cross_section_created,
            cross_section_modified,
            cross_section_selected,
        )

        layer.add_layer(
            "cross_sections",
            type="draw",
            shape="polyline",
            create=cross_section_created,
            modify=cross_section_modified,
            select=cross_section_selected,
            polyline_line_color="yellow",
            polyline_line_width=2.0,
            polyline_line_opacity=1.0,
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
            layer.layer["grid"].deactivate()
            layer.layer["grid_exterior"].deactivate()
            layer.layer["boundary_line"].deactivate()
            layer.layer["observation_points"].deactivate()
        elif mode == "invisible":
            layer.hide()

    def set_crs(self) -> None:
        """Update the model CRS to match the application CRS and re-plot."""
        crs = app.crs
        old_crs = self.domain.crs
        if old_crs != crs:
            self.domain.crs = crs
            self.domain.clear_spatial_attributes()
            self.plot()

    def set_gui_variables(self) -> None:
        """Copy model config and defaults to GUI variables."""
        group = _MODEL
        subgroups = ["numerics", "physics", "output", "geometry", "wind"]

        app.gui.setvar(group, "view_grid", True)

        for groupname in subgroups:
            subgroup = getattr(self.domain.input, groupname)
            for var_name, var_value in vars(subgroup).items():
                if var_name == "comments":
                    continue
                if hasattr(var_value, "__dict__"):
                    for subvar_name, subvar_value in vars(var_value).items():
                        app.gui.setvar(
                            _MODEL,
                            f"{groupname}.{var_name}.{subvar_name}",
                            subvar_value,
                        )
                else:
                    app.gui.setvar(group, f"{groupname}.{var_name}", var_value)

        # Time defaults
        tnow = datetime.datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        app.gui.setvar(group, "time.refdate", tnow)
        app.gui.setvar(group, "time.tstart", tnow)
        app.gui.setvar(group, "time.tstop", tnow + datetime.timedelta(days=1))

        # Domain
        app.gui.setvar(group, "setup.x0", 0)
        app.gui.setvar(group, "setup.y0", 1)
        app.gui.setvar(group, "setup.nmax", 0)
        app.gui.setvar(group, "setup.mmax", 0)
        app.gui.setvar(group, "setup.dx", 0.01)
        app.gui.setvar(group, "setup.dy", 0.01)

        # Observation points
        app.gui.setvar(group, "observation_point_names", [])
        app.gui.setvar(group, "nr_observation_points", 0)
        app.gui.setvar(group, "active_observation_point", 0)

        # Cross sections
        app.gui.setvar(group, "cross_section_names", [])
        app.gui.setvar(group, "nr_cross_sections", 0)
        app.gui.setvar(group, "active_cross_section", 0)

        # Boundary line
        app.gui.setvar(group, "boundary_line_active", 0)

        # Boundary conditions
        app.gui.setvar(group, "boundary_conditions_timeseries_shape", "constant")
        app.gui.setvar(group, "boundary_conditions_timeseries_time_step", 600.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_offset", 0.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_offset_custom", 0.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_amplitude", 1.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_phase", 0.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_period", 43200.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_peak", 1.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_tpeak", 86400.0)
        app.gui.setvar(group, "boundary_conditions_timeseries_duration", 43200.0)
        app.gui.setvar(
            group,
            "boundary_conditions_tide_model",
            app.gui.getvar("tide_models", "names")[0],
        )
        app.gui.setvar(group, "boundary_conditions_tide_offset", 0.0)

        # Thin dams
        app.gui.setvar(group, "thin_dam_names", [])
        app.gui.setvar(group, "nr_thin_dams", 0)
        app.gui.setvar(group, "active_thin_dam", 0)

    def set_input_variables(self) -> None:
        """Copy GUI variables back to the Delft3D-FM model input."""
        subgroups = ["numerics", "physics", "geometry", "wind"]

        for groupname in subgroups:
            subgroup = getattr(self.domain.input, groupname)
            for var_name, var_value in vars(subgroup).items():
                if var_name in ["comments", "landboundaryfile"]:
                    continue
                if hasattr(var_value, "__dict__"):
                    for subvar_name in vars(var_value):
                        value = app.gui.getvar(
                            _MODEL, f"{groupname}.{var_name}.{subvar_name}"
                        )
                        if "filepath" in subvar_name.lower() and value is not None:
                            value = Path(value)
                        setattr(var_value, subvar_name, value)
                else:
                    value = app.gui.getvar(_MODEL, f"{groupname}.{var_name}")
                    if "filepath" in var_name.lower() and value is not None:
                        value = Path(value)
                    setattr(subgroup, var_name, value)

        self.set_timeframe()

        # Output intervals
        for attr in ("hisinterval", "mapinterval", "rstinterval"):
            val = app.gui.getvar(_MODEL, f"output.{attr}")
            if isinstance(val, str):
                val = ast.literal_eval(val)
            setattr(self.domain.input.output, attr, val)

    def set_timeframe(self) -> None:
        """Copy GUI time variables to the model domain."""
        refdate = app.gui.getvar(_MODEL, "time.refdate")
        setattr(self.domain.input.time, "refdate", refdate.strftime("%Y%m%d"))

        start_time = app.gui.getvar(_MODEL, "time.tstart")
        setattr(
            self.domain.input.time, "startdatetime", start_time.strftime("%Y%m%d%H%M%S")
        )

        stop_time = app.gui.getvar(_MODEL, "time.tstop")
        setattr(
            self.domain.input.time, "stopdatetime", stop_time.strftime("%Y%m%d%H%M%S")
        )

    def open(self) -> None:
        """Open an existing Delft3D-FM model from a file dialog."""
        fname = app.gui.window.dialog_open_file(
            "Open file", filter="Delft3D-FM input file (flow.mdu)"
        )
        fname = fname[0]
        if fname:
            dlg = app.gui.window.dialog_wait("Loading Delft3D-FM model ...")
            path = os.path.dirname(fname)
            if not path:
                path = os.getcwd()
            self.domain.path = path
            os.chdir(path)
            self.domain.fname = fname
            self.domain.read_input_file(fname)
            self.domain.read_attribute_files()
            self.set_gui_variables()
            app.crs = self.domain.crs
            self.plot()
            dlg.close()
            bounds = self.domain.grid.bounds(crs=4326, buffer=0.1)
            app.map.fit_bounds(bounds[0], bounds[1], bounds[2], bounds[3])

    def save(self) -> None:
        """Write the current model to disk."""
        self.domain.path = os.getcwd()
        self.domain.write_input_file(
            input_file=os.path.join(self.domain.path, self.domain.fname)
        )

    def load(self) -> None:
        """Re-read the model input file from disk."""
        self.domain.read_input_file(
            input_file=os.path.join(self.domain.path, self.domain.fname)
        )

    def plot(self) -> None:
        """Plot all model layers on the map."""
        layer = app.map.layer[_MODEL]
        layer.layer["grid"].set_data(self.domain.grid)
        layer.layer["boundary_line"].clear()
        layer.layer["boundary_line"].set_data(self.domain.boundary_conditions.gdf)
        layer.layer["observation_points"].set_data(
            self.domain.observation_points.gdf, 0
        )

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
        app.map.layer[_MODEL].layer["observation_points"].set_data(gdf, 0)
        if not self.domain.input.output.obsfile:
            from hydrolib.core.dflowfm.xyn.models import XYNModel

            obs = XYNModel()
            obs.filepath = Path(self.domain.path) / "delft3dfm.obs"
            self.domain.input.output.obsfile = [obs]
        self.domain.observation_points.write()
