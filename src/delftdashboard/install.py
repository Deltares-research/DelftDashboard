import shutil
from pathlib import Path
import subprocess
import os
import yaml


def update_ini_values(ini_file: Path, replacements: dict):
    with open(ini_file, "r") as f:
        # needs at least PyYAML 5.1
        config = yaml.safe_load(f)
        for key in config:
            if key in replacements:
                config[key] = replacements[key]

    with open(os.path.join(ini_file), "w") as f:
        yaml.dump(config, f)


def check_dir_exists(dir_path: Path):
    if not dir_path.exists():
        print(f"Folder '{dir_path}' does not exist. Please provide a valid folder path.")
        exit()

def get_repo_path(repo_name: str):
    path = Path(input(f"Enter the path to your local {repo_name} cloned repository (leave empty to install a non-editable git version):\n"))
    if path.resolve() == Path('.').resolve() and repo_name.lower() != "delftdashboard":
        return None
    check_dir_exists(path)
    return path.resolve()

def main():
    # Set the current working directory to the root for DelftDashboard so relative paths work
    ddb_rootdir = Path(os.path.abspath(__file__)).parent.parent.parent
    os.chdir(ddb_rootdir)

    # Check if the last part of the path is "DelftDashboard"
    if ddb_rootdir.name != "DelftDashboard":
        print(
            f"Please make sure the root directory is 'DelftDashboard'. The current root directory is: {os.getcwd()}"
        )
        exit()

    env_created = (
        input(
            "Have you CREATED and ACTIVATED virtual environment (ddb_fiat or ddb_sfincs or ddb_FloodAdapt)? (y/n): "
        ).lower()
        == "y"
    )
    if not env_created:
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
    P_DRIVE_modelbuilder_Installation = Path("P:/11207949-dhs-phaseii-floodadapt/Model-builder/Installation")

    print("ENTER LOCAL REPOSITORY PATHS, LEAVE EMPTY IF YOU DONT WANT TO HAVE LOCAL EDITABLE VERSIONS" )
    repos = ["hydromt_fiat", "hydromt_sfincs", "guitares"]
    repo_paths = {repo_name : get_repo_path(repo_name) for repo_name in repos}

    user_specific_folder = Path(
        input(
            "Enter the path to a folder containing your personal mapbox_token.txt and census_key.txt (that you generated):\n"
        )
    ).resolve()
    check_dir_exists(user_specific_folder)

    # === FILES THAT NEED TO BE COPIED TO THE REPOSITORY ===
    # In the repo there exists a default catalog, if the user want more, add the path to the catalog in delftdashboard.ini
    data_catalog_USA = P_DRIVE_modelbuilder_Installation / "data_catalog_USA.yml"
    hydromt_fiat_catalog_USA = P_DRIVE_modelbuilder_Installation / "hydromt_fiat_catalog_USA.yml"
    hydromt_sfincs_catalog = P_DRIVE_modelbuilder_Installation / "data_catalog.yml"

    # cannot be in the repo
    bathemetry_dataFolder = P_DRIVE_modelbuilder_Installation / "data" # too large for repo, needed for sfincs
    Hazus_IWR_curves = P_DRIVE_modelbuilder_Installation / "Hazus_IWR_curves.csv" # sensitive data, needed for fiat

    user_specific_files = {
        # These are files each user needs to generate themselves
        "mapbox_token": user_specific_folder / "mapbox_token.txt",
        "census_key": user_specific_folder / "census_key.txt",
    }
    # Check if the user-specific files exist
    for file_name, file_path in user_specific_files.items():
        if not file_path.exists():
            print(
                f"File '{file_path}' does not exist. Please provide a valid file path to {file_name}."
            )
            if file_name == "mapbox_token":
                print(
                    "go to https://www.mapbox.com/ and create an account to request a personal mapbox_token.txt"
                )
            elif file_name == "census_key":
                print(
                    "go to https://api.census.gov/data/key_signup.html to request a personal census_key.txt"
                )
            exit()

    # === TARGET PATHS ===
    # TODO Check which are needed and which can be in the P drive!!
    targetPath_config_folder = Path("src/delftdashboard/config").resolve()
    targetPath_ini_file = (targetPath_config_folder/ "delftdashboard.ini")
    targetPath_bathymetry_database = Path("data/bathymetry").resolve()
    
    targetPath_datalib_delftdashboard = Path(
        "src/delftdashboard/config/data_catalog_USA.yml"
    ).resolve()
    targetPath_datalib_delftdashboard_roel = Path(
        "src/delftdashboard/config/data_catalog.yml"
    ).resolve()
    targetPath_datalib_hydromt_fiat = (
        repo_paths["hydromt_fiat"] / "hydromt_fiat/data/hydromt_fiat_catalog_USA.yml"
    ).resolve()
    targetPath_Hazus_IWR_curves = (
        repo_paths["hydromt_fiat"]
        / "hydromt_fiat/data/damage_functions/flooding/Hazus_IWR_curves.csv"
    ).resolve()

    # === REPLACEMENTS FOR DELFDASHBOARD.INI ===
    # add stuff to this dict if you want to replace something in the delftdashboard.ini
    replacements = {
        "bathymetry_database": str(targetPath_bathymetry_database),
        "data_libs": [
            str(targetPath_datalib_delftdashboard),
            str(targetPath_datalib_hydromt_fiat),
            str(targetPath_datalib_delftdashboard_roel),
        ],
    }

    update_ini_values(targetPath_ini_file, replacements)
    print("delftdashboard.ini updated successfully.")

    # Copy the mapbox_token.txt file
    shutil.copy(
        user_specific_files["mapbox_token"], targetPath_config_folder / "mapbox_token.txt"
    )
    print(f"Copied mapbox_token.txt to {targetPath_config_folder}.")

    # Copy the census_key.txt file
    shutil.copy(
        user_specific_files["census_key"], targetPath_config_folder / "census_key.txt"
    )
    print(f"Copied census_key.txt to {targetPath_config_folder}.")

    # Copy the data_catalog_USA.yml file to the delftdashboard/config folder
    shutil.copy(data_catalog_USA, targetPath_datalib_delftdashboard)
    print(f"Copied data_catalog_USA.yml to {targetPath_datalib_delftdashboard}.")

    # Copy the data_catalog_USA.yml file to the delftdashboard/config folder
    shutil.copy(hydromt_sfincs_catalog, targetPath_datalib_delftdashboard_roel)
    print(f"Copied hydromt_fiat_catalog_USA.yml to {targetPath_datalib_delftdashboard_roel}.")
    
    # Copy the data_catalog_USA.yml file to the hydromt_fiat/ folder
    shutil.copy(hydromt_fiat_catalog_USA, targetPath_datalib_hydromt_fiat)
    print(f"Copied hydromt_fiat_catalog_USA.yml to {targetPath_datalib_hydromt_fiat}.") 
    
    # Copy the Hazus_IWR_curves.csv file
    shutil.copy(Hazus_IWR_curves, targetPath_Hazus_IWR_curves)
    print(f"Copied Hazus_IWR_curves.csv to {targetPath_Hazus_IWR_curves}.")

    # Recursively copy the DelftDashboard/data folder
    shutil.copytree(bathemetry_dataFolder, "data", dirs_exist_ok=True)
    print(f"Copied bathemetry data to {ddb_rootdir/'data'}.")

    print("\nConfidential & user specific files/folder locations updated successfully.")

    print("\nSetting up local editable versions of repositories...")

    # Install the editable repositories
    for repo in repo_paths.values():
        if repo is not None:
            subprocess.run(["pip", "install", "-e", repo], shell=True)

if __name__ == "__main__":
    main()
