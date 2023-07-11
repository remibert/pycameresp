# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" These classes are used to interact with domoticz or other application """
import server.notifier
import server.httpclient
import tools.jsonconfig

class WebhookConfig(tools.jsonconfig.JsonConfig):
	""" Configuration of the webhook """
	def __init__(self):
		""" Constructor """
		tools.jsonconfig.JsonConfig.__init__(self)

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
	config = None
	@staticmethod
	@server.notifier.Notifier.add()
	async def notify_message(notification):
		""" Notify message """
		if WebHook.config is None:
			WebHook.config = WebhookConfig()
			if WebHook.config.load() is False:
				WebHook.config.save()
		else:
			WebHook.config.refresh()

		result = True
		if WebHook.config.activated or notification.forced and notification.url is not None:
			if WebHook.notify_message not in notification.sent:
				result = await server.httpclient.HttpClient.request(method=b"GET", url=notification.url)
				if result is True:
					notification.sent.append(WebHook.notify_message)
		return result
