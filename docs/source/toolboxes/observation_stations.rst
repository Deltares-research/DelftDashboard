Observation Stations
====================

The Observation Stations toolbox (``observation_stations``) provides access
to databases of observation stations (e.g. tide gauges, river gauges). Users
can browse available stations on the map, select stations of interest, and
add them as observation points to the active model.

Parameters
^^^^^^^^^^

Stations (listbox)
   List of available observation stations. Stations are displayed on the
   map as markers.

Naming Option (radio buttons)
   Choose how stations are labeled when added to the model:

   - **Name** -- use the station name.
   - **ID** -- use the station identifier.

Actions
^^^^^^^

Add to Model
   Add the selected station(s) as observation points to the currently
   active model. The station coordinates and chosen label are written to
   the model observation point file.
