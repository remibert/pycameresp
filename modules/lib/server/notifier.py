# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Class used to manage a list of notifier, and postpone notification if wifi station not yet connected """
# pylint:disable=consider-using-f-string
# pylint:disable=consider-using-enumerate
import uasyncio
import wifi.wifi
import wifi.station
import server.wanip
import server.httpclient
import tools.logger
import tools.strings
import tools.tasking
import tools.info
import tools.lang
import tools.date
import tools.topic
import tools.filesystem

class Notification:
	""" Notification message """
	def __init__(self, **kwargs):
		""" Notification constructor """
		self.topic   = kwargs.get("topic",  None)
		self.value   = kwargs.get("value",  None)
		self.message = kwargs.get("message",None)
		self.data    = kwargs.get("data",   None)
		self.forced  = kwargs.get("forced", False)
		self.display = kwargs.get("display",True)
		self.url     = kwargs.get("url",    None)
		self.sent    = []
		self.retry   = 0

class Notifier:
	""" Class used to manage a list of notifier, and postpone notification if wifi station not yet connected """
	notifiers = []
	postponed = []
	wake_up_event = None
	daily_callback = None
	one_per_day = None
	daily_notification = [False]

	@staticmethod
	def init():
		""" Initialize """
		if Notifier.wake_up_event is None:
			Notifier.wake_up_event = uasyncio.Event()

		if Notifier.daily_callback is None:
			Notifier.daily_callback = Notifier.default_daily_notifier

	@staticmethod
	def add():
		""" Add a callback on subscription """
		def add_function(function):
			Notifier.notifiers.append(function)
			return function
		return add_function

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
	def to_string(**kwargs):
		""" Convert notification into string """
		result = b""
		item = kwargs.get("message",None)
		if item is not None:
			result += b"msg='''%s''' "%tools.strings.tobytes(item)
		item = kwargs.get("topic",None)
		if item is not None:
			result += b"topic=%s "%tools.strings.tobytes(item)
		item = kwargs.get("value",None)
		if item is not None:
			result += b"value=%s "%tools.strings.tobytes(item)
		item = kwargs.get("data",None)
		if item is not None:
			result += b"len=%d "%len(item)
		return result

	@staticmethod
	def notify(**kwargs):
		""" Notify message for all notifier registered 
		topic   : topic name of notification
		message : message text 
		data    : binary buffer
		forced  : true to force the notification, false depend of configuration
		display : true to display in syslog, false hide in syslog 
		url     : url link for web hook
		enabled : true to enable notification, false to disable"""
		display = kwargs.get("display",True)
		enabled = kwargs.get("enabled",True)
		forced  = kwargs.get("forced",False)
		message = Notifier.to_string(**kwargs)

		tools.logger.syslog("Notification %s %s"%(tools.strings.tostrings(message), "" if enabled else "not sent"), display=display)

		if enabled or forced:
			# If postponed message list too long
			if len(Notifier.postponed) > 10:
				# Remove older
				notification = Notifier.postponed[0]
				tools.logger.syslog("Notification %s failed to send"%tools.strings.tostrings(notification.message), display=notification.display)
				del Notifier.postponed[0]
			# Add message into postponed list
			Notifier.postponed.append(Notification(**kwargs))
			Notifier.wake_up()
		else:
			return True

	@staticmethod
	async def flush():
		""" Flush postponed message if wan connected """
		# If wan available
		if wifi.wifi.Wifi.is_wan_available():
			result = True
			# Try to send message
			for notification in Notifier.postponed:
				for notifier in Notifier.notifiers:
					if len(Notifier.notifiers) > len(notification.sent):
						res = await notifier(notification)
						if res is False:
							result = False
							if notification.retry == 0:
								tools.logger.syslog("Cannot send notification")
							notification.retry += 1

			not_sent = []
			for notification in Notifier.postponed:
				if len(Notifier.notifiers) > len(notification.sent):
					if notification.retry < 32:
						not_sent.append(notification)

			Notifier.postponed = not_sent

	@staticmethod
	async def task():
		""" Run the task """
		Notifier.init()

		if Notifier.is_one_per_day() or Notifier.daily_notification[0] is True:
			Notifier.daily_notification[0] = False
			if Notifier.daily_callback:
				# pylint:disable=not-callable
				message = Notifier.daily_callback()
				Notifier.notify(topic=tools.topic.information, message=message)

		# If no notification should be sent
		await Notifier.flush()

		try:
			# Wait notification
			await uasyncio.wait_for(Notifier.wake_up_event.wait(), 11)
			# Clear event notification event
			Notifier.wake_up_event.clear()
		except:
			pass

	@staticmethod
	def daily_notify():
		""" Force the send of daily notification """ 
		Notifier.daily_notification[0] = True

	@staticmethod
	def is_one_per_day():
		""" Indicates if the action must be done on per day """
		current_date = tools.date.date_to_bytes()[:14]
		if Notifier.one_per_day is None or (current_date[-2:] == b"12" and current_date != Notifier.one_per_day):
			Notifier.one_per_day = current_date
			if tools.strings.ticks() > 30000:
				return True
		return False

	@staticmethod
	def default_daily_notifier():
		""" Return the default message notification """
		message = "\n - Lan Ip : %s\n"%wifi.station.Station.get_info()[0]
		message += " - Wan Ip : %s\n"%server.wanip.WanIp.wan_ip
		message += " - Uptime : %s\n"%tools.strings.tostrings(tools.info.uptime())
		message += " - %s : %s\n"%(tools.strings.tostrings(tools.lang.memory_label), tools.strings.tostrings(tools.info.meminfo()))
		message += " - %s : %s\n"%(tools.strings.tostrings(tools.lang.flash_label), tools.strings.tostrings(tools.info.flashinfo()))
		return message

	@staticmethod
	def set_daily_notifier(callback):
		""" Replace the daily notification (callback which return a string with message to notify) """
		Notifier.daily_notifier = callback

	@staticmethod
	def start():
		""" Start notifier task """
		tools.tasking.Tasks.create_monitor(Notifier.task)
