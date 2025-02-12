@echo off

set ENVNAME=delftdashboard_git

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

call %CONDAPATH%\Scripts\activate.bat

call %CONDA% env remove -n %ENVNAME%
call %CONDA% create -n %ENVNAME% python=3.12 -y
call %CONDA% activate %ENVNAME%

REM Install a Python package using pip
pip install delftdashboard@git+https://github.com/deltares-research/delftdashboard.git
