import argparse
import subprocess

from config import (
    EXPECTED_STRUCTURE_MSG_INSTALLER,
    INNOSETUP_DEFINES,
    INSTALLER_SCRIPT_PATH,
    ISCC_PATH,
    SPEC_DIR,
    validate_path,
    clean_exe
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


if __name__ == "__main__":
    main()
