rem  script to install delftdashboard and other packages as editable (rather than from PyPi)
rem  open conda powershell prompt
rem  cd to location of this script
rem  call this script with ./make_env.bat

set repos_path=c:\git

call conda create -n delftdashboard_nrl python=3.10

call conda activate delftdashboard_nrl

pause

call pip install -e %repos_path%\delftdashboard
call pip install -e %repos_path%\guitares
call pip install -e %repos_path%\cht_utils
call pip install -e %repos_path%\cht_sfincs
call pip install -e %repos_path%\cht_hurrywave
call pip install -e %repos_path%\cht_bathymetry
call pip install -e %repos_path%\cht_observations
call pip install -e %repos_path%\cht_cyclones
