@echo OFF
set CONDAPATH=c:\work\miniconda3
set ENVNAME=delftdashboard_git

call %CONDAPATH%\Scripts\activate.bat

REM Activate the desired Conda environment
call conda activate %ENVNAME%

call conda update --all

REM Install a Python package using pip
rem pip install delftdashboard@git+https://github.com/deltares-research/delftdashboard.git

REM Optional: Deactivate the environment after installation
conda deactivate
