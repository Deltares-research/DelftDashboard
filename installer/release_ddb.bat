@echo off
REM ============================================================================
REM  release_ddb.bat  -  tag and publish a DelftDashboard release on GitHub
REM
REM  Wraps release_delftdashboard.py. The version is read from
REM  src\delftdashboard\__init__.py. It will:
REM    1. check installer exists, tag is new, gh CLI is logged in
REM    2. git tag v<version>  +  git push origin v<version>
REM    3. gh release create with the installer attached
REM
REM      release_ddb.bat              asks for confirmation first
REM      release_ddb.bat --dry-run    show the commands, run nothing
REM      release_ddb.bat --yes        no confirmation prompt
REM
REM  Run AFTER build_ddb.bat and package_ddb.bat. See compile.md.
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
"%PYTHON%" release_delftdashboard.py %*
set "RC=%errorlevel%"
popd

if not "%RC%"=="0" (
  echo.
  echo Release FAILED with exit code %RC%.
  pause & exit /b %RC%
)
endlocal
