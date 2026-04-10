Tide Stations
=============

The Tide Stations toolbox (``tide_stations``) provides access to tidal
constituent databases. Users can browse tide stations, view predicted tidal
signals, export time series, and add stations as observation points to the
active model.

Dataset Selection
^^^^^^^^^^^^^^^^^

Dataset (listbox)
   Select the tidal dataset to use (e.g. FES2014, TPXO, IHO).

Naming Option (radio buttons)
   Choose how stations are labeled:

   - **Name** -- use the station name.
   - **ID** -- use the station identifier.

Station Browsing
^^^^^^^^^^^^^^^^

Stations (listbox)
   List of tide stations from the selected dataset. Stations are displayed
   on the map as markers.

Draw Polygon
   Draw a polygon on the map to filter stations by geographic area.

Delete Polygon
   Remove the filter polygon and show all stations.

Tide Prediction
^^^^^^^^^^^^^^^

Start Time
   Start date and time for tidal prediction.

End Time
   End date and time for tidal prediction.

Time Step (s)
   Time step in seconds for the predicted tidal signal.

Offset (m)
   Constant water level offset added to the prediction (in metres).

Format (dropdown)
   File format for export.

Main Components (checkbox)
   When checked, only the major tidal constituents are shown in the
   component table.

Component Table
^^^^^^^^^^^^^^^

A sortable table displaying the tidal constituents (amplitude, phase) for
the selected station.

Actions
^^^^^^^

Add to Model
   Add the selected station as an observation point to the active model.

View Tide Signal
   Display a plot of the predicted tidal signal for the selected station
   using the specified time range and settings.

Export Tide Signal
   Export the predicted tidal signal to a file in the selected format.

Export Components
   Export the tidal constituent data to a file (currently disabled).
