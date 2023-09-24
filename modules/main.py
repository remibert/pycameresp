# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" Main module """
import pycameresp

# Start certain features of the Pycameresp platform
# Comment unnecessary lines to decrease RAM footprint
pycameresp.start(\
	device      = "ESP32CAM", # "ESP32ONE" "M5CAMERA-B" : particular type of camera

	# Features
	plugin      = True, # Start all plugins (must be contains lib/plugins/*/__startup__.py)
	#awake       = True, # Awake and deepsleep periodically task
	#battery     = True, # Battery level manager task
	shell       = True, # Shell with text editor task

	# Network
	wifi        = True, # Wifi manager task
	ftp         = True, # Ftp server task
	http        = True, # Http server task
	telnet      = True, # Telnet server task
	ntp         = True, # Ntp synchronisation task
	wanip       = True, # Wanip periodically obtained task
	#mqtt_broker = True, # Mqtt broker task

	# Notifiers
	#mqtt_client = True, # Mqtt client task
	#webhook     = True, # Webhook notification task
	pushover    = True, # Pushover notification task

	# Motion and camera
	presence    = True, # Home occupant presence detection task
	camera      = True, # Camera configuration
	motion      = True, # Motion detection task
	# debug=True, dump=True
	)
