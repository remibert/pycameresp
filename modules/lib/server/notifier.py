# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Class used to manage a list of notifier, and postpone notification if wifi station not yet connected """
from tools import useful
from wifi.station import Station

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
		if len(Notifier.notifiers) == 0 or Station.isActive() is False:
			# Wifi not connected the message is postponed
			Notifier.postponed.append([message, image, forced, display])

			# If postponed message list too long
			if len(Notifier.postponed) > 10:
				# Remove older
				message, image, forced, display = Notifier.postponed[0]
				useful.logError("Wifi not connected for : " + useful.tostrings(message), display=display)
				del Notifier.postponed[0]
		else:
			await Notifier.flush()
			result = True
			for notifier in Notifier.notifiers:
				res = await notifier(message, image, forced, display=display)
				if res == False:
					result = False

	@staticmethod
	async def flush():
		""" Flush postponed message if wan connected """
		if Station.isActive():
			for notification in Notifier.postponed:
				message, image, forced, display = notification
				for notifier in Notifier.notifiers:
					await notifier(message, image, forced, display=display)
			Notifier.postponed.clear()
