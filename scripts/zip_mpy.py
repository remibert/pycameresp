import sys
import useful

ROOT=sys.argv[1]
BOARD=sys.argv[2]
directory="%(ROOT)s/micropython/ports/esp32/build-%(BOARD)s/frozen_mpy/"%globals()
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

useful.zip_dir("%s/shell.zip"%ROOT,directory,  ["*.mpy"], excludeds_shell, True, [["frozen_mpy","lib"]])
useful.zip_dir("%s/server.zip"%ROOT,directory, ["*.mpy"], excludeds      , True, [["frozen_mpy","lib"]])
