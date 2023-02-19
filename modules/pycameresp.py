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

def create_battery_task(loop):
	""" Create async task for battery level monitoring """
	from tools import support
	if support.battery():
		from tools.battery import Battery
		Battery.protect()
		loop.create_task(Battery.periodic_task())

def create_camera_task(loop, device):
	""" Create async task for motion detection and camera streaming """
	from tools.info import iscamera

	# If camera is available (required specific firmware)
	if iscamera():
		# Check if the wakeup was caused by a pin state change
		from tools.awake import Awake
		pin_wake_up = Awake.is_pin_wake_up()

		from video import Camera

		if Camera.is_activated():
			if device == "ESP32ONE":
				from tools import sdcard

				# ESP32ONE device
				Camera.gpio_config(
					pin_pwdn=32, pin_reset=-1, pin_xclk=4, pin_sscb_sda=18, pin_sscb_scl=23,
					pin_d7=36, pin_d6=37, pin_d5=38, pin_d4=39, pin_d3=35, pin_d2=14, pin_d1=13, pin_d0=34,
					pin_vsync=5, pin_href=27, pin_pclk=25, xclk_freq_hz=20000000,
					ledc_timer=0, ledc_channel=0, pixel_format=3, frame_size=13, jpeg_quality=12, fb_count=1, flash_led=0)
				from tools import sdcard
				sdcard.SdCard.set_slot(slot=None) # The slot is good but not working I don't know why
			elif device == "M5CAMERA-B":
				from tools import sdcard

				# ESP32ONE device
				Camera.gpio_config(
					pin_pwdn=-1, pin_reset=15, pin_xclk=27, pin_sscb_sda=22, pin_sscb_scl=23,
					pin_d7=19, pin_d6=36, pin_d5=18, pin_d4=39, pin_d3=5, pin_d2=34, pin_d1= 35, pin_d0=32,
					pin_vsync=25, pin_href=26, pin_pclk=21, xclk_freq_hz=20000000, ledc_timer=0,
					ledc_channel=0 , pixel_format=3, frame_size=13, jpeg_quality=0, fb_count=1, flash_led=14)
				sdcard.SdCard.set_slot(slot=None) # No sdcard available

			# Start camera before wifi to avoid problems
			Camera.open()

			# Start motion detection
			import motion
			motion.start(loop, pin_wake_up)

def default_loader():
	""" The html pages only loaded when the connection of http server is done.
	This reduces memory consumption if the server is not used """
	#pylint:disable=unused-import
	import webpage

def create_network_task(loop, html_loader = None):
	""" Create all servers Http, Ftp, Telnet and wifi manager """
	import server
	page_loader = [default_loader]
	if html_loader is not None:
		page_loader.append(html_loader)
	server.init(loop=loop, page_loader=page_loader)

def create_shell_task(loop):
	""" Create shell asynchronous task (press any key to get shell prompt) """
	# pylint:disable=unused-import
	from shell import async_shell
	loop.create_task(async_shell())

def create_user_task(loop, function, *args, **params):
	""" Create user task """
	from tools import tasking
	async def task(*args, **params):
		await tasking.task_monitoring(function, *args, **params)
	loop.create_task(task(*args, **params))

def run_tasks(loop):
	""" Start all async task """
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
