@echo off
REM ============================================================================
REM  package_ddb.bat  -  package the built executable into a Windows installer
REM
REM  Compiles delftdashboard_nuitka.iss with Inno Setup 6. Run build_ddb.bat
REM  first; this script packages whatever is in dist_nuitka\start_ddb.dist.
REM
REM  Output: dist_innosetup\DelftDashboard_Setup_<version>.exe
REM  See compile.md for full documentation.
REM ============================================================================
setlocal

REM -- Locate ISCC (PATH first, then the default install locations) ------------
set "ISCC="
where iscc >nul 2>&1 && set "ISCC=iscc"
if not defined ISCC if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not defined ISCC (
  echo ERROR: Inno Setup 6 not found. Install it with:
  echo    winget install JRSoftware.InnoSetup
  pause & exit /b 1
)

pushd "%~dp0"

REM -- Make sure there is a build to package -----------------------------------
if not exist "dist_nuitka\start_ddb.dist\DelftDashboard.exe" (
  echo ERROR: no build found in dist_nuitka\start_ddb.dist\
  echo Run build_ddb.bat first.
  popd & pause & exit /b 1
)

"%ISCC%" delftdashboard_nuitka.iss
set "RC=%errorlevel%"
popd

if not "%RC%"=="0" (
  echo.
  echo Packaging FAILED with exit code %RC%.
  pause & exit /b %RC%
)

echo.
echo Installer written to: %~dp0dist_innosetup\
endlocal
