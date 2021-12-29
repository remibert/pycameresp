#!/usr/bin/python3
VERSION="1.0.0"
NAME="CamFlasher"

def execute(command):
	from subprocess import run, PIPE, STDOUT
	print("> %s"%command)
	p = run(command.split(" "), stdout=PIPE, stderr=STDOUT, encoding='utf-8')
	print(p.stdout)

spec = """# -*- mode: python -*-
block_cipher = None

a = Analysis(['main.py'],
             binaries=None,
             datas=[("icons", "icons"),("camflasher.ui",".")],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='%(NAME)s-%(VERSION)s',
          debug=False,
          strip=False,
          upx=True,
          console=False , icon='icons/camflasher.icns')
app = BUNDLE(exe,
             name='%(NAME)s-%(VERSION)s.app',
             icon='./icons/camflasher.icns',
             bundle_identifier='github.com/remibert/pycameresp')
"""

spec_file = open("build-osx.spec","w")
spec_file.write(spec%globals())
spec_file.close()

execute("rm -rf dist build")
execute("pyuic6 camflasher.ui -o camflasher.py")
execute("pyinstaller --log-level=DEBUG --noconfirm --windowed build-osx.spec")
execute("create-dmg %(NAME)s-%(VERSION)s.dmg dist/%(NAME)s-%(VERSION)s.app --volicon icons/camflasher.icns"%(globals()))
execute("rm build-osx.spec")
execute("rm -rf build dist")