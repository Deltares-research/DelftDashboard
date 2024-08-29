@echo OFF
set CONDAPATH=c:\work\miniconda3
set DDBPATH=c:\work\checkouts\git\DelftDashboard\src\delftdashboard
set ENVNAME=ddbtest

rem The following command activates the base environment.
rem call C:\ProgramData\Miniconda3\Scripts\activate.bat C:\ProgramData\Miniconda3
if %ENVNAME%==base (set ENVPATH=%CONDAPATH%) else (set ENVPATH=%CONDAPATH%\envs\%ENVNAME%)

rem Activate the conda environment
rem Using call is required here, see: https://stackoverflow.com/questions/24678144/conda-environments-and-bat-files
call %CONDAPATH%\Scripts\activate.bat %ENVPATH%

rem Run a python script in that environment
echo import delftdashboard > _start_ddb.py
echo delftdashboard.start() >> _start_ddb.py
python start_delftdashboard.py
rem python %DDBPATH%\start_delftdashboard.py

rem Deactivate the environment
call conda deactivate
del _start_ddb.py

rem If conda is directly available from the command line then the following code works.
rem call activate someenv
rem python script.py
rem conda deactivate

rem One could also use the conda run command
rem conda run -n someenv python script.py