Installation
============

DelftDashboard can be installed either as a standalone end-user application or
as a development environment.

End-User Installation (Windows installer)
------------------------------------------

The easiest way to install DelftDashboard on Windows 10/11 is the standalone
installer. No Python or conda installation is required.

1. Download the latest installer
   (``DelftDashboard_Setup_<version>.exe``) from the
   `release page <https://github.com/Deltares-research/DelftDashboard/releases/latest>`_.

2. Run the installer. Windows SmartScreen may warn about an unrecognised
   application; choose *More info* > *Run anyway*.

3. Choose the DelftDashboard folder (default ``C:\DelftDashboard``). The
   program is installed in a ``bin`` sub-folder, and all data the application
   downloads (bathymetry, tide models, ...) is stored in this same folder -
   pick a location with sufficient disk space (several GB). Pointing to an
   existing DelftDashboard folder re-uses the data already in it.

4. Launch DelftDashboard from the Start menu (or the optional desktop
   shortcut). On first start the application creates the ``data``, ``server``
   and ``working_directory`` sub-folders and downloads its database catalogs;
   bathymetry and tide data are downloaded on demand as you use them.

Uninstalling removes only the program (``bin``); downloaded data and your
model files are left untouched.

Developer Requirements
----------------------

- Python 3.12 (recommended) or 3.10+
- `Miniforge3 <https://github.com/conda-forge/miniforge>`_ (recommended conda
  distribution)
- Windows 10/11 (primary platform)

Developer Installation
----------------------

For development, install from source in an editable conda environment.

1. Create and activate a conda environment::

      conda create -n delftdashboard_dev python=3.12
      conda activate delftdashboard_dev

2. Install the package in editable mode with development dependencies::

      pip install -e "/path/to/DelftDashboard[dev]"

   This installs DelftDashboard along with all CHT libraries (``cht_sfincs``,
   ``cht_hurrywave``, ``cht_delft3dfm``, ``cht_bathymetry``, ``cht_tide``,
   ``cht_meteo``, ``cht_nesting``, ``cht_cyclones``, ``cht_tiling``,
   ``cht_utils``, ``cht_physics``, ``cht_observations``, ``cht_tsunami``) and
   the ``guitares`` GUI framework directly from GitHub.

3. Launch from the development working directory::

      python start_delftdashboard.py

   Alternatively, use the batch scripts in the repository::

      run/delftdashboard_dev.bat

Key Dependencies
^^^^^^^^^^^^^^^^

The main runtime dependencies are:

- **GUI**: PySide6, guitares (Deltares MapLibre-based GUI framework)
- **Geospatial**: geopandas, shapely, pyproj, rasterio
- **Scientific**: numpy, scipy, pandas, xarray, matplotlib
- **Data**: hydromt, boto3, pyyaml, toml
- **Model libraries**: cht_sfincs, cht_hurrywave, cht_delft3dfm, and others

First Run
---------

On first launch, DelftDashboard needs to know where its data folder is located.
This is configured through the ``delftdashboard.pth`` file.

Data folder (``delftdashboard.pth``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``.pth`` file contains a single line: the absolute path to the
DelftDashboard data folder. This folder holds bathymetry databases,
tide models, meteo data, and other shared resources.

The file can be placed either in the package directory
(``src/delftdashboard/delftdashboard.pth``) or in the working directory from
which you launch the application. Example contents::

   c:\work\delftdashboard

User configuration (``delftdashboard.ini``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``.ini`` file lives inside the data folder and stores user-specific
settings such as paths to model executables and data directories. This file is
never committed to version control. Example::

   [sfincs]
   exe = c:\models\sfincs\sfincs.exe

   [hurrywave]
   exe = c:\models\hurrywave\hurrywave.exe

Application configuration (``delftdashboard.cfg``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``.cfg`` file at ``src/delftdashboard/config/delftdashboard.cfg`` controls
which GUI framework, map engine, models, and toolboxes are loaded. To
enable or disable a model or toolbox, edit the ``model:`` and ``toolbox:``
sections::

   gui_framework: pyside6
   map_engine: maplibre
   model:
     - name: sfincs_hmt
     - name: hurrywave_hmt
     - name: delft3dfm
   toolbox:
     - name: modelmaker_sfincs_hmt
       for_model: sfincs_hmt
     - name: bathymetry
     - name: drawing
     - name: observation_stations
