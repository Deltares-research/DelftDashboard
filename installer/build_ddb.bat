@echo off
REM ============================================================================
REM  build_ddb.bat  -  build the standalone DelftDashboard executable (Nuitka)
REM
REM  Wraps build_delftdashboard.py using the delftdashboard_dev conda
REM  environment. Any arguments are passed through, e.g.:
REM
REM      build_ddb.bat            release build (no console window)
REM      build_ddb.bat --debug    keep a console window (use while testing)
REM      build_ddb.bat --print    show the nuitka command, don't build
REM
REM  Output: dist_nuitka\start_ddb.dist\DelftDashboard.exe
REM  See compile.md for full documentation.
REM ============================================================================
setlocal

REM -- Config (edit if your environment lives elsewhere) ------------------------
set "PYTHON=%USERPROFILE%\miniforge3\envs\delftdashboard_dev\python.exe"
REM ----------------------------------------------------------------------------

if not exist "%PYTHON%" (
  echo ERROR: Python environment not found: %PYTHON%
  echo Edit the PYTHON variable at the top of this file.
  pause & exit /b 1
)

pushd "%~dp0"
"%PYTHON%" build_delftdashboard.py %*
set "RC=%errorlevel%"
popd

if not "%RC%"=="0" (
  echo.
  echo Build FAILED with exit code %RC%.
  pause & exit /b %RC%
)

echo.
echo Build finished: %~dp0dist_nuitka\start_ddb.dist\DelftDashboard.exe
endlocal
