# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to view recent motion detection """
from server.httpserver import HttpServer
from htmltemplate import *
from webpage import *
from tools import useful


@HttpServer.addRoute(b'/historic', title=b"Historic", index=18, available=useful.iscamera())
async def historic(request, response, args):
	""" Historic motion detection page """
	useful.SdCard.mount()
	pageContent = [\
		Tag(b"""
		<script type='text/javascript'>
		window.onload=loadHistoric;
		var xhttp = new XMLHttpRequest();
		document.onkeydown = checkKey;
		var historic = null;
		var current = 0;

		function loadHistoric()
		{
			xhttp.onreadystatechange = parseHistoric;
			xhttp.open("GET","%s/historic.json",true);
			xhttp.send();
		}

		function parseHistoric() 
		{
			if (xhttp.readyState === XMLHttpRequest.DONE)
			{
				if (xhttp.status === 200)
				{
					historic = JSON.parse(xhttp.responseText);
					current = 0;
					showMotion();
				}
			}
		}

		function showMotion()
		{
			if (historic != null)
			{
				var img    = new Image;
				var motion = historic[current][1];
				img.src    = motion["image"];
				img.onload = function () 
				{
					var ctx = document.getElementById('motion').getContext('2d');
					ctx.strokeStyle = "red";
					ctx.drawImage(img, 0, 0, motion["geometry"]["width"], motion["geometry"]["height"]);
					var x;
					var y;
					var width;
					var height;

					for (let i = 0; i < motion["shapes"].length; i++)
					{
						x = motion["shapes"][i]["x"] + 1;
						y = motion["shapes"][i]["y"] + 1;
						width  = motion["shapes"][i]["width"] -2;
						height = motion["shapes"][i]["height"] -2;
						ctx.strokeRect(x, y, width, height);
					}
					ctx.font = '20px monospace';
					ctx.fillStyle = "red";
					ctx.fillText(motion["date"], 10, 20);
				}
			}
		}

		function firstMotion()
		{
			current = 0;
			showMotion();
		}

		function lastMotion()
		{
			current = historic.length-1;
			showMotion();
		}

		function nextMotion()
		{
			if (current < historic.length+1)
			{
				current = current + 1;
				showMotion();
			}
		}

		function previousMotion()
		{
			if (current > 0)
			{
				current = current -1;
				showMotion();
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
		<br>
		<br>
		<canvas id="motion" width="%d" height="%d"></canvas>
		"""%(useful.tobytes(useful.SdCard.getMountpoint()),800,600)),
	]
	page = mainFrame(request, response, args,b"Historic motion detection",pageContent)
	await response.sendPage(page)

