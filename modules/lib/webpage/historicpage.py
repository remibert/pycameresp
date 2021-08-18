# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to view recent motion detection """
from server.httpserver import HttpServer
from server.server   import Server
from htmltemplate import *
from webpage import *
from motion import Historic
from tools import useful
from video import Camera

@HttpServer.addRoute(b'/historic', title=b"Historic", index=53, available=useful.iscamera())
async def historic(request, response, args):
	""" Historic motion detection page """
	await Historic.getRoot()
	if len(request.params) == 0:
		detailled = False
	else:
		detailled = True
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
  
		const MOTION_FILENAME =0;
		const MOTION_WIDTH    =1;
		const MOTION_HEIGHT   =2;
		const MOTION_SHAPES   =3;
		const MOTION_DIFFS    =4;
		const MOTION_SQUAREX  =5;
		const MOTION_SQUAREY  =6;

		const SHAPE_COUNT     =0;
		const SHAPE_X         =1;
		const SHAPE_Y         =2;
		const SHAPE_WIDTH     =3;
		const SHAPE_HEIGHT    =4;

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
			var canvas = document.getElementById('motion'); 
			canvas.addEventListener("mousedown", function (e) { getClickPosition(canvas, e); });
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
				ctx.fillText("Not yet available, retry again in 5 minutes", 10, 20);
			}
		}

		function imageLoaded()
		{
			if (imageRequest.readyState === XMLHttpRequest.DONE)
			{
				if (imageRequest.status === 200)
				{
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

			// Show thumb image selected
			document.getElementById(previousId).style.border = "";
			document.getElementById(id).style.border = "3px solid dodgerblue";
			previousId = id;

			var squarex = motion[MOTION_SQUAREX];
			var squarey = motion[MOTION_SQUAREY];
			var maxx = motion[MOTION_WIDTH] /squarex;
			var maxy = motion[MOTION_HEIGHT]/squarey;
			
			if (%d)
			{
				for (y = 0; y < maxy; y ++)
				{
					for (x = 0; x < maxx; x ++)
					{
						detection = motion[MOTION_DIFFS][y*maxx + x];
						if (detection != " ")
						{
							ctx.strokeStyle = "yellow";
							ctx.strokeRect(x * squarex + 15, y*squarey +15, squarex-30, squarey-30);
						}
					}
				}
			}

			ctx.strokeStyle = "red";
			for (y = 0; y < maxy; y ++)
			{
				for (x = 0; x < maxx; x ++)
				{
					var detection = motion[MOTION_DIFFS][y*maxx + x];
					if (x >= 1)
					{
						var previous = motion[MOTION_DIFFS][y*maxx + x -1];
						if (previous != detection)
						{
							ctx.beginPath();
							ctx.moveTo(x*squarex, y*squarey);
							ctx.lineTo(x*squarex, y*squarey + squarey);
							ctx.stroke();
						}
					}
				}
			}
			
			for (x = 0; x < maxx; x ++)
			{
				for (y = 0; y < maxy; y ++)
				{
					var detection = motion[MOTION_DIFFS][y*maxx + x];
					if (y >= 1)
					{
						var previous = motion[MOTION_DIFFS][(y-1)*maxx + x];
						if (previous != detection)
						{
							ctx.beginPath();
							ctx.moveTo(x*squarex, y*squarey);
							ctx.lineTo(x*squarex + squarex, y*squarey);
							ctx.stroke();
						}
					}
				}
			}

			// Show text image
			ctx.font = '20px monospace';
			ctx.fillStyle = "red";
			ctx.fillText(getName(motion[MOTION_FILENAME]), 10, 20);

			// Show arrows
			ctx.fillStyle = 'rgba(255,255,255,10)';
			ctx.font = '30px monospace';
			ctx.fillText("\xE2\x86\x90", 0, motion[MOTION_HEIGHT]/2);
			ctx.fillText("\xE2\x86\x92", motion[MOTION_WIDTH]-20, motion[MOTION_HEIGHT]/2);
			ctx.fillText("\xE2\x87\xA4", motion[MOTION_WIDTH]/2, 20);
			ctx.fillText("\xE2\x87\xA5", motion[MOTION_WIDTH]/2, motion[MOTION_HEIGHT]);
		}

		// Convert the filename into text displayed
		function getName(filename)
		{
			filename = filename.split(".")[0];
			lst = filename.split("/");
			filename = lst[lst.length-1];
			spl = filename.split(" ");

			if (spl.length == 3)
			{
				date = spl[0].split("_")[0];
				hour = spl[0].split("_")[1];

				date = date.replaceAll("-","/") + " " + hour.replaceAll("-",":");
				last = spl[1] + " " + spl[2];
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

		function getClickPosition(canvas, e)
		{
			const rect = canvas.getBoundingClientRect();
			const x = e.clientX - rect.left;
			const y = e.clientY - rect.top;

			// If the click is in the middle
			if (x > rect.width/3 && x < (2*rect.width/3) && y > rect.height/3 && y < (2*rect.height/3))
			{
				// Download image
				if (confirm("Download this image ?"))
				{
					downloadMotion();
				}
			}
			else
			{
				if (x < rect.width / 2)
				{
					if (y < rect.height / 2)
					{
						if (x < y)
						{
							previousMotion();
						}
						else
						{
							firstMotion();
						}
					}
					else
					{
						if (x < rect.height - y)
						{
							previousMotion();
						}
						else
						{
							lastMotion();
						}
					}
				}
				else
				{
					if (y < rect.height / 2)
					{
						if (rect.width - x < y)
						{
							nextMotion();
						}
						else
						{
							firstMotion();
						}
					}
					else
					{
						if (rect.width - x < rect.height - y)
						{
							nextMotion();
						}
						else
						{
							lastMotion();
						}
					}
				}
			}
		}

		</script>
		<canvas id="motion" width="%d" height="%d" >The reconstruction is in progress, wait a few minutes after a reboot of the terminal</canvas>
		<br>
		<div id="motions"></div>
		"""%(detailled, 800,600)),
	]
	page = mainFrame(request, response, args,b"Last motion detections",pageContent)
	await response.sendPage(page)

@HttpServer.addRoute(b'/historic/historic.json', available=useful.iscamera())
async def historicJson(request, response, args):
	""" Send historic json file """
	Server.slowDown()
	if await Historic.locked() == False:
		await response.sendBuffer(b"historic.json", await Historic.getJson())
	else:
		await response.sendBuffer(b"historic.json", b"[]")

@HttpServer.addRoute(b'/historic/images/.*', available=useful.iscamera())
async def historicImage(request, response, args):
	""" Send historic image """
	Server.slowDown()
	reserved = await Camera.reserve(Historic, timeout=5, suspension=30)
	try:
		if reserved:
			await Historic.acquire()
			await response.sendFile(useful.tostrings(request.path[len("/historic/images/"):]), base64=True)
		else:
			await response.sendError(status=b"404", content=b"Image not found")
	finally:
		if reserved:
			await Historic.release()
			await Camera.unreserve(Historic)

@HttpServer.addRoute(b'/historic/download/.*', available=useful.iscamera())
async def downloadImage(request, response, args):
	""" Download historic image """
	Server.slowDown()
	reserved = await Camera.reserve(Historic, timeout=5, suspension=30)
	try:
		if reserved:
			await Historic.acquire()
			await response.sendFile(useful.tostrings(request.path[len("/historic/download/"):]), base64=False)
		else:
			await response.sendError(status=b"404", content=b"Image not found")
	finally:
		if reserved:
			await Historic.release()
			await Camera.unreserve(Historic)
