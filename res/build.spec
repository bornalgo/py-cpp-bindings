# -*- mode: python ; coding: utf-8 -*-

import pathlib
block_cipher = None

a = Analysis(
    ['../src/main.py'],
    pathex=[],
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
    [('u', None, 'OPTION'), ('u', None, 'OPTION'), ('u', None, 'OPTION')],
    exclude_binaries=True,
    name='py-cpp-bindings',
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
	icon='icons/logo.ico'#icon=os.path.join(pathlib.Path(__file__).parent.resolve(), 'icons', 'logo.ico')
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='py-cpp-bindings',
)