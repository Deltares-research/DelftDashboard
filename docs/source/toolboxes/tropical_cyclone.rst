Tropical Cyclone
================

The Tropical Cyclone toolbox (``tropical_cyclone``) provides a complete
workflow for importing, editing, and processing tropical cyclone tracks, and
for generating parametric wind field (spiderweb) files for use as model
forcing.

Import Track
------------

Load a tropical cyclone track from a database or file.

Parameters
^^^^^^^^^^

Track Dataset (listbox)
   Select the tropical cyclone track dataset (e.g. IBTrACS, JTWC).

Actions
^^^^^^^

Select Track
   Open a dialog to search for and select a specific track from the
   chosen database.

Load Track
   Load a track from a local file.

Save Track
   Save the current track to a file.

Delete Track
   Remove the current track from memory.


Draw Track
----------

Interactively draw a tropical cyclone track on the map.

Actions
^^^^^^^

Draw Track
   Start drawing a cyclone track on the map (currently under development).


Modify Track
------------

Edit the properties of an existing track.

Actions
^^^^^^^

Modify
   Modify the tropical cyclone track parameters (currently under
   development).


Track Table
-----------

View and edit track data in tabular form.

Actions
^^^^^^^

Edit Table
   Open the track data in a table editor (currently under development).


Wind Field
----------

Generate a parametric wind field (spiderweb) file from the loaded track.

Spiderweb Grid
^^^^^^^^^^^^^^

Radius
   Spiderweb radius in kilometres.

Directional Bins
   Number of directional bins in the spiderweb grid.

Radial Bins
   Number of radial bins in the spiderweb grid.

Wind Profile Settings
^^^^^^^^^^^^^^^^^^^^^

Wind Profile (dropdown)
   Select the parametric wind profile model (e.g. Holland 1980, Holland
   2010, Emanuel-Riehl).

Vmax-Pc Relation (dropdown)
   Select the wind speed -- central pressure relationship.

Rmax Relation (dropdown)
   Select the radius of maximum winds relationship.

Pn
   Background (environmental) pressure in mbar.

Phi
   Inflow angle in degrees.

Wind Factor
   Wind conversion factor (1-minute to 10-minute average).

Rainfall
^^^^^^^^

Rainfall (checkbox)
   Include rainfall in the spiderweb file.

Rainfall Relation (dropdown)
   Select the rainfall relationship model (only enabled when Rainfall is
   checked).

Time
^^^^

Reference Time
   Reference date and time for the spiderweb file.

Actions
^^^^^^^

Load Configuration
   Load spiderweb settings from a configuration file.

Save Configuration
   Save spiderweb settings to a configuration file.

Build Spiderweb
   Generate the spiderweb wind field file. Only enabled when a track is
   loaded.


Ensemble
--------

Generate an ensemble of tropical cyclone tracks for probabilistic
forecasting.

Parameters
^^^^^^^^^^

Start Time (dropdown)
   Select the start time for the ensemble from the loaded track time
   steps.

Duration
   Duration of the ensemble forecast in hours.

Nr Members
   Number of ensemble members (realizations) to generate.

Buffer (m)
   Cone of uncertainty buffer distance in metres.

Actions
^^^^^^^

Make Ensemble
   Generate the ensemble of track variations.
