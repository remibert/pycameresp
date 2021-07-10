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

INACTIVITY=600000

class Streaming:
	""" Management class of video streaming of the camera via an html page """
	streamingId = [0]
	inactivityTimer = [None]
	config = [None]
	durty = [False]

	@staticmethod
	def setConfig(config):
		""" Set current configuration """
		Streaming.config [0] = config
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
	def getHtml(request):
		""" Return streaming html part with javascript code """
		Streaming.streamingId[0] += 1
		return Tag(b"""
		<p>
			<div style="position: relative;">
				<img id="video-stream" src=""/>
				<table id="zoneMasking" style="position: absolute;top:0px" />
			</div>
		</p>
		<script>
			window.onload = () =>
			{
				stopStreaming();
				setTimeout(() => { startStreaming();}, 100);
			}
			function startStreaming()
			{
				window.stop();
				var streamUrl = document.location.protocol + "//" + document.location.hostname + ':%d';
				document.getElementById('video-stream').src = `${streamUrl}/camera/start`;
				setTimeout(() => { stopStreaming(); }, %d);
			}
			function stopStreaming()
			{
				var xhttp = new XMLHttpRequest();
				xhttp.open("GET","camera/stop",true);
				xhttp.send();
			}
		</script>"""%(request.port+1,INACTIVITY))

	@staticmethod
	def inactivityTimeout():
		""" Suspend video streaming after delay """
		Streaming.streamingId[0] += 1

	@staticmethod
	def startInactivityTimer():
		""" Start inactivity timer for stop streaming video after delay """
		Streaming.stopInactivityTimer()
		Streaming.inactivityTimer[0] = machine.Timer(0)
		Streaming.inactivityTimer[0].init(period=INACTIVITY, mode=machine.Timer.ONE_SHOT, callback=Streaming.inactivityTimeout)

	@staticmethod
	def stopInactivityTimer():
		""" Stop inactivity timer """
		if Streaming.inactivityTimer[0]:
			Streaming.inactivityTimer[0].deinit()
			Streaming.inactivityTimer[0] = None

	@staticmethod
	def newStreamingId():
		""" Create new streaming id """
		Streaming.startInactivityTimer()
		Streaming.streamingId[0] += 1
		return Streaming.streamingId[0]

	@staticmethod
	def getStreamingId():
		""" Return the current streaming id """
		return Streaming.streamingId[0]

@HttpServer.addRoute('/camera/stop')
async def cameraStopStreaming(request, response, args):
	""" Stop video streaming """
	Streaming.stopInactivityTimer()
	await response.sendOk()

@HttpServer.addRoute('/camera/start')
async def cameraStartStreaming(request, response, args):
	""" Start video streaming """
	if request.name != "StreamingServer":
		print("Streaming ignored")
		return 

	try:
		print("Start streaming")
		reserved = await Camera.reserve(Streaming, timeout=5, suspension=5)
		if reserved:
			currentStreamingId = Streaming.newStreamingId()
			Camera.open()
			Camera.configure(Streaming.getConfig())

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

			image = Camera.capture()
			length = len(image)
			await writer.write(frame%(b"", length, length))
			await writer.write(image)
			# count = 0

			while currentStreamingId == Streaming.getStreamingId():
				if Streaming.isDurty():
					Camera.configure(Streaming.getConfig())
					Streaming.resetDurty()
				image = Camera.capture()
				length = len(image)
				await writer.write(frame%(identifier, length, length))
				await writer.write(image)
				if micropython == False:
					await uasyncio.sleep(0.1)
				# if count % 50 == 0:
				# 	print("Streaming %d"%count)
				# count += 1
	except Exception as err:
		print(useful.exception(err))
	finally:
		print("Stop streaming")
		if reserved:
			await Camera.unreserve(Streaming)
		await writer.close()
