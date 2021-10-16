# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" These classes are used to send notifications to smartphones, via the pushover application.
See https://www.pushover.net """

import sys
sys.path.append("lib")
import uasyncio
from server.stream import *
from server.httprequest import *
import wifi
from tools import useful, jsonconfig

class PushOverConfig(jsonconfig.JsonConfig):
	""" Configuration of the pushover """
	def __init__(self):
		""" Constructor """
		jsonconfig.JsonConfig.__init__(self)
		self.activated = False
		self.token = b""
		self.user = b""

class Notification:
	""" Class that manages a push over notification """
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
		if wifi.Station.is_active():
			try:
				streamio = None
				# Open pushover connection
				reader,writer = await uasyncio.open_connection(useful.tostrings(self.host), self.port)
				streamio = Stream(reader, writer)

				# Create multipart request
				request = HttpRequest(None)
				request.set_method(b"POST")
				request.set_path  (b"/1/messages.json")
				request.set_header(b"Host",self.host)
				request.set_header(b"Accept-Encoding",b"gzip, deflate")
				request.set_header(b"Accept",         b"*/*")
				request.set_header(b"Connection",     b"keep-alive")
				request.set_header(b"Content-Type",   b"multipart/form-data")

				# Add token in multipart request
				if self.token is not None:
					request.add_part(PartText(b"token",self.token))

				# Add user in multipart request
				if self.user is not None:
					request.add_part(PartText(b"user",self.user))

				# Add message text in multipart request
				request.add_part(PartText(b"message", message))

				# Add image in multipart request
				if image is not None:
					request.add_part(PartBin(b"attachment",b"image.jpg",image, b"image/jpeg"))

				# Send request to pushover
				await request.send(streamio)

				# Create response
				response = HttpResponse(streamio)

				# Receive response from pushover
				await response.receive(streamio)

				# If response failed
				if response.status != b"200":
					# Print error
					useful.syslog("Notification failed to sent", display=display)

				# Close all connection with push over server
				result = True
			except Exception as err:
				useful.syslog(err)
			finally:
				if streamio:
					await streamio.close()
		else:
			useful.syslog("Notification not sent : wifi not connected", display=display)
		return result

async def async_notify(user, token, message, image=None, display=True):
	""" Asyncio notification function (only in asyncio) """
	notification = Notification(host=b"api.pushover.net", port=80, token=token, user=user)
	return await notification.notify(b"%s : %s"%(wifi.Station.get_hostname(), useful.tobytes(message)), image, display)

def notify(user, token, message, image=None):
	""" Notification function """
	loop = uasyncio.get_event_loop()
	loop.run_until_complete(async_notify(user=user, token=token, message=message, image=image))

async def notify_message(message, image = None, forced=False, display=True):
	""" Notify message """
	config = PushOverConfig()
	if config.load() is False:
		config.save()

	if config.activated or forced:
		result = await async_notify(config.user, config.token, message, image, display=True)
	else:
		result = None
	return result
