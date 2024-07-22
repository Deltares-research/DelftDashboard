import argparse
import subprocess
from pathlib import Path

from floodadapt_gui import __version__

ROOT_PATH = Path(__file__).resolve().parent.parent
ISCC_PATH = ROOT_PATH / "distribution" / "InnoSetup6" / "iscc.exe"
SCRIPT_PATH = ROOT_PATH / "distribution" / "make_installer_script.iss"
if not ISCC_PATH.exists():
    raise FileNotFoundError(
        f"Could not find Inno Setup Compiler at {ISCC_PATH}. Please copy it from the Database to <distribution>."
    )

APPLICATION_INFO = {
    "MyAppName": "FloodAdaptModelBuilders",
    "MyAppVersion": f"{__version__}",
    "MyAppPublisher": "Deltares",
    "MyAppURL": "https://www.deltares.nl/software-en-data/producten/floodadapt",
    "MyAppExeName": "FloodAdaptModelBuilders.exe",
    "MyAppRootSourceDir": Path.as_posix(ROOT_PATH),
}


def create_installer_command_args(quiet=False):
    command = [f"{ISCC_PATH.as_posix()}"]
    for key, value in APPLICATION_INFO.items():
        command.append(f"/D{key}={value}")

    if quiet:
        command.append("/Qp")

    command.append(f"{SCRIPT_PATH.as_posix()}")
    return command


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--quiet",
        default=False,
        dest="quiet",
        action="store_true",
        help="print less output to the console",
    )
    args = parser.parse_args()
    return args


def main():
    """
    Create an installer for the ModelBuilder application using Inno Setup Compiler.

    INSTALLER CHECKS:
        1. Make sure the <system> folder to the <_internal> folder.
        2. Make sure you can run the created executable without any issues.
        3. Update the '#define' statements at the top of the script 'make_installer_script.iss' (version, name, paths, etc.)

    BUILDING THE INSTALLER:
        1. Download InnoSetup from SVN: https://repos.deltares.nl/repos/FloodAdapt-Database/InnoSetup6 and copy it to the 'distribution' folder.
        2. Verify the 'APPLICATION_INFO' statements at the top of this file script (version, name, paths, etc.)
        3. Install the created installer on your machine to verify that it works as expected.
    """
    args = parse_args()

    args_list = create_installer_command_args(quiet=args.quiet)

    print("Running command with each line as an arg:")
    [print(arg) for arg in args_list]

    try:
        process = subprocess.run(
            args=args_list,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        print(process.stdout)
        print(f"Installer created at {SCRIPT_PATH.parent / 'Output'}")

    except subprocess.CalledProcessError as e:
        print(f"Command '{e.cmd}' returned non-zero exit status {e.returncode}.")
        print(f"Captured output:\n{e.stdout}")
        exit(e.returncode)


if __name__ == "__main__":
    main()
