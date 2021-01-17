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

streaming = False
cameraConfig = CameraConfig()

@HttpServer.addRoute(b'/camera', title=b"Camera", index=1000)
async def cameraPage(request, response, args):
	""" Camera streaming page """
	framesizes = []
	global streaming
	streaming = False
	for size in [b"1600x1200",b"1280x1024",b"1024x768",b"800x600",b"640x480",b"400x296",b"320x240",b"240x176",b"160x120"  ]:
		framesizes.append(Option(value=size, text=size, selected= True if cameraConfig.framesize == size else False))
	page = mainPage(
		content=\
			[Br(),
				Container(Tag(b"""
<p>
	<button id="toggle-stream" class="btn btn-outline-primary" onclick="onStartVideoClick()">Start streaming</button>
	<figure>
		<div id="container-stream" class="display: none;">
			<img id="video-stream" src="">
		</div>
	</figure>

	<script>
		function onStartVideoClick()
		{
			if (document.getElementById('toggle-stream').innerHTML == 'Start streaming')
			{
				startStreaming();
			}
			else
			{
				stopStreaming();
			}
		}
		window.onload = () => {
			// run in onload
			setTimeout(() => {
				stopStreaming();
			}, 100)
		}
		function startStreaming()
		{
			const button    = document.getElementById('toggle-stream');
			const video     = document.getElementById('video-stream');
			const container = document.getElementById('container-stream');

			window.stop();
			var streamUrl = document.location.origin + ':81';
			video.src = `${streamUrl}/camera/start`;
			button.innerHTML = 'Stop streaming';
			container.style.display = "block";
		}
		function stopStreaming()
		{
			const button    = document.getElementById('toggle-stream');
			const video      = document.getElementById('video-stream');
			const container = document.getElementById('container-stream');

			var xhttp = new XMLHttpRequest();
			xhttp.open("GET","camera/stop",true);
			xhttp.send();
   
			var streamUrl = document.location.origin + ':81';
			video.src = `${streamUrl}/camera/stop`;
			button.innerHTML = 'Start streaming'
			container.style.display = "none";
		}
	</script>
</p>""")),
				Container(Card(Form(\
				[
					ComboCmd(framesizes, text=b"Resolution", path=b"camera/configure", name=b"framesize"),
					SliderCmd(           text=b"Quality"   , path=b"camera/configure", name=b"quality",    min=b"10", max=b"63", step=b"1", value=b"%d"%cameraConfig.quality),
					SliderCmd(           text=b"Brightness", path=b"camera/configure", name=b"brightness", min=b"-2", max=b"2" , step=b"1", value=b"%d"%cameraConfig.brightness),
					SliderCmd(           text=b"Contrast"  , path=b"camera/configure", name=b"contrast"  , min=b"-2", max=b"2" , step=b"1", value=b"%d"%cameraConfig.contrast),
					SliderCmd(           text=b"Saturation", path=b"camera/configure", name=b"saturation", min=b"-2", max=b"2" , step=b"1", value=b"%d"%cameraConfig.saturation),
					SwitchCmd(           text=b"H-Mirror"  , path=b"camera/configure", name=b"hmirror"   , checked=cameraConfig.hmirror),
					SwitchCmd(           text=b"V-Flip"    , path=b"camera/configure", name=b"vflip"     , checked=cameraConfig.vflip),
				])))
			], title=args["title"], active=args["index"], request=request, response=response)
	print("Camera page---")
	await response.sendPage(page)

@HttpServer.addRoute(b'/camera/configure')
async def cameraConfigure(request, response, args):
	""" Real time camera configuration """
	print(useful.tostrings(b"%s=%s"%(request.params[b"name"],request.params[b"value"])))
	cameraConfig.update(request.params)
	Camera.configure(cameraConfig)
	print("configure")
	await response.sendOk()

@HttpServer.addRoute('/camera/stop')
async def cameraStopStreaming(request, response, args):
	""" Stop video streaming """
	global streaming
	streaming = False
	print("Stop streaming......")
	await response.sendOk()

@HttpServer.addRoute('/camera/start')
async def cameraStartStreaming(request, response, args):
	""" Start video streaming """
	global streaming, cameraConfig
	print("Start streaming %d"%request.port)
	if streaming:
		streaming = False
		await uasyncio.sleep(0.2)
	
	if request.port == 80:
		print("Streaming ignored")
		return 
	try:
		
		Camera.open()
		Camera.reserve()
		Camera.configure(cameraConfig)

		print("Start streaming")
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
		streaming = True
		count = 0
		while streaming:
			image = Camera.capture()
			length = len(image)
			await writer.write(frame%(identifier, length, length))
			await writer.write(image)
			if micropython == False:
				await uasyncio.sleep(0.1)
			print("%d"%count)
			count += 1
	except Exception as err:
		print("Stop streaming")
		print(useful.exception(err))
	streaming = False
	Camera.unreserve()
	await writer.close()
