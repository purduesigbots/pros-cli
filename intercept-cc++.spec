# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


intercept-cc_a = Analysis(
    ['intercept-cc.py'],
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
intercept-cc_pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

intercept-cc_exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='intercept-cc++',
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
    name='intercept-cc++',
)
