# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" These classes are used to send notifications to smartphones, via the pushover application.
See https://www.pushover.net """

import sys
sys.path.append("lib")
from tools import useful
import uasyncio
from server.stream import *
from server.httprequest import *
from tools import jsonconfig

class PushOverConfig:
	""" Configuration of the pushover """
	def __init__(self):
		""" Constructor """
		self.activated = False
		self.token = b""
		self.user = b""

	def save(self, file = None):
		""" Save the configuration """
		result = jsonconfig.save(self, file)
		return result

	def update(self, params):
		""" Update configuration """
		result = jsonconfig.update(self, params)
		return result

	def load(self, file = None):
		""" Load configuration """
		result = jsonconfig.load(self, file)
		return result

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

	async def notify(self, message, image=None):
		""" Send a push over notication message, and if image is added it must be a jpeg buffer.
		message : the message of notification (bytes field not a string)
		image : the jpeg image or nothing (bytes field)"""
		try:
			# Open pushover connection
			reader,writer = await uasyncio.open_connection(useful.tostrings(self.host), self.port)
			streamio = Stream(reader, writer)

			# Create multipart request 
			request = HttpRequest(None)
			request.setMethod(b"POST")
			request.setPath  (b"/1/messages.json")
			request.setHeader(b"Host",self.host)
			request.setHeader(b"Accept-Encoding",b"gzip, deflate")
			request.setHeader(b"Accept",         b"*/*")
			request.setHeader(b"Connection",     b"keep-alive")
			request.setHeader(b"Content-Type",   b"multipart/form-data")
			
			# Add token in multipart request
			if self.token != None:
				request.addPart(PartText(b"token",self.token))
			
			# Add user in multipart request
			if self.user != None:
				request.addPart(PartText(b"user",self.user))
			
			 # Add message text in multipart request
			request.addPart(PartText(b"message", message))
	
			# Add image in multipart request
			if image != None:
				request.addPart(PartBin(b"attachment",b"image.jpg",image, b"image/jpeg"))

			# Send request to pushover
			await request.send(streamio)

			# Create response
			response = HttpResponse(streamio)

			# Receive response from pushover
			await response.receive(streamio)

			# If response failed
			if response.status != b"200":
				# Print error
				print("Notification failed to sent")

			# Close all connection with push over server
			writer.close()
			await writer.wait_closed()
			
		except Exception as err:
			# Display exception
			print("Notification exception")
			print(useful.exception(err))

async def asyncNotify(user, token, message, image=None):
	""" Asyncio notification function (only in asyncio) """
	notification = Notification(host=b"api.pushover.net", port=80, token=token, user=user)
	await notification.notify(message, image)

def notify(user, token, message, image=None):
	""" Notification function """
	loop = uasyncio.get_event_loop()
	loop.run_until_complete(asyncNotify(user=user, token=token, message=message, image=image))

async def notifyMessage(message, image = None, forced=False):
	""" Notify message """
	config = PushOverConfig()
	config.load()
	print("%s"%useful.tostrings(message))
	if config.activated or forced:
		await asyncNotify(config.user, config.token, message, image)

if __name__ == "__main__":
	config = pushoverconfig.PushOverConfig()
	config.load()
	notify(token=config.token, user=config.user, message = b"Hello")
