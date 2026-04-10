"""Tiling toolbox for DelftDashboard.

Provides the main Toolbox class for generating tiled web map data
(index tiles and topobathy tiles) from model grids.
"""

from delftdashboard.app import app
from delftdashboard.operations.toolbox import GenericToolbox


class Toolbox(GenericToolbox):
    """Toolbox for generating map tiles from model output."""

    def __init__(self, name: str) -> None:
        """Initialize the tiling toolbox.

        Parameters
        ----------
        name : str
            Name identifier for the toolbox.
        """
        super().__init__()

        self.name = name
        self.long_name = "Tiling"

    def initialize(self) -> None:
        """Set up default GUI variables for zoom level selection."""
        group = "tiling"
        # Make a list of 0 to 23
        lst = list(range(24))
        # And convert to strings
        lststr = [str(i) for i in lst]
        app.gui.setvar(group, "zoom_levels", lst)
        app.gui.setvar(group, "zoom_levels_text", lststr)
        app.gui.setvar(group, "max_zoom", 13)

    def set_layer_mode(self, mode: str) -> None:
        """Handle layer mode changes (no layers for this toolbox).

        Parameters
        ----------
        mode : str
            The requested layer mode.
        """

    def add_layers(self) -> None:
        """Register map layers (none for this toolbox)."""
