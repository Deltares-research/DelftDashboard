import argparse
import subprocess

from config import (
    EXPECTED_STRUCTURE_MSG_INSTALLER,
    INNOSETUP_DEFINES,
    INSTALLER_SCRIPT_PATH,
    ISCC_PATH,
    SPEC_DIR,
    P_DRIVE_INSTALLERS,
    validate_path,
    clean_exe,
    create_zip,
)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--quiet",
        default=False,
        dest="quiet",
        action="store_true",
        help="print less output to the console",
    )

    parser.add_argument(
        "--zip",
        required=False,
        default=False,
        dest="zip",
        action="store_true",
        help="Create a zip file containing the installer after creation and store it on the P drive",
    )
    parser.add_argument(
        "--overwrite",
        required=False,
        default=False,
        dest="overwrite",
        action="store_true",
        help="Overwrite the existing installer instead of raising an error when a version already exists",
    )
    args = parser.parse_args()
    return args


def main():
    """
    Create an installer for the FloodAdapt application using Inno Setup Compiler.

    BUILDING THE INSTALLER:
        1. Make sure you can run the created executable without any issues.
        2. Download InnoSetup from SVN: https://repos.deltares.nl/repos/FloodAdapt-Database/InnoSetup6 and copy it to the 'distribution' folder. See EXPECTED_STRUCTURE_MSG_INSTALLER for more information.
        3. Verify the contents of 'INNOSETUP_DEFINES' in distribution/config.py (version, name, paths, etc.)
        4. Install the created installer on your machine to verify that it works as expected.
    """
    args = parse_args()

    # Validate before running Inno Setup Compiler
    validate_path("ISCC_PATH", ISCC_PATH, EXPECTED_STRUCTURE_MSG_INSTALLER)
    if args.zip:
        if not P_DRIVE_INSTALLERS.exists():
            raise FileNotFoundError(
                f"P_DRIVE_INSTALLERS does not exist: {P_DRIVE_INSTALLERS}. Make sure the P drive is mounted."
            )

    # Make sure the exe doesnt contain any datacatalogs / ini files from testing it
    clean_exe()

    # Create the command
    app_args = [f"/D{key}={value}" for key, value in INNOSETUP_DEFINES.items()]

    cmd_args = [
        f"{ISCC_PATH}",
        f"{INSTALLER_SCRIPT_PATH}",
        *app_args,
    ]
    if args.quiet:
        cmd_args.append("/Qp")

    print("\n".join(cmd_args))
    # Run
    try:
        process = subprocess.Popen(
            args=" ".join(cmd_args),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        while process.poll() is None and process.stdout:
            print(process.stdout.readline(), end="")
        
        if process.returncode != 0:
            if process.stderr:
                print(process.stderr.readlines())
            exit(process.returncode)
       
        print(f"Installer created at {SPEC_DIR / 'Output'}")

    except subprocess.CalledProcessError as e:
        print(f"Command '{e.cmd}' returned non-zero exit status {e.returncode}.")
        print(f"Captured output:\n{e.stdout}")
        exit(e.returncode)

    if args.zip:
        create_zip(
            dir_path=SPEC_DIR / "Output",
            output_dir=P_DRIVE_INSTALLERS,
            overwrite=args.overwrite,
        )


if __name__ == "__main__":
    main()
