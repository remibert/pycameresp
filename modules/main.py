# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# pylint:disable=wrong-import-position
# pylint:disable=wrong-import-order
# pylint:disable=ungrouped-imports
""" Main pycameresp module """
try:
	import machine

	# Force high frequency of esp32
	machine.freq(240000000)
except:
	import sys
	sys.path.append("lib")
	sys.path.append("simul")
	sys.path.append("sample")

# Check the battery level and force deepsleep if it is too low
from tools.battery import Battery
Battery.protect()

# Check if the wakeup was caused by a pin state change
from tools.awake import Awake
pin_wake_up = Awake.is_pin_wake_up()

# Create asyncio loop
import uasyncio
loop = uasyncio.get_event_loop()

# If camera is available (required specific firmware)
from tools.info import iscamera
if iscamera():
	# Start motion detection (can be only used with ESP32CAM)
	import motion
	motion.start(loop, pin_wake_up)

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

# Start all servers Http, Ftp, Telnet and wifi manager
import server
server.init(loop=loop, page_loader=html_page_loader)

# Add shell asynchronous task (press any key to get shell prompt)
# pylint:disable=unused-import
from shell import async_shell,sh
loop.create_task(async_shell())

try:
	# Run asyncio for ever
	loop.run_forever()
except KeyboardInterrupt:
	from tools import logger
	logger.syslog("Ctr-C in main")
except Exception as err:
	from tools import logger, system
	logger.syslog(err)
	system.reboot("Crash in main")
