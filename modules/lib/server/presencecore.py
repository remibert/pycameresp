# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Presence detection (determine if an occupant is present in the house) """
import time
import wifi.wifi
import server.ping
import server.notifier
import tools.lang
import tools.topic

class PresenceCore:
	""" Presence detection of smartphones """
	ABSENCE_TIMEOUT   = 1201
	NO_ANSWER_TIMEOUT = 607
	DNS_POLLING       = 67

	PING_TIMEOUT      = 0.5
	PING_COUNT        = 4

	detected = [False]
	last_time = 0
	last_dns_time = 0

	@staticmethod
	def set_detection(state):
		""" Force presence detection """
		PresenceCore.detected[0] = state

	@staticmethod
	def is_detected():
		""" Indicates if presence detected """
		return PresenceCore.detected[0]

	@staticmethod
	async def detect(presence_config, webhook_config):
		""" Detect the presence or not of smartphones """
		if PresenceCore.last_dns_time + PresenceCore.DNS_POLLING < time.time():
			PresenceCore.last_dns_time = time.time()
			sent,received,success = await server.ping.async_ping(wifi.wifi.Wifi.get_dns(), count=PresenceCore.PING_COUNT, timeout=PresenceCore.PING_TIMEOUT, quiet=True)

			if received == 0:
				wifi.wifi.Wifi.lan_disconnected()
			else:
				wifi.wifi.Wifi.lan_connected()

		presents = []
		current_detected = None
		smartphone_in_list = False

		for smartphone in presence_config.smartphones:
			# If smartphone present
			if smartphone != b"":
				smartphone_in_list = True

				# Ping smartphone
				sent,received,success = await server.ping.async_ping(smartphone, count=PresenceCore.PING_COUNT, timeout=PresenceCore.PING_TIMEOUT, quiet=True)

				# If a response received from smartphone
				if received > 0:
					presents.append(smartphone)
					PresenceCore.last_time = time.time()
					current_detected = True
					wifi.wifi.Wifi.lan_connected()

		# If no smartphones detected during a very long time
		if PresenceCore.last_time + PresenceCore.ABSENCE_TIMEOUT < time.time():
			# Nobody in the house
			current_detected = False

		# If smartphone detected
		if current_detected is True:
			# If no smartphone previously detected
			if PresenceCore.is_detected() != current_detected:
				# Notify the house is not empty
				msg = b""
				for present in presents:
					msg += b"%s "%present
				server.notifier.Notifier.notify(topic=tools.topic.presence_detected, value=tools.topic.value_on,  message=tools.lang.presence_of_s%(msg), enabled=presence_config.notify,url=webhook_config.inhabited_house)
				PresenceCore.set_detection(True)
		# If no smartphone detected
		elif current_detected is False:
			# If smartphone previously detected
			if PresenceCore.is_detected() != current_detected:
				# Notify the house in empty
				server.notifier.Notifier.notify(topic=tools.topic.presence_detected, value=tools.topic.value_off, message=tools.lang.empty_house, enabled=presence_config.notify,url=webhook_config.empty_house)
				PresenceCore.set_detection(False)

		# If all smartphones not responded during a long time
		if PresenceCore.last_time + PresenceCore.NO_ANSWER_TIMEOUT < time.time() and smartphone_in_list is True:
			# Set fast polling rate
			result = False
		else:
			# Reduce polling rate
			result = True
		return result
