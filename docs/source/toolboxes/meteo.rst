Meteorological Data
===================

The Meteorological Data toolbox (``meteo``) manages meteorological forcing
datasets. It supports browsing available datasets, downloading data for
specified time ranges, and generating model forcing files.

Datasets
--------

Browse and configure meteorological datasets.

Parameters
^^^^^^^^^^

Datasets (listbox)
   List of available meteorological datasets.

Source (dropdown)
   Select the meteorological data source (e.g. ERA5, GFS, CFSR).

Bounding Box
   Define the spatial extent for the dataset using map drawing or manual
   coordinate entry:

   - **Lon Min** / **Lon Max** -- longitude range.
   - **Lat Min** / **Lat Max** -- latitude range.

Actions
^^^^^^^

Draw Bounding Box
   Interactively draw the spatial extent on the map.

Add Dataset
   Register a new dataset with the specified source and bounding box.


Download
--------

Download meteorological data for a dataset and time range.

Parameters
^^^^^^^^^^

Datasets (listbox)
   Select the dataset to download.

Start Time
   First time in the download range.

Stop Time
   Last time in the download range.

Actions
^^^^^^^

Download
   Fetch the data from the remote source and store it locally.


Model Forcing
-------------

Generate model-specific forcing files from downloaded meteorological data.

Parameters
^^^^^^^^^^

Datasets (listbox)
   Select the dataset to use for model forcing.

Start Time
   First time in the forcing range.

Stop Time
   Last time in the forcing range.

Actions
^^^^^^^

Generate Forcing Files
   Create forcing files (wind, pressure, precipitation, etc.) in the
   format required by the active model.
