@echo off
rem ===========================================================================
rem  Create the DelftDashboard build environment and install the
rem  DelftDashboard / cht / hydromt repos as editable packages.
rem
rem  Works from a plain Command Prompt: no "conda init" or Miniforge Prompt
rem  needed - Miniforge is located and activated by this script.
rem
rem  Prerequisites: Miniforge (winget install CondaForge.Miniforge3) and the
rem  repos cloned into %GITDIR% (default C:\git) at the branches in repos.txt.
rem
rem  Usage:   setup_env.bat
rem  Options: set GITDIR=D:\git        (where the repos are cloned)
rem           set ENVNAME=ddb_build    (environment name)
rem ===========================================================================
setlocal EnableDelayedExpansion

if "%GITDIR%"=="" set "GITDIR=C:\git"
if "%ENVNAME%"=="" set "ENVNAME=delftdashboard_dev"
set "HERE=%~dp0"

rem -- Locate Miniforge ------------------------------------------------------
set "CONDAROOT="
for %%d in ("%USERPROFILE%\miniforge3" "%LOCALAPPDATA%\miniforge3" "%ProgramData%\miniforge3" "%USERPROFILE%\mambaforge" "%USERPROFILE%\miniconda3") do (
    if not defined CONDAROOT if exist "%%~d\Scripts\activate.bat" set "CONDAROOT=%%~d"
)
if not defined CONDAROOT (
    echo ERROR: Miniforge not found. Install it with:
    echo    winget install CondaForge.Miniforge3
    exit /b 1
)
echo Using conda at %CONDAROOT%
call "%CONDAROOT%\Scripts\activate.bat" "%CONDAROOT%"
if errorlevel 1 ( echo ERROR: could not activate conda & exit /b 1 )

rem -- Create the environment (only if it does not exist yet) -----------------
if exist "%CONDAROOT%\envs\%ENVNAME%\python.exe" (
    echo Environment %ENVNAME% already exists - skipping creation.
) else (
    echo Creating environment %ENVNAME% from environment.yml - this takes a while ...
    call conda env create -f "%HERE%environment.yml" -n %ENVNAME%
    if errorlevel 1 ( echo ERROR: environment creation failed & exit /b 1 )
)
call conda activate %ENVNAME%
if errorlevel 1 ( echo ERROR: could not activate %ENVNAME% & exit /b 1 )

rem -- Editable installs ---------------------------------------------------
rem --no-deps keeps the exact versions pinned in environment.yml (otherwise pip
rem would re-resolve dependencies, e.g. pull cht packages from git main).
rem Folder names as cloned next to DelftDashboard (note hydromt_hurrywave).
set "FAILED="
for %%r in (DelftDashboard cosmos guitares cht_beware cht_cyclones cht_delft3dfm cht_meteo cht_nesting cht_observations cht_physics cht_tide cht_tiling cht_tsunami cht_utils cht_xbeach hydromt_sfincs hydromt_hurrywave) do (
    if exist "%GITDIR%\%%r\" (
        echo Installing %%r ...
        python -m pip install -e "%GITDIR%\%%r" --no-deps -q
        if errorlevel 1 set "FAILED=!FAILED! %%r"
    ) else (
        echo MISSING checkout: %GITDIR%\%%r
        set "FAILED=!FAILED! %%r[missing]"
    )
)

rem -- Check ----------------------------------------------------------------
echo.
python -c "import delftdashboard, nuitka; print('delftdashboard', delftdashboard.__version__, '| nuitka OK')"
if errorlevel 1 set "FAILED=!FAILED! import-check"
if exist "%CONDA_PREFIX%\Library\bin\ffmpeg.exe" (
    echo ffmpeg OK - MP4 export will be bundled
) else (
    echo WARNING: ffmpeg missing - MP4 animation export will fall back to GIF
)

echo.
if defined FAILED (
    echo FAILED:!FAILED!
    exit /b 1
)
echo Environment %ENVNAME% is ready. Next:
echo    conda activate %ENVNAME%
echo    cd %GITDIR%\DelftDashboard\installer
echo    python build_delftdashboard.py --debug
endlocal
