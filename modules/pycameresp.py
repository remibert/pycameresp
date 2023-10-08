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
	Feature activation flags (if absent value is false) :
		- awake        : activate awake mode
		- battery      : activate battery level
		- mqtt_client  : activate mqtt client
		- mqtt_broker  : activate mqtt broker
		- ntp          : activate ntp time synchronisation
		- http         : activate http server
		- telnet       : activate telnet server
		- pushover     : activate pushover notification
		- presence     : activate presence detection of occupant in the house
		- motion       : activate motion detection
		- camera       : activate the camera
		- plugin       : activate autostart of plugin
		- shell        : activate shell
		- webhook      : activate webhook notification
		- wifi         : activate wifi manager

	Logger configuration :
		- log_size     : maximal size of syslog file
		- log_quantity : maximal quantity of syslog files
	
	Tcp ip ports configuration :
		- ftp_port         : tcp ip ftp port (default 21)
		- telnet_port      : tcp ip telnet port (default 23)
		- http_port        : tcp ip http port (default 80)
		- mqtt_broker_port : tcp ip mqtt broker port (default 1883)
		- mqtt_port        : tcp ip mqtt client port (default 1883)
	"""
	# pylint:disable=consider-using-f-string
	import tools.info
	import tools.support
	import tools.logger
	import tools.features

	# Get the features configuration
	tools.features.FeaturesConfig(**kwargs)
	features = tools.features.features

	# Configure logger
	tools.logger.set_size(size=features.log_size, quantity=features.log_quantity)

	# If periodic awake feature selected
	if features.awake:
		# Manage the awake of device
		import tools.awake
		pin_wake_up = tools.awake.Awake.is_pin_wake_up()
		tools.awake.Awake.start()
	else:
		pin_wake_up = False

	# Start the periodic task it required to periodic garbage collection and watchdog
	import server.periodic
	server.periodic.Periodic.start(**kwargs)

	# If one network task selected
	if  features.mqtt_client or features.ntp      or features.http   or \
		features.webhook     or features.ftp      or features.telnet or \
		features.presence    or features.pushover or features.wifi   or \
		features.mqtt_broker :

		# Start the wifi task
		import wifi.wifi
		wifi.wifi.Wifi.start()

	# If camera is available (required specific firmware)
	if tools.info.iscamera() and (features.motion or features.camera) :
		import video.video
		if video.video.Camera.is_activated():
			import tools.sdcard
			if "ESP32CAM" in os.uname().machine:
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
						ledc_channel=0, pixel_format=3, frame_size=13, jpeg_quality=0, fb_count=1, flash_led=14)
					tools.sdcard.SdCard.set_slot(slot=None) # No sdcard available
				elif features.device == "FREENOVE CAM ESP32":
					# Freenove ESP32-Wrover CAM device
					video.video.Camera.gpio_config(
						pin_pwdn=-1, pin_reset=-1, pin_xclk=21, pin_sscb_sda=26, pin_sscb_scl=27, 
						pin_d7=35, pin_d6=34, pin_d5=39, pin_d4=36,
						pin_d3=19,  pin_d2=18, pin_d1=5, pin_d0=4,
						pin_vsync=25, pin_href=23, pin_pclk=22, xclk_freq_hz=20000000, 
						ledc_timer=0, ledc_channel=0, pixel_format=3, frame_size=13, jpeg_quality=0, fb_count=1, flash_led=0)
					tools.sdcard.SdCard.set_slot(slot=None) # No sdcard available
				else:
					# ESP32CAM default configuration
					pass
			elif "FREENOVE CAM" in os.uname().machine:
				features.device = "FREENOVE CAM"
				# Micropython patched to support this microcard
				tools.sdcard.SdCard.set_slot(slot=0, clk=39, d0=40, cmd=38, width=1)

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

	# If the presence of occupant of the house must be detected
	if features.presence:
		# Detects the presence of occupants in the house
		import server.presence
		server.presence.Presence.start()

	# If the battery level must be managed
	if features.battery and tools.support.battery():
		import tools.battery
		tools.battery.Battery.start()

	# If a notifier feature selected
	if features.pushover or features.mqtt_client or features.webhook:
		import server.notifier
		server.notifier.Notifier.start()

	# If http server feature selected (http_port=80)
	if features.http:
		import server.httpserver
		server.httpserver.HttpServer.start(**kwargs)
		@server.httpserver.HttpServer.add_pages()
		def pages_loader():
			import webpage

	# If the get of wan ip address selected
	if features.wanip:
		import server.wanip
		server.wanip.WanIp.start()

	# If the pushover notificiation selected
	if features.pushover:
		import server.pushover

	# If the webhook notification selected
	if features.webhook:
		import server.webhook

	# If the ftp server selected (ftp_port=21)
	if features.ftp:
		import server.ftpserver
		server.ftpserver.FtpServer.start(**kwargs)

	# If the telnet server selected (telnet_port=23)
	if features.telnet and tools.support.telnet():
		import server.telnet
		server.telnet.Telnet.start(**kwargs)

	# If the mqtt client and mqtt notification selected
	if features.mqtt_client:
		import server.mqttclient
		server.mqttclient.MqttClient.start(**kwargs)

	# If the mqtt broker selected
	if features.mqtt_broker:
		import server.mqttbroker
		server.mqttbroker.MqttBroker.start(**kwargs)

	# If the time synchronisation selected
	if features.ntp:
		import server.ntp
		server.ntp.Ntp.start()

	# If the start of plugins selected
	if features.plugin:
		import tools.plugin
		tools.plugin.PluginStarter.start(**kwargs)

	# If the shell and commands line selected
	if features.shell:
		import shell.shelltask
		shell.shelltask.Shell.start()

	# Run all asynchronous tasks
	import tools.tasking
	tools.tasking.Tasks.run()
