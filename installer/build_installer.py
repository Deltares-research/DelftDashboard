"""Build a DelftDashboard installer using conda-pack.

Creates a clean minimal conda environment, installs all dependencies,
packs it into a relocatable archive, and generates installer scripts.

Usage:
    python build_installer.py

Output:
    installer/dist/delftdashboard_env.tar.gz  (conda-pack archive)
    installer/dist/install.bat                (Windows installer)
"""

import os
import subprocess
import sys

# Configuration
DIST_ENV_NAME = "ddb_dist"
PYTHON_VERSION = "3.12"
MINIFORGE = os.path.expanduser("~/miniforge3")
CONDA = os.path.join(MINIFORGE, "condabin", "conda.bat")
INSTALLER_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(INSTALLER_DIR, "dist")
REQUIREMENTS = os.path.join(INSTALLER_DIR, "requirements_minimal.txt")
ARCHIVE_NAME = "delftdashboard_env.tar.gz"
VERSION = "0.1.0"


def run(cmd, check=True, **kwargs):
    """Run a command and print it."""
    print(f"  > {cmd}")
    subprocess.run(cmd, shell=True, check=check, **kwargs)


def create_clean_environment():
    """Create a fresh conda environment with only what DDB needs."""
    print(f"\n=== Creating clean environment '{DIST_ENV_NAME}' ===")

    # Remove if exists
    run(f'"{CONDA}" env remove -n {DIST_ENV_NAME} -y', check=False)

    # Create with Python only
    run(f'"{CONDA}" create -n {DIST_ENV_NAME} python={PYTHON_VERSION} -c conda-forge -y')

    # Install conda-pack in the new env
    run(f'"{CONDA}" install -n {DIST_ENV_NAME} conda-pack -c conda-forge -y')

    # Install all requirements via pip
    pip = os.path.join(MINIFORGE, "envs", DIST_ENV_NAME, "python.exe")
    run(f'"{pip}" -m pip install -r "{REQUIREMENTS}"')


def pack_environment():
    """Pack the clean environment into a tar.gz archive."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    archive_path = os.path.join(OUTPUT_DIR, ARCHIVE_NAME)

    if os.path.exists(archive_path):
        os.remove(archive_path)

    print(f"\n=== Packing environment '{DIST_ENV_NAME}' ===")
    print("This may take several minutes...")

    python = os.path.join(MINIFORGE, "envs", DIST_ENV_NAME, "python.exe")
    run(
        f'"{python}" -c "'
        f"import conda_pack; "
        f"conda_pack.pack(name='{DIST_ENV_NAME}', "
        f"output=r'{archive_path}', force=True)"
        f'"'
    )

    size_mb = os.path.getsize(archive_path) / (1024 * 1024)
    print(f"Archive created: {archive_path} ({size_mb:.0f} MB)")
    return archive_path


def create_installer_bat():
    """Create the Windows installer batch script."""
    install_bat = os.path.join(OUTPUT_DIR, "install.bat")

    with open(install_bat, "w") as f:
        f.write(f"""@echo off
setlocal

echo ============================================
echo   DelftDashboard Installer v{VERSION}
echo ============================================
echo.

set "INSTALL_DIR=%USERPROFILE%\\DelftDashboard"

echo Default install location: %INSTALL_DIR%
echo.
set /p "CUSTOM_DIR=Install location (press Enter for default): "
if not "%CUSTOM_DIR%"=="" set "INSTALL_DIR=%CUSTOM_DIR%"
echo.
echo Installing to: %INSTALL_DIR%
set /p "CONFIRM=Continue? (Y/N): "
if /i not "%CONFIRM%"=="Y" exit /b 1

echo.
echo Creating installation directory...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo.
echo Extracting environment (this may take a few minutes)...
tar -xzf "%~dp0{ARCHIVE_NAME}" -C "%INSTALL_DIR%"

echo.
echo Fixing path prefixes...
pushd "%INSTALL_DIR%"
call "%INSTALL_DIR%\\Scripts\\activate.bat"
conda-unpack
popd

echo.
echo Creating launcher...
(
    echo @echo off
    echo call "%INSTALL_DIR%\\Scripts\\activate.bat"
    echo cd /d "%%USERPROFILE%%"
    echo python -c "import delftdashboard; delftdashboard.start()"
) > "%INSTALL_DIR%\\delftdashboard.bat"

echo.
echo Creating desktop shortcut...
powershell -Command ^
    "$ws = New-Object -ComObject WScript.Shell; ^
     $s = $ws.CreateShortcut([System.IO.Path]::Combine( ^
         [Environment]::GetFolderPath('Desktop'), 'DelftDashboard.lnk')); ^
     $s.TargetPath = '%INSTALL_DIR%\\delftdashboard.bat'; ^
     $s.WorkingDirectory = '%USERPROFILE%'; ^
     $s.Description = 'DelftDashboard'; ^
     $s.Save()"

echo.
echo ============================================
echo   Installation complete!
echo ============================================
echo.
echo Launch from the desktop shortcut or run:
echo   %INSTALL_DIR%\\delftdashboard.bat
echo.
pause
""")
    print(f"Installer created: {install_bat}")


if __name__ == "__main__":
    print(f"DelftDashboard Installer Builder v{VERSION}")
    print(f"Python: {PYTHON_VERSION}")
    print(f"Output: {OUTPUT_DIR}")

    create_clean_environment()
    pack_environment()
    create_installer_bat()

    print(f"\n=== Done! ===")
    print(f"Distribute these files:")
    print(f"  {os.path.join(OUTPUT_DIR, ARCHIVE_NAME)}")
    print(f"  {os.path.join(OUTPUT_DIR, 'install.bat')}")
