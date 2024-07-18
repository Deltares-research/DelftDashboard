import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import PyInstaller.__main__  # noQA
except Exception:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller==6.7"])
    import PyInstaller.__main__  # noQA

from PyInstaller.utils.hooks import collect_delvewheel_libs_directory  # noQA

PROJECT_NAME = "FloodAdaptModelbuilders"

PROJECT_ROOT = Path(__file__).parents[1].resolve()
SRC_DIR = PROJECT_ROOT / "src" / "delftdashboard"
BUILD_DIR = PROJECT_ROOT / "build"
DIST_DIR = PROJECT_ROOT / "distribution"
SITE_PACKAGES_PATH = Path(sys.executable).parent / "Lib" / "site-packages"

# List of packages that are imported in delftdashboard, but that pyinstaller will miss due to guitares' dynamic imports
IMPORT_LIST = [
    "guitares",
    "rasterio",
    "rasterio.sample",
    "fiat",
    "cht_cyclones",
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


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--onefile",
        default=False,
        dest="onefile",
        action="store_true",
        help="Instead of an _internal directory, create the exe as one file",
    )
    parser.add_argument(
        "--no_console",
        default=False,
        dest="no_console",
        action="store_true",
        help="Do not open a console window when running the executable. By default, a console window is opened.",
    )
    parser.add_argument(
        "--mapbox-token",
        required=True,
        default=None,
        dest="mapbox_token",
        type=str,
        help="Mapbox token to use in the executable. This is stored as a repository secret in github and teamcity.",
    )

    args = parser.parse_args()
    return args


def get_hidden_imports(packages: list[str]) -> list[str]:
    """
    Get the list of hidden imports for the executable.

    Args:
        packages (list[str]): List of packages.

    Returns
    -------
        list: The list of hidden imports for the executable.
    """

    def _import_hidden_delftdashboard_module(
        hidden_imports: list, module_path: Path, module_parents: str = ""
    ) -> None:
        """
        Recursively imports hidden modules from the given module path and adds them to the hidden_imports list.

        Args:
            hidden_imports (list): The list to store the imported hidden modules.
            module_path (Path): The path of the module to import hidden modules from.
            module_parents (str): The parent module path.

        Returns
        -------
            None
        """
        module_name = module_path.name
        if not module_path.is_dir():
            return

        if module_name in hidden_imports:
            return

        import_str = (
            f"{module_parents}.{module_name}" if module_parents else module_name
        )
        hidden_imports.append(import_str)

        for node in os.listdir(module_path):
            node = Path(node)
            if not node.is_dir():  # only import directories
                continue

            full_path = module_path / node

            # If the node is a directory and does not start with an underscore, import it
            if os.path.isdir(full_path) and (not node.name.startswith("_")):

                _import_hidden_delftdashboard_module(
                    hidden_imports,
                    full_path,
                    module_parents=f"{module_parents}.{node.name}",
                )

    hidden_imports = []
    for module in os.listdir(SRC_DIR):
        module = Path(SRC_DIR, module)
        if not module.is_dir() or module.name.startswith("_"):
            continue
        _import_hidden_delftdashboard_module(hidden_imports, module, "delftdashboard")

    for package_name in packages:
        hidden_imports.append(package_name)

    return hidden_imports


def get_datas(datas: list = None) -> list:
    """
    Get the non-python files to be included in the executable.

    Returns
    -------
        list[Tuple[Path, str]]: A list of tuples containing the path to the data file or directory and the destination path within the executable.
    """
    if datas is None:
        datas = []

    # Add the delftdashboard folder to _internal/delftdashboard
    datas.append((SRC_DIR, "delftdashboard"))

    # Add the branca templates folder to _internal/branca/templates
    datas.append(
        (
            (SITE_PACKAGES_PATH / "branca" / "templates" / "*.js"),
            "branca/templates",
        )
    )

    # Add the mapbox server folder to _internal/guitares/pyqt5/mapbox/server
    datas.append(
        (
            (SITE_PACKAGES_PATH / "guitares" / "pyqt5" / "mapbox" / "server"),
            "guitares/pyqt5/mapbox/server",
        )
    )

    return datas


def add_secrets(datas: list, mapbox_token: str):
    with open(DIST_DIR / "mapbox_token.js", "w") as js_file:
        js_file.write(f"mapbox_token = '{mapbox_token}';")
    with open(DIST_DIR / "mapbox_token.txt", "w") as txt_file:
        txt_file.write(mapbox_token)

    # Overwrite template mapbox_token.js in guitares/pyqt/mapbox/server
    # Usually, this is done when initializing the gui for the first time.
    # Guitares.GUI copies from mapboxtoken.txt to mapboxtoken.js.
    # In teamcity we are never running it so we need to do it manually
    datas.append(
        (
            (DIST_DIR / "mapbox_token.txt"),
            "delftdashboard/config",
        )
    )
    datas.append(
        (
            (DIST_DIR / "mapbox_token.js"),
            "guitares/pyqt5/mapbox/server",
        )
    )
    return datas


def copy_shapely_libs():
    # This has to be done now as the hook-shapely.py script is not updated to handle this apparently
    shapely_dir = os.path.join(SITE_PACKAGES_PATH, "shapely")
    if not os.path.exists(shapely_dir):
        raise FileNotFoundError("Shapely not found in site-packages")

    shapely_libs_dir = os.path.join(SITE_PACKAGES_PATH, "Shapely.libs")
    if not os.path.exists(shapely_libs_dir):
        os.makedirs(shapely_libs_dir)

    dlls = [
        os.path.join(shapely_dir, "geos.dll"),
        os.path.join(shapely_dir, "geos_c.dll"),
    ]
    for dll in dlls:
        if not os.path.exists(dll):
            raise FileNotFoundError(f"{dll} not found in shapely")
        shutil.copy(src=dll, dst=shapely_libs_dir)


def run_pyinstaller(
    hidden_imports: list[str],
    datas: list[str],
    args,
) -> None:
    """
    Run PyInstaller to build an executable.

    Args:
        hidden_imports (list[str]): A list of hidden imports.
        datas (list[str]): A list of data files to be included in the distribution.
        args: command line arguments from argparse.

    Returns
    -------
        None
    """
    entry_point = SRC_DIR / "delftdashboard_gui.py"
    spec_path = DIST_DIR / "spec"
    icon_path = DIST_DIR / "icons" / "deltares_logo.jpeg"

    command = [
        str(entry_point),
        "--noconfirm",
        f"--icon={icon_path}",
        f"--name={PROJECT_NAME}",
        f"--workpath={BUILD_DIR}",
        f"--distpath={DIST_DIR}",
        f"--specpath={spec_path}",
    ]
    different_metadata_name = {
        "xrspatial": "xarray_spatial",
        "cht": "deltares_coastalhazardstoolkit",
        "fiat": "DELFT-fiat",
    }

    command.append("--collect-all=delftdashboard")
    command.append("--copy-metadata=delftdashboard")

    for hidden_import in hidden_imports:
        # Skip hidden imports that are (delftdashboard) modules without meta data
        if hidden_import.startswith("delftdashboard"):
            continue
        if "." in hidden_import:
            continue

        command.append(f"--collect-all={hidden_import}")
        command.append(
            f"--copy-metadata={different_metadata_name.get(hidden_import, hidden_import)}"
        )

    for data in datas:
        command.append(f"--add-data={data[0]}:{data[1]}")

    if args.no_console:
        command.append("--no-console")

    if args.onefile:
        command.append("--onefile")

    PyInstaller.__main__.run(command)

    print("\nFinished making the executable for delftdashboard")
    print(f"\nExecutable can be found at: {DIST_DIR / PROJECT_NAME}\n\n")


def main() -> None:
    """
    Build the executable of delftdashboard.

    It functions as follows:
        1. parse command line arguments
        2. define project constants at the top of the script
        3. collect dynamic/variable hidden imports, data files and secrets
        4. compile the executable using PyInstaller.

    Note:
        This function assumes that the necessary dependencies are already installed and that your environment is activated.
        It is also important to NOT have editable installs of the dependent packages, as these do not have the package-metadata that pyinstaller requires.
        This script will install the dependent packages before creating the executable by doing 'pip install .' followed by pip install <dependency_path> for all paths specified in ensure_most_recent.
        If you want to skip this step, you can provide the --no-deps flag to this script.

        Then, install all required depenedencies using 'pip install .' (NOT 'pip install -e .'), and provide --no-deps to this script.
        Or you can clone them and run this script, which will do 'pip install .' for you!


    EXECUTABLE CHECKS:
        1. Make sure the executable runs without any issues.
        2. Make sure the structure is as expected (see below).

        Structure of the executable:
        <Delftdashboard>/<dist>/<Modelbuilders>:
            <_internal>
            YOUR_EXE_NAME.exe

        <_internal>:
            <SOURCE>                                        ->  <DESTINATION>               (CONTENTS)
            <your_env>/<Lib>/<site-packages>/<dependency>   ->  <_internal>/<dependency>    (e.g. hydromt, hydromt_sfincs, hydromt_fiat, flood_adapt, delftdashboard, guitares, etc.)
    """
    # 1 parse command line arguments
    args = parse_args()

    # 2. get hidden imports, data files, and add secrets
    hidden_imports = get_hidden_imports(IMPORT_LIST)
    datas = get_datas()
    datas = add_secrets(datas, mapbox_token=args.mapbox_token)

    copy_shapely_libs()
    binaries = []
    for package in ["numpy", "fiona", "shapely", "rasterio"]:
        datas, binaries = collect_delvewheel_libs_directory(
            package, datas=datas, binaries=binaries
        )

    # 3. compile the executable using PyInstaller
    run_pyinstaller(
        hidden_imports,
        datas,
        args,
    )


if __name__ == "__main__":
    main()