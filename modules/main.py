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

machine.freq(240000000)

# Can only be done once at boot before start the camera and sd card
onBattery   = Battery.isActivated()

# If the power supply is the mains
if onBattery == False:
	from tools import useful
	isPinWakeUp = False

	# Create asyncio loop
	loop = uasyncio.get_event_loop()

	# Html pages loader
	def pageLoader():
		# The html pages only loaded when the connection of http server is done
		# This reduces memory consumption if the server is not used
		import webpage
		from server.httpserver import HttpServer

		try:
			# Welcome page (can be suppressed)
			from welcome import welcomePage
		except ImportError as err:
			#print(useful.exception(err))
			pass

		try:
			# Sample page (can be suppressed)
			import sample
		except ImportError as err:
			#print(useful.exception(err))
			pass

	import server

	# Start all server (Http, Ftp, Telnet) and start wifi manager
	# If you set the last parameter to True it preloads the pages of the http server at startup
	server.start(loop=loop, pageLoader=pageLoader, preload=False, httpPort=80)
	isPinWakeUp = False
else:
	# Check if PIR detection
	isPinWakeUp = Battery.isPinWakeUp()
	print("Detection %s"%(isPinWakeUp))

	# Check the battery level and force deepsleep is to low
	Battery.protect()

	# Create asyncio loop
	loop = uasyncio.get_event_loop()

	from tools import useful


# If camera is available (required specific firmware)
if useful.iscamera():
	# Start motion detection (only used with ESP32CAM)
	import motion 
	motion.start(loop, onBattery, isPinWakeUp)

from shell.shell import asyncShell
loop.create_task(asyncShell())

# Run asyncio for ever
loop.run_forever()
