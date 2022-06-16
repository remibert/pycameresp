#!/usr/bin/python3
""" Build standalone executable for camflasher """
import platform
import sys
import subprocess
import os
import os.path
import shutil
import time
import zipfile

NAME="CamFlasher"
SPEC = """# -*- mode: python -*-
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
if sys.platform == "win32":
	ICONS = "icons/camflasher.ico"
	import struct
	version = struct.calcsize("P")*8
	TARGET = "windows_%s_%d"%(platform.uname()[2], version)
	if platform.uname()[2] == "7":
		UIC = 5
	EXE = "%(NAME)s.exe"%globals()
elif sys.platform == "linux":
	ICONS = "icons/camflasher.ico"
	TARGET = "linux"
	EXE = "%(NAME)s"%globals()
elif sys.platform == "darwin":
	ICONS = "icons/camflasher.icns"
	TARGET = "osx"
	EXE = "%(NAME)s.dmg"%globals()

def execute(commands):
	""" Execute shell commands """
	commands = commands%globals()
	for command in commands.split("\n"):
		command = command.strip()
		if len(command) >= 1 and command[0] == "#":
			print("\x1B[38;33m" + command + "\x1B[m")
		elif command.strip() != "":
			print("\x1B[38;32m> " + command + "\x1B[m")
			command = command.replace("\t"," ")
			cmds = command.split(" ")
			cmd = []
			for part in cmds:
				if len(part) > 0:
					cmd.append(part)
			if cmd[0] == "cd":
				command = command.strip()
				current_dir = command[3:].strip()
				if current_dir[0] == '"' and current_dir[-1] == '"':
					current_dir = current_dir.strip('"')
				os.chdir(current_dir)
			elif cmd[0] == "removetree" or cmd[0] == "removedir":
				directory = cmd[1]
				while os.path.exists(directory):
					try:
						shutil.rmtree(directory,0,lambda function,directory,dummy: (os.chmod(directory, 0o777),os.remove(directory)))
					except OSError:
						print ("! Remove dir failed '%s'"%directory)
					if os.path.exists(directory):
						time.sleep(1)
			elif cmd[0] == "copyfile":
				shutil.copyfile(cmd[1],cmd[2])
			elif cmd[0] == "copytree" or cmd[0] == "copydir":
				shutil.copytree(cmd[1],cmd[2])
			elif cmd[0] == "remove":
				os.remove(cmd[1])
			else:
				pipe = subprocess.Popen(command, stdout=sys.stdout, stderr=sys.stderr, shell=True)
				lines = pipe.communicate()[0]
		else:
			print("")

def main():
	""" Build standalone executable for camflasher """
	global ICONS, TARGET, EXE, NAME, UIC, SPEC

	spec_file = open("build-%(TARGET)s.spec"%globals(),"w")
	spec_file.write(SPEC%globals())
	spec_file.close()

	execute("""
		##########################
		# Remove old build files #
		##########################
		removedir esptool_
		removedir esptool
		removedir build

		########################
		# Build user interface #
		########################
		pyuic%(UIC)s camflasher.ui -o camflasher.py
		pyuic%(UIC)s dialogflash.ui -o dialogflash.py
		pyuic%(UIC)s dialogabout.ui -o dialogabout.py
		pyuic%(UIC)s dialogoption.ui -o dialogoption.py

		###############################
		# Remove installed esptool.py #
		###############################
		pip3 uninstall -y -q esptool

		####################
		# Patch esptool.py #
		####################
		git clone https://github.com/espressif/esptool.git -q esptool_
		copytree esptool_/esptool esptool

		################
		# Copy scripts #
		################
		copyfile ../../modules/lib/tools/strings.py     strings.py
		copyfile ../../modules/lib/tools/filesystem.py  filesystem.py
		copyfile ../../modules/lib/tools/exchange.py    exchange.py

		#############
		# Build exe #
		#############
		pyinstaller --log-level=ERROR --noconfirm --distpath dist/%(TARGET)s build-%(TARGET)s.spec"""%globals())

	if sys.platform == "darwin":
		execute("create-dmg dist/%(TARGET)s/%(NAME)s.dmg dist/%(TARGET)s/%(NAME)s.app --volicon %(ICONS)s"%(globals()))

	zip_filename = "dist/%(NAME)s_%(TARGET)s.zip"%globals()
	with zipfile.ZipFile(zip_filename, 'w') as myzip:
		myzip.write("dist/%(TARGET)s/%(EXE)s"%globals(), EXE)

	execute("""
		#####################
		# Reinstall esptool #
		#####################
		# pip3 -q install esptool

		##################
		# Clean up build #
		##################
		remove build-%(TARGET)s.spec
		remove strings.py
		remove filesystem.py
		remove exchange.py
		remove camflasher.py
		remove dialogflash.py
		remove dialogabout.py
		remove dialogoption.py
		removedir esptool_
		# removedir esptool
		removedir build"""%globals())

if __name__ == "__main__":
	main()
