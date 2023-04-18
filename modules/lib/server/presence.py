# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Presence detection (determine if an occupant is present in the house) """
import wifi.wifi
import server.notifier
import server.webhook
import tools.logger
import tools.jsonconfig
import tools.lang
import tools.tasking
import tools.topic

class PresenceConfig(tools.jsonconfig.JsonConfig):
	""" Configuration class of presence detection """
	def __init__(self):
		tools.jsonconfig.JsonConfig.__init__(self)
		# Indicates if the presence detection is activated
		self.activated = False

		# Ip addresses of smartphones
		self.smartphones = [b"",b"",b"",b"",b""]

		# Notify presence
		self.notify = False

class Presence:
	""" Presence detection of smartphones """
	FAST_POLLING     = 7
	SLOW_POLLING     = 53
	core             = None
	polling_duration = 0
	presence_config  = None
	webhook_config   = None
	activated        = None

	@staticmethod
	def is_detected():
		""" Indicates if presence detected """
		if Presence.core is None:
			return False
		else:
			return Presence.core.is_detected()

	@staticmethod
	def init():
		""" Reload configuration if changed """
		if Presence.presence_config:
			if Presence.presence_config.refresh():
				tools.logger.syslog("Change presence config %s"%Presence.presence_config.to_string(), display=False)
			Presence.webhook_config.refresh()
		else:
			Presence.presence_config = PresenceConfig()
			Presence.presence_config.load_create()
			Presence.webhook_config = server.webhook.WebhookConfig()
			Presence.webhook_config.load_create()
			Presence.polling_duration = Presence.FAST_POLLING

	@staticmethod
	async def detect():
		""" Detect presence """
		if Presence.core is None:
			# pylint:disable=redefined-outer-name
			import server.presencecore
			Presence.core = server.presencecore.PresenceCore
		return await Presence.core.detect(Presence.presence_config, Presence.webhook_config)

	@staticmethod
	async def task():
		""" Run the task """
		Presence.init()

		# If configuration must be read
		if Presence.presence_config.activated is True and wifi.wifi.Wifi.is_lan_available():
			if await Presence.detect():
				# Reduce polling rate
				Presence.polling_duration = Presence.SLOW_POLLING
			else:
				# Set fast polling rate
				Presence.polling_duration = Presence.FAST_POLLING
		else:
			Presence.polling_duration = Presence.SLOW_POLLING
			Presence.core = None

		# If the presence detection change
		if Presence.activated != Presence.presence_config.activated:
			if Presence.presence_config.activated:
				server.notifier.Notifier.notify(topic=tools.topic.presence_detection, value=tools.topic.value_on,  message=tools.lang.presence_detection_on,  enabled=Presence.presence_config.notify)
			else:
				server.notifier.Notifier.notify(topic=tools.topic.presence_detection, value=tools.topic.value_off, message=tools.lang.presence_detection_off, enabled=Presence.presence_config.notify)
			Presence.activated = Presence.presence_config.activated

		# Wait before new ping
		await tools.tasking.Tasks.wait_resume(duration=Presence.polling_duration*1000, name="presence")
		return True

	@staticmethod
	def start():
		""" Start presence survey task """
		tools.tasking.Tasks.create_monitor(Presence.task)
