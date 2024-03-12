# -*- mode: python ; coding: utf-8 -*-

import os
import pkgutil
import sys
import shutil
import importlib
from pathlib import Path

sys.setrecursionlimit(sys.getrecursionlimit() * 10)
block_cipher = None

if os.environ.get("SRC_PATH") is None:
    print("SRC_PATH environment variable not set. Please set before running building the executable")
    exit()

a = Analysis(
    [Path(os.environ.get("SRC_PATH"), "delftdashboard_gui.py")],
    pathex=[os.environ.get("SRC_PATH")],
    binaries=[],
    datas=[],
    hiddenimports=[],
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
)