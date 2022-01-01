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
          console=False , icon='%(ICONS)s')
app = BUNDLE(exe,
             name='%(NAME)s-%(VERSION)s.app',
             icon='%(ICONS)s',
             bundle_identifier='github.com/remibert/pycameresp')
"""

from sys import platform
from shutil import rmtree
from os import remove
if platform == "win32" or platform == "linux":
	ICONS = "icons/camflasher.ico"
	execute("pyuic5 camflasher.ui -o camflasher.py")
elif platform == "linux":
	ICONS = "icons/camflasher.ico"
	execute("pyuic6 camflasher.ui -o camflasher.py")
elif platform == "darwin":
	ICONS = "icons/camflasher.icns"
	execute("pyuic6 camflasher.ui -o camflasher.py")

spec_file = open("build-%(platform)s.spec"%globals(),"w")
spec_file.write(spec%globals())
spec_file.close()

execute("pyinstaller --log-level=DEBUG --noconfirm --windowed build-%(platform)s.spec"%globals())

if platform == "darwin":
	execute("create-dmg dist/%(NAME)s-%(VERSION)s.dmg dist/%(NAME)s-%(VERSION)s.app --volicon %(ICONS)s"%(globals()))
rmtree("build")
remove("build-%(platform)s.spec"%globals())
