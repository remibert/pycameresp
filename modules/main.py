# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Main module """
import pycameresp

# Start certain functionality of the Pycameresp platform
pycameresp.start(\
	device   = "ESP32CAM", # "ESP32ONE" "M5CAMERA-B" : type of camera device

	# Features
	starter  = True, # Automatic start all __startup__.py if it is present
	awake    = True, # Awake and deepsleep periodically task
	battery  = True, # Battery level manager task
	shell    = True, # Shell with text editor task

	# Notifiers
	mqtt     = True, # Mqtt client task
	webhook  = True, # Webhook notification task
	pushover = True, # Pushover notification task

	# Servers and network
	ftp      = True, # Ftp server task
	http     = True, # Http server task
	telnet   = True, # Telnet server task
	ntp      = True, # Ntp synchronisation task
	wanip    = True, # Wanip periodically obtained task
	wifi     = True, # Wifi manager task

	# Motion and camera
	presence = True, # Presence of inoccupant task
	camera   = True, # Camera configuration
	motion   = True, # Motion detection task
	)
