rem Script to create the editable delftdashboard environment
rem The delftdashboard_dev environment only needs to be created and used if you are interested in editing the source code!

rem CHANGE GITDIR to point to you local repos folder !!!
set GITDIR=c:\work\checkouts\git
set ENVNAME=delftdashboard_dev

call mamba env remove -n delftdashboard_dev
call mamba create -n delftdashboard_dev python=3.12
call mamba activate delftdashboard_dev

rem We first install delftdashboard, which also install some cht packages from PyPi. Then we override with editable packages.

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
rem pip install -e %GITDIR%\hydromt
rem pip install -e %GITDIR%\hydromt_sfincs

