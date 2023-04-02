# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" These classes are used to interact with domoticz or other application """
from server import notifier, httpclient
from tools import jsonconfig

class WebhookConfig(jsonconfig.JsonConfig):
	""" Configuration of the webhook """
	def __init__(self):
		""" Constructor """
		jsonconfig.JsonConfig.__init__(self)

		# Indicates if the presence detection is activated
		self.activated = False

		# Webhook when motion detected
		self.motion_detected = b""

		# Webhook when no motion detected
		self.no_motion_detected = b""

		# Webhook when the house contains its occupants
		self.inhabited_house = b""

		# Webhook when the house is empty
		self.empty_house = b""

class WebHook:
	""" Webhook """
	@staticmethod
	@notifier.Notifier.add()
	async def notify_message(notification):
		""" Notify message """
		config = WebhookConfig()
		if config.load() is False:
			config.save()

		if config.activated or notification.forced and notification.url is not None:
			if WebHook.notify_message not in notification.sent:
				result = await httpclient.HttpClient.request(method=b"GET", url=notification.url)
				if result is True:
					notification.sent.append(WebHook.notify_message)
			else:
				result = None
		else:
			result = None
		return result
