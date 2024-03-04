# -*- mode: python ; coding: utf-8 -*-

import glob
import os
import pkgutil
import sys

sys.setrecursionlimit(sys.getrecursionlimit() * 10)
block_cipher = None
os.environ['GDAL_DATA'] = 'C:/OSGeo4W/apps/gdal/share/gdal'

# HOW TO MAKE EXECUTABLE:
# pyinstaller --clean -y src/delftdashboard/delftdashboard_compile.spec 
# copy hydromt, numpy, xrspatial, xarray, xarray-spatial, xugrid data + meta-data to _internals

project_name = 'FloodAdaptModelbuilder'

project_root = os.fspath(r"C:/Users/blom_lk/dev/Workspace_ModelBuilder/DelftDashboard")
src_path = os.path.join(project_root, "src", "delftdashboard")

#### HIDDEN IMPORTS #####
hidden_imports = []

models = ["sfincs_hmt", "fiat"]
toolboxes = ["modelmaker_sfincs_hmt", "modelmaker_fiat"]
misc = ["cyclone_track_selector", "select_utm_zone", "select_watershed"]

# Models
for model in models:
    files = glob.glob(os.path.join(src_path, "models", model, "*.py"))
    for file in files:
        file = os.path.basename(file)
        if file[0] == "_":
            continue
        file = file[:-3]            
        module = "delftdashboard.models." + model + "." + file
        hidden_imports.append(module)

# Toolboxes
for toolbox in toolboxes:
    files = glob.glob(os.path.join(src_path, "toolboxes", toolbox, "*.py"))
    for file in files:
        file = os.path.basename(file)
        if file[0] == "_":
            continue
        file = file[:-3]            
        module = "delftdashboard.toolboxes." + toolbox + "." + file
        hidden_imports.append(module)

# Misc
for misc_module in misc:
    files = glob.glob(os.path.join(src_path, "misc", misc_module, "*.py"))
    for file in files:
        file = os.path.basename(file)
        if file[0] == "_":
            continue
        file = file[:-3]            
        module = "delftdashboard.misc." + misc_module + "." + file
        hidden_imports.append(module)

# Menu
files = glob.glob(os.path.join(src_path, "menu", "*.py"))
for file in files:
    file = os.path.basename(file)
    if file[0] == "_":
        continue
    file = file[:-3]
    module = "delftdashboard.menu." + file
    hidden_imports.append(module)

import numpy
for package in pkgutil.iter_modules(numpy.__path__, prefix="numpy."):
    hidden_imports.append(package.name)

import xugrid
for package in pkgutil.iter_modules(xugrid.__path__, prefix="xugrid."):
    hidden_imports.append(package.name)

import rasterio
for package in pkgutil.iter_modules(rasterio.__path__, prefix="rasterio."):
    hidden_imports.append(package.name)

import guitares 
for package in pkgutil.iter_modules(guitares.__path__, prefix="guitares."):
    hidden_imports.append('guitares')

import pyogrio
for package in pkgutil.iter_modules(pyogrio.__path__, prefix="pyogrio."):
    hidden_imports.append('pyogrio')
hidden_imports.append('pyogrio._geometry')


#### DATA FILES #####
datas = []
# Add non-python files
env_root_path = os.path.normpath(os.path.dirname(sys.executable))
site_packages_path = os.path.normpath(os.path.join(env_root_path, os.fspath('Lib/site-packages')))

gdal_bin_path = os.path.join(env_root_path, "Library", "bin")

datas.append( (os.path.normpath( os.path.join(site_packages_path, "branca/templates/*.js")), "branca/templates") )
datas.append( (os.path.normpath( os.path.join(site_packages_path, "guitares/pyqt5/mapbox/server")), "guitares/pyqt5/mapbox/server") )

datas.append((src_path, 'delftdashboard'))

a = Analysis(
    [os.path.join(src_path, "delftdashboard_gui.py")],
    pathex=[src_path],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

def match_any_substring(substrings: list, in_what: str) -> bool:
    for s in substrings:
        if s in in_what:
            return True
    return False

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=project_name,
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
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=project_name,
)

# tocopy = [
#    hydromt-0.9.4.dist-info/,
#    xarray_spatial-0.3.7.dist-info/,
#    numpy-1.26.4.dist-info/,
#    xrspatial/,
#    xarray/,
#    xugrid/,
#    xarray-2024.2.0.dist-info/,
#    xugrid-0.9.0.dist-info/
# ]
# TODO for folder in to_copy: paste into _internals
# TODO set GDAL_DATA env var in ddb somewhere?