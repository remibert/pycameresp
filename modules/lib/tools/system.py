# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" System utilities functions """
import time
from tools import filesystem, logger

def reboot(message="Reboot"):
	""" Reboot command """
	logger.syslog(message)
	from tools.lang import RegionConfig
	region_config = RegionConfig()
	if region_config.load():
		region_config.current_time = time.time() + 8
		region_config.save()
	try:
		if filesystem.ismicropython():
			import camera
			camera.deinit()
	except:
		pass
	try:
		import machine
		machine.deepsleep(1000)
	except:
		pass
