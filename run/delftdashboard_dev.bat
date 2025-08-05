@echo OFF
set ENVNAME=delftdashboard_dev

:: Check if the directory C:\Users\%USERNAME%\miniconda3 exists
if exist "C:\Users\%USERNAME%\miniconda3" (
    set CONDAPATH=c:\users\%USERNAME%\miniconda3
	set CONDA=conda
) else (
    :: Check if the directory C:\Users\%USERNAME%\miniforge3 exists
    if exist "C:\Users\%USERNAME%\miniforge3" (
        set CONDAPATH=c:\users\%USERNAME%\miniforge3
		set CONDA=mamba
    ) else (
        :: Neither exist. Stop.
        echo Miniconda nor Miniforge was found. Please install either miniconda or miniforge.
		echo If you already installed one of them, please add the path to this script!
		echo e.g. for miniconda:
		echo CONDAPATH=d:\work\miniconda3
		echo set CONDA=conda
		echo or for miniforge:
		echo CONDAPATH=d:\work\miniforge3
		echo set CONDA=mamba
        pause
        exit
    )
)

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
