# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
import sys
try:
	import uasyncio
except:
	sys.path.append("lib")
	sys.path.append("simul")
sys.path.append("sample")
import uasyncio
import machine
from tools.battery import Battery
from tools import useful

machine.freq(240000000)

# Check the battery level and force deepsleep is to low
Battery.protect()

# Can only be done once at boot before start the camera and sd card
isPinWakeUp = Battery.isPinWakeUp()

# Html pages loader
def pageLoader():
	# The html pages only loaded when the connection of http server is done
	# This reduces memory consumption if the server is not used
	import webpage
	from server.httpserver import HttpServer

	try:
		# Welcome page (can be suppressed)
		from welcome import welcomePage
	except ImportError as err:
		pass

	try:
		# Sample page (can be suppressed)
		import sample
	except ImportError as err:
		pass

# Create asyncio loop
loop = uasyncio.get_event_loop()

# Start all server (Http, Ftp, Telnet) and start wifi manager
# If you set the last parameter to True it preloads the pages of the http server at startup
import server 
server.init(loop=loop, pageLoader=pageLoader, preload=False, httpPort=80)

# If camera is available (required specific firmware)
if useful.iscamera():
	# Start motion detection (only used with ESP32CAM)
	import motion 
	motion.start(loop, isPinWakeUp)

from shell.shell import asyncShell
loop.create_task(asyncShell())

try:
	# Run asyncio for ever
	loop.run_forever()
except Exception as err:
	useful.exception(err)
finally:
	useful.reboot("Crash in main")
