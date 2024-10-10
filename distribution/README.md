# Read this before building the executable 

All files in `distribution` are for the bundling, please don't change these if you are not sure.

Below is a description of the purpose of each file / dir:

- `data` contains [`Watersheds`, `TopoBathy`]:
    - the data to be included in the exe. Will be copied directly to `dist/PROJECT_NAME` (next to the exe file and _internal dir)
    - make sure the contents are referenced correctly in `data_catalog.yml`
- `data-catalog.yml`:
    - the only data catalog that will be included in the the exe 
    - make sure the paths are correct and point to the data in the 
- `delftdashboard.ini`:
    - should reference all data_libs (paths to data_catalog.yml files) as relative paths starting with _internal
    - should reference the bathymetry_database if you have one
- `LICENCE.txt`
    - the licence to be included in the installer
- `make_installer_script.iss`:
    - The InnoSetup script that creates the install wizard and compresses the bundled exe.


Python files:
- `build_executable.py`: bundle the exe from a working environment
- `build_installer.py`: using the bundled exe, make an installer that will install the bundle onto any windows PC
- `rth-delftdashboard.py`: is run when the exe is started, before any other code is ran. (some temporary fixes/hacky stuff is in here)
