import shutil
import subprocess
from pathlib import Path
import os
import sys
import importlib
from importlib.metadata import PackageNotFoundError
import argparse
import PyInstaller.__main__


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
            print(f"Could not update {package_path}. Please check if it is installed and if it is a git repository.")
            print(e)
            exit()
        finally:
            os.chdir(cwd)

def check_pyinstaller() -> None:
    """
    Checks if Pyinstaller is installed and installs it if not found.

    This function runs the command 'pyinstaller -v' to check if Pyinstaller is installed.
    If Pyinstaller is not found, it prompts the user to install it.
    If the user chooses to install it, the function runs the command 'pip install pyinstaller'.

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
            return

def run_pyinstaller(spec_file: Path, build_dir: Path, dist_dir: Path, clean_flag: bool) -> None:
    """
    Run PyInstaller to build an executable from a spec file.

    Args:
        spec_file (Path): The path to the spec file.
        build_dir (Path): The directory to store the build files.
        dist_dir (Path): The directory to store the distribution files.
        clean_flag (bool): Flag indicating whether to clean the build files before running PyInstaller.

    Returns:
        None
    """
    command = [
        str(spec_file),
        "--noconfirm",
        f"--workpath={build_dir}",
        f"--distpath={dist_dir}"
    ]
    
    if clean_flag:
        command.append("--clean")
    PyInstaller.__main__.run(command)


def full_package_copy(to_copy: list, src_path: Path, internal_dir: Path) -> None:
    """
    Copy the specified packages and their associated metadata files to the internal directory.

    Args:
        to_copy (list): A list of package names to be copied.
        src_path (Path): The source path where the packages are located.
        internal_dir (Path): The internal directory where the packages will be copied to.

    Returns:
        None
    """
    env_root_path = os.path.normpath(os.path.dirname(sys.executable))
    site_packages_path = os.path.normpath(Path(env_root_path, os.fspath('Lib/site-packages')))

    shutil.copytree(src_path, (internal_dir / "delftdashboard"), dirs_exist_ok=True)

    for module in to_copy:
        try:
            version = importlib.metadata.version(module)
            module_dir = Path(site_packages_path, module)

            dist_info_dir = Path(site_packages_path, f"{module}-{version}.dist-info")
            if module_dir.exists() and dist_info_dir.exists():
                shutil.copytree(module_dir, internal_dir / module_dir.name, dirs_exist_ok=True)
                shutil.copytree(dist_info_dir, internal_dir / dist_info_dir.name, dirs_exist_ok=True)
                print(f"Copied {module_dir.name} and {dist_info_dir.name} to {internal_dir}")
            else:
                print(f"Could not find {module_dir} or {dist_info_dir} in your environment. Please investigate your environment.")
        except PackageNotFoundError:
            print(f"Could not find {module} in your environment. Please install it.")


def ddb_module_copy(modules: list[str], src_path: Path, internal_dir: Path) -> None:
    """
    Copy the contents of the specified modules from the source path to the internal directory.

    Args:
        modules (list): A list of module names to be copied.
        src_path (str): The source path where the modules are located.
        internal_dir (str): The internal directory where the modules will be copied to.

    Returns:
        None
    """
    for folder in modules:
        shutil.copytree(src_path / folder, internal_dir / folder, dirs_exist_ok=True)
        print(f"Copied {src_path / folder} to {internal_dir / folder}")


def copy_gdal_data(internal_dir: Path) -> None:
    """
    Copy GDAL data files to the specified internal directory.

    Args:
        internal_dir (str): The path to the internal directory where the GDAL data files will be copied.

    Note:
        Copy the GDAL_DATA folder to the dist folder for the run time hook 'pyi_rth_osgeo.py' that sets the env var GDAL_DATA when starting the executable.
        Requires fiona to be installed in site-packages

    Returns:
        None
    """
    env_root_path = os.path.normpath(os.path.dirname(sys.executable))
    site_packages_path = os.path.normpath(Path(env_root_path, os.fspath('Lib/site-packages')))
    
    gdal_data_src = os.path.normpath(Path(site_packages_path, "fiona", "gdal_data"))
    gdal_data_dst = os.path.normpath(Path(internal_dir, "share", "gdal"))
    shutil.copytree(gdal_data_src, gdal_data_dst)


def setup_executable(project_name: str, user_files: Path, setup_folder: Path, exe_dir: Path, internal_dir: Path) -> None:
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
    shutil.copytree(user_files, exe_dir, dirs_exist_ok=True)
    print(f"Copied {user_files} to {exe_dir}")

    setup_folder_dst = Path(internal_dir, "_setup")
    shutil.copytree(setup_folder, setup_folder_dst, dirs_exist_ok=True)
    print(f"Copied {setup_folder} to {setup_folder_dst}")

    data_catalog_yml = internal_dir / "delftdashboard" / "config" / "data_catalog.yml"
    delftdashboard_ini = internal_dir / "delftdashboard" / "config" / "delftdashboard.ini"
    
    os.remove(data_catalog_yml)
    os.remove(delftdashboard_ini)

    executable_path = Path(exe_dir, f"{project_name}.exe")
    print("\nFinished making the executable for DelftDashboard")
    print(f"\nExecutable can be found at: {executable_path}\n\n")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--clean", default=False, action="store_true", 
                    help="Clean build files before compiling the executable")
    parser.add_argument("--no-compile", dest="compile", action="store_false", 
                    help="Skip running PyInstaller. Use this flag if you only want to update the internal folder with your current environment. By default, PyInstaller is run.")
    args = parser.parse_args()
    return args


def main() -> None:
    """
    Main function for building the executable of the FloodAdapt Model Builder.

    This function performs the following steps:
    1. Parses command line arguments.
    2. Defines the project root and project name.
    3. Ensures that the most recent commits of dependent projects are included.
    4. Sets up file paths for the delftdashboard source files and executable setup files.
    5. Sets up destination directories for the build, distribution, and executable.
    6. Sets environment variables for the .spec file to use.
    7. Compiles the executable using PyInstaller if specified.
    8. Copies missing and incomplete packages to the distribution folder.
    9. Copies delftdashboard modules to the distribution folder.
    10. Copies the GDAL_DATA folder to the distribution folder.
    11. Formats the executable folder with user files and setup folder.

    Note: This function assumes that the necessary dependencies are already installed.

    Args:
        None

    Returns:
        None
    """
    # 1 parse command line arguments
    args = parse_args()
    clean_flag = "--clean" if args.clean else ""
    
    # 2 define project root and project name
    project_root = Path(__file__).resolve().parents[3]
    project_name = "FloodAdapt_Model_Builder"

    # 3 ensure most recent commits of dependency projects@main from a local clone on the same level as project_root
    packages = ["hydromt_sfincs", "hydromt_fiat"]
    ensure_most_recent(project_root, packages)

    # 4 set up source paths
    src_path = Path(project_root, "src", "delftdashboard")
    setup_exe_folder = Path(src_path, "setup_executable")
    user_files = Path(setup_exe_folder, "user")
    setup_folder = Path(setup_exe_folder, "setup")
    spec_file = Path(setup_exe_folder, "delftdashboard_compile.spec")

    # 5 set up distribution paths
    build_dir = Path(project_root, "build")
    dist_dir = Path(project_root, "dist")
    exe_dir = Path(dist_dir, project_name)
    internal_dir = Path(exe_dir, "_internal")
    
    # 6 set environment variables for the .spec file to use
    os.environ["PROJECT_ROOT"] = str(project_root)
    os.environ["PROJECT_NAME"] = str(project_name)
    os.environ["EXE_DIR"] = str(exe_dir)

    # 7 compile the executable using PyInstaller if specified
    if args.compile:
        check_pyinstaller()
        run_pyinstaller(spec_file, build_dir, dist_dir, clean_flag)

    # 8 copy missing and incomplete packages to the distribution folder
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
        "cht",
        "cht_cyclones",
        "cht_meteo",
        "cht_observations",
        "cht_tide",
        "cht_tiling",
        "fiona" # This needs to be here for the gdal_data hook to work
    ]
    full_package_copy(missing, src_path, internal_dir)
    
    # 9 copy delftdashboard modules to the distribution folder
    ddb_modules = [
        "layers",
        "menu",
        "misc",
        "models",
        "operations",
        "toolboxes",
    ]
    ddb_module_copy(ddb_modules, src_path, internal_dir)
    
    # 10 copy the GDAL_DATA folder to the distribution folder
    copy_gdal_data(internal_dir)

    # 11 format the executable folder with user files and setup folder
    setup_executable(project_name, user_files, setup_folder, exe_dir, internal_dir)

if __name__ == "__main__":
    main()
