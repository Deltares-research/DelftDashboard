@ECHO OFF

pushd %~dp0

REM Command file for Sphinx documentation.
REM
REM Finds a working sphinx in this order, VERIFYING each candidate actually
REM runs before using it:
REM   1. the SPHINXBUILD environment variable, if set and working
REM   2. sphinx-build from PATH (e.g. delftdashboard_dev activated)
REM   3. the delftdashboard_dev conda environment directly
REM so it also works from a plain console:  make.bat html

set "DEVPY=%USERPROFILE%\miniforge3\envs\delftdashboard_dev\python.exe"

if "%SPHINXBUILD%" == "" goto try_path
%SPHINXBUILD% --version >NUL 2>NUL
if %errorlevel% == 0 goto have_sphinx
echo WARNING: SPHINXBUILD is set to "%SPHINXBUILD%" but that does not run; ignoring it.

:try_path
sphinx-build --version >NUL 2>NUL
if %errorlevel% == 0 (
	set SPHINXBUILD=sphinx-build
	goto have_sphinx
)

if exist "%DEVPY%" (
	"%DEVPY%" -m sphinx --version >NUL 2>NUL
	if not errorlevel 1 (
		set SPHINXBUILD="%DEVPY%" -m sphinx
		goto have_sphinx
	)
)

echo.
echo.No working Sphinx found. Looked for: the SPHINXBUILD environment
echo.variable, sphinx-build on PATH, and the delftdashboard_dev conda
echo.environment. Install Sphinx in delftdashboard_dev with:
echo.
echo.    pip install sphinx pydata-sphinx-theme
echo.
popd
exit /b 1

:have_sphinx
set SOURCEDIR=source
set BUILDDIR=build

if "%1" == "" goto help

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%

:end
popd
