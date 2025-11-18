# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files
import sys

# --- Read VERSION at build time ---
version_file = Path("VERSION")
if version_file.exists():
    with version_file.open() as f:
        app_version = f.read().strip()
else:
    app_version = "0.0.0"

# --- Analysis ---
a = Analysis(
    ['src/hazbin_tracker/main.py'],
    pathex=[],
    binaries=[],
    datas=[('VERSION', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

# --- Python modules ---
pyz = PYZ(a.pure)

# --- Executable ---
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='HazbinTracker',
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

# --- Collect files ---
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='HazbinTracker',
)

# --- Bundle for macOS ---
app = BUNDLE(
    coll,
    name='HazbinTracker.app',
    icon='resources/icons/HazbinTracker.icns',
    bundle_identifier=None,
    info_plist={
        "CFBundleShortVersionString": app_version,  # shown in Finder
        "CFBundleVersion": app_version,             # internal build number
        "LSUIElement": True,                        # hide dock icon for tray app
    },
)
