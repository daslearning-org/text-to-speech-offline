# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=collect_data_files('kivy') + # add all paths which are required
    [
        ('data', 'data'),
        ('models', 'models'),
        ('screens', 'screens'),
        ('main_layout.kv', '.')
    ],
    hiddenimports=[
        "kivymd.uix.screen",
        "kivymd.uix.bottomnavigation",
        "kivy.parser",
        "screens.tts",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='dlTTS-v0.0.1',
    icon='data/images/favicon.ico',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
