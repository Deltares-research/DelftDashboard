import shutil
import subprocess
from pathlib import Path
import os
import sys
import importlib
from importlib.metadata import PackageNotFoundError
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--clean", default=False, action="store_true", help="Clean build files before compiling the executable")
args = parser.parse_args()

clean_flag = "--clean" if args.clean else ""

def main():
    # define project
    project_root = Path(__file__).resolve().parents[3]
    project_name = "FloodAdapt_Model_Builder"

    # sources
    src_path = Path(project_root, "src", "delftdashboard")
    
    setup_exe_folder = Path(src_path, "setup_executable")
    user_files = Path(setup_exe_folder, "user")
    setup_folder = Path(setup_exe_folder, "setup")
    spec_file = Path(setup_exe_folder, "delftdashboard_compile.spec")

    # destinations
    build_dir = Path(project_root, "build")
    dist_dir = Path(project_root, "dist")
    exe_dir = Path(dist_dir, project_name)
    internal_dir = Path(exe_dir, "_internal")
    
    # set environment variables to allow .spec file to use them
    os.environ["PROJECT_ROOT"] = str(project_root)
    os.environ["PROJECT_NAME"] = str(project_name)
    os.environ["EXE_DIR"] = str(exe_dir)

    # Check pyinstaller is installed
    try:
        subprocess.run(["pyinstaller", "-v"])
    except Exception:
        print("Could not find Pyinstaller. Do you want to install it? (y/n)")
        if input().lower() == "y":
            subprocess.run(["pip", "install", "pyinstaller"])
        else:
            return
    
    # compile the executable
    command = [
        "pyinstaller",
        spec_file,
        "--noconfirm",
        f"--workpath={build_dir}",
        f"--distpath={dist_dir}"
    ]
    if clean_flag:
        command.append("--clean")
    subprocess.run(command)

    # TODO copy GDAL header files to the dist folder
    # TODO add runtimehook to set GDAL_DATA environment variable

    # check for missing metadata
    env_root_path = os.path.normpath(os.path.dirname(sys.executable))
    site_packages_path = os.path.normpath(Path(env_root_path, os.fspath('Lib/site-packages')))

    # Pyinstaller does not include all the srcfiles and metadata files for some packages
    # Add entries here to solve runtime errors from missing packages and/or metadata
    missing_metadata = ["delftdashboard", "hydromt", "hydromt_fiat", "hydromt_sfincs", "numpy", "distributed", "xugrid"]
    for module in missing_metadata:
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

    # copy the delftdashboard folder to the dist folder
    shutil.copytree(src_path, internal_dir / "delftdashboard", dirs_exist_ok=True)
    print("\n\n")

    # copy the user files and setup folder to the dist folder
    shutil.copytree(user_files, exe_dir, dirs_exist_ok=True)
    print(f"Copied {user_files} to {exe_dir}")

    _setup_folder = Path(internal_dir, "_setup")
    shutil.copytree(setup_folder, _setup_folder, dirs_exist_ok=True)
    print(f"Copied {setup_folder} to {_setup_folder}")
    
    shutil.copytree(src_path / "config", internal_dir / "delftdashboard" / "config", dirs_exist_ok=True)
    print(f"Copied {setup_folder} to {_setup_folder}")


    executable_path = Path(exe_dir, f"{project_name}.exe")
    print("\nFinished making the executable for DelftDashboard")
    print(f"\nExectubale can be found at: {executable_path}\n\n")

if __name__ == "__main__":
    main()
