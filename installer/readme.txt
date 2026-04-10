DelftDashboard Installer - Build & Install Instructions
=======================================================

OVERVIEW
--------
The installer packages the DelftDashboard Python environment into a
self-contained archive that can be extracted on any Windows machine.
It uses conda-pack to bundle all conda/pip dependencies into a single
archive. No Python, conda, or pip is needed on the target machine.

Note: PyInstaller was evaluated but is not suitable for DDB due to the
complex GDAL/rasterio/pyogrio DLL chain and many dynamically imported
packages (cht_*, hydromt plugins, guitares). conda-pack is the
recommended approach.


STEP 1: BUILD (developer machine)
----------------------------------
Prerequisites:
  - miniforge3 installed at ~/miniforge3
  - conda-pack installed: conda install conda-pack -c conda-forge

Option A - Build from clean environment (recommended for distribution):
  cd c:\work\checkouts\git\DelftDashboard\installer
  python build_installer.py

  This creates a fresh "ddb_dist" environment, installs all packages
  from GitHub (non-editable), packs it, and generates install.bat.
  Takes ~15 minutes. Output in installer\dist\:
    - delftdashboard_env.tar.gz  (~800 MB)
    - install.bat

Option B - Build from dev environment (for testing):
  python -c "import conda_pack; conda_pack.pack(
      name='delftdashboard_dev',
      output='dist/delftdashboard_env.tar.gz',
      force=True,
      ignore_editable_packages=True)"

  Note: This excludes editable packages. You'll also need the
  post_install.bat to fetch them from GitHub on the target machine.


STEP 2: DISTRIBUTE
-------------------
Ship these files to the end user:
  - delftdashboard_env.tar.gz  (~800 MB)
  - install.bat


STEP 3: INSTALL (end user machine)
-----------------------------------
Prerequisites:
  - Windows 10/11 (64-bit)
  - ~3 GB free disk space
  - Internet connection (only for first run: map tiles + data downloads)

Steps:
  1. Put both files in the same folder
  2. Double-click install.bat
     - Choose install location (default: C:\Users\<you>\DelftDashboard)
     - Extracts the environment (~2 minutes)
     - Fixes path prefixes (conda-unpack)
     - Creates delftdashboard.bat launcher
     - Creates a desktop shortcut
  3. Done! Launch from desktop shortcut

On first launch, a dialog will ask you to select the data folder.
This is where bathymetry, meteo, and other datasets are stored.


OPTIONAL: Professional Installer with Inno Setup
--------------------------------------------------
For a proper .exe installer with progress bar and uninstaller:
  1. Install Inno Setup (free): https://jrsoftware.org/isdl.php
  2. Open installer\delftdashboard.iss in Inno Setup Compiler
  3. Update the [Files] Source path to point to the conda-pack output
  4. Click Build > Compile
  5. Output: dist_innosetup\DelftDashboard_Setup_0.1.0.exe


TROUBLESHOOTING
---------------
Q: install.bat fails with "tar is not recognized"
A: tar is built into Windows 10+. On older Windows, install 7-Zip
   and extract the .tar.gz manually.

Q: "conda-unpack is not recognized"
A: Re-run install.bat. If it persists, open a command prompt in the
   install directory and run: Scripts\conda-unpack.exe

Q: DelftDashboard starts but shows a blank map
A: Check your internet connection. Map tiles are loaded from the web.

Q: How do I change the data folder?
A: Edit delftdashboard.pth in the DDB package directory. It contains
   a single line with the path to your data folder.

Q: How do I uninstall?
A: Delete the install folder and the desktop shortcut.
