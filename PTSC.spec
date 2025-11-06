# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path

block_cipher = None

# Collect data files (only if they exist)
datas = [
    ('app.py', '.'),
    ('converters', 'converters'),
    ('parsers', 'parsers'),
    ('generators', 'generators'),
    ('utils', 'utils'),
    ('samples', 'samples'),
    ('docs', 'docs'),
]

# Add .streamlit folder if it exists
if Path('.streamlit').exists():
    datas.append(('.streamlit', '.streamlit'))

# Collect package metadata for streamlit and other packages
from PyInstaller.utils.hooks import copy_metadata, collect_data_files, collect_all
datas += copy_metadata('streamlit')
datas += copy_metadata('altair')
datas += copy_metadata('click')
datas += copy_metadata('toml')

# Collect python-dotenv
tmp_datas, tmp_binaries, tmp_hiddenimports = collect_all('dotenv')
datas += tmp_datas

# Collect streamlit static files (required for web UI)
datas += collect_data_files('streamlit', include_py_files=False)

# Collect code_editor component files (frontend build)
datas += collect_data_files('code_editor', include_py_files=False)

# Collect all necessary files
a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'streamlit',
        'streamlit.runtime',
        'streamlit.runtime.scriptrunner',
        'streamlit.runtime.scriptrunner.magic_funcs',
        'streamlit.web',
        'streamlit.web.cli',
        'code_editor',
        'pandas',
        'lxml',
        'xml.etree.ElementTree',
        'hashlib',
        'validators',
        'altair',
        'plotly',
        'click',
        'toml',
        'pyarrow',
        'dotenv',
        'google.generativeai',
        'google.ai.generativelanguage',
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
    name='PTSC',
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
    name='PTSC',
)
