# -*- mode: python -*-
a = Analysis(['poppage.py'],
             pathex=['__output__'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)

# Hack to prevent warning due to multiple header files. Taken from
# `http://stackoverflow.com/a/19163950`.
for d in a.datas:
    if 'pyconfig' in d[0]:
        a.datas.remove(d)
        break

pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='poppage.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True )
