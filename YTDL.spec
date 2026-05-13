import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# 1. Setup data files
added_files = [
    ('ui', 'ui'),
    ('server.py', '.'),
]

# 2. Handle imageio_ffmpeg binaries
try:
    import imageio_ffmpeg
    imageio_ffmpeg_binaries = os.path.join(
        os.path.dirname(imageio_ffmpeg.__file__), 'binaries'
    )
    if os.path.exists(imageio_ffmpeg_binaries):
        added_files.append((imageio_ffmpeg_binaries, 'imageio_ffmpeg/binaries'))
except ImportError:
    pass

# 3. Collect yt_dlp data
added_files += collect_data_files('yt_dlp')

# 4. Define hidden imports (Ensuring tkinter is recognized)
hidden_imports = collect_submodules('yt_dlp') + [
    'flask',
    'flask.templating',
    'jinja2',
    'werkzeug',
    'webview',
    'webview.platforms',
    'imageio_ffmpeg',
    'engineio',
    'engineio.async_drivers',
    'tkinter',
    'tkinter.filedialog',
]

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # REMOVED 'tkinter' from the excludes list below:
    excludes=['matplotlib', 'numpy', 'pandas'], 
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='YTDL',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False, # Set to True if you need to see error logs during testing
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)