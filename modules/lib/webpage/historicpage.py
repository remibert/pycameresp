# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to view recent motion detection """
# pylint:disable=anomalous-unicode-escape-in-string
from server.httpserver     import HttpServer
from htmltemplate          import *
from webpage.mainpage      import main_frame
from webpage.streamingpage import Streaming
from motion                import Historic
from video                 import Camera
from tools                 import lang,info, strings,tasking

def get_days_pagination(last_days, request):
	""" Get the pagination html part of days """
	current_day = b""
	last_days = list(last_days)

	if len(last_days) > 0:
		last_days.sort()
		last_days.reverse()

		pages = []

		day_id = int(request.params.get(b"day_id",0))
		max_days = 5
		if len(last_days) > max_days:
			if day_id - 2 < 0:
				begin_day = 0
				end_day   = len(last_days) if len(last_days) < max_days else max_days
			elif day_id + 3 > len(last_days):
				end_day   = len(last_days)
				begin_day = 0 if len(last_days) < max_days else len(last_days) - max_days
			else:
				begin_day = day_id - max_days // 2
				end_day   = day_id + (max_days//2 + 1)

			if begin_day > 0:
				pages.append(PageItem(text=b"...", class_=b"", href=b"/historic?day_id=%d"%(begin_day-1)))
		else:
			begin_day = 0
			end_day = len(last_days)

		i = begin_day
		for day in last_days[begin_day:end_day]:
			pages.append(PageItem(text=day[8:10],
				class_=b"",
				active=b"active" if day_id == i else b"",
				href=b"/historic?day_id=%d"%i if day_id != i else b""))
			if day_id == i:
				current_day = day
			i += 1

		if len(last_days) > max_days:
			if end_day < len(last_days):
				pages.append(PageItem(text=b"...", class_=b"", href=b"/historic?day_id=%d"%(end_day)))

		pagination_begin = Pagination(pages, class_=b"pagination-sm", id=b"pagination_begin")
		pagination_end   = Pagination(pages, class_=b"pagination-sm", id=b"pagination_end")
		result = pagination_begin, pagination_end,current_day
	else:
		result = None,None,current_day
	return result


@HttpServer.add_route(b'/historic', menu=lang.menu_motion, item=lang.item_historic, available=info.iscamera() and Camera.is_activated())
async def historic(request, response, args):
	""" Historic motion detection page """
	Streaming.stop()
	Historic.get_root()
	last_days = await Historic.get_last_days()
	pagination_begin, pagination_end,current_day = get_days_pagination(last_days, request)

	if pagination_end is not None and pagination_begin is not None:
		page_content = [\
			pagination_begin,
			Tag(b"""

			<div class="modal" id="zoom_window">
				<div class="modal-dialog modal-fullscreen">
					<div class="modal-content">
						<div class="modal-header">
							<button type="button" class="btn " data-bs-dismiss="modal">Close</button>
							<button type="button" class="btn-close" data-bs-dismiss="modal"></button>
						</div>
						<div class="modal-body" >
							<canvas id="zoom_image" class="w-100" data-bs-dismiss="modal"/>
						</div>
					</div>
				</div>
			</div>

			<script type='text/javascript'>

			window.onload = load_historic;

			var current_day = '%s';

			var historic = null;
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
						select_day();
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

			function rtrim(x, characters)
			{
				var start = 0;
				var end = x.length - 1;
				while (characters.indexOf(x[end]) >= 0)
				{
					end -= 1;
				}
				return x.substr(0, end + 1);
			}

			function ltrim(x, characters) 
			{
				var start = 0;
				while (characters.indexOf(x[start]) >= 0)
				{
					start += 1;
				}
				var end = x.length - 1;
				return x.substr(start);
			}

			function get_day(id)
			{
				var filename = historic[id][MOTION_FILENAME];
				filename = ltrim(filename, "/");
				filename = filename.split("/");
				return filename[1]+"/"+filename[2]+"/"+filename[3];
			}

			function select_day()
			{
				if (historic.length > 0)
				{
					for (i = 0; i < historic.length; i++)
					{
						if (get_day(i) == current_day)
						{
							last_id = i;
							break;
						}
					}
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
							div.className = "col-lg-2  pb-1";

							var canvas = document.createElement("canvas");
								canvas.width     = motion[MOTION_WIDTH ] * get_quality();
								canvas.height    = motion[MOTION_HEIGHT] * get_quality();
								canvas.id        = last_id;
								canvas.className = "w-100";
								canvas.setAttribute("data-bs-toggle","modal");
								canvas.setAttribute("data-bs-target","#zoom_window");
								canvas.onclick = e => 
									{
										var view = document.getElementById('zoom_image');
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
							if (get_day(last_id) == current_day)
							{
								setTimeout(load_image, 1);
							}
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


				var font_size = 35 * get_quality();
				ctx.font = font_size + "px monospace";
				var width = ctx.measureText(get_name(motion[MOTION_FILENAME])).width;
				ctx.fillStyle = 'rgba(0,0,0,0.3)';

				ctx.fillRect(0,(motion[MOTION_HEIGHT] * get_quality())-font_size, 
					width+get_quality(), font_size+10);

				ctx.fillStyle = 'rgba(255,255,255,0.5)';
				ctx.fillText(get_name(motion[MOTION_FILENAME]),  3, (motion[MOTION_HEIGHT] * get_quality() - 5*get_quality() ));
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
			<div id="motions" class="row"></div>
			"""%(current_day)),
			Br(),
			pagination_end
		]
	else:
		page_content = Tag(b"<span>%s</span>"%lang.historic_not_available)
	page = main_frame(request, response, args,lang.last_motion_detections,Form(page_content))
	await response.send_page(page)

@HttpServer.add_route(b'/historic/historic.json', available=info.iscamera() and Camera.is_activated())
async def historic_json(request, response, args):
	""" Send historic json file """
	tasking.Tasks.slow_down()
	try:
		await response.send_buffer(b"historic.json", await Historic.get_json())
	except Exception as err:
		await response.send_not_found(err)

@HttpServer.add_route(b'/historic/images/.*', available=info.iscamera() and Camera.is_activated())
async def historic_image(request, response, args):
	""" Send historic image """
	tasking.Tasks.slow_down()
	reserved = await Camera.reserve(Historic, timeout=5, suspension=15)
	try:
		if reserved:
			await Historic.acquire()
			await response.send_file(strings.tostrings(request.path[len("/historic/images/"):]), base64=True)
		else:
			await response.send_not_found()
	finally:
		if reserved:
			await Historic.release()
			await Camera.unreserve(Historic)

@HttpServer.add_route(b'/historic/download/.*', available=info.iscamera() and Camera.is_activated())
async def download_image(request, response, args):
	""" Download historic image """
	tasking.Tasks.slow_down()
	reserved = await Camera.reserve(Historic, timeout=5, suspension=15)
	try:
		if reserved:
			await Historic.acquire()
			await response.send_file(strings.tostrings(request.path[len("/historic/download/"):]), base64=False)
		else:
			await response.send_not_found()
	finally:
		if reserved:
			await Historic.release()
			await Camera.unreserve(Historic)
