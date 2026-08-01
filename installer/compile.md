# Compiling DelftDashboard to a standalone executable

This document describes how to build the standalone Windows executable
(Nuitka, PySide6 + MapLibre) and package it into an installer (Inno Setup).

## Overview

```
build_delftdashboard.py  --(nuitka)-->  dist_nuitka\start_ddb.dist\DelftDashboard.exe
delftdashboard_nuitka.iss --(iscc)--->  dist_innosetup\DelftDashboard_Setup_<ver>.exe
```

The executable is a **standalone folder** (exe + all DLLs + data files), not a
one-file exe. The installer copies that folder to `<install dir>\bin\` and asks
the user where the (potentially large, downloaded) data folder should live.

## Prerequisites

- Conda environment **`delftdashboard_dev`** with the full DelftDashboard
  dependency stack installed (editable checkouts of hydromt, hydromt_sfincs,
  hydromt_hurrywave, guitares, cht_* etc.), plus:
  - `nuitka` (tested with 4.1.3)
  - a C compiler: MSVC if present; otherwise Nuitka downloads MinGW
    automatically (`--assume-yes-for-downloads`)
- **Inno Setup 6** for the installer
  (`winget install JRSoftware.InnoSetup`; `ISCC.exe` ends up in
  `C:\Program Files (x86)\Inno Setup 6\`)

## Building the executable

```bat
conda activate delftdashboard_dev
cd c:\work\checkouts\git\DelftDashboard\installer
python build_delftdashboard.py            :: release build (no console)
python build_delftdashboard.py --debug    :: console window (use while testing!)
python build_delftdashboard.py --print    :: show the nuitka command, don't build
```

Output: `installer\dist_nuitka\start_ddb.dist\DelftDashboard.exe`

Notes on build time:
- "Pass 1" (Nuitka's whole-program Python analysis) is single-threaded and
  scales with the number of included modules; it cannot be parallelised.
- The C compile step (thousands of files) is parallel (`--jobs`) and cached
  (ccache): the **first** build is slow (up to hours), rebuilds after small
  changes are much faster. Keep `dist_nuitka\start_ddb.build\` between builds.

### What the build script handles (hard-won knowledge)

The include lists in `build_delftdashboard.py` encode everything below. If you
add a dependency and the frozen exe fails, this table is the debugging guide.

| Problem class | Symptom in frozen exe | Solution in script |
|---|---|---|
| Dynamic imports (models/toolboxes via importlib) | missing modules | `--include-package=delftdashboard` (whole tree) |
| Entry-point discovery (`importlib.metadata.entry_points`) | no models/toolboxes/hydromt plugins appear | `--include-distribution-metadata=<dist>` for every plugin package |
| External toolboxes (tiling, tsunami, watersheds, model_database) | `No module named delftdashboard_*_toolbox` | included as package + data + metadata |
| Cython-internal imports | `No module named netCDF4.utils` / `cftime._strptime` | force-include `netCDF4`, `cftime` |
| numba stack (pyflwdir hard-requires numba) | ImportError numba excluded | include `numba`, `llvmlite`, `pyflwdir`, `numba_celltree` |
| Lazy `__getattr__` imports | `No module named plotly.graph_objs._scatter` | force-include `plotly`, `_plotly_utils` |
| Conditional imports (`HAS_S3FS` in hydromt) | bathymetry tiles never download | force-include `s3fs`, `fsspec`, `aiobotocore`, `botocore` (+ their data) |
| Package data files | `FileNotFoundError ...\hydrolib\...\*.yaml`, `ddlpy\endpoints.json` | `--include-package-data=` hydrolib, dfm_tools, ddlpy, ... |
| ctypes-loaded DLLs (skipped by package-data!) | `Could not find module ...\meshkernel\MeshKernelApi.dll` | explicit `--include-data-files` (see `_extra_data_files()`) |
| Unconditional new deps | `No module named rio_vrt` | keep env up to date; include `rio_vrt` |
| Second Qt binding | huge build / conflicts | `--nofollow-import-to=PyQt5`, `guitares.pyqt5` |
| GDAL/PROJ data | CRS errors | package-data for rasterio/fiona/pyogrio/pyproj |
| Windows version resource | FATAL: version info needed | `--product-version/--file-version` (from installed dist version) |

### Frozen-runtime behaviour (implemented in the source, not the script)

- **Entry point** `src/delftdashboard/start_ddb.py`:
  - sets `NUMBA_CACHE_DIR` to a writable per-user dir *before* numba is
    imported (numba `cache=True` writes next to bundled modules otherwise,
    which hangs the first JIT compile in a frozen build);
  - restores `sys.excepthook` (rasterio 1.5 installs a broken recursive hook
    that turns any unhandled exception into a segfault when frozen);
  - catches startup errors, prints the traceback and keeps the console open.
- **Data folder resolution** (`operations/initialize.py`, compiled builds):
  1. `DELFTDASHBOARD_DATA` environment variable, else
  2. `delftdashboard.pth` file next to the exe (written by the installer), else
  3. `%LOCALAPPDATA%\DelftDashboard`.
- **Working directory**: when launched from its own bin folder, cd to the
  remembered last working directory (stored in
  `<DelftDashboard folder>\last_working_directory.txt`) or
  `<DelftDashboard folder>\working_directory` (next to `data` and `server`);
  when launched from another folder, that folder is respected and remembered.
- **Bathymetry catalogs**: two files in ``data\bathymetry\`` have a defined
  role. ``data_catalog_s3.yml`` is a copy of the catalog on the DDB S3 bucket
  (the source of truth for the S3 datasets), refreshed at every online start -
  never edit it. ``data_catalog_local.yml`` is optional and user-managed (the
  bathymetry import toolbox appends to it); its entries always win over
  same-named S3 datasets. Legacy root/per-dataset ``data_catalog.yml`` files
  are still read for backward compatibility. Tiles/COGs download on demand,
  so a fresh data folder gets a working bathymetry list on first run.
- **Numba/datashader warmup** (background thread at startup): pre-compiles
  xugrid `snap_to_grid`, `burn_vector_geometry` (mask polygons), and the
  datashader line/points/trimesh aggregations.
- **Datashader compile cache patch**: datashader's `toolz.memoize` keys never
  match under Nuitka, so every render would recompile its numba aggregation;
  `_patch_datashader_compile_cache()` re-keys the cache on argument *content*.
- **No `tf.spread`**: the mask overlays in hydromt_sfincs / hydromt_hurrywave
  use a scipy `binary_dilation` instead (`_dilate_bool_agg`). tf.spread
  numba-compiles a closure kernel per marker size, which can never be disk
  cached and took minutes per compile inside the frozen exe.

### Post-build checklist

1. `dist_nuitka\start_ddb.dist\QtWebEngineProcess.exe` exists (map view).
2. `...\delftdashboard\server\index.html` and `...\delftdashboard\config\delftdashboard.cfg` exist.
3. `...\meshkernel\MeshKernelApi.dll` exists.
4. Launch (debug build): all toolboxes and models load, **map renders**.
5. `set DELFTDASHBOARD_DATA=c:\work\delftdashboard` and check background
   topography loads; pan to an uncached area to confirm tile download (s3fs).
6. Build a small model: grid, bathymetry, **update mask with a polygon**
   (fast, no hang), save; model files land in the working directory.

## Building the installer

```bat
cd c:\work\checkouts\git\DelftDashboard\installer
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" delftdashboard_nuitka.iss
```

Output: `installer\dist_innosetup\DelftDashboard_Setup_<version>.exe`

What the installer does (`delftdashboard_nuitka.iss`):
- asks for ONE DelftDashboard folder (default `C:\DelftDashboard`; must be
  writable, so not Program Files) and installs the dist into `<folder>\bin\`;
- writes `<folder>` to `bin\delftdashboard.pth` (read by the exe at startup),
  so `data\`, `server\`, `working_directory\` and `delftdashboard.ini` are all
  created by the app inside that same folder;
- creates Start-menu / optional desktop shortcuts;
- uninstall removes `bin\` but **never** the data and user files next to it.

Remember to bump `#define MyAppVersion` in the `.iss` (and the version of the
installed `delftdashboard` package, which feeds the exe's version resource).

## Release procedure

The version has a single source of truth: ``__version__`` in
``src/delftdashboard/__init__.py``. Everything else derives from it: pyproject
(dynamic attr), the GUI (window title and Help > About), the exe version
resource (read by ``build_delftdashboard.py``), and the installer name/version
(``package_ddb.bat`` passes it to ISCC as ``/DMyAppVersion``).

1. Bump ``__version__`` in ``src/delftdashboard/__init__.py`` and commit.
2. ``build_ddb.bat``           (exe: ``dist_nuitka\start_ddb.dist``)
3. Test the exe (see the post-build checklist above).
4. ``package_ddb.bat``         (installer: ``dist_innosetup\DelftDashboard_Setup_<version>.exe``)
5. Test the installer on a clean machine / user profile.
6. ``release_ddb.bat``         (git tag v<version>, push, GitHub release with the
   installer attached; ``--dry-run`` shows what it would do). Read the Docs
   rebuilds automatically on push, and its download link points at the latest
   GitHub release.

## Known follow-ups

- **Code signing**: the unsigned exe is treated with maximum suspicion by
  antivirus software; besides SmartScreen warnings this can drastically slow
  numba JIT compilation at runtime (executable-page allocations get scanned).
  Signing benefits both.
- Linux (AppImage) and macOS (.app/.dmg + notarization) require building on
  those platforms; a CI matrix (GitHub Actions) is the practical route.

## File inventory

| File | Role |
|---|---|
| `installer/build_ddb.bat` | one-click Nuitka build (wraps the script below) |
| `installer/build_delftdashboard.py` | Nuitka build script |
| `installer/package_ddb.bat` | one-click installer build (wraps ISCC) |
| `installer/delftdashboard_nuitka.iss` | Inno Setup installer script |
| `installer/compile.md` | this document |
| `src/delftdashboard/config/images/deltares.ico` | exe + installer icon (lives with the app's other images) |

Older build routes (PyInstaller specs, a conda-pack installer, and the
FloodAdapt-era `distribution/` folder) were removed in August 2026; recover
them from git history if ever needed. NOTE: no license page is currently
shown by the installer (to add one: `LicenseFile=` in the `.iss`).
