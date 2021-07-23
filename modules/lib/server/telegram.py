# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" These classes are used to send notifications to smartphones, via the telegram application.
See https://telegram.org """

import sys
sys.path.append("lib")
from tools import useful
import uasyncio
from server.stream import *
from server.httprequest import *
from tools import jsonconfig
import wifi

class TelegramConfig(jsonconfig.JsonConfig):
	""" Configuration of the telegram """
	def __init__(self):
		""" Constructor """
		jsonconfig.JsonConfig.__init__(self)
		self.activated = False
		self.botToken = b""
		self.chatId = b""


class Notification:
	""" Class that manages a telegram notification """
	def __init__(self, host, port, botToken=None, chatId=None):
		""" Constructor
		host : hostname of telegram server (b"api.telegram.org")
		port : port of telegram server (80)
		botToken : bot token (you must create it on the web site http://telegram.org) 
		chatId : chat id (you must create it on the web site http://telegram.org) """
		self.botToken = botToken
		self.chatId  = chatId
		self.host  = host
		self.port  = port

	async def notify(self, message, image=None):
		""" Send telegram notication message, and if image is added it must be a jpeg buffer.
		message : the message of notification (bytes field not a string)
		image : the jpeg image or nothing (bytes field)"""
		if wifi.Station.isActive():
			try:
				# Open connection
				reader,writer = await uasyncio.open_connection(useful.tostrings(self.host), self.port, ssl=True)
				streamio = Stream(reader, writer)

				# Create multipart request 
				request = HttpRequest(None)
				request.setMethod(b"POST")
				if image == None:
					request.setPath  (b"/bot%s/sendMessage"%self.botToken)
				else:
					request.setPath  (b"/bot%s/sendPhoto"%self.botToken)
				request.setHeader(b"Host",self.host)
				request.setHeader(b"Accept-Encoding",b"gzip, deflate")
				request.setHeader(b"Accept",         b"*/*")
				request.setHeader(b"Connection",     b"keep-alive")
				request.setHeader(b"Content-Type",   b"multipart/form-data")
				
				# Add chatId in multipart request
				if self.chatId != None:
					request.addPart(PartText(b"chat_id",self.chatId))
				
				# Add image in multipart request
				if image != None:
					request.addPart(PartBin(b"photo",b"image.jpg",image, b"image/jpeg"))

					# Add message text in multipart request
					request.addPart(PartText(b"caption", message))
				else:
					# Add message text in multipart request
					request.addPart(PartText(b"text", message))

				# Send request
				await request.send(streamio)

				# Create response
				response = HttpResponse(streamio)

				# Receive response
				await response.receive(streamio)

				# If response failed
				if response.status != b"200":
					# Print error
					print("Notification failed to sent")

				# Close all connection
				writer.close()
				await writer.wait_closed()
				
			except Exception as err:
				useful.exception(err)
		else:
			print("Notification not sent : wifi not connected")

async def asyncNotify(chatId, botToken, message, image=None):
	""" Asyncio notification function (only in asyncio) """
	notification = Notification(host=b"api.telegram.org", port=443, botToken=botToken, chatId=chatId)
	await notification.notify(b"%s : %s"%(wifi.Station.getHostname(), message), image)

def notify(chatId, botToken, message, image=None):
	""" Notification function """
	loop = uasyncio.get_event_loop()
	loop.run_until_complete(asyncNotify(chatId=chatId, botToken=botToken, message=message, image=image))

async def notifyMessage(message, image = None, forced=False):
	""" Notify message """
	config = TelegramConfig()
	config.load()
	print("%s"%useful.tostrings(message))
	if config.activated or forced:
		await asyncNotify(config.chatId, config.botToken, message, image)

if __name__ == "__main__":
	config = telegram.TelegramConfig()
	config.load()
	notify(botToken=config.botToken, chatId=config.chatId, message = b"Hello")
