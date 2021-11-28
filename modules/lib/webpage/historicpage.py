# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to view recent motion detection """
from server.httpserver import HttpServer
from server.server     import Server
from htmltemplate      import *
from webpage.mainpage  import main_frame
from motion            import Historic
from video             import Camera
from tools             import useful, lang

@HttpServer.add_route(b'/historic', menu=lang.menu_motion, item=lang.item_historic, available=useful.iscamera() and Camera.is_activated())
async def historic(request, response, args):
	""" Historic motion detection page """
	await Historic.get_root()
	if len(request.params) == 0:
		detailled = False
	else:
		detailled = True
	pageContent = [\
		Tag(b"""
		<script type='text/javascript'>

		document.onkeydown = check_key;
		window.onload = load_historic;

		var historic = null;
		var images = [];
		var current_id = 0;
		var last_id = 0;
		var previousId = 0;
		var historic_request = new XMLHttpRequest();
		var image_request    = new XMLHttpRequest();

		setInterval(show, 200);
  
		const MOTION_FILENAME =0;
		const MOTION_WIDTH    =1;
		const MOTION_HEIGHT   =2;
		const MOTION_DIFFS    =3;
		const MOTION_SQUAREX  =4;
		const MOTION_SQUAREY  =5;

		function download(fileUrl) 
		{
			var a = document.createElement("a");
			a.href = fileUrl;
			filename = fileUrl.split("/").pop();
			a.setAttribute("download", filename);
			a.click();
		}

		function download_motion()
		{
			download("/historic/download/" + historic[current_id][MOTION_FILENAME]);
		}

		function load_historic()
		{
			var canvas = document.getElementById('motion'); 
			canvas.addEventListener("mousedown", function (e) { get_click_position(canvas, e); });
			historic_request.onreadystatechange = historic_loaded;
			historic_request.open("GET","historic/historic.json",true);
			historic_request.send();
		}

		function historic_loaded() 
		{
			if (historic_request.readyState === XMLHttpRequest.DONE)
			{
				if (historic_request.status === 200)
				{
					historic = JSON.parse(historic_request.responseText);
					load_image();
				}
			}
		}

		function load_image()
		{
			if (historic.length > 0)
			{
				var motion = historic[last_id];
				image_request.onreadystatechange = image_loaded;
				image_request.open("GET","/historic/images/" + motion[MOTION_FILENAME],true);
				image_request.send();
			}
			else
			{
				var ctx = document.getElementById('motion').getContext('2d');
				ctx.font = '25px Arial';
				ctx.fillStyle = "black";
				ctx.fillText("%s", 10, 20);
			}
		}

		function image_loaded()
		{
			if (image_request.readyState === XMLHttpRequest.DONE)
			{
				if (image_request.status === 200)
				{
					var motion = historic[last_id];
					var image = new Image();
					image.id     = last_id;
					image.src    = 'data:image/jpeg;base64,' + image_request.response;
					image.width  = motion[MOTION_WIDTH] /15;
					image.height = motion[MOTION_HEIGHT]/15;
					image.alt    = get_name(motion[MOTION_FILENAME]);
					image.title  = get_name(motion[MOTION_FILENAME]);
					image.style  = "padding: 1px;";
					image.onclick = e => 
						{
							click_motion(parseInt(e.target.id,10));
						};
					images.push(image);
					document.getElementById('motions').appendChild(image);
					last_id = last_id + 1;
					if (last_id < historic.length-1)
					{
						setTimeout(load_image, 1);
					}
				}
			}
		}

		function show()
		{
			show_motion(current_id);
		}

		function show_motion(id)
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
			ctx.fillText(get_name(motion[MOTION_FILENAME]), 10, 20);

			// Show arrows
			ctx.fillStyle = 'rgba(255,255,255,10)';
			ctx.font = '30px monospace';
			ctx.fillText("\xE2\x86\x90", 0, motion[MOTION_HEIGHT]/2);
			ctx.fillText("\xE2\x86\x92", motion[MOTION_WIDTH]-20, motion[MOTION_HEIGHT]/2);
			ctx.fillText("\xE2\x87\xA4", motion[MOTION_WIDTH]/2, 20);
			ctx.fillText("\xE2\x87\xA5", motion[MOTION_WIDTH]/2, motion[MOTION_HEIGHT]);
		}

		// Convert the filename into text displayed
		function get_name(filename)
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

		function click_motion(id)
		{
			current_id = id;
			show_motion(id);
		}

		function first_motion()
		{
			current_id = 0;
			show_motion(current_id);
		}

		function last_motion()
		{
			current_id = last_id-1;
			show_motion(current_id);
		}

		function next_motion()
		{
			if (current_id + 1 < last_id)
			{
				current_id = current_id + 1;
				show_motion(current_id);
			}
		}

		function previous_motion()
		{
			if (current_id > 0)
			{
				current_id = current_id -1;
				show_motion(current_id);
			}
		}

		function check_key(e)
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
				previous_motion();
			}
			else if (e.keyCode == '39')// right arrow
			{
				next_motion();
			}
			else if (e.keyCode == '35') // end
			{
			}
			else if (e.keyCode == '36') // home
			{
			}
			else if (e.keyCode == '33') // page up
			{
				first_motion();
			}
			else if (e.keyCode == '34') // page down
			{
				last_motion();
			}
		}

		function get_click_position(canvas, e)
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
					download_motion();
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
							previous_motion();
						}
						else
						{
							first_motion();
						}
					}
					else
					{
						if (x < rect.height - y)
						{
							previous_motion();
						}
						else
						{
							last_motion();
						}
					}
				}
				else
				{
					if (y < rect.height / 2)
					{
						if (rect.width - x < y)
						{
							next_motion();
						}
						else
						{
							first_motion();
						}
					}
					else
					{
						if (rect.width - x < rect.height - y)
						{
							next_motion();
						}
						else
						{
							last_motion();
						}
					}
				}
			}
		}

		</script>
		<canvas id="motion" width="%d" height="%d" ></canvas>
		<br>
		<div id="motions"></div>
		"""%(lang.historic_not_available, detailled, 800,600)),
	]
	page = main_frame(request, response, args,lang.last_motion_detections,pageContent)
	await response.send_page(page)

@HttpServer.add_route(b'/historic/historic.json', available=useful.iscamera() and Camera.is_activated())
async def historic_json(request, response, args):
	""" Send historic json file """
	Server.slow_down()
	if await Historic.locked() is False:
		await response.send_buffer(b"historic.json", await Historic.get_json())
	else:
		await response.send_buffer(b"historic.json", b"[]")

@HttpServer.add_route(b'/historic/images/.*', available=useful.iscamera() and Camera.is_activated())
async def historic_image(request, response, args):
	""" Send historic image """
	Server.slow_down()
	reserved = await Camera.reserve(Historic, timeout=5, suspension=15)
	try:
		if reserved:
			await Historic.acquire()
			await response.send_file(useful.tostrings(request.path[len("/historic/images/"):]), base64=True)
		else:
			await response.send_error(status=b"404", content=b"Image not found")
	finally:
		if reserved:
			await Historic.release()
			await Camera.unreserve(Historic)

@HttpServer.add_route(b'/historic/download/.*', available=useful.iscamera() and Camera.is_activated())
async def download_image(request, response, args):
	""" Download historic image """
	Server.slow_down()
	reserved = await Camera.reserve(Historic, timeout=5, suspension=15)
	try:
		if reserved:
			await Historic.acquire()
			await response.send_file(useful.tostrings(request.path[len("/historic/download/"):]), base64=False)
		else:
			await response.send_error(status=b"404", content=b"Image not found")
	finally:
		if reserved:
			await Historic.release()
			await Camera.unreserve(Historic)
