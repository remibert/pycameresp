# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" Create zip packages """
# pylint:disable=consider-using-f-string
import os
import sys
from zipfile import ZipFile, ZIP_DEFLATED
import useful

ROOT=sys.argv[1]
BOARD=sys.argv[2]
MICRO=sys.argv[3]
BOARD_VARIANT=sys.argv[4]
PYCAMERESP=sys.argv[5]
MICRO=MICRO.lower()

MPY_DIRECTORY="%(ROOT)s/micropython-%(MICRO)s/ports/esp32/build-%(BOARD)s%(BOARD_VARIANT)s/frozen_mpy/"%globals()
print(MPY_DIRECTORY)
PY_DIRECTORY="%(ROOT)s/micropython-%(MICRO)s/ports/esp32/modules/"%globals()
excludeds = [
	"_boot.*",
	"apa106.*",
	"flashbdev.*",
	"dht.*",
	"ds18x20.*",
	"neopixel.*",
	"ntptime.*",
	"onewire.*",
	"upip_utarfile.*",
	"upip.*",
	"webrepl_setup.*",
	"webrepl.*",
	"websocket_helper.*",
	"inisetup.*",
	"*/motion/*",
	"*/video/*",
	"*/uasyncio/*"]

excludeds_shell = excludeds + [
	"*/webpage/*",
	"*/server/*",
	"*/wifi/*",
	"*/htmltemplate/*"]

def zip_mpy():
	""" Zip micropython compiled """
	useful.zip_dir("%s/delivery/shell.zip"%PYCAMERESP,MPY_DIRECTORY,  ["*.mpy"], excludeds_shell, False, [["frozen_mpy","lib"]])
	useful.zip_dir("%s/delivery/server.zip"%PYCAMERESP,MPY_DIRECTORY, ["*.mpy"], excludeds      , False, [["frozen_mpy","lib"]])
	z = ZipFile("%s/delivery/server.zip"%PYCAMERESP, "a",ZIP_DEFLATED)
	z.write(os.path.normpath("%s/modules/main.py"%PYCAMERESP),"main.py")
	z.write(os.path.normpath("%s/modules/pycameresp.py"%PYCAMERESP),"pycameresp.py")
	z.write(os.path.normpath("%s/modules/www/bootstrap.bundle.min.js"%PYCAMERESP),"www/bootstrap.bundle.min.js")
	z.write(os.path.normpath("%s/modules/www/bootstrap.min.css"%PYCAMERESP),"www/bootstrap.min.css")
	z.close()

def zip_editor():
	""" Zip file editor source """
	useful.zip_dir("%s/delivery/editor.zip"%PYCAMERESP,
		directory=PY_DIRECTORY,
		includes=[
			"*/editor*.py",
			"*/keyboard*.py",
			"*/filesystem.py",
			"*/jsonconfig.py",
			"*/terminal.py",
			"*/logger.py",
			"*/useful.py",
			"*/strings.py",
			"*/fnmatch.py",
			"*/date.py"],
		excludes=[],
		display=False,
		renames=[["shell","editor"],["tools","editor/tools"],["modules",""]]
		)

def zip_plugin(pycameresp_dir, name):
	""" Zip one plugin directory """
	useful.zip_dir("%s/delivery/%s.zip"%(pycameresp_dir, name),
		directory = "%s/modules"%pycameresp_dir,
		includes  = ["*/lib/plugins/%s/*.py"%name,"*/www/%s.html"%name],
		prefix    = "%s/modules"%pycameresp_dir,
		excludes  = [],
		display   = False)

def zip_plugins(pycameresp_dir):
	""" Zip all plugins directories """
	for name in os.listdir(pycameresp_dir + "/modules/lib/plugins"):
		if name != ".DS_Store":
			print("Zip plugin '%s'"%name)
			zip_plugin(pycameresp_dir, name)

def zip_all(pycameresp_dir):
	""" Zip alls """
	zip_plugins(pycameresp_dir)
	zip_mpy()
	zip_editor()

if __name__=="__main__":
	zip_all(PYCAMERESP)
