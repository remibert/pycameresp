#!/usr/bin/python3
""" Build standalone executable for camflasher """
from platform import uname
from sys import platform
from shutil import rmtree
from os import remove

NAME="CamFlasher"

def execute(command):
	""" Execute command """
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
          name='%(NAME)s',
          debug=False,
          strip=False,
          upx=True,
          console=False , icon='%(ICONS)s')
app = BUNDLE(exe,
             name='%(NAME)s.app',
             icon='%(ICONS)s',
             bundle_identifier='github.com/remibert/pycameresp')
"""
UIC = 6
if platform == "win32":
	ICONS = "icons/camflasher.ico"
	import struct
	version = struct.calcsize("P")*8
	TARGET = "windows_%s_%d"%(uname()[2], version)
	if uname()[2] == "7":
		UIC = 5
elif platform == "linux":
	ICONS = "icons/camflasher.ico"
	TARGET = "linux"
elif platform == "darwin":
	ICONS = "icons/camflasher.icns"
	TARGET = "osx"

execute("pyuic%(UIC)s camflasher.ui -o camflasher.py"%globals())
execute("pyuic%(UIC)s dialogflash.ui -o dialogflash.py"%globals())
execute("pyuic%(UIC)s dialogabout.ui -o dialogabout.py"%globals())

spec_file = open("build-%(TARGET)s.spec"%globals(),"w")
spec_file.write(spec%globals())
spec_file.close()

execute("pyinstaller --log-level=DEBUG --noconfirm --distpath dist/%(TARGET)s --windowed build-%(TARGET)s.spec"%globals())

if platform == "darwin":
	execute("create-dmg dist/%(TARGET)s/%(NAME)s.dmg dist/%(TARGET)s/%(NAME)s.app --volicon %(ICONS)s"%(globals()))
rmtree("build")
remove("build-%(TARGET)s.spec"%globals())
