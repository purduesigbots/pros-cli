# -*- mode: python ; coding: utf-8 -*-

# Write version info into _constants.py resource file

from distutils.util import get_platform


with open('_constants.py', 'w') as f:
    f.write(f'{key}=\'{value}\'' for key, value in {
            'CLI_VERSION': open('version').read().strip(),
            'FROZEN_PLATFORM_V1': 'Windows64' if get_platform() == 'win-amd64' else 'Windows86'
            }.items())

block_cipher = None


a = Analysis(
    ['pros/cli/main.py'],
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
    [],
    exclude_binaries=True,
    name='pros',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='universal2',
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
    name='pros',
)
