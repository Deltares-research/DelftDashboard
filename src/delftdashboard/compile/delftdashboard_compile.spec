# -*- mode: python ; coding: utf-8 -*-

import glob
import os
import pkgutil
import rasterio

block_cipher = None

hidden_imports = []

path = r"c:\work\checkouts\git\DelftDashboard\src\delftdashboard" 

models = ["sfincs", "hurrywave"]
toolboxes = ["modelmaker_sfincs", "modelmaker_hurrywave", "drawing", "tropical_cyclone"]

# Models
for model in models:
    files = glob.glob(os.path.join(path, "models", model, "*.py"))
    for file in files:
        file = os.path.basename(file)
        if file[0] == "_":
            continue
        file = file[:-3]            
        module = "delftdashboard.models." + model + "." + file
        hidden_imports.append(module)

# Toolboxes
for toolbox in toolboxes:
    files = glob.glob(os.path.join(path, "toolboxes", toolbox, "*.py"))
    for file in files:
        file = os.path.basename(file)
        if file[0] == "_":
            continue
        file = file[:-3]            
        module = "delftdashboard.toolboxes." + toolbox + "." + file
        hidden_imports.append(module)

# Menu
files = glob.glob(os.path.join(path, "menu", "*.py"))
for file in files:
    file = os.path.basename(file)
    if file[0] == "_":
        continue
    file = file[:-3]            
    module = "delftdashboard.menu." + file
    hidden_imports.append(module)

# list all rasterio and fiona submodules, to include them in the package
for package in pkgutil.iter_modules(rasterio.__path__, prefix="rasterio."):
    hidden_imports.append(package.name)

a = Analysis(
    ['delftdashboard_gui.py'],
    pathex=[],
    binaries=[],
    datas=[],
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
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='delftdashboard',
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
    name='delftdashboard',
)
