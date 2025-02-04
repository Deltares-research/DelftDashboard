@echo OFF
set CONDAPATH=c:\work\miniconda3
set ENVNAME=delftdashboard_git

call %CONDAPATH%\Scripts\activate.bat

REM Activate the desired Conda environment
call conda create -n %ENVNAME% python=3.11 -y
call conda activate %ENVNAME%

REM Install a Python package using pip
pip install delftdashboard@git+https://github.com/deltares-research/delftdashboard.git

REM Optional: Deactivate the environment after installation
conda deactivate
