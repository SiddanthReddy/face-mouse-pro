# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_all, collect_submodules

# Dynamically resolve root project directory relative to spec location
PROJECT_ROOT = os.path.abspath(SPECPATH)
datas = [
    (os.path.join(PROJECT_ROOT, 'config'), 'config'),
]

# Include assets if present
if os.path.exists(os.path.join(PROJECT_ROOT, 'assets')):
    datas.append((os.path.join(PROJECT_ROOT, 'assets'), 'assets'))

binaries = []
hiddenimports = []
hiddenimports += collect_submodules('face_mouse_core')

# Collect dynamic packages
for pkg in ['mediapipe', 'cv2', 'pyautogui', 'customtkinter', 'PIL']:
    tmp_ret = collect_all(pkg)
    datas += tmp_ret[0]
    binaries += tmp_ret[1]
    hiddenimports += tmp_ret[2]

a = Analysis(
    [os.path.join(PROJECT_ROOT, 'main.py')],
    pathex=[PROJECT_ROOT],
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
    name='FaceMousePro',
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
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FaceMousePro',
)
