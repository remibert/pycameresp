# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Class used to manage a list of notifier, and postpone notification if wifi station not yet connected """
# pylint:disable=consider-using-enumerate
import wifi
from tools import useful

class Notifier:
	""" Class used to manage a list of notifier, and postpone notification if wifi station not yet connected """
	notifiers = []
	postponed = []

	@staticmethod
	def add(callback):
		""" Add notifier callback """
		Notifier.notifiers.append(callback)

	@staticmethod
	def remove(callback):
		""" Remove notifier callback """
		for i in range(len(Notifier.notifiers)):
			if Notifier.notifiers[i] == callback:
				del Notifier.notifiers[i]
				break

	@staticmethod
	def is_empty():
		""" Indicates that no notifier registered or not """
		if len(Notifier.notifiers) == 0:
			return True
		return False

	@staticmethod
	async def notify(message, image = None, forced=False, display=True):
		""" Notify message for all notifier registered """
		result = True
		useful.syslog("Notification '%s'"%useful.tostrings(message), display=display)

		# Add message into postponed list
		Notifier.postponed.append([message, image, forced, display])

		# Try to send all message postponed
		return await Notifier.flush()

	@staticmethod
	async def flush():
		""" Flush postponed message if wan connected """
		result = False
		# If postponed message list too long
		if len(Notifier.postponed) > 10:
			# Remove older
			message, image, forced, display = Notifier.postponed[0]
			useful.syslog("Notification '%s' failed to send"%useful.tostrings(message), display=display)
			del Notifier.postponed[0]

		# If wan available
		if wifi.Wifi.is_wan_available():
			result = True
			wanOk = None

			# Try to send message
			for notifier in Notifier.notifiers:
				for notification in Notifier.postponed:
					message, image, forced, display = notification
					res = await notifier(message, image, forced, display=display)
					if res is False:
						result = False
						wanOk = False
						break
					elif res is True:
						wanOk = True

			# If wan connected
			if wanOk is True:
				wifi.Wifi.wan_connected()
			# If wan problem detected
			if wanOk is False:
				wifi.Wifi.wan_disconnected()

			# If all message notified
			if result:
				Notifier.postponed.clear()
			else:
				useful.syslog("Cannot send notification")
		return result
