# -*- mode: python ; coding: utf-8 -*-
# HFA_2025.spec
# PyInstaller spec file for Huemanity for ALL 2026 by Troyski

block_cipher = None

a = Analysis(
    ['HFA_2026_by_Troyski_v2.py'],
    pathex=['C:\\Users\\Troy\\PycharmProjects\\HFA_2025'],
    binaries=[],
    datas=[
        ('IMAGES\\ICOs\\HUEMANITY_for_ALL.ico', 'IMAGES\\ICOs'),
        ('IMAGES\\HFA - Colors MOST beautiful when MIXED.png', 'IMAGES'),
        ('HFA_ALL_palettes.py', '.'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'numpy',
    ],
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
    name='HFA_2026_by_Troyski_v3',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='IMAGES\\ICOs\\HUEMANITY_for_ALL.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='HFA_2026_by_Troyski_v3',
)