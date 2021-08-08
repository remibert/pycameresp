# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to see the camera streaming """
from server.httpserver import HttpServer
from htmltemplate import *
from webpage import *
from server.httprequest import *
from tools import useful
from video import Camera
import uasyncio

class Streaming:
	""" Management class of video streaming of the camera via an html page """
	streamingId = [0]
	inactivity = [None]
	config = [None]
	durty = [False]

	@staticmethod
	def setConfig(config):
		""" Set current configuration """
		Streaming.config[0] = config
		Streaming.durty[0] = True

	@staticmethod
	def getConfig():
		""" Get current configuration """
		return Streaming.config[0]

	@staticmethod
	def isDurty():
		""" Indicates if the configuration changed """
		return Streaming.durty[0]

	@staticmethod
	def resetDurty():
		""" Reset the configuration changed flag """
		Streaming.durty[0] = False

	@staticmethod
	def getHtml(request, width=None, height=None):
		""" Return streaming html part with javascript code """
		Streaming.activity()
		Streaming.streamingId[0] += id(request)
		if width != None and height != None:
			size = b'width="%d" height="%d"'%(width, height)
		else:
			size = b""
		return Tag(b"""
		<p>
			<div style="position: relative;">
				<img id="video-stream" src="" %s/>
				<table id="zoneMasking" style="position: absolute;top:0px" />
			</div>
		</p>
		<script>
			var streamUrl = document.location.protocol + "//" + document.location.hostname + ':%d';
			document.getElementById('video-stream').src = `${streamUrl}/camera/start?streamingid=%d`;
		</script>"""%(size, request.port+1,Streaming.streamingId[0]))

	@staticmethod
	def inactivityTimeout(timer):
		""" Suspend video streaming after delay """
		Streaming.streamingId[0] += 1

	@staticmethod
	def activity():
		""" User activity detected """
		if Streaming.inactivity[0]:
			Streaming.inactivity[0].stop()
			Streaming.inactivity[0] = None
		Streaming.inactivity[0] = useful.Inactivity(Streaming.inactivityTimeout, duration=useful.LONG_WATCH_DOG, timerId=1)

	@staticmethod
	def getStreamingId():
		""" Return the current streaming id """
		return Streaming.streamingId[0]

@HttpServer.addRoute(b'/camera/start', available=useful.iscamera())
async def cameraStartStreaming(request, response, args):
	""" Start video streaming """
	if request.name != "StreamingServer":
		return 

	try:
		writer = None
		currentStreamingId = int(request.params[b"streamingid"])
		reserved = await Camera.reserve(request, timeout=20, suspension=5)
		print("Start streaming %d"%currentStreamingId)
		if reserved:
			Camera.open()

			response.setStatus(b"200")
			response.setHeader(b"Content-Type"               ,b"multipart/x-mixed-replace")
			response.setHeader(b"Transfer-Encoding"          ,b"chunked")
			response.setHeader(b"Access-Control-Allow-Origin",b"*")

			await response.serialize(response.streamio)
			writer = response.streamio
			identifier = b"\r\n%x\r\n\r\n--%s\r\n\r\n"%(len(response.identifier) + 6, response.identifier)
			frame = b'%s36\r\nContent-Type: image/jpeg\r\nContent-Length: %8d\r\n\r\n\r\n%x\r\n'

			if useful.ismicropython():
				micropython = True
			else:
				micropython = False

			if Streaming.isDurty():
				Camera.configure(Streaming.getConfig())
				Streaming.resetDurty()

			image = Camera.capture()
			length = len(image)
			try:
				await writer.write(frame%(b"", length, length))
				await writer.write(image)
			except:
				currentStreamingId = 0

			while currentStreamingId == Streaming.getStreamingId():
				if Streaming.isDurty():
					Camera.configure(Streaming.getConfig())
					Streaming.resetDurty()
				image = Camera.capture()
				length = len(image)
				try:
					await writer.write(frame%(identifier, length, length))
					await writer.write(image)
				except:
					break
				if micropython == False:
					await uasyncio.sleep(0.1)
	except Exception as err:
		useful.exception(err)
	finally:
		if reserved:
			print("End streaming %d"%currentStreamingId)
			await Camera.unreserve(request)
		if writer:
			await writer.close()
