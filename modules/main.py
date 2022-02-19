# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Main pycameresp module """
# pylint:disable=wrong-import-position
# pylint:disable=wrong-import-order
import sys
try:
	import uasyncio
except:
	sys.path.append("lib")
	sys.path.append("simul")
sys.path.append("sample")
import uasyncio
import machine
from tools import battery, awake, logger, system, info

# Force high frequency of esp32
machine.freq(240000000)

# Check the battery level and force deepsleep is to low
battery.Battery.protect()

# Can only be done once at boot before start of the camera and sd card
pinWakeUp = awake.Awake.is_pin_wake_up()

def html_page_loader():
	""" Html pages loader """
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
server.init(loop=loop, page_loader=html_page_loader)

# If camera is available (required specific firmware)
if info.iscamera():
	# Start motion detection (can be only used with ESP32CAM)
	import motion
	motion.start(loop, pinWakeUp)

# Add shell asynchronous task (press any key to get shell prompt)
# pylint:disable=unused-import
from shell import async_shell,sh
loop.create_task(async_shell())

try:
	# Run asyncio for ever
	loop.run_forever()
except KeyboardInterrupt:
	logger.syslog("Control C in main")
except Exception as err:
	logger.syslog(err)
	system.reboot("Crash in main")
