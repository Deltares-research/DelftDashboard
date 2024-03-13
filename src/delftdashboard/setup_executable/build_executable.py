import argparse
import importlib
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Tuple

import PyInstaller.__main__


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--clean",
        default=False,
        dest="clean",
        action="store_true",
        help="Clean build files before compiling the executable",
    )
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
        "--no-deps",
        dest="update_deps",
        action="store_false",
        help="Skip updating the dependent packages. By default, the most recent commits of the dependent packages are included in the build.",
    )

    args = parser.parse_args()
    return args


def ensure_most_recent(project_root: Path, packages: list[str] = None) -> None:
    """
    Ensures that the specified packages are updated to the most recent version.

    Args:
        project_root (Path): The root directory of the project.
        packages (list[str]): A list of package names to update. Assumes the packages are located in the same folder as the project root. Defaults to None.

    Raises:
        Exception: If the package cannot be updated.

    Returns:
        None
    """
    cwd = os.getcwd()
    package_paths = [Path(project_root.parent, package) for package in packages]
    for package_path in package_paths:
        print(f"Updating {package_path}")
        try:
            os.chdir(package_path)
            subprocess.run(["git", "pull", "origin"])
            subprocess.run(["git", "checkout", "main"])
            subprocess.run(["pip", "install", "."])
        except Exception as e:
            print(
                f"Could not update {package_path}. Please check if it is installed and if it is a git repository."
            )
            print(e)
            exit()
        finally:
            os.chdir(cwd)


def get_hidden_imports(src_path, ddb_modules, packages):
    """
    Get the list of hidden imports for the executable.

    Args:
        src_path (Path): The source path of the executable.
        ddb_modules (list[str]): List of Delft Dashboard modules.
        packages (list[str]): List of packages.

    Returns:
        list: The list of hidden imports for the executable.
    """

    def import_hidden_ddb_module(
        hidden_imports: list, module_path: Path, module_parents: str
    ) -> None:
        """
        Recursively imports hidden modules from the given module path and adds them to the hidden_imports list.

        Args:
            hidden_imports (list): The list to store the imported hidden modules.
            module_path (Path): The path of the module to import hidden modules from.
            module_parents (str): The parent module path.

        Returns:
            None
        """
        for node in os.listdir(module_path):
            full_path = Path(module_path, node)
            basename = os.path.basename(node)

            # If the node is a directory, import the hidden modules from the directory
            if os.path.isdir(full_path) and (not basename.startswith("_")):
                import_hidden_ddb_module(
                    hidden_imports,
                    full_path,
                    module_parents=f"{module_parents}.{basename}",
                )

            else:
                # If the node is a python file, add it to the hidden imports list
                if (basename.endswith(".py")) and not basename.startswith("_"):
                    file = basename[:-3]
                    module = f"{module_parents}.{file}"
                    hidden_imports.append(module)

    hidden_imports = []
    for module in ddb_modules:
        module_path = Path(src_path, module)
        import_hidden_ddb_module(
            hidden_imports, module_path, module_parents=f"delftdashboard.{module}"
        )

    for package_name in packages:
        hidden_imports.append(package_name)
    return hidden_imports


def get_datas(src_path, ddb_modules) -> list[Tuple[Path, str]]:
    """
    This function is used to get the non-python files to be included in the executable.

    Returns:
        list[Tuple[Path, str]]: A list of tuples containing the path to the data file or directory and the destination path within the executable.
    """

    datas = []
    for module in ddb_modules:
        # Add them directly to _internal
        datas.append(
            (
                os.path.normpath(Path(src_path, module)),
                module,
            )
        )

    env_root_path = os.path.normpath(os.path.dirname(sys.executable))
    site_packages_path = os.path.normpath(
        Path(env_root_path, os.fspath("Lib/site-packages"))
    )
    # Add the branca templates folder
    datas.append(
        (
            os.path.normpath(Path(site_packages_path, "branca", "templates/*.js")),
            "branca/templates",
        )
    )
    # Add the mapbox server folder
    datas.append(
        (
            os.path.normpath(
                Path(site_packages_path, "guitares", "pyqt5", "mapbox", "server")
            ),
            "guitares/pyqt5/mapbox/server",
        )
    )
    # Add the gdal_data folder from fiona
    datas.append(
        (
            os.path.normpath(Path(site_packages_path, "fiona", "gdal_data")),
            "share/gdal",
        )
    )

    # files that we want to take from 'src/delftdashboard/setup_executable/setup' instead of 'src/delftdashboard' before including in '_internal/delftdashboard/config'
    _files_to_ddbconfig = [
        "mapbox_token.txt",
        "census_key.txt",
        "data_catalog.yml",
        "delftdashboard.ini",
    ]

    # Add all non-python files from 'src/delftdashboard/**' to '_internal/delftdashboard/**' keeping the same structure
    for root, dirs, files in os.walk(src_path):
        # For each file to include, append it to the datas list with the correct relative path
        for file in files:
            if file.endswith(".py") or file.endswith(".pyc"):
                continue
            full_file_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_file_path, str(src_path))
            if file in _files_to_ddbconfig:
                # Copy from setup folder
                datas.append(
                    (
                        os.path.normpath(
                            Path(src_path, "setup_executable", "setup", file)
                        ),
                        os.path.join("delftdashboard", os.path.dirname(relative_path)),
                    )
                )
            else:
                # Do the normal copy
                datas.append(
                    (
                        full_file_path,
                        os.path.join("delftdashboard", os.path.dirname(relative_path)),
                    )
                )
    return datas


def run_pyinstaller(
    src_path: Path,
    project_name: str,
    build_dir: Path,
    dist_dir: Path,
    hidden_imports: list[str],
    datas: list[str],
    icon_path: Path,
    args,
) -> None:
    """
    Run PyInstaller to build an executable.

    Args:
        src_path (Path): The path to the source directory.
        project_name (str): The name of the project.
        build_dir (Path): The directory to store the build files.
        dist_dir (Path): The directory to store the distribution files.
        hidden_imports (list[str]): A list of hidden imports.
        datas (list[str]): A list of data files to be included in the distribution.
        icon_path (Path): The path to the icon file.
        args: command line arguments from argparse.

    Returns:
        None
    """
    try:
        subprocess.run(["pyinstaller", "-v"])
    except Exception:
        print("Could not find Pyinstaller. Do you want to install it? (y/n)")
        if input().lower() == "y":
            subprocess.run(["pip", "install", "pyinstaller"])
        else:
            exit()

    entry_point = src_path / "delftdashboard_gui.py"
    spec_path = src_path / "setup_executable"

    command = [
        str(entry_point),
        "--noconfirm",
        f"--icon={icon_path}",
        f"--name={project_name}",
        f"--workpath={build_dir}",
        f"--distpath={dist_dir}",
        f"--specpath={spec_path}",
        "--collect-all=delftdashboard",
        "--copy-metadata=delftdashboard",
    ]
    different_metadata_name = {
        "xrspatial": "xarray_spatial",
        "cht": "deltares_coastalhazardstoolkit",
    }

    added_packages = []
    for hidden_import in hidden_imports:
        command.append(f"--hidden-import={hidden_import}")

        package = hidden_import.split(".")[0]
        if package not in added_packages:
            added_packages.append(package)
            command.append(f"--collect-all={package}")

            if package in different_metadata_name:
                package = different_metadata_name[package]

            if not package.startswith("delftdashboard"):
                command.append(f"--copy-metadata={package}")

    for data in datas:
        command.append(f"--add-data={data[0]}:{data[1]}")

    if args.clean:
        command.append("--clean")

    if args.no_console:
        command.append("--no-console")

    if args.onefile:
        command.append("--onefile")

    PyInstaller.__main__.run(command)


def setup_executable(
    project_name: str,
    user_files: Path,
    exe_dir: Path,
) -> None:
    """
    Copies user files and setup folder to the executable directory, removes specific files,
    and creates an executable for DelftDashboard.

    Args:
        project_name (str): The name of the project.
        user_files (Path): The path to the user files directory.
        setup_folder (Path): The path to the setup folder in the repository.
        exe_dir (Path): The path to the executable directory.
        internal_dir (Path): The path to the internal directory.

    Returns:
        None
    """
    # Copy instructions & other files to the executable directory
    shutil.copytree(user_files, exe_dir, dirs_exist_ok=True)
    print(f"Copied {user_files} to {exe_dir}")

    # Make an empty data directory
    data_dir = exe_dir / "data"
    os.makedirs(data_dir, exist_ok=True)
    print(f"Created {data_dir}")

    # Print location
    executable_path = Path(exe_dir, f"{project_name}.exe")
    print("\nFinished making the executable for DelftDashboard")
    print(f"\nExecutable can be found at: {executable_path}\n\n")


def main() -> None:
    """
    Main function for building the executable of the FloodAdapt Model Builder.
    It functions as follows:
        1. parse command line arguments
        2. define project root, project name and icon
        3. ensure most recent commits of dependency projects@main from a local clone on the same level as project_root
        4. set up source paths
        5. set up distribution paths
        6. get hidden imports and datas
        7. compile the executable using PyInstaller if specified
        8. format the executable folder with user files, setup folder & instructions

    Note:
        This function assumes that the necessary dependencies are already installed and that your environment is activated.
        It is also important to NOT have editable installs of the dependent packages, as these do not have the package-metadata that pyinstaller requires.
        So packages like hydromt, hydromt_sfincs, hydromt_fiat, flood_adapt and guitares should cloned next to DelftDashboard if you want to use commits more recent than the latest release.
        Then you can install them using 'pip install .' and not 'pip install -e .', and provide --no-deps to this script.
        Or you can clone them and run this script, which will do 'pip install .' for you!

    Args:
        None

    Returns:
        None
    """
    # 1 parse command line arguments
    args = parse_args()

    # 2 define project root, project name and icon
    project_root = Path(__file__).resolve().parents[3]
    project_name = "FloodAdapt_Model_Builder"
    icon_path = Path(
        project_root, "src", "delftdashboard", "setup_executable", "setup", "icon.ico"
    )

    # 3 ensure most recent commits of dependency projects@main from a local clone on the same level as project_root
    if args.update_deps:
        packages = ["hydromt_sfincs", "hydromt_fiat"]
        ensure_most_recent(project_root, packages)

    # 4 set up source paths
    src_path = Path(project_root, "src", "delftdashboard")
    setup_exe_folder = Path(src_path, "setup_executable")
    user_files = Path(setup_exe_folder, "user")

    # 5 set up distribution paths
    build_dir = Path(project_root, "build")
    dist_dir = Path(project_root, "dist")
    exe_dir = Path(dist_dir, project_name)

    ddb_modules = [
        "layers",
        "menu",
        "misc",
        "models",
        "operations",
        "toolboxes",
    ]

    missing = [
        "hydromt",
        "hydromt_fiat",
        "hydromt_sfincs",
        "flood_adapt",
        "numpy",
        "pyogrio",
        "rasterio",
        "shapely",
        "distributed",
        "xugrid",
        "xarray",
        "xrspatial",
        "openpyxl",
        "pandas",
        "guitares",
        "cht",
        "cht_cyclones",
        "cht_meteo",
        "cht_observations",
        "cht_tide",
        "cht_tiling",
        "fiona",  # This needs to be here for the gdal_data hook to work
    ]

    # 6. get hidden imports and data files
    hidden_imports = get_hidden_imports(src_path, ddb_modules, missing)
    datas = get_datas(src_path, ddb_modules)

    # 7 compile the executable using PyInstaller
    run_pyinstaller(
        src_path,
        project_name,
        build_dir,
        dist_dir,
        hidden_imports,
        datas,
        icon_path,
        args,
    )

    # 8 format the executable folder with user files, setup folder & instructions
    setup_executable(project_name, user_files, exe_dir)


if __name__ == "__main__":
    main()
