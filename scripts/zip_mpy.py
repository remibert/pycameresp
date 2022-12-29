import sys
import useful

ROOT=sys.argv[1]
BOARD=sys.argv[2]
PYCAMERESP=sys.argv[3]
MPY_DIRECTORY="%(ROOT)s/micropython/ports/esp32/build-%(BOARD)s/frozen_mpy/"%globals()
PY_DIRECTORY="%(ROOT)s/micropython/ports/esp32/modules/"%globals()
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

useful.zip_dir("%s/delivery/shell.zip"%PYCAMERESP,MPY_DIRECTORY,  ["*.mpy"], excludeds_shell, False, [["frozen_mpy","lib"]])


from zipfile import ZipFile, ZIP_DEFLATED 
import os.path
useful.zip_dir("%s/delivery/server.zip"%PYCAMERESP,MPY_DIRECTORY, ["*.mpy"], excludeds      , False, [["frozen_mpy","lib"]])
z = ZipFile("%s/delivery/server.zip"%PYCAMERESP, "a",ZIP_DEFLATED)
z.write(os.path.normpath("%s/modules/main.py"%PYCAMERESP),"main.py")
z.write(os.path.normpath("%s/modules/pycameresp.py"%PYCAMERESP),"pycameresp.py")
z.write(os.path.normpath("%s/modules/www/bootstrap.bundle.min.js"%PYCAMERESP),"www/bootstrap.bundle.min.js")
z.write(os.path.normpath("%s/modules/www/bootstrap.min.css"%PYCAMERESP),"www/bootstrap.min.css")
z.close()

useful.zip_dir("%s/delivery/editor.zip"%PYCAMERESP,PY_DIRECTORY,  ["*/editor*.py","*/filesystem.py","*/jsonconfig.py","*/terminal.py","*/logger.py","*/useful.py","*/strings.py","*/fnmatch.py","*/date.py"],[], False, [["shell","editor"],["tools","editor"],["modules",""]])
useful.zip_dir("%s/delivery/electricmeter.zip"%PYCAMERESP,"%s/modules"%PYCAMERESP,  ["*/lib/electricmeter/*.py","*/www/electricmeter.html"],[], False, [["modules",""]])
