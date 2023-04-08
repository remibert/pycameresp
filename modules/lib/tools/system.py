# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" System utilities functions """
# pylint:disable=global-variable-not-assigned
import time
import tools.filesystem
import tools.logger
import tools.region

actions = []

def add_action(action):
	""" Add an action to do before the reboot """
	actions.append(action)

def reboot(message="Reboot"):
	""" Reboot command """
	global actions
	region_config = tools.region.RegionConfig.get()
	if region_config.load():
		region_config.current_time = time.time() + 8
		region_config.save()
	try:
		if tools.filesystem.ismicropython():
			import camera
			camera.deinit()
	except:
		pass

	if len(actions) > 0:
		tools.logger.syslog("Execute actions before reboot")

	for action in actions:
		try:
			action()
		except Exception as err:
			tools.logger.syslog(err)

	tools.logger.syslog(message)
	try:
		import machine
		machine.deepsleep(1000)
	except:
		pass
