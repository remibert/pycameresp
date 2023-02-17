# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to see the camera streaming """
from server.httpserver  import HttpServer
from server.httprequest import *
from server.server      import Server
from htmltemplate       import *
from video              import Camera
import uasyncio
from tools              import logger,tasking,info,watchdog

class Streaming:
	""" Management class of video streaming of the camera via an html page """
	streaming_id = [0]
	inactivity = [None]
	config = [None]
	durty = [False]

	@staticmethod
	def set_config(config):
		""" Set current configuration """
		Streaming.config[0] = config
		Streaming.durty[0] = True

	@staticmethod
	def get_config():
		""" Get current configuration """
		return Streaming.config[0]

	@staticmethod
	def is_durty():
		""" Indicates if the configuration changed """
		return Streaming.durty[0]

	@staticmethod
	def reset_durty():
		""" Reset the configuration changed flag """
		Streaming.durty[0] = False

	@staticmethod
	def get_html(request):
		""" Return streaming html part with javascript code """
		Streaming.activity()
		Streaming.streaming_id[0] += id(request)
		return Tag(b"""
		<p>
			<div style="position: relative;">
				<img id="video-stream" src="" width="100%%"/>
				<table id="zone_masking" style="position: absolute;top:0px" />
			</div>
		</p>
		<script>
			var streamUrl = document.location.protocol + "//" + document.location.hostname + ':%d';
			document.getElementById('video-stream').src = `${streamUrl}/camera/start?streaming_id=%d`;
		</script>"""%(request.port+1,Streaming.streaming_id[0]))

	@staticmethod
	def activity():
		""" User activity detected """
		if Streaming.inactivity[0]:
			Streaming.inactivity[0].stop()
			Streaming.inactivity[0] = None
		Streaming.inactivity[0] = tasking.Inactivity(Streaming.stop, duration=watchdog.LONG_WATCH_DOG, timer_id=1)

	@staticmethod
	def get_streaming_id():
		""" Return the current streaming id """
		return Streaming.streaming_id[0]

	@staticmethod
	def stop():
		""" Stop streaming """
		Streaming.streaming_id[0] += 1

@HttpServer.add_route(b'/camera/start', available=info.iscamera() and Camera.is_activated())
async def camera_start_streaming(request, response, args):
	""" Start video streaming """
	Server.slow_down()
	if request.name != "StreamingServer":
		return

	try:
		writer = None
		currentstreaming_id = int(request.params[b"streaming_id"])
		reserved = await Camera.reserve(request, timeout=20, suspension=15)
		if reserved:
			failed = False
			Camera.open()

			response.set_status(b"200")
			response.set_header(b"Content-Type"               ,b"multipart/x-mixed-replace")
			response.set_header(b"Transfer-Encoding"          ,b"chunked")
			response.set_header(b"Access-Control-Allow-Origin",b"*")

			await response.serialize(response.streamio)
			writer = response.streamio
			identifier = b"\r\n%x\r\n\r\n--%s\r\n\r\n"%(len(response.identifier) + 6, response.identifier)
			frame = b'%s36\r\nContent-Type: image/jpeg\r\nContent-Length: %8d\r\n\r\n\r\n%x\r\n'

			if filesystem.ismicropython():
				micropython = True
			else:
				micropython = False

			if Streaming.is_durty():
				Camera.configure(Streaming.get_config())
				Streaming.reset_durty()

			image = Camera.capture()
			length = len(image)
			try:
				await writer.write(frame%(b"", length, length))
				await writer.write(image)
			except Exception as err:
				failed = True
				currentstreaming_id = 0

			while currentstreaming_id == Streaming.get_streaming_id():
				if Streaming.is_durty():
					Camera.configure(Streaming.get_config())
					Streaming.reset_durty()
				image = Camera.capture()
				length = len(image)
				try:
					await writer.write(frame%(identifier, length, length))
					await writer.write(image)
				except Exception as err:
					failed = True
					break
				if micropython is False:
					await uasyncio.sleep(0.1)
			if failed is False:
				await writer.write(identifier)
		else:
			pass
	except Exception as err:
		logger.syslog(err)
	finally:
		if reserved:
			await Camera.unreserve(request)
		if writer:
			await writer.close()
