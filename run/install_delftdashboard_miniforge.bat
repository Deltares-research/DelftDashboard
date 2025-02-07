@echo OFF
set CONDAPATH=c:\work\miniforge3
set ENVNAME=delftdashboard_git

call %CONDAPATH%\Scripts\activate.bat

REM Activate the desired Conda environment
call mamba env remove -n %ENVNAME%
call mamba create -n %ENVNAME% python=3.12 -y
call mamba activate %ENVNAME%

REM Install a Python package using pip
pip install delftdashboard@git+https://github.com/deltares-research/delftdashboard.git

REM Optional: Deactivate the environment after installation
mamba deactivate
