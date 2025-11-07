# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['launch_all_modules.py'],
    pathex=[],
    binaries=[],
    datas=[('CTC_Office', 'CTC_Office'), ('Wayside_Controller', 'Wayside_Controller'), ('Track_Model', 'Track_Model'), ('Train Model', 'Train Model'), ('train_controller_sw', 'train_controller_sw')],
    hiddenimports=[],
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
    name='launch_all_modules',
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
    name='launch_all_modules',
)
