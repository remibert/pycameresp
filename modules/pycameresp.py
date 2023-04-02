# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# pylint:disable=wrong-import-position
# pylint:disable=wrong-import-order
# pylint:disable=ungrouped-imports
# pylint:disable=unused-import
""" Main pycameresp module """
try:
	import machine

	# Force high frequency of esp32
	machine.freq(240000000)
except:
	pass

from tools import tasking

def start(**kwargs):
	""" Start pycameresp tasks 
	Parameters :
		- battery : activate battery survey (default False)
		- mqtt : activate mqtt client (default False)
		- ntp : activate ntp time synchronisation (default False)
		- http : activate http server (default False)
		- telnet : activate telnet server (default False)
		- pushover : activate pushover notification (default False)
		- presence : active presence of occupant in the house (default False)
		- motion : activate motion detection (default False)
		- starter : activate autostart of extension modules (default False)
		- shell : activate shell (default False)
		- webhook : activate webhook notification (default False)
	"""
	http_started = False
	device = kwargs.get("device","ESP32CAM")

	# Manage the awake of device
	from tools.awake import Awake
	pin_wake_up = Awake.is_pin_wake_up()
	Awake.start()

	# Manage the battery level
	if kwargs.get("battery",False):
		from tools.battery import Battery
		Battery.start()

	# Manage the network task
	if  kwargs.get("mqtt",False) or kwargs.get("ntp",False)    or kwargs.get("http",False) or kwargs.get("webhook",False) or\
		kwargs.get("ftp",False)  or kwargs.get("telnet",False) or kwargs.get("presence",False) or kwargs.get("pushover",False):

		# Manage the wifi task
		from wifi.wifi import Wifi
		Wifi.start()

		# Manage the periodic task (periodic gc, watchdog)
		from server.periodic import Periodic
		Periodic.start()

		# Manage the notifier task
		from server.notifier import Notifier
		Notifier.start()

	# Manage the http server (http_port=80)
	if kwargs.get("http",False):
		from server.httpserver import HttpServer
		HttpServer.start(**kwargs)
		http_started = True
		@HttpServer.add_pages()
		def pages_loader():
			import webpage

	# Manage the get of wan ip address
	if kwargs.get("wanip",False):
		from server.wanip import WanIp
		WanIp.start()

	# Manage the pushover notificiation
	if kwargs.get("pushover",False):
		from server.pushover import PushOver

	# Manage the webhook notification
	if kwargs.get("webhook",False):
		from server.webhook import WebHook

	# Manage the ftp server (ftp_port=21)
	if kwargs.get("ftp",False):
		from server.ftpserver import Ftp
		Ftp.start(**kwargs)

	# Manage the telnet server (telnet_port=23)
	if kwargs.get("telnet",False):
		from server.telnet import Telnet
		Telnet.start(**kwargs)

	# Manage the mqtt client
	if kwargs.get("mqtt",False):
		from server.mqttclient import MqttClient
		MqttClient.start(**kwargs)

	# Manage the time synchronisation
	if kwargs.get("ntp",False):
		from server.ntp import Ntp
		Ntp.start()

	# Manage the autostart add on component
	if kwargs.get("starter",False):
		from tools.starter import Starter
		Starter.start(**kwargs)

	# Manage the shell and commands line
	if kwargs.get("shell",False):
		from shell.shelltask import Shell
		Shell.start()

	from tools.info import iscamera

	# If camera is available (required specific firmware)
	if iscamera():
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
			else:
				# ESP32CAM default configuration
				pass

			# Start camera before wifi to avoid problems
			Camera.open()

			# If motion detection activated
			if kwargs.get("motion",False):
				# Manage motion detection history
				from motion.historic import Historic
				Historic.start()

				# Manage motion detection
				from motion.motion import Motion
				Motion.start(pin_wake_up=pin_wake_up)

				# Detects the presence of occupants in the house
				from server.presence import Presence
				Presence.start()

				# If http server started
				if http_started:
					# Start streaming http server
					args = kwargs.copy()
					args["name"] = "StreamingServer"
					args["http_port"] = kwargs.get("http_port",80)+1
					HttpServer.start(**args)

	# Run all asynchronous tasks
	tasking.Tasks.run()
