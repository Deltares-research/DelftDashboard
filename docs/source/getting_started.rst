Getting Started
===============

This guide introduces the DelftDashboard interface and the typical workflow for
building a numerical model.

GUI Layout
----------

The application window is divided into three main areas:

- **Map view** (right side) -- An interactive map powered by MapLibre that
  displays the model domain, grid, bathymetry, boundary conditions, and other
  spatial data. You can pan, zoom, and click on the map to select or place
  features.
- **Side panel** (left side) -- Contains tabbed panels for the currently active
  model or toolbox. Each tab exposes controls for a specific aspect of the
  model setup (e.g. grid, bathymetry, boundary conditions).
- **Menu bar** (top) -- Provides access to file operations, the model selector,
  the toolbox selector, and application settings.

Models and Toolboxes
--------------------

DelftDashboard separates concerns into **models** and **toolboxes**:

- A **model** represents a specific numerical engine (e.g. SFINCS, HurryWave,
  Delft3D-FM). Selecting a model loads its domain object and displays its
  configuration tabs in the side panel.
- A **toolbox** provides functionality that may apply to one or more models.
  Examples include the Model Maker (grid generation and bathymetry assignment),
  the Bathymetry browser, and the Observation Stations manager. Some toolboxes
  are model-specific (e.g. the SFINCS Model Maker only appears when the SFINCS
  model is active), while others are available for all models.

At any time, exactly one model and one toolbox are active. Their panels share
the left side of the window, with the model panel on top and the toolbox panel
below.

Basic Workflow
--------------

A typical workflow for building a model follows these steps:

1. **Select a model** -- Use the menu bar to choose the model you want to build
   (e.g. SFINCS, HurryWave, or Delft3D-FM).

2. **Open the Model Maker toolbox** -- Switch to the Model Maker toolbox for
   the selected model. This toolbox guides you through domain setup.

3. **Define the domain** -- Draw or specify the model extent on the map. Set
   the grid resolution and orientation.

4. **Generate the grid** -- Click the generate button to create the
   computational grid. For SFINCS this may be a regular or quadtree grid; for
   Delft3D-FM it may be an unstructured mesh.

5. **Add bathymetry** -- Select one or more topography/bathymetry datasets from
   the data catalog and interpolate them onto the grid. Datasets are applied in
   priority order (last dataset overwrites earlier ones where they overlap).

6. **Set boundary conditions** -- Define open boundaries and assign forcing
   data such as water levels, wave conditions, or meteorological fields.

7. **Configure observation points** -- Place observation stations where you want
   time-series output.

8. **Save and run** -- Save the model input files and launch the simulation
   using the configured executable path.

Coordinate Reference System
----------------------------

DelftDashboard supports working in different coordinate reference systems (CRS).
A CRS selector in the menu bar lets you choose the projection for the current
model. The map always displays in Web Mercator (EPSG:3857), but model
coordinates are stored in the selected CRS. Common choices include:

- **WGS 84 (EPSG:4326)** -- Geographic coordinates (longitude/latitude).
- **UTM zones** -- Projected coordinates in metres, suitable for local or
  regional models.

When you change the CRS, all model layers are reprojected automatically.
