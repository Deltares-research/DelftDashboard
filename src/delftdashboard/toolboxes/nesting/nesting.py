"""Nesting toolbox class for managing model nesting GUI state and initialization."""

from __future__ import annotations

from delftdashboard.app import app
from delftdashboard.operations.toolbox import GenericToolbox


class Toolbox(GenericToolbox):
    """Toolbox for coupling overall and detail models via nesting steps."""

    def __init__(self, name: str) -> None:
        """Initialize the nesting toolbox.

        Parameters
        ----------
        name : str
            Short name for this toolbox instance.
        """
        super().__init__()

        self.name = name
        self.long_name = "Nesting"

    def initialize(self) -> None:
        """Register all GUI variables for the nesting toolbox."""
        group = "nesting"

        app.gui.setvar(group, "obs_point_prefix", "nest")

        app.gui.setvar(group, "detail_model_type", "")
        app.gui.setvar(group, "detail_model_file", "")
        app.gui.setvar(group, "detail_model_types", [])
        app.gui.setvar(group, "detail_model_type_long_names", [])
        app.gui.setvar(group, "detail_model_loaded", False)

        app.gui.setvar(group, "overall_model_type", "")
        app.gui.setvar(group, "overall_model_file", "")
        app.gui.setvar(group, "overall_model_types", [])
        app.gui.setvar(group, "overall_model_type_long_names", [])
        app.gui.setvar(group, "overall_model_loaded", False)

        app.gui.setvar(group, "water_level_correction", 0.0)

    def set_layer_mode(self, mode: str) -> None:
        """Set the visibility mode for nesting map layers (no-op).

        Parameters
        ----------
        mode : str
            The layer mode to apply.
        """
        pass

    def add_layers(self) -> None:
        """Add map layers for the nesting toolbox (no-op)."""
        pass
