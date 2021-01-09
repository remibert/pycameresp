# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to see the camera streaming """
from server.httpserver import HttpServer
from htmltemplate import *
from webpage import *
from server.httprequest import *
from tools import useful
from video import Camera

content = b'''
	<style>
		section.main {
			display: flex
		}

		#menu,section.main {
			flex-direction: column
		}

		#menu {
			display: none;
			flex-wrap: nowrap;
			min-width: 340px;
			padding: 8px;
			border-radius: 4px;
			margin-top: -10px;
			margin-right: 10px;
		}

		#content {
			display: flex;
			flex-wrap: wrap;
			align-items: stretch
		}

		figure {
			padding: 0px;
			margin: 0;
			-webkit-margin-before: 0;
			margin-block-start: 0;
			-webkit-margin-after: 0;
			margin-block-end: 0;
			-webkit-margin-start: 0;
			margin-inline-start: 0;
			-webkit-margin-end: 0;
			margin-inline-end: 0
		}

		figure img {
			display: block;
			width: 100%;
			height: auto;
			border-radius: 4px;
			margin-top: 8px;
		}

		@media (min-width: 800px) and (orientation:landscape) {
			#content {
				display:flex;
				flex-wrap: nowrap;
				align-items: stretch
			}

			figure img {
				display: block;
				max-width: 100%;
				max-height: calc(100vh - 40px);
				width: auto;
				height: auto
			}

			figure {
				padding: 0 0 0 0px;
				margin: 0;
				-webkit-margin-before: 0;
				margin-block-start: 0;
				-webkit-margin-after: 0;
				margin-block-end: 0;
				-webkit-margin-start: 0;
				margin-inline-start: 0;
				-webkit-margin-end: 0;
				margin-inline-end: 0
			}
		}

		section#buttons {
			display: flex;
			flex-wrap: nowrap;
			justify-content: space-between
		}

		#nav-toggle {
			cursor: pointer;
			display: block
		}

		#nav-toggle-cb {
			outline: 0;
			opacity: 0;
			width: 0;
			height: 0
		}

		#nav-toggle-cb:checked+#menu {
			display: flex
		}

		.input-group {
			display: flex;
			flex-wrap: nowrap;
			line-height: 22px;
			margin: 5px 0
		}

		.input-group>label {
			display: inline-block;
			padding-right: 10px;
			min-width: 47%
		}

		.range-max,.range-min {
			display: inline-block;
			padding: 0 5px
		}

		.image-container {
			position: relative;
			min-width: 160px
		}

		.hidden {
			display: none
		}
	</style>
	<section class="main">
		<div id="content">
			<div id="sidebar">
				<input type="checkbox" id="nav-toggle-cb" checked="checked">
				<nav id="menu">
					<div class="input-group" id="framesize-group">
						<label for="framesize">Resolution</label>
						<select id="framesize" class="form-control default-action">
							<option value="UXGA">UXGA(1600x1200)</option>
							<option value="SXGA">SXGA(1280x1024)</option>
							<option value="XGA">XGA(1024x768)</option>
							<option value="SVGA" selected="selected">SVGA(800x600)</option>
							<option value="VGA">VGA(640x480)</option>
							<option value="CIF">CIF(400x296)</option>
							<option value="QVGA">QVGA(320x240)</option>
							<option value="HQVGA">HQVGA(240x176)</option>
							<option value="QQVGA">QQVGA(160x120)</option>
						</select>
					</div>
					<div class="input-group" id="quality-group">
						<label for="quality">Quality</label>
						<div class="range-min">10</div>
						<input type="range" id="quality" min="10" max="63" value="10" class="custom-range default-action">
						<div class="range-max">63</div>
					</div>
					<div class="input-group" id="brightness-group">
						<label for="brightness">Brightness</label>
						<div class="range-min">-2</div>
						<input type="range" id="brightness" min="-2" max="2" value="0" class="custom-range default-action">
						<div class="range-max">2</div>
					</div>
					<div class="input-group" id="contrast-group">
						<label for="contrast">Contrast</label>
						<div class="range-min">-2</div>
						<input type="range" id="contrast" min="-2" max="2" value="0" class="custom-range default-action">
						<div class="range-max">2</div>
					</div>
					<div class="input-group" id="saturation-group">
						<label for="saturation">Saturation</label>
						<div class="range-min">-2</div>
						<input type="range" id="saturation" min="-2" max="2" value="0" class="custom-range default-action">
						<div class="range-max">2</div>
					</div>
					<div class="input-group" id="hmirror-group">
						<label for="hmirror">H-Mirror</label>
						<div class="custom-control custom-switch">
							<input id="hmirror" type="checkbox" class="custom-control-input default-action">
							<label class="custom-control-label" for="hmirror"></label>
						</div>
					</div>
					<div class="input-group" id="vflip-group">
						<label for="vflip">V-Flip</label>
						<div class="custom-control custom-switch">
							<input id="vflip" type="checkbox" class="custom-control-input default-action">
							<label class="custom-control-label" for="vflip"></label>
						</div>
					</div>
					<section id="buttons">
						<button id="toggle-stream" class="btn btn-primary">Start</button>
					</section>
				</nav>
			</div>
			<figure>
				<div id="stream-container" class="image-container hidden">
					
					<img id="stream" src="">
				</div>
			</figure>
		</div>
	</section>

	<script>
	document.addEventListener('DOMContentLoaded', function (event) 
	{
		var baseHost = document.location.origin
		var streamUrl = baseHost + ':81'

		const hide = el => 
		{
			el.classList.add('hidden')
		}
		
		const show = el => 
		{
			el.classList.remove('hidden')
		}

		const disable = el => 
		{
			el.classList.add('disabled')
			el.disabled = true
		}

		const enable = el => 
		{
			el.classList.remove('disabled')
			el.disabled = false
		}

		const updateValue = (el, value, updateRemote) => 
		{
			updateRemote = updateRemote == null ? true : updateRemote
			let initialValue
			if (el.type === 'checkbox')
			{
				initialValue = el.checked
				value = !!value
				el.checked = value
			}
			else
			{
				initialValue = el.value
				el.value = value
			}

			if (updateRemote && initialValue !== value) 
			{
				updateConfig(el);
			}
		}

		function updateConfig (el)
		{
			let value
			switch (el.type)
			{
			case 'checkbox':
				value = el.checked ? 1 : 0
				break
			case 'range':
			case 'select-one':
				value = el.value
				break
			case 'button':
			case 'submit':
				value = '1'
				break
			default:
				return
			}

			const query = `${baseHost}/control?var=${el.id}&val=${value}`

			fetch(query).then(response => 
			{
				console.log(`request to ${query} finished, status: ${response.status}`)
			})
		}

		// read initial values
		fetch(`${baseHost}/status`).then(function (response) 
		{
			return response.json()
		}).then(function (state) 
		{
			document.querySelectorAll('.default-action').forEach(el => 
			{
				updateValue(el, state[el.id], false)
			})
		})

		const view = document.getElementById('stream')
		const viewContainer = document.getElementById('stream-container')
		const streamButton = document.getElementById('toggle-stream')
		
		const stopStream = () => 
		{
			window.stop();
			streamButton.innerHTML = 'Start'
		}

		const startStream = () => 
		{
			view.src = `${streamUrl}/stream`
			show(viewContainer)
			streamButton.innerHTML = 'Stop'
		}

		streamButton.onclick = () => 
		{
			const streamEnabled = streamButton.innerHTML === 'Stop'
			if (streamEnabled)
			{
				stopStream()
			}
			else
			{
				startStream()
			}
		}

		// Attach default on change action
		document.querySelectorAll('.default-action').forEach(el => 
		{
			el.onchange = () => updateConfig(el)
		})

		framesize.onchange = () => 
		{
			updateConfig(framesize)
			if (framesize.value > 5) 
			{
				updateValue(detect, false)
				updateValue(recognize, false)
			}
		}
	})

	</script>
'''

@HttpServer.addRoute(b'/camera', title=b"Camera", index=18, available=useful.iscamera())
async def camera(request, response, args):
	""" Camera page """
	page = mainPage(
		content=[Tag(content)], title=args["title"], active=args["index"], request=request, response=response)
	global cameraControl
	cameraControl = CameraControl()
	await response.sendPage(page)

class CameraControl:
	""" Class that collects the camera rendering configuration """
	def __init__(self):
		""" Constructor """
		self.quality    = 10
		self.pixformat  = b"JPEG"
		self.brightness = 0
		self.contrast   = 0
		self.saturation = 0
		self.hmirror    = 0
		self.vflip      = 0
		self.framesize  = b"SVGA"

	def configure(self):
		""" Configure the camera """
		Camera.pixformat (self.pixformat)
		Camera.framesize (self.framesize)
		Camera.quality   (self.quality)
		Camera.brightness(self.brightness)
		Camera.contrast  (self.contrast)
		Camera.saturation(self.saturation)
		Camera.hmirror   (self.hmirror)
		Camera.vflip     (self.vflip)

	def change(self, param, value):
		""" Change the camera parameter """
		if   param == b"framesize":
			self.framesize  = value
			if Camera.isReserved():
				Camera.framesize (self.framesize)
		elif param == b"quality":
			self.quality    = int(value)
			if Camera.isReserved():
				Camera.quality   (self.quality)
		elif param == b"brightness":
			self.brightness = int(value)
			if Camera.isReserved():
				Camera.brightness(self.brightness)
		elif param == b"contrast":
			self.contrast   = int(value)
			if Camera.isReserved():
				Camera.contrast  (self.contrast)
		elif param == b"saturation":
			self.saturation = int(value)
			if Camera.isReserved():
				Camera.saturation(self.saturation)
		elif param == b"hmirror":
			self.hmirror    = int(value)
			if Camera.isReserved():
				Camera.hmirror   (self.hmirror)
		elif param == b"vflip":
			self.vflip      = int(value)
			if Camera.isReserved():
				Camera.vflip     (self.vflip)

cameraControl = CameraControl()

@HttpServer.addRoute('/status')
async def status(request, response, args):
	""" Status of camera """
	await response.sendOk()

@HttpServer.addRoute('/control')
async def control(request, response, args):
	""" Control of camera rendering """
	param = request.params[b"var"]
	value = request.params[b"val"]
	cameraControl.change(param, value)
	await response.sendOk()

@HttpServer.addRoute('/stream')
async def stream(request, response, args):
	""" Video streaming """
	if request.port == 80:
		print("Streaming ignored")
		return 
	try:
		Camera.open()
		Camera.reserve()
		cameraControl.configure()

		print("Start streaming")
		response.setStatus(b"200")
		response.setHeader(b"Content-Type",b"multipart/x-mixed-replace")
		response.setHeader(b"Transfer-Encoding",b"chunked")
		response.setHeader(b"Access-Control-Allow-Origin","*")

		await response.serialize(response.streamio)
		writer = response.streamio
		identifier = b"\r\n%x\r\n\r\n--%s\r\n\r\n"%(len(response.identifier) + 6, response.identifier)
		frame = b'%s36\r\nContent-Type: image/jpeg\r\nContent-Length: %8d\r\n\r\n\r\n%x\r\n'

		if useful.ismicropython():
			image = Camera.capture()
			length = len(image)
			await writer.write(frame%(b"", length, length))
			await writer.write(image)

			while True:
				image = Camera.capture()
				length = len(image)
				await writer.write(frame%(identifier, length, length))
				await writer.write(image)
		else:
			image = Camera.capture()
			length = len(image)
			await writer.write(frame%(b"", length, length))
			await writer.write(image)
   
			while True:
				image = Camera.capture()
				length = len(image)
				await writer.write(frame%(identifier, length, length))
				await writer.write(image)
				await asyncio.sleep(0.1)

	except Exception as err:
		print("Stop streaming")
		# print(useful.exception(err))
	Camera.unreserve()
