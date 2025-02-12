rem Script to create the editable delftdashboard environment
rem The delftdashboard_dev environment only needs to be created and used if you are interested in editing the source code!

rem CHANGE GITDIR to point to you local repos folder !!!
set GITDIR=c:\work\checkouts\git
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

call %CONDAPATH%\Scripts\activate.bat

call %CONDA% env remove -n %ENVNAME%
call %CONDA% create -n %ENVNAME% python=3.12
call %CONDA% activate %ENVNAME%

pip install -e %GITDIR%\delftdashboard
pip install -e %GITDIR%\guitares
pip install -e %GITDIR%\cht_bathymetry
pip install -e %GITDIR%\cht_beware
pip install -e %GITDIR%\cht_cyclones
pip install -e %GITDIR%\cht_delft3dfm
pip install -e %GITDIR%\cht_hurrywave
pip install -e %GITDIR%\cht_meteo
pip install -e %GITDIR%\cht_nesting
pip install -e %GITDIR%\cht_observations
pip install -e %GITDIR%\cht_physics
pip install -e %GITDIR%\cht_sfincs
pip install -e %GITDIR%\cht_tide
pip install -e %GITDIR%\cht_tiling
pip install -e %GITDIR%\cht_tsunami
pip install -e %GITDIR%\cht_utils
pip install -e %GITDIR%\cht_xbeach
pip install -e %GITDIR%\cosmos
