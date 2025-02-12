@echo off

set ENVNAME=delftdashboard_git

REM Set you miniconda3 path here!
rem CONDAPATH=c:\work\miniconda3
rem set CONDA=conda

REM Set your miniforge3 path here!
set CONDAPATH=c:\work\miniforge3
set CONDA=mamba

call %CONDAPATH%\Scripts\activate.bat

call %CONDA% env remove -n %ENVNAME%
call %CONDA% create -n %ENVNAME% python=3.12 -y
call %CONDA% activate %ENVNAME%

REM Install a Python package using pip
pip install delftdashboard@git+https://github.com/deltares-research/delftdashboard.git
