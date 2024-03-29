# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" These classes are used to send notifications to smartphones, via the pushover application.
See https://www.pushover.net """
# pylint:disable=wrong-import-position
import uasyncio
import server.stream
import server.notifier
import server.httprequest
import wifi.wifi
import tools.logger
import tools.jsonconfig
import tools.strings

class PushOverConfig(tools.jsonconfig.JsonConfig):
	""" Configuration of the pushover """
	def __init__(self):
		""" Constructor """
		tools.jsonconfig.JsonConfig.__init__(self)
		self.activated = False
		self.token = b""
		self.user = b""

class PushOver:
	""" Class that manages a push over notification """
	config = None
	def __init__(self, host, port, token=None, user=None):
		""" Constructor
		host : hostname of pushover (b"api.pushover.net")
		port : port of pushover (80)
		token : pushover token (you must create it on the web site http://www.pushover.net)
		user : pushover user (you must create it on the web site http://www.pushover.net) """
		self.token = token
		self.user  = user
		self.host  = host
		self.port  = port

	async def notify(self, message, image=None, display=True):
		""" Send a push over notication message, and if image is added it must be a jpeg buffer.
		message : the message of notification (bytes field not a string)
		image : the jpeg image or nothing (bytes field)"""
		result = False
		if wifi.station.Station.is_active():
			try:
				streamio = None
				# Open pushover connection
				reader,writer = await uasyncio.open_connection(tools.strings.tostrings(self.host), self.port)
				streamio = server.stream.Stream(reader, writer)

				# Create multipart request
				request = server.httprequest.HttpRequest(None)
				request.set_method(b"POST")
				request.set_path  (b"/1/messages.json")
				request.set_header(b"Host",self.host)
				request.set_header(b"Accept",         b"*/*")
				request.set_header(b"Connection",     b"keep-alive")
				request.set_header(b"Content-Type",   b"multipart/form-data")

				# Add token in multipart request
				if self.token is not None:
					request.add_part(server.httprequest.PartText(b"token",self.token))

				# Add user in multipart request
				if self.user is not None:
					request.add_part(server.httprequest.PartText(b"user",self.user))

				# Add message text in multipart request
				request.add_part(server.httprequest.PartText(b"message", message))

				# Add image in multipart request
				if image is not None:
					request.add_part(server.httprequest.PartBin(b"attachment",b"image.jpg",image, b"image/jpeg"))

				# Send request to pushover
				await request.send(streamio)

				# Create response
				response = server.httprequest.HttpResponse(streamio)

				# Receive response from pushover
				await response.receive(streamio)

				# If response failed
				if response.status != b"200":
					# Print error
					tools.logger.syslog("Notification failed to sent", display=display)

				# Close all connection with push over server
				result = True
				wifi.wifi.Wifi.wan_connected()
			except Exception as err:
				wifi.wifi.Wifi.wan_disconnected()
				tools.logger.syslog(err)
			finally:
				if streamio:
					await streamio.close()
		else:
			tools.logger.syslog("Notification not sent : wifi not connected", display=display)
		return result

	@staticmethod
	@server.notifier.Notifier.add()
	async def notify_message(notification):
		""" Notify message """
		if PushOver.config is None:
			PushOver.config = PushOverConfig()
			PushOver.config.load_create()
		else:
			PushOver.config.refresh()

		if PushOver.config.activated or notification.forced:
			if notification.message is not None or notification.data is not None:
				if PushOver.notify_message not in notification.sent:
					result = await async_notify(PushOver.config.user, PushOver.config.token, notification.message, notification.data, display=notification.display)
					if result is True:
						notification.sent.append(PushOver.notify_message)
				else:
					result = True
			else:
				result = True
		else:
			result = True
		return result

async def async_notify(user, token, message, image=None, display=True):
	""" Asyncio notification function (only in asyncio) """
	notification = PushOver(host=b"api.pushover.net", port=80, token=token, user=user)
	return await notification.notify(tools.strings.tobytes(message), image, display)

def notify(user, token, message, image=None):
	""" Notification function """
	loop = uasyncio.get_event_loop()
	loop.run_until_complete(async_notify(user=user, token=token, message=message, image=image))
