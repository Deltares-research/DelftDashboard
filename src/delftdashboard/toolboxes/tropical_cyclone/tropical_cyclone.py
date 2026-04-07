"""Tropical cyclone toolbox for track management and spiderweb generation."""

import datetime
import os

import pandas as pd
from cht_cyclones import CycloneTrackDatabase, TropicalCyclone

from delftdashboard.app import app
from delftdashboard.operations.toolbox import GenericToolbox


class Toolbox(GenericToolbox):
    """Toolbox for tropical cyclone track management and wind field generation."""

    def __init__(self, name: str) -> None:
        """Initialize the tropical cyclone toolbox.

        Parameters
        ----------
        name : str
            Name identifier for the toolbox.
        """
        super().__init__()

        self.name = name
        self.long_name = "Tropical Cyclone"

    def initialize(self) -> None:
        """Set up GUI variables, load track database, and configure defaults."""
        # Set variables
        self.tc = TropicalCyclone()
        self.track_dataset = None

        group = "tropical_cyclone"

        app.gui.setvar(group, "name", "")
        app.gui.setvar(group, "track_loaded", False)

        # Loop through the config and set the GUI variables
        for key in self.tc.config:
            app.gui.setvar(group, key, self.tc.config[key])

        app.gui.setvar(group, "ensemble_start_time", None)
        app.gui.setvar(group, "ensemble_start_time_index", 0)
        app.gui.setvar(group, "ensemble_number_of_realizations", 100)
        app.gui.setvar(group, "ensemble_duration", 72)
        app.gui.setvar(group, "ensemble_cone_buffer", 300000.0)
        app.gui.setvar(group, "ensemble_cone_only_forecast", True)
        app.gui.setvar(group, "ensemble_start_time", None)

        app.gui.setvar(group, "track_time_strings", [])

        # Draw track defaults
        app.gui.setvar(group, "draw_start_datetime", None)
        app.gui.setvar(group, "draw_dt_hours", 6.0)
        app.gui.setvar(group, "draw_vmax", 100.0)
        app.gui.setvar(group, "draw_rmax", 25.0)
        app.gui.setvar(group, "draw_name", "TC Deepak")
        app.gui.setvar(group, "draw_vt", 10.0)

        # Modify track state
        app.gui.setvar(group, "track_modified", False)
        app.gui.setvar(group, "track_table", pd.DataFrame())

        app.gui.setvar(group, "include_rainfall", False)
        app.gui.setvar(group, "wind_profile_options", ["holland2010"])
        app.gui.setvar(group, "wind_profile_option_strings", ["Holland (2010)"])
        app.gui.setvar(group, "vmax_pc_options", ["holland2008"])
        app.gui.setvar(group, "vmax_pc_option_strings", ["Holland (2008)"])
        app.gui.setvar(group, "rmax_options", ["nederhoff2019"])
        app.gui.setvar(group, "rmax_option_strings", ["Nederhoff et al. (2019)"])
        app.gui.setvar(group, "rainfall_options", ["ipet"])
        app.gui.setvar(group, "rainfall_option_strings", ["IPET"])

        # Read track database
        s3_bucket = app.config["s3_bucket"]
        s3_key = "data/tropical_cyclones"
        path = os.path.join(app.config["data_path"], "tropical_cyclones")
        self.cyclone_track_database = CycloneTrackDatabase(
            path, s3_bucket=s3_bucket, s3_key=s3_key, check_online=app.online
        )
        short_names, long_names = self.cyclone_track_database.dataset_names()
        app.gui.setvar("tropical_cyclone", "track_dataset_long_names", long_names)
        app.gui.setvar("tropical_cyclone", "track_dataset_names", short_names)
        app.gui.setvar("tropical_cyclone", "selected_track_dataset", short_names[0])

    def set_layer_mode(self, mode: str) -> None:
        """Control visibility of tropical cyclone map layers.

        Parameters
        ----------
        mode : str
            One of "active", "inactive", or "invisible".
        """
        if mode == "active":
            # Make container layer visible
            app.map.layer[self.name].show()
            # Always show track layer
            app.map.layer[self.name].layer["cyclone_track"].show()
            # But hide ensemble layers
            app.map.layer[self.name].layer["cyclone_track_ensemble"].hide()
            app.map.layer[self.name].layer["cyclone_track_ensemble_cone"].hide()
        elif mode == "inactive":
            # Make all layers invisible
            app.map.layer[self.name].hide()
        if mode == "invisible":
            # Make all layers invisible
            app.map.layer[self.name].hide()

    def add_layers(self) -> None:
        """Register map layers for cyclone tracks and ensembles."""
        # Add Mapbox layers
        layer = app.map.add_layer(self.name)
        layer.add_layer(
            "cyclone_track_ensemble",
            type="line",
            line_color="white",
            line_width=1,
            line_opacity=0.5,
        )
        layer.add_layer(
            "cyclone_track_ensemble_cone",
            type="line",
            line_color="white",
            line_width=2,
            line_opacity=1.0,
        )
        layer.add_layer(
            "cyclone_track",
            type="cyclone_track",
            line_color="dodgerblue",
            line_width=2,
            line_color_selected="red",
            line_width_selected=3,
            hover_param="description",
            icon_size=0.75,
        )

        # Drawing layer for manually drawing a track polyline
        from .draw import track_drawn
        from .modify import track_modified_on_map, track_edit_finished

        layer.add_layer(
            "draw_track",
            type="draw",
            shape="polyline",
            create=track_drawn,
            modify=track_modified_on_map,
            deselect=track_edit_finished,
            polyline_line_color="dodgerblue",
            polyline_line_width=2,
        )

    def track_added(self) -> None:
        """Reset ensemble state and plot a newly added track."""
        app.gui.setvar("tropical_cyclone", "ensemble_start_time", None)
        app.gui.setvar("tropical_cyclone", "ensemble_start_time_index", 0)
        app.gui.setvar("tropical_cyclone", "track_loaded", True)
        self.plot_track()

    def plot_track(self) -> None:
        """Update the cyclone track layer on the map."""
        app.map.layer[self.name].layer["cyclone_track"].set_data(self.tc.track.gdf)

    def build_spiderweb(self) -> None:
        """Generate a spiderweb wind field file and apply it to the active model."""
        file_name = app.gui.window.dialog_save_file(
            "Save spiderweb file", "*.spw", self.tc.name + ".spw"
        )
        if len(file_name[0]) == 0:
            return
        spw_file = file_name[0]  # Full file name

        # Save config
        self.set_config()

        # Build and save the spw file
        p = app.gui.window.dialog_progress(
            "               Generating wind fields ...                ",
            len(self.tc.track.gdf),
        )
        self.tc.compute_wind_field(
            filename=spw_file, progress_bar=p, format="ascii", error_stats=False
        )
        p.close()

        # Get the active model
        model = app.active_model
        if model.name == "sfincs_cht":
            # Add the spw file to the model
            spw_file = file_name[2]  # No path
            model.domain.input.variables.spwfile = spw_file
            # Do some other stuff here as well specific to SFINCS
            # Turn on barometric pressure
            model.domain.input.variables.baro = True
            # Turn on meteo output
            model.domain.input.variables.storemeteo = True
            # Set the meteo forcing type to spiderweb (used in Meteo tab)
            app.gui.setvar("sfincs_cht", "meteo_forcing_type", "spiderweb")
            # If the CRS of the model is a UTM zone, we need to set the utmzone variable
            if model.domain.crs.is_projected:
                # Check name of CRS
                crs_name = model.domain.crs.name
                if "UTM" in crs_name:
                    # Get the UTM zone from the CRS name
                    utmstr = crs_name.split(" ")[-1]
                    # Set the UTM zone variable
                    model.domain.input.variables.utmzone = utmstr
            model.set_gui_variables()

            # Check if model simulation time is within the track time
            t0_model = model.domain.input.variables.tstart
            t1_model = model.domain.input.variables.tstop

            date_format = "%Y%m%d %H%M%S"
            # Get first row of track
            date_string = self.tc.track.gdf.iloc[0]["datetime"]
            t0_track = datetime.datetime.strptime(date_string, date_format)
            # Get last row of track
            date_string = self.tc.track.gdf.iloc[-1]["datetime"]
            t1_track = datetime.datetime.strptime(date_string, date_format)

            if t0_model < t0_track or t1_model > t1_track:
                app.gui.window.dialog_warning(
                    "The time of the cyclone track does not fully cover the simulation time. Please adjust the start and/or stop time of the model simulation!"
                )

        elif model.name == "hurrywave":
            # Add the spw file to the model
            model.domain.input.variables.spwfile = file_name[2]
            # Do some other stuff here as well specific to HurryWave
            # If the CRS of the model is a UTM zone, we need to set the utmzone variable
            if model.domain.crs.is_projected:
                # Check name of CRS
                crs_name = model.domain.crs.name
                if "UTM" in crs_name:
                    # Get the UTM zone from the CRS name
                    utmstr = crs_name.split(" ")[-1]
                    # Set the UTM zone variable
                    model.domain.input.variables.utmzone = utmstr
            model.set_gui_variables()

            # Check if model simulation time is within the track time
            t0_model = model.domain.input.variables.tstart
            t1_model = model.domain.input.variables.tstop

            date_format = "%Y%m%d %H%M%S"
            # Get first row of track
            date_string = self.tc.track.gdf.iloc[0]["datetime"]
            t0_track = datetime.datetime.strptime(date_string, date_format)
            # Get last row of track
            date_string = self.tc.track.gdf.iloc[-1]["datetime"]
            t1_track = datetime.datetime.strptime(date_string, date_format)

            if t0_model < t0_track or t1_model > t1_track:
                app.gui.window.dialog_warning(
                    "The time of the cyclone track does not fully cover the simulation time. Please adjust the start and/or stop time of the model simulation!"
                )

    def load_track(self) -> None:
        """Load a cyclone track from a .cyc file via dialog."""
        file_name = app.gui.window.dialog_open_file("Open track", "*.cyc")
        if file_name[0]:
            self.tc.read_track(file_name[0])
            self.tc.name = os.path.basename(file_name[0]).split(".")[0]
            app.gui.setvar("tropical_cyclone", "ensemble_start_time", None)
            app.gui.setvar("tropical_cyclone", "ensemble_start_time_index", 0)
            app.gui.setvar("tropical_cyclone", "track_loaded", True)
            self.plot_track()

    def save_track(self) -> None:
        """Save the current cyclone track to a .cyc file via dialog."""
        name = self.tc.name.replace(" ", "_").lower()
        file_name = app.gui.window.dialog_save_file(
            "Save track", "*.cyc", name + ".cyc"
        )
        if file_name[0]:
            self.tc.name = os.path.basename(file_name[0]).split(".")[0]
            self.tc.write_track(file_name[0])

    def delete_track(self) -> None:
        """Delete the current cyclone track and clear the map layer."""
        self.tc = TropicalCyclone()
        app.gui.setvar("tropical_cyclone", "track_loaded", False)
        app.map.layer["tropical_cyclone"].layer["cyclone_track"].clear()

    def load_config(self) -> None:
        """Load cyclone configuration from a .cfg file via dialog."""
        file_name = app.gui.window.dialog_open_file(
            "Open cyclone configuration", "*.cfg"
        )
        if file_name[0]:
            self.tc.read_config(file_name[0])
            # Loop through the config and set the GUI variables
            for key in self.tc.config:
                app.gui.setvar("tropical_cyclone", key, self.tc.config[key])
            # Update the GUI variables
            app.gui.window.update()

    def save_config(self) -> None:
        """Save the current cyclone configuration to a .cfg file via dialog."""
        name = self.tc.name.replace(" ", "_").lower()
        file_name = app.gui.window.dialog_save_file(
            "Save configuration", "*.cfg", name + ".cfg"
        )
        self.set_config()
        if file_name[0]:
            self.tc.write_config(file_name[0])

    def set_config(self) -> None:
        """Sync GUI variable values back to the cyclone configuration dict."""
        for key in self.tc.config:
            self.tc.config[key] = app.gui.getvar("tropical_cyclone", key)
