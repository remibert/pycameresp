# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Presence detection (determine if an occupant is present in the house) """
import time
import wifi
from server.ping import async_ping
from server.notifier import Notifier
from server.server import Server
from tools import useful, jsonconfig, lang, tasking

class PresenceConfig(jsonconfig.JsonConfig):
	""" Configuration class of presence detection """
	def __init__(self):
		jsonconfig.JsonConfig.__init__(self)
		# Indicates if the presence detection is activated
		self.activated = False

		# Ip addresses of smartphones
		self.smartphones = [b"",b"",b"",b"",b""]

		# Notify presence
		self.notify = True

class Presence:
	""" Presence detection of smartphones """
	ABSENCE_TIMEOUT   = 1201
	NO_ANSWER_TIMEOUT = 607
	FAST_POLLING      = 2.
	SLOW_POLLING      = 53
	DNS_POLLING       = 67

	PING_TIMEOUT      = 0.5
	PING_COUNT        = 4

	detected = [False]

	@staticmethod
	def is_detected():
		""" Indicates if presence detected """
		return Presence.detected[0]

	@staticmethod
	def set_detection(state):
		""" Force presence detection """
		Presence.detected[0] = state

	@staticmethod
	def init():
		""" Initialize the task """
		Presence.readConfig = 0.
		Presence.pollingDuration = Presence.FAST_POLLING
		Presence.config = PresenceConfig()
		Presence.activated = None
		Presence.lastTime = 0
		Presence.lastDnsTime = 0
		Presence.detected[0] = False
		Presence.configRefreshCounter = 0

	@staticmethod
	async def task():
		""" Run the task """
		# If configuration must be read
		if Presence.config:
			if Presence.configRefreshCounter % 7 == 0 or Presence.pollingDuration == Presence.SLOW_POLLING:
				if Presence.config.is_changed():
					if Presence.config.load() is False:
						Presence.config.save()
					useful.syslog("Change presence config %s"%Presence.config.to_string(), display=False)
			Presence.configRefreshCounter += 1

		if Presence.config.activated is True and wifi.Wifi.is_lan_available():
			if Presence.lastDnsTime + Presence.DNS_POLLING < time.time():
				Presence.lastDnsTime = time.time()
				sent,received,success = await async_ping(wifi.Wifi.get_dns(), count=Presence.PING_COUNT, timeout=Presence.PING_TIMEOUT, quiet=True)

				if received == 0:
					wifi.Wifi.lan_disconnected()
				else:
					wifi.Wifi.lan_connected()
		if Presence.config.activated is True and wifi.Wifi.is_lan_available():
			presents = []
			currentDetected = None
			smartphoneInList = False

			for smartphone in Presence.config.smartphones:
				# If smartphone present
				if smartphone != b"":
					smartphoneInList = True

					# Ping smartphone
					sent,received,success = await async_ping(smartphone, count=Presence.PING_COUNT, timeout=Presence.PING_TIMEOUT, quiet=True)

					# If a response received from smartphone
					if received > 0:
						presents.append(smartphone)
						Presence.lastTime = time.time()
						currentDetected = True
						wifi.Wifi.lan_connected()

			# If no smartphones detected during a very long time
			if Presence.lastTime + Presence.ABSENCE_TIMEOUT < time.time():
				# Nobody in the house
				currentDetected = False

			# If smartphone detected
			if currentDetected is True:
				# If no smartphone previously detected
				if Presence.is_detected() != currentDetected:
					# Notify the house is not empty
					msg = b""
					for present in presents:
						msg += b"%s "%present
					if Presence.config.notify:
						await Notifier.notify(lang.presence_of_s%(msg))
					Presence.set_detection(True)
			# If no smartphone detected
			elif currentDetected is False:
				# If smartphone previously detected
				if Presence.is_detected() != currentDetected:
					# Notify the house in empty
					if Presence.config.notify:
						await Notifier.notify(lang.empty_house)
					Presence.set_detection(False)

			# If all smartphones not responded during a long time
			if Presence.lastTime + Presence.NO_ANSWER_TIMEOUT < time.time() and smartphoneInList is True:
				# Set fast polling rate
				Presence.pollingDuration = Presence.FAST_POLLING
			else:
				# Reduce polling rate
				Presence.pollingDuration = Presence.SLOW_POLLING
		else:
			Presence.pollingDuration = Presence.SLOW_POLLING
			Presence.set_detection(False)

		# If the presence detection change
		if Presence.activated != Presence.config.activated:
			if Presence.config.notify:
				if Presence.config.activated:
					await Notifier.notify(lang.presence_detection_on)
				else:
					await Notifier.notify(lang.presence_detection_off)

			Presence.activated = Presence.config.activated

		# Wait before new ping
		await Server.wait_resume(Presence.pollingDuration)
		return True

async def detect_presence():
	""" Detect the presence of occupants of the housing and automatically suspend the detection (ping the ip of occupants smartphones) """
	Presence.init()
	await tasking.task_monitoring(Presence.task)
