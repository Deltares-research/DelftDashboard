# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('../src/delftdashboard/config', 'delftdashboard/config'), ('../src/delftdashboard/server', 'delftdashboard/server')]
binaries = []
hiddenimports = ['delftdashboard.models.sfincs_hmt.sfincs_hmt', 'delftdashboard.models.sfincs_cht.sfincs_cht', 'delftdashboard.models.hurrywave_hmt.hurrywave_hmt', 'delftdashboard.models.hurrywave.hurrywave', 'delftdashboard.models.delft3dfm.delft3dfm', 'delftdashboard.models.sfincs_hmt.domain', 'delftdashboard.models.sfincs_hmt.timeframe', 'delftdashboard.models.sfincs_hmt.numerics', 'delftdashboard.models.sfincs_hmt.output', 'delftdashboard.models.sfincs_hmt.meteo', 'delftdashboard.models.sfincs_hmt.physics', 'delftdashboard.models.sfincs_hmt.physics_constants', 'delftdashboard.models.sfincs_hmt.physics_meteo', 'delftdashboard.models.sfincs_hmt.physics_roughness', 'delftdashboard.models.sfincs_hmt.physics_advection', 'delftdashboard.models.sfincs_hmt.physics_viscosity', 'delftdashboard.models.sfincs_hmt.boundary_conditions', 'delftdashboard.models.sfincs_hmt.discharge_points', 'delftdashboard.models.sfincs_hmt.observation_points', 'delftdashboard.models.sfincs_hmt.observation_points_observation_points', 'delftdashboard.models.sfincs_hmt.observation_points_cross_sections', 'delftdashboard.models.sfincs_hmt.structures_thin_dams', 'delftdashboard.models.sfincs_hmt.structures_weirs', 'delftdashboard.models.sfincs_hmt.structures_drainage_structures', 'delftdashboard.models.sfincs_hmt.waves', 'delftdashboard.models.sfincs_hmt.waves_snapwave', 'delftdashboard.models.sfincs_hmt.waves_boundary_conditions', 'delftdashboard.models.sfincs_hmt.waves_wave_makers', 'delftdashboard.models.hurrywave_hmt.domain', 'delftdashboard.models.hurrywave_hmt.timeframe', 'delftdashboard.models.hurrywave_hmt.numerics', 'delftdashboard.models.hurrywave_hmt.output', 'delftdashboard.models.hurrywave_hmt.meteo', 'delftdashboard.models.hurrywave_hmt.physics_constants', 'delftdashboard.models.hurrywave_hmt.physics_meteo', 'delftdashboard.models.hurrywave_hmt.physics_roughness', 'delftdashboard.models.hurrywave_hmt.boundary_conditions', 'delftdashboard.models.hurrywave_hmt.observation_points_regular', 'delftdashboard.models.hurrywave_hmt.observation_points_spectra', 'delftdashboard.models.delft3dfm.domain', 'delftdashboard.models.delft3dfm.generic', 'delftdashboard.models.delft3dfm.timeframe', 'delftdashboard.models.delft3dfm.meteo', 'delftdashboard.models.delft3dfm.boundary_conditions', 'delftdashboard.models.delft3dfm.observation_points_regular', 'delftdashboard.models.delft3dfm.observation_points_crs', 'delftdashboard.models.delft3dfm.observation_points_spectra', 'delftdashboard.models.delft3dfm.structures_thin_dams', 'delftdashboard.toolboxes.modelmaker_sfincs_hmt.modelmaker_sfincs_hmt', 'delftdashboard.toolboxes.modelmaker_sfincs_cht.modelmaker_sfincs_cht', 'delftdashboard.toolboxes.modelmaker_hurrywave_hmt.modelmaker_hurrywave_hmt', 'delftdashboard.toolboxes.modelmaker_hurrywave.modelmaker_hurrywave', 'delftdashboard.toolboxes.modelmaker_delft3dfm.modelmaker_delft3dfm', 'delftdashboard.toolboxes.bathymetry.bathymetry', 'delftdashboard.toolboxes.drawing.drawing', 'delftdashboard.toolboxes.flood_map.flood_map', 'delftdashboard.toolboxes.meteo.meteo', 'delftdashboard.toolboxes.nesting.nesting', 'delftdashboard.toolboxes.observation_stations.observation_stations', 'delftdashboard.toolboxes.tide_stations.tide_stations', 'delftdashboard.toolboxes.tiling.tiling', 'delftdashboard.toolboxes.tropical_cyclone.tropical_cyclone', 'delftdashboard.toolboxes.watersheds.watersheds', 'delftdashboard.toolboxes.model_database.model_database', 'delftdashboard.toolboxes.modelmaker_sfincs_hmt.domain', 'delftdashboard.toolboxes.modelmaker_sfincs_hmt.bathymetry', 'delftdashboard.toolboxes.modelmaker_sfincs_hmt.quadtree', 'delftdashboard.toolboxes.modelmaker_sfincs_hmt.roughness', 'delftdashboard.toolboxes.modelmaker_sfincs_hmt.subgrid', 'delftdashboard.toolboxes.modelmaker_sfincs_hmt.mask_active_cells', 'delftdashboard.toolboxes.modelmaker_sfincs_hmt.mask_active_cells_snapwave', 'delftdashboard.toolboxes.modelmaker_sfincs_hmt.mask_boundary_cells', 'delftdashboard.toolboxes.modelmaker_sfincs_hmt.mask_boundary_cells_snapwave', 'delftdashboard.toolboxes.modelmaker_hurrywave_hmt.domain', 'delftdashboard.toolboxes.modelmaker_hurrywave_hmt.quadtree', 'delftdashboard.toolboxes.modelmaker_hurrywave_hmt.bathymetry', 'delftdashboard.toolboxes.modelmaker_hurrywave_hmt.mask_active_cells', 'delftdashboard.toolboxes.modelmaker_hurrywave_hmt.mask_boundary_cells', 'delftdashboard.toolboxes.modelmaker_hurrywave_hmt.waveblocking', 'delftdashboard.toolboxes.modelmaker_hurrywave_hmt.boundary_points', 'delftdashboard.toolboxes.modelmaker_delft3dfm.domain', 'delftdashboard.toolboxes.modelmaker_delft3dfm.bathymetry', 'delftdashboard.toolboxes.modelmaker_delft3dfm.boundary', 'delftdashboard.toolboxes.modelmaker_delft3dfm.refinement', 'delftdashboard.toolboxes.modelmaker_delft3dfm.exclude', 'delftdashboard.toolboxes.modelmaker_delft3dfm.mask_active_cells', 'delftdashboard.toolboxes.modelmaker_delft3dfm.roughness', 'delftdashboard.toolboxes.modelmaker_delft3dfm.subgrid', 'delftdashboard.toolboxes.flood_map.topobathy', 'delftdashboard.toolboxes.flood_map.indices', 'delftdashboard.toolboxes.flood_map.prepare', 'delftdashboard.toolboxes.flood_map.view', 'delftdashboard.toolboxes.flood_map.export', 'delftdashboard.toolboxes.drawing.polyline', 'delftdashboard.toolboxes.drawing.polygon', 'delftdashboard.toolboxes.nesting.nest1', 'delftdashboard.toolboxes.nesting.nest2', 'delftdashboard.toolboxes.meteo.datasets', 'delftdashboard.toolboxes.meteo.download', 'delftdashboard.toolboxes.meteo.model_forcing', 'delftdashboard.toolboxes.tropical_cyclone.import', 'delftdashboard.toolboxes.tropical_cyclone.draw', 'delftdashboard.toolboxes.tropical_cyclone.modify', 'delftdashboard.toolboxes.tropical_cyclone.table', 'delftdashboard.toolboxes.tropical_cyclone.ensemble', 'delftdashboard.toolboxes.tropical_cyclone.wind_field', 'delftdashboard.toolboxes.tiling.topobathy_tiles', 'delftdashboard.toolboxes.tiling.index_tiles', 'delftdashboard.toolboxes.model_database.view_database', 'delftdashboard.toolboxes.model_database.add_model', 'delftdashboard.toolboxes.model_database.generate_database', 'delftdashboard.menu.file', 'delftdashboard.menu.model', 'delftdashboard.menu.toolbox', 'delftdashboard.menu.topography', 'delftdashboard.menu.coordinate_system', 'delftdashboard.menu.view', 'delftdashboard.menu.help', 'delftdashboard.operations.bathy_topo_selector', 'delftdashboard.operations.topography', 'hydromt_sfincs', 'hydromt_sfincs.sfincs', 'hydromt_hurrywave', 'hydromt_hurrywave.hurrywave', 'cht_sfincs', 'cht_hurrywave', 'cht_delft3dfm', 'cht_xbeach', 'cht_beware', 'cht_nesting', 'cht_tiling', 'cht_meteo', 'cht_tide', 'cht_cyclones', 'cht_utils', 'cht_observations', 'cht_tsunami', 'cht_physics', 'rasterio', 'rioxarray', 'fiona', 'pyogrio', 'pyproj', 'xugrid', 'datashader', 'scipy.interpolate']
tmp_ret = collect_all('hydromt')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('hydromt_sfincs')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('hydromt_hurrywave')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('rasterio')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('fiona')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pyproj')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('xugrid')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('PySide6.QtWebEngineCore')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('PySide6.QtWebChannel')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('PySide6.QtWebEngineWidgets')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['..\\src\\delftdashboard\\start_ddb.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5', 'tkinter', 'test', 'unittest', 'numba', 'llvmlite', 'sklearn', 'scikit-learn', 'eccodes', 'black', 'pytest', 'IPython', 'jupyter', 'notebook'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DelftDashboard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DelftDashboard',
)
