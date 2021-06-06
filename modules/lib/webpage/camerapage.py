# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to see the camera streaming """
from server.httpserver import HttpServer
from htmltemplate import *
from webpage import *
from server.httprequest import *
from tools import useful
from video import CameraConfig, Camera
import uasyncio

cameraStreamingId = 0
cameraConfig = CameraConfig()
INACTIVITY=600000
@HttpServer.addRoute(b'/camera', title=b"Camera", index=100)
async def cameraPage(request, response, args):
	""" Camera streaming page """
	global cameraStreamingId
	cameraStreamingId += 1
	framesizes = []

	for size in [b"1600x1200",b"1280x1024",b"1024x768",b"800x600",b"640x480",b"400x296",b"320x240",b"240x176",b"160x120"  ]:
		framesizes.append(Option(value=size, text=size, selected= True if cameraConfig.framesize == size else False))
	page = mainFrame(request, response, args, b"Camera",
		Tag(b"""
<p>
	<figure>
		<div id="container-stream" class="display: none;">
			<img id="video-stream" src="">
		</div>
	</figure>

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
			document.getElementById('container-stream').style.display = "block";
			setTimeout(() => { stopStreaming(); }, %d);
		}
		function stopStreaming()
		{
			var xhttp = new XMLHttpRequest();
			xhttp.open("GET","camera/stop",true);
			xhttp.send();
		}
	</script>
</p>"""%(request.port+1,INACTIVITY)),
				ComboCmd(framesizes, text=b"Resolution", path=b"camera/configure", name=b"framesize"),
				SliderCmd(           text=b"Quality"   , path=b"camera/configure", name=b"quality",    min=b"10", max=b"63", step=b"1", value=b"%d"%cameraConfig.quality),
				SliderCmd(           text=b"Brightness", path=b"camera/configure", name=b"brightness", min=b"-2", max=b"2" , step=b"1", value=b"%d"%cameraConfig.brightness),
				SliderCmd(           text=b"Contrast"  , path=b"camera/configure", name=b"contrast"  , min=b"-2", max=b"2" , step=b"1", value=b"%d"%cameraConfig.contrast),
				SliderCmd(           text=b"Saturation", path=b"camera/configure", name=b"saturation", min=b"-2", max=b"2" , step=b"1", value=b"%d"%cameraConfig.saturation),
				SwitchCmd(           text=b"H-Mirror"  , path=b"camera/configure", name=b"hmirror"   , checked=cameraConfig.hmirror),
				SwitchCmd(           text=b"V-Flip"    , path=b"camera/configure", name=b"vflip"     , checked=cameraConfig.vflip))
	await response.sendPage(page)

@HttpServer.addRoute(b'/camera/configure')
async def cameraConfigure(request, response, args):
	""" Real time camera configuration """
	print(useful.tostrings(b"%s=%s"%(request.params[b"name"],request.params[b"value"])))
	cameraConfig.update(request.params)
	if Camera.isReserved():
		startInactivityTimer()
		Camera.configure(cameraConfig)
	await response.sendOk()

@HttpServer.addRoute('/camera/stop')
async def cameraStopStreaming(request, response, args):
	""" Stop video streaming """
	global cameraStreamingId 
	cameraStreamingId += 1
	stopInactivityTimer()
	await response.sendOk()

def inactivityTimeoutStreaming(param=None):
	""" Suspend video streaming after delay """
	global cameraStreamingId
	cameraStreamingId += 1

inactivityTimer = None
def startInactivityTimer():
	""" Start inactivity timer for stop streaming video after delay """
	global inactivityTimer
	stopInactivityTimer()
	inactivityTimer = machine.Timer(0)
	inactivityTimer.init(period=INACTIVITY, mode=machine.Timer.ONE_SHOT, callback=inactivityTimeoutStreaming)

def stopInactivityTimer():
	""" Stop inactivity timer """
	global inactivityTimer
	if inactivityTimer:
		inactivityTimer.deinit()
		inactivityTimer = None

@HttpServer.addRoute('/camera/start')
async def cameraStartStreaming(request, response, args):
	""" Start video streaming """
	global cameraConfig, cameraStreamingId
	
	if request.name != "StreamingServer":
		print("Streaming ignored")
		return 

	try:
		print("Start streaming")
		cameraStreamingId += 1
		currentStreamingId = cameraStreamingId

		startInactivityTimer()
		Camera.open()
		Camera.reserve()
		Camera.configure(cameraConfig)

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

		while currentStreamingId == cameraStreamingId:
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
		Camera.unreserve()
		await writer.close()
