import shutil
from pathlib import Path
import subprocess
import os
from typing import Union
import yaml
import sys


def check_dir_exists(dir_path: Path) -> bool:
    if not dir_path.exists():
        print(
            f"Folder '{dir_path}' does not exist. Please provide a valid folder path."
        )
        return False
    return True


def get_repo_path(repo_name: str) -> Union[Path, None]:
    valid_path = False
    path = Path()

    while not valid_path:
        user_input = input(
            f"\nEnter the path to your local {repo_name} cloned repository (leave empty to install a non-editable git version):\n"
        )
        if user_input is None:
            return None
        else:
            path = Path(user_input).resolve()
            valid_path = check_dir_exists(path)
    return path


def get_and_check_script_location() -> Path:
    script_path = Path(os.path.abspath(__file__))
    ddb_src_dir = script_path.parent.parent

    if ddb_src_dir.name != "src":
        print(
            f"Please make sure this script is in the directory: '<root>/src/delftDashboard/'. The current location is: {script_path}"
        )
        exit()
    return script_path


def check_env_creation() -> None:
    python_path = sys.executable
    env_active = any(
        env_name in python_path
        for env_name in ["ddb_fiat", "ddb_sfincs", "ddb_dev", "ddb_floodadapt"]
    )
    if not env_active:
        print(
            """
            Please CREATE and ACTIVATE the virtual environment for DelftDashboard before running this script.\n
            You can do this by running the following commands in a terminal:\n
            conda init\n
            cd <location of your repository clone of DelftDashboard>\n
            mamba env create --file=./src/delftdashboard/env/ddb_FloodAdapt.yml --force\n
            conda activate ddb_FloodAdapt\n
            Now you can run this script.
            """
        )
        exit()


def get_repo_paths() -> dict:
    print(
        f"\nEnter local repository paths RELATIVE to the CURRENT WORKING DIRECTORY:\n{os.getcwd()}\nLeave empty if you dont want to have a local editable installation of the repository."
    )

    repos = ["hydromt_fiat", "hydromt_sfincs", "guitares"]
    repo_paths = {repo_name: get_repo_path(repo_name) for repo_name in repos}

    return repo_paths


def get_and_copy_user_files(ddb_config_dir: Path) -> None:
    valid = False
    user_specific_folder = Path()

    while not valid:
        user_specific_folder = Path(
            input(
                "\nEnter the path to a folder containing your personal mapbox_token.txt and census_key.txt (that you generated):\n"
            )
        ).resolve()
        valid = check_dir_exists(user_specific_folder)

    # These are files each user needs to generate themselves
    user_specific_files = {
        "mapbox_token.txt": user_specific_folder / "mapbox_token.txt",
        "census_key.txt": user_specific_folder / "census_key.txt",
    }
    # Check if the user-specific files exist
    for file_name, file_path in user_specific_files.items():
        if not file_path.exists():
            print(
                f"File '{file_path}' does not exist. Please provide a valid file path to {file_name}"
            )
            if file_name == "mapbox_token.txt":
                print(
                    "go to https://www.mapbox.com/ and create an account to request a personal mapbox_token.txt"
                )
            elif file_name == "census_key.txt":
                print(
                    "go to https://api.census.gov/data/key_signup.html to request a personal census_key.txt"
                )
            exit()
        else:
            shutil.copy(user_specific_files[file_name], ddb_config_dir / file_name)
            print(f"Copied {file_name} to {ddb_config_dir}")


def copy_p_drive_files(
    p_drive_modelbuilder_installation: Path,
    ddb_config_dir: Path,
    repo_paths: dict,
) -> dict:
    # == P DRIVE FILES ==
    file_names = [
        "delftdashboard.ini",
        "data_catalog_USA.yml",
        "hydromt_fiat_catalog_USA.yml",
        "data_catalog.yml",
        "data",
        "Hazus_IWR_curves.csv",
    ]
    keys = [
        "delftdashboard.ini",
        "datalib_delftdashboard",
        "hydromt_fiat_catalog_USA",
        "hydromt_sfincs_catalog",
        "dataFolder_bathymetry",
        "Hazus_IWR_curves",
    ]

    p_drive_files = {
        key: p_drive_modelbuilder_installation / file_name
        for key, file_name in zip(keys, file_names)
    }

    # === TARGET PATHS ===
    target_paths = {
        "delftdashboard.ini": ddb_config_dir / "delftdashboard.ini",
        "datalib_delftdashboard": ddb_config_dir / "data_catalog_USA.yml",
        "hydromt_sfincs_catalog": ddb_config_dir / "data_catalog.yml",
        "dataFolder_bathymetry": ddb_config_dir.parent.parent.parent / "data",
    }

    # this will be gone eventually when hydromt_fiat is updated to not hardcoded to need the catalog anymore
    while repo_paths["hydromt_fiat"] is None:
        print(
            "Currrently, hydromt_fiat is required to be locally installed to run DelftDashboard, please provide the path to your local clone:\n"
        )
        repo_paths["hydromt_fiat"] = get_repo_path("hydromt_fiat")

    target_paths.update(
        {
            "hydromt_fiat_catalog_USA": repo_paths["hydromt_fiat"]
            / Path("hydromt_fiat", "data", "hydromt_fiat_catalog_USA.yml"),
            "Hazus_IWR_curves": repo_paths["hydromt_fiat"]
            / Path(
                "hydromt_fiat",
                "data",
                "damage_functions",
                "flooding",
                "Hazus_IWR_curves.csv",
            ),
        }
    )

    # Copy files and folders from P drive to target paths
    for source_name, source_path in p_drive_files.items():
        if source_path.is_dir():
            # Recursively copy folders
            shutil.copytree(
                p_drive_files[source_name],
                target_paths[source_name],
                dirs_exist_ok=True,
            )
            print(f"Copied folder {source_name} to {target_paths[source_name]}")
        else:
            # Copy files
            shutil.copy(source_path, target_paths[source_name])
            print(f"Copied file {source_name} to {target_paths[source_name]}")

    print("\nConfidential files and data folder locations updated successfully.")

    return target_paths


def update_delftdashboard_ini(target_paths: dict) -> None:
    # In the repo there exists a default catalog, if the user want more, add the path to the data_libs here
    replacements = {
        "dataFolder_bathymetry": os.fspath(target_paths["dataFolder_bathymetry"]),
        "data_libs": [
            os.fspath(target_paths["datalib_delftdashboard"]),
            os.fspath(target_paths["hydromt_fiat_catalog_USA"]),
            os.fspath(target_paths["hydromt_sfincs_catalog"]),
        ],
    }

    with open(target_paths["delftdashboard.ini"], "r+") as f:
        config = yaml.safe_load(f)
        for key in config:
            if key in replacements:
                config[key] = replacements[key]
        yaml.dump(config, f)
    print("delftdashboard.ini updated successfully.")


def optional_editable_install(repo_paths: dict) -> None:
    print("\nSetting up local editable versions of repositories...")
    # Install the optional repositories
    for repo in repo_paths.values():
        if repo is not None:
            subprocess.run(["pip", "install", "-e", repo], shell=True)


def main():
    script_path = get_and_check_script_location()
    ddb_config_dir = script_path.parent / "config"

    p_drive_modelbuilder_installation = Path(
        "P:", "11207949-dhs-phaseii-floodadapt", "Model-builder", "Installation"
    )

    check_env_creation()
    repo_paths = get_repo_paths()
    get_and_copy_user_files(ddb_config_dir)
    target_paths = copy_p_drive_files(
        p_drive_modelbuilder_installation, ddb_config_dir, repo_paths
    )
    update_delftdashboard_ini(target_paths)

    # Install the required repositories
    subprocess.run(["pip", "install", "-e", "."], shell=True)

    optional_editable_install(repo_paths)


if __name__ == "__main__":
    main()
