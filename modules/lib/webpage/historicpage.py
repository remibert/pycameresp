# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to view recent motion detection """
# pylint:disable=anomalous-unicode-escape-in-string
from server.httpserver     import HttpServer
from server.server         import Server
from htmltemplate          import *
from webpage.mainpage      import main_frame
from webpage.streamingpage import Streaming
from motion                import Historic
from video                 import Camera
from tools                 import lang,info, strings

@HttpServer.add_route(b'/historic', menu=lang.menu_motion, item=lang.item_historic, available=info.iscamera() and Camera.is_activated())
async def historic(request, response, args):
	""" Historic motion detection page """
	Streaming.stop()
	Historic.get_root()
	pageContent = [\
		Tag(b"""

		<div class="modal" id="myModal">
			<div class="modal-dialog modal-fullscreen">
				<div class="modal-content">
					<div class="modal-header">
						<button type="button" class="btn " data-bs-dismiss="modal">Close</button>
						<button type="button" class="btn-close" data-bs-dismiss="modal"></button>
					</div>
					<div class="modal-body" >
						<canvas id="view_image" class="w-100" data-bs-dismiss="modal"/>
					</div>
				</div>
			</div>
		</div>

		<script type='text/javascript'>

		window.onload = load_historic;

		var historic = null;
		var current_id = 0;
		var last_id = 0;
		var historic_request = new XMLHttpRequest();
		var image_request    = new XMLHttpRequest();

		const MOTION_FILENAME =0;
		const MOTION_WIDTH    =1;
		const MOTION_HEIGHT   =2;
		const MOTION_DIFFS    =3;
		const MOTION_SQUAREX  =4;
		const MOTION_SQUAREY  =5;

		function load_historic()
		{
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
		}

		function get_quality()
		{
			if (/iPhone|iPad|iPod|Android/i.test(navigator.userAgent))
			{
				return 1;
			}
			else
			{
				return 2;
			}
		}

		function image_loaded()
		{
			if (image_request.readyState === XMLHttpRequest.DONE)
			{
				if (image_request.status === 200)
				{
					var motion = historic[last_id];

					var div = document.createElement("div");
						div.className = "col-lg-2  pb-1 border bg-light";

						var canvas = document.createElement("canvas");
							canvas.width     = motion[MOTION_WIDTH ] * get_quality();
							canvas.height    = motion[MOTION_HEIGHT] * get_quality();
							canvas.id        = last_id;
							canvas.className = "w-100";
							canvas.setAttribute("data-bs-toggle","modal");
							canvas.setAttribute("data-bs-target","#myModal");
							canvas.onclick = e => 
								{
									var view = document.getElementById('view_image');
									var destCtx = view.getContext('2d');
									view.width     = motion[MOTION_WIDTH ] * get_quality();
									view.height    = motion[MOTION_HEIGHT] * get_quality();

									destCtx.drawImage(canvas, 0, 0);
								};

						var image = new Image();
							image.src        = 'data:image/jpeg;base64,' + image_request.response;
							image.onload     = function(){show_motion(canvas.id, image);};

						div.appendChild(canvas);

					if (last_id == 0)
					{
						document.getElementById('motions').replaceChildren(div);
					}
					else
					{
						document.getElementById('motions').appendChild(div);
					}
					last_id = last_id + 1;
					if (last_id < historic.length-1)
					{
						setTimeout(load_image, 1);
					}
				}
				else 
				{
					setTimeout(load_image, 1);
				}
			}
		}

		function get_difference(motion, x, y)
		{
			var squarex = motion[MOTION_SQUAREX];
			var maxx    = motion[MOTION_WIDTH] /squarex;
			var bitpos  = y*maxx + x;
			if (typeof motion[MOTION_DIFFS] === 'string')
			{
				return motion[MOTION_DIFFS][bitpos];
			}
			else
			{
				var word = parseInt(bitpos/32);
				var bit  = 31-bitpos%%32;
				var mask = 1 << bit;
				var val  = motion[MOTION_DIFFS][word];
				if (val & mask)
				{
					return "#";
				}
				else
				{
					return " ";
				}
			}
		}

		function show_motion(id, image)
		{
			var x;
			var y;

			var motion = historic[id];
			var canvas = document.getElementById(id);
			var ctx = canvas.getContext('2d');

			var squarex = motion[MOTION_SQUAREX] * get_quality();
			var squarey = motion[MOTION_SQUAREY] * get_quality();
			var maxx = (motion[MOTION_WIDTH] /squarex) * get_quality();
			var maxy = (motion[MOTION_HEIGHT]/squarey) * get_quality();

			ctx.drawImage(image, 0, 0, motion[MOTION_WIDTH ]  , motion[MOTION_HEIGHT], 0, 0, motion[MOTION_WIDTH ] * get_quality(), motion[MOTION_HEIGHT] * get_quality());

			ctx.strokeStyle = "red";
			ctx.lineWidth =  1 * get_quality();
			for (y = 0; y < maxy; y ++)
			{
				for (x = 0; x < maxx; x ++)
				{
					var detection = get_difference(motion, x, y);
					if (x >= 1)
					{
						var previous = get_difference(motion, x-1, y);
						if (previous != detection)
						{
							ctx.beginPath();
							ctx.moveTo(0 + x*squarex, 0 + y*squarey);
							ctx.lineTo(0 + x*squarex, 0 + y*squarey + squarey);
							ctx.stroke();
						}
					}
				}
			}
			
			for (x = 0; x < maxx; x ++)
			{
				for (y = 0; y < maxy; y ++)
				{
					var detection = get_difference(motion, x, y);
					if (y >= 1)
					{
						var previous = get_difference(motion, x, y-1);
						if (previous != detection)
						{
							ctx.beginPath();
							ctx.moveTo(0 + x*squarex, 0 + y*squarey);
							ctx.lineTo(0 + x*squarex + squarex, 0 + y*squarey);
							ctx.stroke();
						}
					}
				}
			}

			ctx.font = "40px monospace";
			var width = ctx.measureText(get_name(motion[MOTION_FILENAME])).width;
			ctx.fillStyle = 'rgba(0,0,0,0.3)';

			ctx.fillRect(10,(motion[MOTION_HEIGHT] * get_quality())-40-15, width, 40);

			ctx.fillStyle = 'rgba(255,255,255,0.5)';
			ctx.fillText(get_name(motion[MOTION_FILENAME]),  10, (motion[MOTION_HEIGHT] * get_quality())-20);

		}

		// Convert the filename into text displayed
		function get_name(filename)
		{
			filename = filename.split(".")[0];
			lst = filename.split("/");
			filename = lst[lst.length-1];
			filename = filename.replace("D= ","D=");
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

		function get_date(filename)
		{
			return get_name(filename).substring(0,10);
		}

		</script>
		<div id="motions" class="row">
		<span>%s</span>
		</div>
		"""%(lang.historic_not_available)),
	]
	page = main_frame(request, response, args,lang.last_motion_detections,pageContent)
	await response.send_page(page)

@HttpServer.add_route(b'/historic/historic.json', available=info.iscamera() and Camera.is_activated())
async def historic_json(request, response, args):
	""" Send historic json file """
	Server.slow_down()
	try:
		await response.send_buffer(b"historic.json", await Historic.get_json())
	except Exception as err:
		logger.syslog(err)
		await response.send_error(status=b"404", content=b"Historic problem")

@HttpServer.add_route(b'/historic/images/.*', available=info.iscamera() and Camera.is_activated())
async def historic_image(request, response, args):
	""" Send historic image """
	Server.slow_down()
	reserved = await Camera.reserve(Historic, timeout=5, suspension=15)
	try:
		if reserved:
			await Historic.acquire()
			await response.send_file(strings.tostrings(request.path[len("/historic/images/"):]), base64=True)
		else:
			await response.send_error(status=b"404", content=b"Image not found")
	finally:
		if reserved:
			await Historic.release()
			await Camera.unreserve(Historic)

@HttpServer.add_route(b'/historic/download/.*', available=info.iscamera() and Camera.is_activated())
async def download_image(request, response, args):
	""" Download historic image """
	Server.slow_down()
	reserved = await Camera.reserve(Historic, timeout=5, suspension=15)
	try:
		if reserved:
			await Historic.acquire()
			await response.send_file(strings.tostrings(request.path[len("/historic/download/"):]), base64=False)
		else:
			await response.send_error(status=b"404", content=b"Image not found")
	finally:
		if reserved:
			await Historic.release()
			await Camera.unreserve(Historic)
