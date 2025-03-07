@echo OFF
set CONDAPATH=c:\users\%USERNAME%\miniforge3
set ENVNAME=delftdashboard_dev

rem The following command activates the base environment.
if %ENVNAME%==base (set ENVPATH=%CONDAPATH%) else (set ENVPATH=%CONDAPATH%\envs\%ENVNAME%)

rem Activate the conda environment
rem Using call is required here, see: https://stackoverflow.com/questions/24678144/conda-environments-and-bat-files
call %CONDAPATH%\Scripts\activate.bat %ENVPATH%

rem Run a python script in that environment
echo import delftdashboard > _start_ddb.py
echo delftdashboard.start() >> _start_ddb.py
python _start_ddb.py

del _start_ddb.py
