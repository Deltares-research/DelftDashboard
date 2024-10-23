import os
import shutil
import sys
from pathlib import Path

from delftdashboard import __version__ as ddb_version

# List of packages that are (partly) imported/used in floodadapt_gui and its dependencies.
# but that pyinstaller will miss due to guitares' dynamic imports / imports in functions
DEPENDENCIES = [
    "delftdashboard",
    "guitares",
    "rasterio",
    "rasterio.sample",
    "fiat",
    "cht",
    "cht_cyclones",
    "cht_observations",
    "geopandas",
    "pandas",
    "shapely",
    "flood_adapt",
    "shapely._geos",
    "pyogrio",
    "pyogrio._geometry",
    "netCDF4",
    "scipy",
    "zarr",
    "rioxarray",
    "charset_normalizer",
    "charset_normalizer.md__mypyc",
    "fiona",
    "fiona.enums",
    "plotly",
    "tomli_w",
    "numpy",
    "numpy_financial",
    "pydantic",
    "pydantic_core",
    "annotated_types",
    "duckdb",
    "xugrid",
    "hydromt",
    "hydromt_fiat",
    "hydromt_sfincs",
]

# Pyinstaller requires metadata for all packages. Some packages have different metadata names than their import names.
DIFFERENT_METADATA_NAME = {
    "xrspatial": "xarray_spatial",
    "cht": "deltares_coastalhazardstoolkit",
    "fiat": "DELFT-fiat",
}

# List of patterns to exclude from the file and hidden imports collection
EXCLUDES = [
    "tests",
    "test",
    "example",
    "examples",
    "log",
    "logs",
    ".pyc",
    "__pycache__",
]

# List of packages that for some reason do not include all their .dll dependencies in the wheel, so we have to include them manually
MANUAL_BINARIES = ["numpy", "fiona", "shapely", "rasterio"]


# msg for FileNotFoundError in build_executable.py
EXPECTED_STRUCTURE_MSG_EXE = """
Expected structure for this script to work:
DelftDashboard (PROJECT_ROOT_DIR)
├── distribution (SPEC_DIR)
│   ├── icons
│   │   ├── deltares_logo.jpeg (LOGO)
│   ├── build_executable.py
│   ├── config.py
│   ├── ...
│   ├── rth-delftdashboard.py (RTH_HOOK)
├── src/delftdashboard (SRC_DIR)
│       ├── config/images
│       │       ├── deltares_logo.png (LOGO)
│       ├── ...
│       ├── delftdashboard_gui.py (ENTRY_POINT)
...

environment:
    site-packages (SITE_PACKAGES_DIR)
    ├── branca
    │   ├── templates
    │   │   ├── ...
    ├── ...
    ...
"""

EXPECTED_STRUCTURE_MSG_INSTALLER = """
Expected structure for this script to work:
DelftDashboard (PROJECT_ROOT_DIR)
├── distribution (SPEC_DIR)
│   ├── InnoSetup6
│   │   ├── iscc.exe (ISCC_PATH)
│   │   ├── ...
│   ├── ...
│   ├── make_installer_script.iss (INSTALLER_SCRIPT_PATH)
│   ├── build_installer.py
│   ├── config.py
│   ├── ...
│   ├── rth-delftdashboard.py (RTH_HOOK)
├── dist (DIST_DIR)
|  ├── FloodAdaptModelBuilder (PROJECT_NAME)
|  |  ├── _internal (INTERNAL_DIR)
|  |  |  ├── delftdashboard
|  |  |  |  ├── system (EXE_SYSTEM_DIR)
|  |  |  ├── flood_adapt
|  |  |  |  ├── system (EXE_SYSTEM_DIR)
|  |  |  |  ├── ...
|  |  |  ├── ...
|  |  ├── ...
"""

# Project definitions
PROJECT_NAME = "FloodAdaptModelBuilder"
PROJECT_ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT_DIR / "src" / "delftdashboard"
SPEC_DIR = PROJECT_ROOT_DIR / "distribution"
DIST_DIR = PROJECT_ROOT_DIR / "dist"
BUILD_DIR = PROJECT_ROOT_DIR / "build"

# Environment
SITE_PACKAGES_DIR = Path(sys.executable).parent / "Lib" / "site-packages"
BRANCA_TEMPLATES_DIR = SITE_PACKAGES_DIR / "branca" / "templates"
SHAPELY_DIR = SITE_PACKAGES_DIR / "shapely"
SHAPELY_LIBS_DIR = SITE_PACKAGES_DIR / "Shapely.libs"

# dst paths
INTERNAL_DIR = DIST_DIR / PROJECT_NAME / "_internal"
EXE_CONFIG_DIR = INTERNAL_DIR / "delftdashboard" / "config"
EXE_DATA_DIR = DIST_DIR / PROJECT_NAME / "data"

# src paths
DATA_DIR = SPEC_DIR / "data"
DATA_CATALOG = SPEC_DIR / "data_catalog.yml"
DELFTDASHBOARD_INI = SPEC_DIR / "delftdashboard.ini"
LOGO = SPEC_DIR / "icons" / "deltares_logo.jpeg"
ICON = SPEC_DIR / "icons" / "deltares.ico"
LICENCE = SPEC_DIR / "LICENSE.txt"
RTH_HOOK = SPEC_DIR / "rth-delftdashboard.py"
ENTRY_POINT = SRC_DIR / "delftdashboard_gui.py"
MAPBOX_TOKEN_TXT = SPEC_DIR / "mapbox_token.txt"
MAPBOX_TOKEN_JS = SPEC_DIR / "mapbox_token.js"
CENSUS_KEY_TXT = SPEC_DIR / "census_key.txt"
ISCC_PATH = SPEC_DIR / "InnoSetup6" / "iscc.exe"
INSTALLER_SCRIPT_PATH = SPEC_DIR / "make_installer_script.iss"

PYINSTALLER_DEFINES = {
    "SRC_DIR": SRC_DIR,
    "SPEC_DIR": SPEC_DIR,
    "DATA_DIR": DATA_DIR,
    "DATA_CATALOG": DATA_CATALOG,
    "DELFTDASHBOARD_INI": DELFTDASHBOARD_INI,
    "SITE_PACKAGES_DIR": SITE_PACKAGES_DIR,
    "BRANCA_TEMPLATES": BRANCA_TEMPLATES_DIR,
    "SHAPELY_DIR": SHAPELY_DIR,
    "LOGO": LOGO,
    "RTH_HOOK": RTH_HOOK,
    "ENTRY_POINT": ENTRY_POINT,
}

INNOSETUP_DEFINES = {
    "MyAppName": PROJECT_NAME,
    "MyAppVersion": f"{ddb_version}",
    "MyAppPublisher": "Deltares",
    "MyAppURL": "https://www.deltares.nl/software-en-data/producten/floodadapt",
    "MyAppExeName": f"{PROJECT_NAME}.exe",
    "MyAppExeDir": str(DIST_DIR / PROJECT_NAME),
    "MyAppIcon": str(ICON),
    "MyAppLicense": str(LICENCE),
}


def _validate_path(varname: str, path: Path, expected_structure_message="") -> None:
    if not path.exists():
        raise FileNotFoundError(
            f"{varname} does not exist: {path}.\n{expected_structure_message}"
        )


def _excluding_filter(module: str, patterns: list[str] = EXCLUDES) -> bool:
    return not any(pattern in module for pattern in patterns)


def _validate_env_has_no_editable_installations() -> None:
    """Editable installations have a file: '__editable__.<package_name>-<version>.pth file in the environment."""
    env_name = Path(sys.executable).parent.name
    editable_installs = "\n".join(
        [
            "".join(
                p.name.replace("__editable__.", "").replace(".pth", "").split("-")[:-1]
            )
            for p in list(SITE_PACKAGES_DIR.glob("__editable__.*.pth"))
        ]
    )

    msg = f"Editable installations found in the environment: {env_name}\n{editable_installs}\nPlease pip install these without the flag '-e' before running the build script as pyinstaller does not support editable installations."

    assert not editable_installs, msg

def _increase_recursion_limit(limit: int = 5000) -> None:
    """Explanation: Python's stack-limit is a safety-belt against endless recursion,
       eating up memory. PyInstaller imports modules recursively. If the structure
       how modules are imported within your program is awkward, this leads to the
       nesting being too deep and hitting Python's stack-limit.
       With the default recursion limit (1000), the recursion error occurs at about
       115 nested imported, with limit 2000 at about 240, with limit 5000 at about
       660.
    """
    sys.setrecursionlimit(limit)
    print(f"Recursion limit increased to {sys.getrecursionlimit()}")

def _copy_shapely_libs():
    """Explanation: The hook for shapely expects the .dll files to be in the shapely.libs directory, so we have to copy them there"""
    SHAPELY_LIBS_DIR.mkdir(exist_ok=True)
    dlls = [ SHAPELY_DIR / "geos.dll", SHAPELY_DIR / "geos_c.dll" ]
    for dll in dlls:
        if not dll.exists():
            raise FileNotFoundError(f"{dll} not found in {SHAPELY_DIR}")
        shutil.copy2(src=dll, dst=SHAPELY_LIBS_DIR)

def clean_exe():
    TO_DELETE = ["data_catalog", "delftdashboard.ini"]
    for root, dirs, files in os.walk(EXE_CONFIG_DIR):
        for file in files:
            if any([name in file for name in TO_DELETE]):
                os.remove(os.path.join(root, file))
    shutil.copy2(src=DATA_CATALOG, dst=EXE_CONFIG_DIR)
    shutil.copy2(src=DELFTDASHBOARD_INI, dst=EXE_CONFIG_DIR)
