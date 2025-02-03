# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
from PyInstaller.utils.hooks import copy_metadata

datas = [('C:\\Users\\blom_lk\\dev\\Workspace_ModelBuilder\\DelftDashboard\\src\\delftdashboard', 'delftdashboard'), ('C:\\Users\\blom_lk\\AppData\\Local\\miniforge3\\envs\\modelbuilders\\Lib\\site-packages\\branca\\templates\\*.js', 'branca/templates'), ('C:\\Users\\blom_lk\\AppData\\Local\\miniforge3\\envs\\modelbuilders\\Lib\\site-packages\\guitares\\pyqt5\\mapbox\\server', 'guitares/pyqt5/mapbox/server'), ('C:\\Users\\blom_lk\\dev\\Workspace_ModelBuilder\\DelftDashboard\\distribution\\mapbox_token.txt', 'delftdashboard/config'), ('C:\\Users\\blom_lk\\dev\\Workspace_ModelBuilder\\DelftDashboard\\distribution\\mapbox_token.js', 'guitares/pyqt5/mapbox/server')]
binaries = []
hiddenimports = []
datas += copy_metadata('delftdashboard')
datas += copy_metadata('guitares')
datas += copy_metadata('rasterio')
datas += copy_metadata('DELFT-fiat')
datas += copy_metadata('cht_cyclones')
datas += copy_metadata('geopandas')
datas += copy_metadata('pandas')
datas += copy_metadata('shapely')
datas += copy_metadata('flood_adapt')
datas += copy_metadata('pyogrio')
datas += copy_metadata('netCDF4')
datas += copy_metadata('scipy')
datas += copy_metadata('zarr')
datas += copy_metadata('rioxarray')
datas += copy_metadata('charset_normalizer')
datas += copy_metadata('fiona')
datas += copy_metadata('plotly')
datas += copy_metadata('tomli_w')
datas += copy_metadata('numpy')
datas += copy_metadata('numpy_financial')
datas += copy_metadata('pydantic')
datas += copy_metadata('pydantic_core')
datas += copy_metadata('annotated_types')
datas += copy_metadata('duckdb')
datas += copy_metadata('xugrid')
datas += copy_metadata('hydromt')
datas += copy_metadata('hydromt_fiat')
datas += copy_metadata('hydromt_sfincs')
tmp_ret = collect_all('delftdashboard')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('guitares')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('rasterio')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('fiat')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('cht_cyclones')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('geopandas')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pandas')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('shapely')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('flood_adapt')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pyogrio')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('netCDF4')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('scipy')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('zarr')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('rioxarray')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('charset_normalizer')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('fiona')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('plotly')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('tomli_w')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('numpy')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('numpy_financial')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pydantic')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pydantic_core')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('annotated_types')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('duckdb')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('xugrid')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('hydromt')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('hydromt_fiat')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('hydromt_sfincs')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['C:\\Users\\blom_lk\\dev\\Workspace_ModelBuilder\\DelftDashboard\\src\\delftdashboard\\delftdashboard_gui.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='FloodAdapt Modelbuilders',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\Users\\blom_lk\\dev\\Workspace_ModelBuilder\\DelftDashboard\\distribution\\icons\\deltares_logo.jpeg'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FloodAdapt Modelbuilders',
)
