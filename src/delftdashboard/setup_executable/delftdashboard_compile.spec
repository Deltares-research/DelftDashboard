# -*- mode: python ; coding: utf-8 -*-

import os
import pkgutil
import sys
import shutil
import importlib
from pathlib import Path

#### SETTINGS & VARIABLES #####
sys.setrecursionlimit(sys.getrecursionlimit() * 10)
block_cipher = None
# os.environ['GDAL_DATA'] = 'C:/OSGeo4W/apps/gdal/share/gdal'

if os.environ.get("PROJECT_ROOT") is None:
    print("PROJECT_ROOT environment variable not set. Please set before running building the executable")
    exit()

if os.environ.get("PROJECT_NAME") is None:
    print("PROJECT_NAME environment variable not set. Please set before running building the executable")
    exit()

if os.environ.get("EXE_DIR") is None:
    print("EXE_DIR environment variable not set. Please set before running building the executable")
    exit()

project_root = Path(os.environ.get("PROJECT_ROOT"))
project_name = os.environ.get("PROJECT_NAME")
exe_dir = os.environ.get("EXE_DIR")

src_path = Path(project_root, "src", "delftdashboard")

#### HIDDEN IMPORTS #####
hidden_imports = []

def import_hidden_ddb_module(hidden_imports, module_path, module_parents):
    for node in os.listdir(module_path):
        full_path = Path(module_path, node)
        basename = os.path.basename(node)

        if os.path.isdir(full_path) and (not basename.startswith("_")):
            import_hidden_ddb_module(hidden_imports, full_path, module_parents=f"{module_parents}.{basename}")
        
        else:
            if (not basename.endswith(".py")) or (basename.startswith("__")):
                continue
            file = basename[:-3]
            module = f"{module_parents}.{file}"
            hidden_imports.append(module)

def import_hidden_package(package_name):
    full_package = importlib.import_module(package_name)
    for package in pkgutil.iter_modules(full_package.__path__, prefix=f"{full_package.__name__}."):
        hidden_imports.append(package.name)

# Import hidden modules
internal_dir = Path(exe_dir, '_internal')
ddb_modules = ["layers", "menu", "misc", "models", "operations", "toolboxes"]

for module in ddb_modules:
    module_path = Path(src_path, module)
    import_hidden_ddb_module(hidden_imports, module_path, module_parents=f"delftdashboard.{module}")

import_hidden_package('numpy')
import_hidden_package('xugrid')
import_hidden_package('rasterio')
import_hidden_package('guitares')
import_hidden_package('pyogrio')
hidden_imports.append('pyogrio._geometry')


#### DATA FILES #####
datas = []

# Add non-python files
env_root_path = os.path.normpath(os.path.dirname(sys.executable))
site_packages_path = os.path.normpath(Path(env_root_path, os.fspath('Lib/site-packages')))

datas.append( (os.path.normpath( Path(site_packages_path, "branca/templates/*.js")), "branca/templates") )
datas.append( (os.path.normpath( Path(site_packages_path, "guitares/pyqt5/mapbox/server")), "guitares/pyqt5/mapbox/server") )


#### PYINSTALLER #####

a = Analysis(
    [Path(src_path, "delftdashboard_gui.py")],
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