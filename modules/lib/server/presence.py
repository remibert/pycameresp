# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Presence detection (determine if an occupant is present in the house) """
import wifi
from server.notifier import Notifier
from server.server import Server
from server.webhook import WebhookConfig
from tools import logger,jsonconfig,lang,tasking

class PresenceConfig(jsonconfig.JsonConfig):
	""" Configuration class of presence detection """
	def __init__(self):
		jsonconfig.JsonConfig.__init__(self)
		# Indicates if the presence detection is activated
		self.activated = False

		# Ip addresses of smartphones
		self.smartphones = [b"",b"",b"",b"",b""]

		# Notify presence
		self.notify = False

class Presence:
	""" Presence detection of smartphones """
	FAST_POLLING      = 7.
	SLOW_POLLING      = 53
	presencecore     = None

	@staticmethod
	def is_detected():
		""" Indicates if presence detected """
		if Presence.presencecore is None:
			return False
		else:
			return Presence.presencecore.is_detected()

	@staticmethod
	def init():
		""" Initialize the task """
		Presence.polling_duration = Presence.FAST_POLLING
		Presence.config = PresenceConfig()
		Presence.webhook = WebhookConfig()
		Presence.activated = None
		Presence.refresh_config = 0

	@staticmethod
	def reload_config():
		""" Reload configuration if changed """
		if Presence.config:
			if Presence.refresh_config % 7 == 0 or Presence.polling_duration == Presence.SLOW_POLLING:
				if Presence.config.is_changed():
					if Presence.config.load() is False:
						Presence.config.save()
					logger.syslog("Change presence config %s"%Presence.config.to_string(), display=False)

				if Presence.webhook.is_changed():
					if Presence.webhook.load() is False:
						Presence.webhook.save()

			Presence.refresh_config += 1

	@staticmethod
	async def detect():
		""" Detect presence """
		if Presence.presencecore is None:
			import server.presencecore
			Presence.presencecore = server.presencecore.PresenceCore
		return await Presence.presencecore.detect(Presence.config, Presence.webhook)

	@staticmethod
	async def task():
		""" Run the task """
		Presence.reload_config()

		# If configuration must be read
		if Presence.config.activated is True and wifi.Wifi.is_lan_available():
			if await Presence.detect():
				# Reduce polling rate
				Presence.polling_duration = Presence.SLOW_POLLING
			else:
				# Set fast polling rate
				Presence.polling_duration = Presence.FAST_POLLING
		else:
			Presence.polling_duration = Presence.SLOW_POLLING
			Presence.presencecore = None

		# If the presence detection change
		if Presence.activated != Presence.config.activated:
			if Presence.config.activated:
				Notifier.notify(lang.presence_detection_on, enabled=Presence.config.notify)
			else:
				Notifier.notify(lang.presence_detection_off, enabled=Presence.config.notify)

			Presence.activated = Presence.config.activated

		# Wait before new ping
		await Server.wait_resume(Presence.polling_duration, name="presence")
		return True

async def presence_task():
	""" Detect the presence of occupants of the housing and automatically suspend the detection (ping the ip of occupants smartphones) """
	Presence.init()
	await tasking.task_monitoring(Presence.task)
