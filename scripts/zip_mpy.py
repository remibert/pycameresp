import sys
import useful

ROOT=sys.argv[1]
BOARD=sys.argv[2]
MPY_DIRECTORY="%(ROOT)s/micropython/ports/esp32/build-%(BOARD)s/frozen_mpy/"%globals()
PY_DIRECTORY="%(ROOT)s/micropython/ports/esp32/modules/"%globals()
excludeds = [
	"_boot.mpy",
	"apa106.mpy",
	"flashbdev.mpy",
	"dht.mpy",
	"ds18x20.mpy",
	"neopixel.mpy",
	"ntptime.mpy",
	"onewire.mpy",
	"upip_utarfile.mpy",
	"upip.mpy",
	"webrepl_setup.mpy",
	"webrepl.mpy",
	"websocket_helper.mpy",
	"inisetup.mpy",
	"*/homekit/*",
	"*/motion/*",
	"*/video/*",
	"*/uasyncio/*"]

excludeds_shell = excludeds + [
	"*/webpage/*",
	"*/server/*",
	"*/wifi/*",
	"*/htmltemplate/*"]

useful.zip_dir("%s/shell.zip"%ROOT,MPY_DIRECTORY,  ["*.mpy"], excludeds_shell, True, [["frozen_mpy","lib"]])
useful.zip_dir("%s/server.zip"%ROOT,MPY_DIRECTORY, ["*.mpy"], excludeds      , True, [["frozen_mpy","lib"]])
useful.zip_dir("%s/editor.zip"%ROOT,PY_DIRECTORY,  ["*/editor.py","*/filesystem.py","*/terminal.py","*/logger.py","*/useful.py","*/strings.py","*/fnmatch.py"],[], True, [["shell","editor"],["tools","editor"],["modules",""]])