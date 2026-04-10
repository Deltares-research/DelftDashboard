@echo off
echo Installing DelftDashboard packages from GitHub...

call "%~dp0Scripts\activate.bat"

pip install --no-deps git+https://github.com/deltares-research/cht_utils.git
pip install --no-deps git+https://github.com/deltares-research/cht_tide.git
pip install --no-deps git+https://github.com/deltares-research/cht_observations.git
pip install --no-deps git+https://github.com/deltares-research/cht_meteo.git
pip install --no-deps git+https://github.com/deltares-research/cht_cyclones.git
pip install --no-deps git+https://github.com/deltares-research/cht_nesting.git
pip install --no-deps git+https://github.com/deltares-research/cht_tiling.git
pip install --no-deps git+https://github.com/deltares-research/cht_sfincs.git
pip install --no-deps git+https://github.com/deltares-research/cht_hurrywave.git
pip install --no-deps git+https://github.com/deltares-research/cht_delft3dfm.git
pip install --no-deps git+https://github.com/deltares-research/cht_xbeach.git
pip install --no-deps git+https://github.com/deltares-research/cht_beware.git
pip install --no-deps git+https://github.com/deltares-research/cht_tsunami.git
pip install --no-deps git+https://github.com/deltares-research/cht_physics.git
pip install --no-deps git+https://github.com/Deltares-research/hydromt_sfincs.git
pip install --no-deps git+https://github.com/Deltares-research/hydromt_hurrywave.git
pip install --no-deps git+https://github.com/Deltares-research/Guitares.git
pip install --no-deps git+https://github.com/Deltares-research/DelftDashboard.git
pip install --no-deps git+https://github.com/Deltares-research/hydromt.git

echo Done!
