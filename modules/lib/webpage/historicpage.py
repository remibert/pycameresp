# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to view recent motion detection """
from server.httpserver import HttpServer
from htmltemplate import *
from webpage import *
from motion import Historic
from tools import useful
from video import Camera

@HttpServer.addRoute(b'/historic', title=b"Historic", index=18, available=useful.iscamera())
async def historic(request, response, args):
	""" Historic motion detection page """
	await Historic.getRoot()
	pageContent = [\
		Tag(b"""
		<script type='text/javascript'>

		document.onkeydown = checkKey;
		window.onload = loadHistoric;

		var historic = null;
		var images = [];
		var currentId = 0;
		var lastId = 0;
		var previousId = 0;
		var historicRequest = new XMLHttpRequest();
		var imageRequest    = new XMLHttpRequest();

		setInterval(show, 200);
  
		const MOTION_FILENAME=0;
		const MOTION_WIDTH=1;
		const MOTION_HEIGHT=2;
		const MOTION_SHAPES=3;
		const SHAPE_COUNT=0;
		const SHAPE_X=1;
		const SHAPE_Y=2;
		const SHAPE_WIDTH=3;
		const SHAPE_HEIGHT=4;

		function download(fileUrl) 
		{
			var a = document.createElement("a");
			a.href = fileUrl;
			filename = fileUrl.split("/").pop();
			a.setAttribute("download", filename);
			a.click();
		}

		function downloadMotion()
		{
			download("/historic/download/" + historic[currentId][MOTION_FILENAME]);
		}

		function loadHistoric()
		{
			console.log("loadHistoric");
			historicRequest.onreadystatechange = historicLoaded;
			historicRequest.open("GET","historic/historic.json",true);
			historicRequest.send();
		}

		function historicLoaded() 
		{
			if (historicRequest.readyState === XMLHttpRequest.DONE)
			{
				if (historicRequest.status === 200)
				{
					historic = JSON.parse(historicRequest.responseText);
					loadImage();
				}
			}
		}

		function loadImage()
		{
			if (historic.length > 0)
			{
				var motion = historic[lastId];
				imageRequest.onreadystatechange = imageLoaded;
				imageRequest.open("GET","/historic/images/" + motion[MOTION_FILENAME],true);
				imageRequest.send();
			}
			else
			{
				var ctx = document.getElementById('motion').getContext('2d');
				ctx.font = '25px Arial';
				ctx.fillStyle = "black";
				ctx.fillText("Not yet available, try again in few minutes", 10, 20);
			}
		}

		function imageLoaded()
		{
			if (imageRequest.readyState === XMLHttpRequest.DONE)
			{
				if (imageRequest.status === 200)
				{
					console.log("imageLoaded create image");
					var motion = historic[lastId];
					var image = new Image();
					image.id     = lastId;
					image.src    = 'data:image/jpeg;base64,' + imageRequest.response;
					image.width  = motion[MOTION_WIDTH] /15;
					image.height = motion[MOTION_HEIGHT]/15;
					image.alt    = getName(motion[MOTION_FILENAME]);
					image.title  = getName(motion[MOTION_FILENAME]);
					image.style  = "padding: 1px;";
					image.onclick = e => 
						{
							clickMotion(parseInt(e.target.id,10));
						};
					images.push(image);
					document.getElementById('motions').appendChild(image);
					lastId = lastId + 1;
					if (lastId < historic.length-1)
					{
						setTimeout(loadImage, 1);
					}
				}
			}
		}

		function show()
		{
			showMotion(currentId);
		}

		function showMotion(id)
		{
			var motion = historic[id];
			var ctx = document.getElementById('motion').getContext('2d');
			
			ctx.drawImage(document.getElementById(id), 0, 0, motion[MOTION_WIDTH], motion[MOTION_HEIGHT]);
			var x;
			var y;
			var width;
			var height;

			document.getElementById(previousId).style.border = "";
			document.getElementById(id).style.border = "3px solid dodgerblue";
			previousId = id;

			var bigger = 0;
			var biggerId = 0;
			var size = 0;
			for (let i = 0; i < motion[MOTION_SHAPES].length; i++)
			{
				size = motion[MOTION_SHAPES][i][SHAPE_WIDTH]*motion[MOTION_SHAPES][i][SHAPE_HEIGHT];
				if (size > bigger)
				{
					bigger = size;
					biggerId = i;
				}
			}

			for (let i = 0; i < motion[MOTION_SHAPES].length; i++)
			{
				x      = motion[MOTION_SHAPES][i][SHAPE_X]      + 1;
				y      = motion[MOTION_SHAPES][i][SHAPE_Y]      + 1;
				width  = motion[MOTION_SHAPES][i][SHAPE_WIDTH]  - 2;
				height = motion[MOTION_SHAPES][i][SHAPE_HEIGHT] - 2;
				if (i == biggerId)
				{
					ctx.strokeStyle = "red";
					ctx.strokeRect(x, y, width, height);
				}
				else
				{
					if (motion[MOTION_SHAPES][i][SHAPE_COUNT] >= 10)
					{
						ctx.strokeStyle = "white";
						ctx.strokeRect(x, y, width, height);
					}
				}
			}
			ctx.font = '20px monospace';
			ctx.fillStyle = "red";
			ctx.fillText(getName(motion[MOTION_FILENAME]), 10, 20);

			console.log("loaded " +id);
		}
  
		function getName(filename)
		{
			filename = filename.split(".")[0];
			lst = filename.split("/");
			filename = lst[lst.length-1];
			spl = filename.split(" ");

			if (spl.length >= 3)
			{
				date = spl[0].replaceAll("-","/") + " " + spl[1].replaceAll("-",":")
				if (spl.length >= 4)
				{
					last = spl[2] + " " + spl[3];
				}
				else
				{
					last = spl[2];
				}
				result = date + " "+ last;
			}
			else
			{
				result = filename;
			}
			return result;
		}

		function clickMotion(id)
		{
			currentId = id;
			showMotion(id);
		}

		function firstMotion()
		{
			currentId = 0;
			showMotion(currentId);
		}

		function lastMotion()
		{
			currentId = lastId-1;
			showMotion(currentId);
		}

		function nextMotion()
		{
			if (currentId + 1 < lastId)
			{
				currentId = currentId + 1;
				showMotion(currentId);
			}
		}

		function previousMotion()
		{
			if (currentId > 0)
			{
				currentId = currentId -1;
				showMotion(currentId);
			}
		}

		function checkKey(e)
		{
			e = e || window.event;

			if (e.keyCode == '38') // up arrow
			{
			}
			else if (e.keyCode == '40') // down arrow
			{
			}
			else if (e.keyCode == '37') // left arrow
			{
				previousMotion();
			}
			else if (e.keyCode == '39')// right arrow
			{
				nextMotion();
			}
			else if (e.keyCode == '35') // end
			{
			}
			else if (e.keyCode == '36') // home
			{
			}
			else if (e.keyCode == '33') // page up
			{
				firstMotion();
			}
			else if (e.keyCode == '34') // page down
			{
				lastMotion();
			}
		}

		</script>
		<button type="button" class="btn btn-outline-primary" onclick="firstMotion()"    >|&lt-</button>
		<button type="button" class="btn btn-outline-primary" onclick="previousMotion()" >&lt-</button>
		<button type="button" class="btn btn-outline-primary" onclick="nextMotion()"     >-&gt</button>
		<button type="button" class="btn btn-outline-primary" onclick="lastMotion()"     >-&gt|</button>
		<button type="button" class="btn btn-outline-primary" onclick="downloadMotion()">Download</button>
		<br>
		<br>
		<canvas id="motion" width="%d" height="%d">The reconstruction is in progress, wait a few minutes after a reboot of the terminal</canvas>
		<br>
		<br>
		<div id="motions"></div>
		"""%(800,600)),
	]
	page = mainFrame(request, response, args,b"Last motion detections",pageContent)
	await response.sendPage(page)

@HttpServer.addRoute(b'/historic/historic.json', available=useful.iscamera())
async def historicJson(request, response, args):
	""" Send historic json file """
	if await Historic.locked() == False:
		await response.sendBuffer(b"historic.json", await Historic.getJson())
	else:
		await response.sendBuffer(b"historic.json", b"[]")

@HttpServer.addRoute(b'/historic/images/.*', available=useful.iscamera())
async def historicImage(request, response, args):
	""" Send historic image """
	Camera.reserve()
	try:
		await Historic.acquire()
		await response.sendFile(useful.tostrings(request.path[len("/historic/images/"):]), base64=True)
	finally:
		await Historic.release()
		Camera.unreserve()

@HttpServer.addRoute(b'/historic/download/.*', available=useful.iscamera())
async def downloadImage(request, response, args):
	""" Download historic image """
	Camera.reserve()
	try:
		await Historic.acquire()
		await response.sendFile(useful.tostrings(request.path[len("/historic/download/"):]), base64=False)
	finally:
		await Historic.release()
		Camera.unreserve()
