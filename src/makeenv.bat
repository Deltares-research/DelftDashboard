conda create -n delftdashboard python=3.10

conda activate delftdashboard

conda install -c conda-forge hydromt

pip install -e c:\work\checkouts\git\CoastalHazardsToolkit
pip install -e c:\work\checkouts\git\GUITools
pip install -e c:\work\checkouts\git\hydromt_sfincs

# To export this environment: 
conda env export -f environment.yml --no-builds
