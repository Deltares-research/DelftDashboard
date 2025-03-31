import argparse
from pathlib import Path

from config import (
    BRANCA_TEMPLATES_DIR,
    BUILD_DIR,
    DEPENDENCIES,
    DIFFERENT_METADATA_NAME,
    DIST_DIR,
    ENTRY_POINT,
    EXCLUDES,
    EXPECTED_STRUCTURE_MSG_EXE,
    LOGO,
    MANUAL_BINARIES,
    MAPBOX_TOKEN_JS,
    MAPBOX_TOKEN_TXT,
    PROJECT_NAME,
    PYINSTALLER_DEFINES,
    RTH_HOOK,
    SPEC_DIR,
    CENSUS_KEY_TXT,
    excluding_filter,
    validate_env_has_no_editable_installations,
    validate_path,
    increase_recursion_limit,
    copy_shapely_libs,
    add_data_dir,
    clean_exe
)


try:
    import PyInstaller.__main__
    from PyInstaller.utils.hooks import (
        collect_data_files,
        collect_delvewheel_libs_directory,
        collect_dynamic_libs,
        collect_submodules,
    )
except ImportError as e:
    e.msg += "\n\nBuild tools are not installed (correctly). Run `pip install .[build]` to install the required build tools."
    raise e


def parse_args():
    parser = argparse.ArgumentParser(
        description="Build the FloodAdapt Modelbuilder executable using PyInstaller. For more information on pyinstaller, see the https://pyinstaller.org/en/stable.",
        usage="python build_executable.py --mapbox-token <token> --census-key <key> [--no-console] [--debug]. \n\nIMPORTANT: run this script in an ACTIVATED ENVIRONMENT WITH ONLY NON EDITABLE installs of python packages (Pyinstaller will not include them otherwise)\n ",
    )
    parser.add_argument(
        "--mapbox-token",
        required=True,
        dest="mapbox_token",
        type=str,
        help="Mapbox token to use in the executable. This is stored as a repository secret in github and teamcity.",
    )
    parser.add_argument(
        "--census-key",
        required=True,
        dest="census_key",
        type=str,
        help="Census key to use in the executable. This is stored as a repository secret in github and teamcity.",
    )
    parser.add_argument(
        "--no-console",
        required=False,
        default=False,
        dest="no_console",
        action="store_true",
        help="Enable or disable the terminal when running the executable.",
    )
    parser.add_argument(
        "--debug",
        required=False,
        default=False,
        dest="debug",
        type=bool,
        help="Set to True to save debugging information to text files and print more information during the build process",
    )
    parser.add_argument(
        "--include-data",
        required=False,
        default=False,
        dest="include_data",
        action="store_true",
        help="Include the data directory in the exe. This copies the data directory: `distribution/data` to the exe directory after building the exe.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Increase the recursion limit for PyInstaller
    increase_recursion_limit()

    # Define paths and variables
    validate_env_has_no_editable_installations()

    # Validate before running PyInstaller
    for varname, path in PYINSTALLER_DEFINES.items():
        validate_path(varname, path, EXPECTED_STRUCTURE_MSG_EXE)

    # Collect data files, dynamic libraries and hidden imports
    datas: list[tuple[str, str]] = []
    binaries: list[tuple[str, str]] = []
    hidden_imports: list[str] = []

    for package_name in DEPENDENCIES:
        datas += collect_data_files(
            package_name, include_py_files=True, excludes=EXCLUDES
        )
        binaries += collect_dynamic_libs(package_name)
        hidden_imports += collect_submodules(package_name, filter=excluding_filter)

    # Create mapbox token files
    with open(MAPBOX_TOKEN_TXT, "w") as f:
        f.write(args.mapbox_token)
    with open(MAPBOX_TOKEN_JS, "w") as f:
        f.write(f"mapbox_token = '{args.mapbox_token}';")

    # Add the mapbox token files
    datas.append((str(MAPBOX_TOKEN_TXT), "delftdashboard/config"))
    datas.append((str(MAPBOX_TOKEN_JS), "guitares/pyqt5/mapbox/server"))

    # Create the census_key file
    with open(CENSUS_KEY_TXT, "w") as f:
        f.write(args.census_key)
    
    datas.append((str(CENSUS_KEY_TXT), "delftdashboard/config"))

    # Add the branca templates (for guitares)
    datas.append((str(BRANCA_TEMPLATES_DIR / "*.js"), "branca/templates"))

    # Some packages for some reason do not include the .dll files from the .libs dir in their wheel, so we have to include them manually
    copy_shapely_libs()
    for package in MANUAL_BINARIES:
        datas, binaries = collect_delvewheel_libs_directory(
            package, datas=datas, binaries=binaries
        )

    # Create the PyInstaller command https://pyinstaller.org/en/stable/usage.html#running-pyinstaller-from-python-code
    add_datas = [f"--add-data={data[0]}:{data[1]}" for data in datas]
    add_binaries = [f"--add-binary={bin[0]}:{bin[1]}" for bin in binaries]
    add_hidden_imports = [
        f"--hidden-import={hidden_import}" for hidden_import in hidden_imports
    ]
    copy_metadata = [
        f"--recursive-copy-metadata={DIFFERENT_METADATA_NAME.get(package, package)}"
        for package in hidden_imports
        if "." not in package  # Only copy metadata for top-level packages
    ]

    cmd_args = [
        "--noconfirm",
        f"--name={PROJECT_NAME}",
        f"--workpath={BUILD_DIR}",
        f"--distpath={DIST_DIR}",
        f"--specpath={SPEC_DIR}",
        f"--icon={LOGO}",
        f"--runtime-hook={RTH_HOOK}",
        *add_datas,
        *add_binaries,
        *add_hidden_imports,
        *copy_metadata,
        f"{ENTRY_POINT}",
    ]
    if args.no_console:
        cmd_args.append("--noconsole")

    # Debugging
    if args.debug:
        cmd_args.append("--log-level=DEBUG")

        debugging_info = {
            "datas": add_datas,
            "binaries": add_binaries,
            "hidden_imports": add_hidden_imports,
            "cmd_args": cmd_args,
        }
        for name, data in debugging_info.items():
            with open(Path(__file__).parent / f"{name}.txt", "w") as f:
                print("\n".join(data), file=f)

    PyInstaller.__main__.run(cmd_args)

    # Make sure data catalogs + ini files are valid for distribution
    clean_exe()

    # Always create the structure for the data directory, optionally include the data itself in the exe
    add_data_dir(args.include_data)
    

if __name__ == "__main__":
    main()
