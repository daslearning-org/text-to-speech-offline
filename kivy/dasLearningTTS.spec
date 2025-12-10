# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# piper paths
# data_path = "/home/somnath/codes/git/my-org/text-to-speech-offline/kivy/.env/lib/python3.11/site-packages/piper/espeak-ng-data"
from pathlib import Path
import piper
piper_dir = Path(piper.__file__).parent
espeak_data_dir = piper_dir / "espeak-ng-data"

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[ #collect_data_files('kivy') + # add all paths which are required
        ('data', 'data'),
        ('screens', 'screens'),
        ('main_layout.kv', '.'),
        (str(espeak_data_dir), 'piper/espeak-ng-data')
    ],
    hiddenimports=[
        "kivymd.uix.screen",
        "kivymd.uix.bottomnavigation",
        "kivymd.icon_definitions",
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
    name='dlTTS-v0.3.0',
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
