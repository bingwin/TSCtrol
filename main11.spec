# -*- mode: python -*-

block_cipher = None
added_files=[
    ('./resources','resources'),
    ('./resources/ico','ico'),
    ('./resources/ico/*.ico','ico'),
    ('./resources/ico/*.icns','ico'),
]

a = Analysis(['main.py'],
             pathex=['/Users/tieniu/Documents/pyqt/TSCtrol'],
             binaries=[],
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True ,
         )

app = BUNDLE(exe,
         name='TSCtrol.app',
         icon='resources/ico/AppIcon.icns',
         bundle_identifier="TSCtrol",

    )
