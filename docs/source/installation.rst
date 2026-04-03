Installation
============

DelftDashboard can be installed either as a standalone end-user application or
as a development environment.

Requirements
------------

- Python 3.12 (recommended) or 3.10+
- `Miniforge3 <https://github.com/conda-forge/miniforge>`_ (recommended conda
  distribution)
- Windows 10/11 (primary platform)

End-User Installation
---------------------

The end-user installation uses a pre-built conda-pack archive that contains all
dependencies.

1. Download the installer archive from the release page.

2. Extract the archive to a folder of your choice (e.g.
   ``C:\Program Files\DelftDashboard``).

3. Run the post-install script to finalise paths::

      post_install.bat

4. Launch the application::

      delftdashboard.bat

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
