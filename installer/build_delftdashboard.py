"""Build a standalone DelftDashboard executable using Nuitka (PySide6 + MapLibre).

Targets the PySide6 GUI backend with the MapLibre map engine (the active
configuration in ``config/delftdashboard.cfg``) and produces a self-contained
folder that is packaged by the Inno Setup script ``delftdashboard_nuitka.iss``.
See ``compile.md`` for full documentation.

Usage
-----
    cd c:\\work\\checkouts\\git\\DelftDashboard\\installer
    python build_delftdashboard.py            # normal build (no console window)
    python build_delftdashboard.py --debug    # keep console window for tracebacks
    python build_delftdashboard.py --print     # print the nuitka command and exit

Output
------
    dist_nuitka/start_ddb.dist/DelftDashboard.exe   (folder with all dependencies)

Notes
-----
* The first run may download a C compiler (MinGW) and ccache; allow several
  minutes. Subsequent builds are cached and much faster.
* The acid test after a successful build is that the **map renders** (not a
  blank panel). If it is blank, check that QtWebEngineProcess.exe and the
  ``delftdashboard/server`` assets landed in the dist folder (see the checklist
  printed at the end of the build).
"""

import importlib.metadata
import importlib.util
import os
import re
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths (resolved relative to this script, so cwd does not matter)
# ---------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent
REPO = HERE.parent
SRC = REPO / "src" / "delftdashboard"

PYTHON = sys.executable
ENTRY = SRC / "start_ddb.py"
ICON = SRC / "config" / "images" / "deltares.ico"
OUTPUT_DIR = HERE / "dist_nuitka"

# ---------------------------------------------------------------------------
# Packages whose full source tree must be included.
#
# Nuitka cannot see the models / toolboxes / callback modules that DelftDashboard
# loads dynamically via importlib.import_module and importlib.metadata entry
# points, so we force-include the whole ``delftdashboard`` package. The same
# applies to guitares (backend chosen at runtime) and to the geospatial / cht /
# hydromt packages that are imported by name.
# ---------------------------------------------------------------------------
INCLUDE_PACKAGES = [
    # Application + GUI framework
    "delftdashboard",
    "guitares",
    # External DelftDashboard toolboxes: separate (editable) packages discovered
    # at runtime via the "delftdashboard.toolboxes" entry-point group. Nuitka
    # can't see them without an explicit include (metadata is added below too).
    "delftdashboard_tiling_toolbox",
    "delftdashboard_tsunami_toolbox",
    "delftdashboard_watersheds_toolbox",
    "delftdashboard_model_database_toolbox",
    # HydroMT core + plugins (discovered through entry points)
    "hydromt",
    "hydromt_sfincs",
    "hydromt_hurrywave",
    # Coastal Hazards Toolkit packages (imported dynamically by callbacks)
    "cht_sfincs",
    "cht_hurrywave",
    "cht_delft3dfm",
    "cht_xbeach",
    "cht_beware",
    "cht_nesting",
    "cht_tiling",
    "cht_meteo",
    "cht_tide",
    "cht_cyclones",
    "cht_utils",
    "cht_observations",
    "cht_tsunami",
    "cht_physics",
    # Geospatial stack with plugin / driver machinery Nuitka misses
    "rasterio",
    "rioxarray",
    "rio_vrt",  # imported unconditionally by hydromt._utils.caching
    "fiona",
    "pyogrio",
    "pyproj",
    "xugrid",
    "datashader",
    # netCDF4's Cython extension (_netCDF4) imports netCDF4.utils internally at
    # init; Nuitka cannot see imports made from compiled .pyx code, so the whole
    # package must be force-included (else: "No module named 'netCDF4.utils'").
    # cftime (a netCDF4 dependency) has the same issue: its _cftime extension
    # imports cftime._strptime internally.
    "netCDF4",
    "cftime",
    # numba + llvmlite: required by pyflwdir (imported by hydromt). Both use
    # C extensions / a bundled LLVM shared library, so they must be force-
    # included together with their package data (see INCLUDE_PACKAGE_DATA).
    "numba",
    "llvmlite",
    "pyflwdir",
    # numba_celltree: xugrid uses it (via burn_vector_geometry) to rasterise
    # polygons onto the grid for the active-cell mask. Force-include so all its
    # numba-jitted submodules are present in the frozen build.
    "numba_celltree",
    # plotly loads its graph_objs trace submodules (e.g. graph_objs._scatter)
    # lazily via __getattr__, which Nuitka's import-following misses; force-
    # include the whole package (also covers its _plotly_utils helper).
    "plotly",
    "_plotly_utils",
    # S3 stack for the slippy_tile bathymetry driver (downloads gebco/other tiles
    # from the deltares-ddb bucket). hydromt imports s3fs behind a try/except
    # (HAS_S3FS), which Nuitka drops, so force-include the whole chain.
    "s3fs",
    "fsspec",
    "aiobotocore",
    "botocore",
    # NOTE: scipy is deliberately NOT force-included here. It is imported
    # statically (e.g. "from scipy.interpolate import ...") so Nuitka's normal
    # import-following compiles only the submodules actually used. Force-
    # including the whole scipy tree emits thousands of extra C files and was a
    # major driver of the multi-hour C-compilation step. Its data and metadata
    # are still shipped below. If a scipy submodule is missing at runtime, add a
    # targeted "--include-module=scipy.<submodule>" rather than the whole package.
]

# ---------------------------------------------------------------------------
# Packages whose non-Python data files must ship (proj.db, GDAL data, driver
# tables, template assets, ...).
# ---------------------------------------------------------------------------
INCLUDE_PACKAGE_DATA = [
    "delftdashboard",
    "guitares",
    # External toolbox packages ship config/YAML panel definitions.
    "delftdashboard_tiling_toolbox",
    "delftdashboard_tsunami_toolbox",
    "delftdashboard_watersheds_toolbox",
    "delftdashboard_model_database_toolbox",
    "rasterio",
    "fiona",
    "pyogrio",
    "pyproj",
    "rioxarray",
    "xugrid",
    "hydromt",
    "hydromt_sfincs",
    "hydromt_hurrywave",
    "geopandas",
    "shapely",
    "pandas",
    "branca",
    "plotly",
    "datashader",
    "netCDF4",
    "scipy",
    "numba",
    "llvmlite",  # ships the bundled LLVM shared library
    # delft3dfm model chain: hydrolib.core loads bundled *.yaml data files at
    # import (e.g. extold/data/old-external-forcing-data.yaml), and dfm_tools /
    # ddlpy ship data too (ddlpy/endpoints.json). All must be included as data.
    "hydrolib",
    "dfm_tools",
    "ddlpy",
    # meshkernel loads its native MeshKernelApi.dll via ctypes at runtime, from a
    # path relative to the package. If a rebuild does not pick up the DLL through
    # package-data, switch to an explicit --include-data-files for it.
    "meshkernel",
    # botocore/aiobotocore ship large data trees (AWS service + endpoint specs)
    # that must be present for s3fs to talk to S3; fsspec/s3fs ship data too.
    "botocore",
    "aiobotocore",
    "fsspec",
    "s3fs",
    "cht_cyclones",
    "cht_tide",
    "cht_tiling",
]

# ---------------------------------------------------------------------------
# Distribution metadata to embed. REQUIRED for anything discovered through
# importlib.metadata.entry_points() (models/toolboxes, hydromt plugins) and for
# packages that call importlib.metadata.version() at import time. Without this,
# entry_points() returns nothing and no models/toolboxes appear in the GUI.
# ---------------------------------------------------------------------------
INCLUDE_METADATA = [
    "delftdashboard",
    "guitares",
    # Required so entry_points(group="delftdashboard.toolboxes") finds these.
    "delftdashboard_tiling_toolbox",
    "delftdashboard_tsunami_toolbox",
    "delftdashboard_watersheds_toolbox",
    "delftdashboard_model_database_toolbox",
    "hydromt",
    "hydromt_sfincs",
    "hydromt_hurrywave",
    "rasterio",
    "geopandas",
    "pandas",
    "shapely",
    "fiona",
    "pyogrio",
    "pyproj",
    "numpy",
    "scipy",
    "netCDF4",
    "xugrid",
    "plotly",
    "numba",
    "llvmlite",
    "cht_cyclones",
]

# ---------------------------------------------------------------------------
# Data directories to copy verbatim (source -> destination inside the dist).
# NOTE: delftdashboard's own config/ and server/ trees are already shipped by
# ``--include-package-data=delftdashboard`` (they live inside the package), so
# they are intentionally NOT listed here to avoid duplicate-file warnings. Use
# this list only for assets that live OUTSIDE an included package.
# ---------------------------------------------------------------------------
DATA_DIRS: list[tuple[Path, str]] = []

# ---------------------------------------------------------------------------
# Modules to NOT follow. PyQt5 (and the guitares.pyqt5 backend) must be excluded
# so Nuitka does not try to bundle a second, unused Qt binding alongside PySide6.
# The rest are heavy libraries not needed at runtime.
# ---------------------------------------------------------------------------
NOFOLLOW = [
    "PyQt5",
    "guitares.pyqt5",
    "tkinter",
    # NOTE: numba / llvmlite are NOT excluded - hydromt imports pyflwdir, which
    # hard-imports numba (no pure-Python fallback). They are force-included below.
    "sklearn",
    "scikit-learn",
    "eccodes",
    "black",
    "pytest",
    "IPython",
    "jupyter",
    "notebook",
    "test",
]


def _numeric_version(dist: str = "delftdashboard", fallback: str = "0.0.1") -> str:
    """Return the leading numeric dotted version of ``dist`` (e.g. ``0.0.1``).

    Windows version resources require a purely numeric, dotted version, so any
    ``devN`` / ``rcN`` / ``+localtag`` suffix is stripped. Falls back to
    ``fallback`` if the distribution is not installed or has no numeric prefix.
    """
    try:
        raw = importlib.metadata.version(dist)
    except importlib.metadata.PackageNotFoundError:
        return fallback
    match = re.match(r"\d+(?:\.\d+){0,3}", raw)
    return match.group(0) if match else fallback


def _extra_data_files() -> list[tuple[str, str]]:
    """Return (source, dest) pairs for individual files Nuitka won't auto-include.

    Nuitka's ``--include-package-data`` deliberately skips DLLs (it treats them
    as binaries), so a DLL loaded via ctypes from a package directory is missed.
    meshkernel loads its MeshKernelApi.dll that way, so it is added explicitly
    here with the source path resolved from the installed package location.
    """
    files: list[tuple[str, str]] = []
    spec = importlib.util.find_spec("meshkernel")
    if spec and spec.origin:
        dll = Path(spec.origin).parent / "MeshKernelApi.dll"
        if dll.exists():
            files.append((str(dll), "meshkernel/MeshKernelApi.dll"))
        else:
            print(f"WARNING: MeshKernelApi.dll not found next to {spec.origin}")
    return files


def _module_installed(name: str) -> bool:
    """Return True if the top-level module of ``name`` can be located."""
    top = name.split(".")[0]
    try:
        return importlib.util.find_spec(top) is not None
    except (ImportError, ValueError, ModuleNotFoundError):
        return False


def _dist_installed(name: str) -> bool:
    """Return True if distribution metadata for ``name`` is available."""
    try:
        importlib.metadata.distribution(name)
        return True
    except importlib.metadata.PackageNotFoundError:
        return False


def _filter(names: list[str], check) -> tuple[list[str], list[str]]:
    """Split ``names`` into (present, missing) using the ``check`` predicate."""
    present = [n for n in names if check(n)]
    missing = [n for n in names if n not in present]
    return present, missing


def build(debug: bool = False, print_only: bool = False) -> None:
    """Assemble and run the Nuitka command.

    Parameters
    ----------
    debug : bool, optional
        Keep a console window so startup tracebacks are visible. Default False
        (windowed / no console), suitable for a release build.
    print_only : bool, optional
        Print the assembled command and return without running Nuitka.
    """
    if not ENTRY.exists():
        raise FileNotFoundError(f"Entry point not found: {ENTRY}")

    # Fail fast (with a helpful hint) if Nuitka is not in this environment,
    # rather than letting subprocess raise an opaque "No module named nuitka".
    if not print_only and importlib.util.find_spec("nuitka") is None:
        env = Path(PYTHON).parents[1].name
        raise SystemExit(
            f"ERROR: Nuitka is not installed in the '{env}' environment "
            f"({PYTHON}).\n"
            f"       Build from an environment that has Nuitka AND the full "
            f"DelftDashboard dependency set (e.g. 'delftdashboard_dev'),\n"
            f"       or install it here with:  {PYTHON} -m pip install nuitka"
        )

    # Drop anything not installed in the current environment so a partial dev
    # env still builds (with a warning) instead of hard-failing.
    packages, miss_pkg = _filter(INCLUDE_PACKAGES, _module_installed)
    package_data, miss_data = _filter(INCLUDE_PACKAGE_DATA, _module_installed)
    metadata, miss_meta = _filter(INCLUDE_METADATA, _dist_installed)
    for label, missing in (
        ("package", miss_pkg),
        ("package-data", miss_data),
        ("metadata", miss_meta),
    ):
        if missing:
            print(f"WARNING: skipping missing {label}: {', '.join(missing)}")

    console = "force" if debug else "disable"

    cmd = [
        PYTHON, "-m", "nuitka",
        "--standalone",
        "--assume-yes-for-downloads",
        "--enable-plugin=pyside6",
        # Speed up the (slow) C-compilation / link step:
        #   --lto=no  : skip link-time optimization (much faster final link,
        #               marginally larger/slower exe - fine for now).
        #   --jobs=N  : compile with all CPU cores (defaults to CPU count, but
        #               pinned here to be explicit).
        "--lto=no",
        f"--jobs={os.cpu_count() or 1}",
        f"--output-dir={OUTPUT_DIR}",
        "--output-filename=DelftDashboard.exe",
        f"--windows-console-mode={console}",
        "--product-name=DelftDashboard",
        "--company-name=Deltares",
        f"--product-version={_numeric_version()}",
        f"--file-version={_numeric_version()}",
    ]

    if ICON.exists():
        cmd.append(f"--windows-icon-from-ico={ICON}")
    else:
        print(f"WARNING: icon not found, building without it: {ICON}")

    for pkg in packages:
        cmd.append(f"--include-package={pkg}")
    for pkg in package_data:
        cmd.append(f"--include-package-data={pkg}")
    for dist in metadata:
        cmd.append(f"--include-distribution-metadata={dist}")
    for src, dst in DATA_DIRS:
        if src.exists():
            cmd.append(f"--include-data-dir={src}={dst}")
        else:
            print(f"WARNING: data dir not found, skipping: {src}")
    for src, dst in _extra_data_files():
        cmd.append(f"--include-data-files={src}={dst}")
    for mod in NOFOLLOW:
        cmd.append(f"--nofollow-import-to={mod}")

    cmd.append(str(ENTRY))

    print(f"Nuitka command ({len(cmd)} args):\n")
    print(" ".join(cmd))
    print()

    if print_only:
        return

    print("Running Nuitka (this can take several minutes)...\n")
    subprocess.run(cmd, check=True)

    dist = OUTPUT_DIR / "start_ddb.dist"
    print("\nBuild complete!")
    print(f"Executable: {dist / 'DelftDashboard.exe'}")
    print("\nPost-build checklist (PySide6 + MapLibre):")
    print(f"  1. QtWebEngineProcess.exe present in {dist}")
    print(f"  2. Assets present:                  {dist / 'delftdashboard' / 'server' / 'index.html'}")
    print(f"  3. Config present:                  {dist / 'delftdashboard' / 'config' / 'delftdashboard.cfg'}")
    print("  4. Launch it: the map panel must render (not blank).")


if __name__ == "__main__":
    build(
        debug="--debug" in sys.argv,
        print_only="--print" in sys.argv,
    )
