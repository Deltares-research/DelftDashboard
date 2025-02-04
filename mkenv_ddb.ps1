# To create the cosmos environment, do the following:
#
# open conda powershell
# cd c:\work\cosmos\run_folder
# ./mkenv.ps1

conda create -n delftdashboard python=3.10
conda activate delftdashboard
pip install -e c:\work\checkouts\git\guitares
pip install -e c:\work\checkouts\git\cht_bathymetry
pip install -e c:\work\checkouts\git\cht_cyclones
pip install -e c:\work\checkouts\git\cht_sfincs
pip install -e c:\work\checkouts\git\cht_delft3dfm
pip install -e c:\work\checkouts\git\cht_utils
pip install -e c:\work\checkouts\git\cht_meteo
pip install -e c:\work\checkouts\git\cht_nesting
pip install -e c:\work\checkouts\git\cht_hurrywave
pip install -e c:\work\checkouts\git\cht_tide
pip install -e c:\work\checkouts\git\cht_tsunami
pip install -e c:\work\checkouts\git\cht_tiling
pip install -e c:\work\checkouts\git\cht_physics
pip install -e c:\work\checkouts\git\delftdashboard
pip install boto3
