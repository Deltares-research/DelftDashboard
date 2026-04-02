"""Meteo toolbox providing access to meteorological datasets."""

import datetime

from delftdashboard.app import app
from delftdashboard.operations.toolbox import GenericToolbox


class Toolbox(GenericToolbox):
    """Toolbox for managing meteorological data sources and downloads.

    Parameters
    ----------
    name : str
        Short name used as a key in the toolbox registry.
    """

    def __init__(self, name: str) -> None:
        super().__init__()

        self.name: str = name
        self.long_name: str = "Meteo"

    def initialize(self) -> None:
        """Set up GUI variables for meteo datasets, sources, and time range."""
        sources: list[str] = app.meteo_database.list_sources()
        datasets: list[str] = app.meteo_database.list_dataset_names()

        group = "meteo"

        app.gui.setvar(group, "dataset_names", datasets)
        app.gui.setvar(group, "dataset_long_names", datasets)
        if len(datasets) > 0:
            app.gui.setvar(group, "selected_dataset", datasets[0])
        else:
            app.gui.setvar(group, "selected_dataset", "")

        app.gui.setvar(group, "source_names", sources)
        app.gui.setvar(group, "source_long_names", sources)
        if len(sources) > 0:
            app.gui.setvar(group, "selected_source", sources[0])
        else:
            app.gui.setvar(group, "selected_source", "")

        app.gui.setvar(group, "lon_min", 0.0)
        app.gui.setvar(group, "lon_max", 0.0)
        app.gui.setvar(group, "lat_min", 0.0)
        app.gui.setvar(group, "lat_max", 0.0)

        app.gui.setvar(group, "edit_bbox", False)

        tstart = datetime.datetime(2020, 1, 1, 0, 0, 0)
        tstop = datetime.datetime(2020, 1, 2, 0, 0, 0)
        app.gui.setvar(group, "tstart", tstart)
        app.gui.setvar(group, "tstop", tstop)

    def set_layer_mode(self, mode: str) -> None:
        """Set the visibility mode for meteo map layers.

        Parameters
        ----------
        mode : str
            Layer mode (currently unused).
        """
        pass

    def add_layers(self) -> None:
        """Add map layers for the meteo toolbox."""
        pass
