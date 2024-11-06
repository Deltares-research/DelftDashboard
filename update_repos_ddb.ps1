# Checkout the following git repositories in e.g. c:\work\checkouts\git_cosmos_tsunami (or another folder)
# Open conda powershell
# cd c:\work\cosmos\run_folder
# ./pull_repos.ps1

$repos_path = "c:\git"

cd $repos_path\cht_bathymetry
git pull 
cd $repos_path\cht_cyclones
git pull 
cd $repos_path\cht_sfincs
git pull 
cd $repos_path\cht_utils
git pull 
cd $repos_path\cht_meteo
git pull 
cd $repos_path\cht_nesting
git pull 
cd $repos_path\cht_hurrywave
git pull 
cd $repos_path\cht_delft3dfm
git pull 
cd $repos_path\cht_tide
git pull 
cd $repos_path\cht_tsunami
git pull 
cd $repos_path\cht_tiling
git pull 
cd $repos_path\cht_physics
git pull 
cd $repos_path\delftdashboard
git pull 
cd $repos_path\cosmos
git pull 
