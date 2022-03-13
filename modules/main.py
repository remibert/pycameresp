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
	# Uncomment if it is ESP32ONE device
	# motion.start(loop, pin_wake_up, \
	# 	pwdn=32,reset=-1,xclk=4,siod=18,sioc=23,d7=36,d6=37,d5=38,d4=39,d3=35,d2=14,d1=13,d0=34,vsync=5,
	# 	href=27,pclk=25,freq_hz=20000000,ledc_timer=0,ledc_channel=0,pixel_format=3,frame_size=13,jpeg_quality=12,fb_count=1,flash_led=0)
	# from tools import sdcard
	# sdcard.SdCard.set_slot(0) # The slot is good but not working I don't know why

	# For ESP32CAM comment if if is not ESP32CAM
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
