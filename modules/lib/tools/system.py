# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" System utilities functions """
# pylint:disable=global-variable-not-assigned
import time
from tools import filesystem, logger

actions = []

def add_action(action):
	""" Add an action to do before the reboot """
	actions.append(action)

def reboot(message="Reboot"):
	""" Reboot command """
	global actions
	from tools import region
	region_config = region.RegionConfig.get()
	if region_config.load():
		region_config.current_time = time.time() + 8
		region_config.save()
	try:
		if filesystem.ismicropython():
			import camera
			camera.deinit()
	except:
		pass

	if len(actions) > 0:
		logger.syslog("Execute actions before reboot")

	for action in actions:
		try:
			action()
		except Exception as err:
			logger.syslog(err)

	logger.syslog(message)
	try:
		import machine
		machine.deepsleep(1000)
	except:
		pass
