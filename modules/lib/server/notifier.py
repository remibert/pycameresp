# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Class used to manage a list of notifier, and postpone notification if wifi station not yet connected """
# pylint:disable=consider-using-f-string
# pylint:disable=consider-using-enumerate
import uasyncio
import wifi
from server.httpclient import *
from tools import logger,strings,tasking


class Notification:
	""" Notification message """
	def __init__(self, message, image, forced, display):
		""" Notification constructor """
		self.message = message
		self.image   = image
		self.forced  = forced
		self.display = display


class WebHook:
	""" Notification via webhook """
	def __init__(self, name, url):
		self.url = url
		self.name = name


class Notifier:
	""" Class used to manage a list of notifier, and postpone notification if wifi station not yet connected """
	notifiers = []
	postponed = []
	webhooks  = {}
	wake_up_event = None

	@staticmethod
	def init():
		""" Initialize """
		if Notifier.wake_up_event is None:
			Notifier.wake_up_event = uasyncio.Event()

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
	def wake_up():
		""" Wake up notifier it to perform tasks """
		Notifier.init()
		Notifier.wake_up_event.set()

	@staticmethod
	def notify(message, image=None, forced=False, display=True, enabled=True):
		""" Notify message for all notifier registered """
		logger.syslog("Notification '%s' %s"%(strings.tostrings(message), "" if enabled else "not sent"), display=display)

		if enabled or forced:
			# Add message into postponed list
			Notifier.postponed.append(Notification(message, image, forced, display))
			Notifier.wake_up()
		else:
			return True

	@staticmethod
	def webhook(name, url):
		""" Notify webhook """
		if len(url):
			logger.syslog("Webhook name='%s' url='%s'"%(name,strings.tostrings(url)))

			# Add message into postponed list
			Notifier.webhooks[name] = WebHook(name, url)
			Notifier.wake_up()

	@staticmethod
	async def flush():
		""" Flush postponed message if wan connected """
		result = False
		# If postponed message list too long
		if len(Notifier.postponed) > 10:
			# Remove older
			notification = Notifier.postponed[0]
			logger.syslog("Notification '%s' failed to send"%strings.tostrings(notification.message), display=notification.display)
			del Notifier.postponed[0]

		# If wan available
		if wifi.Wifi.is_wan_available():
			result = True
			wanOk = None

			# Try to send message
			for notifier in Notifier.notifiers:
				for notification in Notifier.postponed:
					res = await notifier(notification.message, notification.image, notification.forced, display=notification.display)
					if res is False:
						result = False
						wanOk = False
						break
					elif res is True:
						wanOk = True

			# If all message notified
			if result:
				Notifier.postponed.clear()

			# Call webhook
			for webhook in Notifier.webhooks.values():
				if await HttpClient.request(method=b"GET", url=webhook.url) is None:
					result = False

			# Clear all webhook
			Notifier.webhooks.clear()

			# If wan connected
			if wanOk is True:
				wifi.Wifi.wan_connected()
			# If wan problem detected
			if wanOk is False:
				wifi.Wifi.wan_disconnected()

			# If all message notified
			if result is False:
				logger.syslog("Cannot send notification")
		return result

	@staticmethod
	async def task():
		""" Run the task """
		# If no notification should be sent
		if len(Notifier.postponed) == 0 and len(Notifier.webhooks) == 0:
			Notifier.init()
			# Wait notification
			await Notifier.wake_up_event.wait()

			# Clear event notification event
			Notifier.wake_up_event.clear()
		# Flush all notifications postponed
		await Notifier.flush()

async def notifier_task():
	""" Notifier task """
	await tasking.task_monitoring(Notifier.task)
