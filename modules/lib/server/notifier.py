# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Class used to manage a list of notifier, and postpone notification if wifi station not yet connected """
from tools import useful
from wifi.station import Station

class Notifier:
	""" Class used to manage a list of notifier, and postpone notification if wifi station not yet connected """
	notifiers = []
	postponed = []
	status    = [0]

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
	def isEmpty():
		""" Indicates that no notifier registered or not """
		if len(Notifier.notifiers) == 0:
			return True
		return False

	@staticmethod
	async def notify(message, image = None, forced=False, display=True):
		""" Notify message for all notifier registered """
		result = True
		useful.logError(message, display=display)

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
			useful.logError("Wifi not connected for : " + useful.tostrings(message), display=display)
			del Notifier.postponed[0]

		if Station.isActive():
			result = True
			# Try to send message
			for notification in Notifier.postponed:
				message, image, forced, display = notification

				for notifier in Notifier.notifiers:
					if await notifier(message, image, forced, display=display) == False:
						useful.logError("Cannot send notification")
						result = False
						
			# If all message sent clear all
			if result:
				Notifier.status[0] = 1
				Notifier.postponed.clear()
			else:
				Notifier.status[0] = -1

		return result

	@staticmethod
	def getStatus():
		""" Get the status of notifier (0:not connected, 1:success, -1:failed) """
		return Notifier.status[0]

