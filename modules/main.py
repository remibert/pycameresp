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
from tools.awake import Awake
from tools.useful import iscamera, syslog, reboot

# Force high frequency of esp32
machine.freq(240000000)

# Check the battery level and force deepsleep is to low
Battery.protect()

# Can only be done once at boot before start of the camera and sd card
pinWakeUp = Awake.isPinWakeUp()

# Html pages loader
def htmlPageLoader():
	# pylint: disable=unused-import
	# pylint: disable=redefined-outer-name

	# The html pages only loaded when the connection of http server is done
	# This reduces memory consumption if the server is not used
	import webpage

	try:
		# Sample page (can be suppressed)
		import sample
	except ImportError as err:
		pass

# Create asyncio loop
loop = uasyncio.get_event_loop()

# Start all servers Http, Ftp, Telnet and wifi manager
import server 
server.init(loop=loop, pageLoader=htmlPageLoader)

# If camera is available (required specific firmware)
if iscamera():
	# Start motion detection (can be only used with ESP32CAM)
	import motion 
	motion.start(loop, pinWakeUp)

# Add shell asynchronous task (press any key to get shell prompt)
from shell.shell import asyncShell
loop.create_task(asyncShell())

try:
	# Run asyncio for ever
	loop.run_forever()
except KeyboardInterrupt:
	syslog("Control C in main")
except Exception as err:
	syslog(err)
	reboot("Crash in main")
