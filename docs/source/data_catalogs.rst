Data Catalogs
=============

DelftDashboard uses `HydroMT's DataCatalog
<https://deltares.github.io/hydromt/latest/>`_ to manage topography and
bathymetry datasets. This page explains how datasets are organised, how the
catalog is loaded, and how to add new datasets.

Overview
--------

All topography/bathymetry data lives under a single root directory (the
``bathymetry`` folder inside the DelftDashboard data path). Each dataset
occupies its own sub-folder and is described by a ``data_catalog.yml`` file
that follows HydroMT's catalog format.

The :class:`~delftdashboard.operations.topography.TopographyDataCatalog` class
loads these YAML files at startup and exposes methods to list sources, query
dataset names, check spatial coverage, and fetch raster data.

Dataset Types
-------------

Two dataset formats are supported:

Slippy tiles (Terrain-RGB PNGs)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Datasets stored as a tree of PNG images following the slippy-map tile scheme
(``{z}/{x}/{y}.png``). Elevation values are encoded in the red, green, and blue
channels of each pixel using the Terrain-RGB convention. These tiles can be
served locally or fetched on demand from an S3 bucket.

Example directory layout::

   gebco_2024/
       data_catalog.yml
       0/
           0/
               0.png
           1/
               0.png
       1/
           ...

Cloud Optimized GeoTIFFs (COG)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Single-file raster datasets stored as Cloud Optimized GeoTIFFs. These files
support efficient partial reads (windowed access), making them suitable for
large datasets. They can reside on local disk or on S3-compatible object
storage.

Catalog YAML Format
--------------------

Each dataset has a ``data_catalog.yml`` file. The format follows HydroMT's
source specification with additional custom metadata fields used by
DelftDashboard.

Example for a slippy-tile dataset:

.. code-block:: yaml

   meta:
     root: .

   gebco_2024:
     data_type: RasterDataset
     driver: raster
     path: "{zoom_level}/{x}/{y}.png"
     metadata:
       source: GEBCO
       long_name: GEBCO 2024 Global Bathymetry
       difference_with_msl: 0.0

Example for a COG dataset:

.. code-block:: yaml

   meta:
     root: .

   cudem_ninth_texas:
     data_type: RasterDataset
     driver: raster
     path: cudem_ninth_texas.tif
     metadata:
       source: NOAA
       long_name: CUDEM 1/9 arc-second Texas
       difference_with_msl: 0.0

Custom Metadata Fields
^^^^^^^^^^^^^^^^^^^^^^

DelftDashboard uses the following custom fields in the ``metadata`` block:

- **source** -- The data provider name (e.g. ``GEBCO``, ``NOAA``, ``EMODnet``).
  Used to group datasets in the GUI source selector.
- **long_name** -- A human-readable description shown in the dataset list.
- **difference_with_msl** -- Vertical offset in metres between the dataset's
  reference datum and mean sea level. Applied during bathymetry interpolation.

Master Catalog
--------------

Optionally, a master ``data_catalog.yml`` at the root of the bathymetry folder
can list all datasets in a single file. If this file exists, it is loaded
instead of scanning sub-folders individually::

   bathymetry/
       data_catalog.yml          <-- master catalog (optional)
       gebco_2024/
           data_catalog.yml      <-- per-dataset catalog
           ...
       cudem_ninth_texas/
           data_catalog.yml
           cudem_ninth_texas.tif

If no master catalog is present, the ``TopographyDataCatalog`` automatically
discovers all ``data_catalog.yml`` files in immediate sub-folders.

Adding a New Dataset
--------------------

Via the GUI
^^^^^^^^^^^

1. Open the **Bathymetry** toolbox.
2. Click **Import** and select the raster file (GeoTIFF) or tile folder.
3. Fill in the metadata fields (source, long name, datum offset).
4. The GUI writes the ``data_catalog.yml`` and copies or links the data into
   the bathymetry folder.

Manually
^^^^^^^^

1. Create a sub-folder under the bathymetry root directory::

      mkdir bathymetry/my_dataset

2. Place your data file(s) in the folder.

3. Create a ``data_catalog.yml`` file:

   .. code-block:: yaml

      meta:
        root: .

      my_dataset:
        data_type: RasterDataset
        driver: raster
        path: my_dataset.tif
        metadata:
          source: MyOrg
          long_name: My Custom Bathymetry Dataset
          difference_with_msl: 0.0

4. Restart DelftDashboard. The new dataset will appear in the source and
   dataset lists.

S3 Auto-Download
----------------

For slippy-tile datasets, DelftDashboard can automatically download missing
tiles from an S3 bucket. When a tile is requested but not found on local disk,
the application uses ``boto3`` to fetch it from the configured S3 path and
caches it locally for future use. This allows working with large global
datasets without downloading the entire tile set upfront.

The TopographyDataCatalog Class
-------------------------------

The :class:`~delftdashboard.operations.topography.TopographyDataCatalog` class
is the primary interface between the GUI and the data catalog. Key methods:

- ``sources()`` -- Returns a list of unique data-provider names (e.g.
  ``["GEBCO", "NOAA", "EMODnet"]``).
- ``dataset_names(source=None)`` -- Returns dataset names, long names, and
  source names, optionally filtered by provider.
- ``get_source(name)`` -- Returns the raw HydroMT source object for a dataset.
- ``check_coverage(selected_datasets, bbox, crs)`` -- Tests which datasets
  have data within a given bounding box.
- ``get_rasterdataset(name, **kwargs)`` -- Fetches raster data, forwarding
  keyword arguments to HydroMT's ``DataCatalog.get_rasterdataset()``.
- ``resolve_elevation_list(selected_datasets, geom, res)`` -- Fetches raster
  data for a list of datasets and returns them in the format expected by
  HydroMT's elevation builders.
- ``add_to_model_catalog(model_data_catalog)`` -- Injects all topography
  sources into a model's ``DataCatalog`` instance.
