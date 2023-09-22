# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
# pylint:disable=wrong-import-position
# pylint:disable=wrong-import-order
# pylint:disable=ungrouped-imports
# pylint:disable=unused-import
""" Main pycameresp module """
try:
	import machine
	import os
	# Force high frequency of esp32
	machine.freq(240000000)
except:
	pass

def start(**kwargs):
	""" Start pycameresp tasks 
	Parameters :
		- awake        : activate awake mode (default False)
		- battery      : activate battery level (default False)
		- mqtt_client  : activate mqtt client (default False)
		- mqtt_broker  : activate mqtt broker (default False)
		- ntp          : activate ntp time synchronisation (default False)
		- http         : activate http server (default False)
		- telnet       : activate telnet server (default False)
		- pushover     : activate pushover notification (default False)
		- presence     : activate presence detection of occupant in the house (default False)
		- motion       : activate motion detection (default False)
		- camera       : activate the camera (default False)
		- plugin       : activate autostart of extension plugin (default False)
		- shell        : activate shell (default False)
		- webhook      : activate webhook notification (default False)
		- wifi         : activate wifi manager (default False)
		- log_size     : maximal size of syslog file
		- log_quantity : maximal quantity of syslog files
	"""
	# pylint:disable=consider-using-f-string
	import tools.info
	import tools.support
	import tools.logger
	import tools.features

	tools.features.FeaturesConfig(**kwargs)
	features = tools.features.features

	tools.logger.set_size(size=features.log_size, quantity=features.log_quantity)

	if features.awake:
		# Manage the awake of device
		import tools.awake
		pin_wake_up = tools.awake.Awake.is_pin_wake_up()
		tools.awake.Awake.start()
	else:
		pin_wake_up = False

	# Manage the periodic task (periodic garbage collection and watchdog)
	import server.periodic
	server.periodic.Periodic.start(**kwargs)

	# Manage the network task
	if  features.mqtt_client or features.ntp      or features.http   or \
		features.webhook     or features.ftp      or features.telnet or \
		features.presence    or features.pushover or features.wifi   or \
		features.mqtt_broker :

		# Manage the wifi task
		import wifi.wifi
		wifi.wifi.Wifi.start()

	# If camera is available (required specific firmware)
	if tools.info.iscamera() and (features.motion or features.camera) :
		import video.video
		if video.video.Camera.is_activated():
			import tools.sdcard
			if features.device == "ESP32ONE":
				# ESP32ONE device
				video.video.Camera.gpio_config(
					pin_pwdn=32, pin_reset=-1, pin_xclk=4, pin_sscb_sda=18, pin_sscb_scl=23,
					pin_d7=36, pin_d6=37, pin_d5=38, pin_d4=39,
					pin_d3=35, pin_d2=14, pin_d1=13, pin_d0=34,
					pin_vsync=5, pin_href=27, pin_pclk=25, xclk_freq_hz=20000000,
					ledc_timer=0, ledc_channel=0, pixel_format=3, frame_size=13, jpeg_quality=12, fb_count=1, flash_led=0)
				tools.sdcard.SdCard.set_slot(slot=None) # The slot is good but not working I don't know why
			elif features.device == "M5CAMERA-B":
				# M5CAMERA-B device
				video.video.Camera.gpio_config(
					pin_pwdn=-1, pin_reset=15, pin_xclk=27, pin_sscb_sda=22, pin_sscb_scl=23,
					pin_d7=19, pin_d6=36, pin_d5=18, pin_d4=39,
					pin_d3=5,  pin_d2=34, pin_d1=35, pin_d0=32,
					pin_vsync=25, pin_href=26, pin_pclk=21, xclk_freq_hz=20000000, ledc_timer=0,
					ledc_channel=0 , pixel_format=3, frame_size=13, jpeg_quality=0, fb_count=1, flash_led=14)
				tools.sdcard.SdCard.set_slot(slot=None) # No sdcard available
			elif "FREENOVE CAM S3" in os.uname().machine:
				features.device = "FREENOVE CAM S3"
				tools.sdcard.SdCard.set_slot(slot=0, clk=39, d0=40, cmd=38, width=1)
			else:
				# ESP32CAM default configuration
				pass

			# Start camera before wifi to avoid problems
			video.video.Camera.open()

			# If motion detection activated
			if features.motion:
				# Manage motion detection history
				import motion.historic
				motion.historic.Historic.start()

				# Manage motion detection
				import motion.motion
				motion.motion.Motion.start(pin_wake_up=pin_wake_up)

			# If http server started
			if features.http:
				import server.httpserver
				# Start streaming http server
				args = kwargs.copy()
				args["name"] = "HttpStreaming"
				args["http_port"] = features.http_port+1
				server.httpserver.HttpServer.start(**args)

	if features.presence:
		# Detects the presence of occupants in the house
		import server.presence
		server.presence.Presence.start()

	# Manage the battery level
	if features.battery and tools.support.battery():
		import tools.battery
		tools.battery.Battery.start()

	if features.pushover or features.mqtt_client or features.webhook:
		# Manage the notifier task
		import server.notifier
		server.notifier.Notifier.start()

	# Manage the http server (http_port=80)
	if features.http:
		import server.httpserver
		server.httpserver.HttpServer.start(**kwargs)
		@server.httpserver.HttpServer.add_pages()
		def pages_loader():
			import webpage

	# Manage the get of wan ip address
	if features.wanip:
		import server.wanip
		server.wanip.WanIp.start()

	# Manage the pushover notificiation
	if features.pushover:
		import server.pushover

	# Manage the webhook notification
	if features.webhook:
		import server.webhook

	# Manage the ftp server (ftp_port=21)
	if features.ftp:
		import server.ftpserver
		server.ftpserver.FtpServer.start(**kwargs)

	# Manage the telnet server (telnet_port=23)
	if features.telnet and tools.support.telnet():
		import server.telnet
		server.telnet.Telnet.start(**kwargs)

	# Manage the mqtt client and mqtt notification
	if features.mqtt_client:
		import server.mqttclient
		server.mqttclient.MqttClient.start(**kwargs)

	# Manage the mqtt broker
	if features.mqtt_broker:
		import server.mqttbroker
		server.mqttbroker.MqttBroker.start(**kwargs)

	# Manage the time synchronisation
	if features.ntp:
		import server.ntp
		server.ntp.Ntp.start()

	# Manage the autostart add on component
	if features.plugin:
		import tools.plugin
		tools.plugin.PluginStarter.start(**kwargs)

	# Manage the shell and commands line
	if features.shell:
		import shell.shelltask
		shell.shelltask.Shell.start()

	# Run all asynchronous tasks
	import tools.tasking
	tools.tasking.Tasks.run()
