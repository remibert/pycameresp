# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" Function define the web page to see the camera streaming """
import server.httpserver
from htmltemplate          import *
import webpage.mainpage
import webpage.streamingpage
import video.video
import motion.motioncore
import tools.lang
import tools.info

zone_config = video.video.CameraConfig()

def zone_masking(config, disabled):
	""" displays an html page to hide certain area of the camera, in order to ignore movements """
	_ = motion.motioncore.SnapConfig.get()

	width   = motion.motioncore.SnapConfig.get().diff_x
	height  = motion.motioncore.SnapConfig.get().diff_y
	maxi    = motion.motioncore.SnapConfig.get().max
	if disabled:
		buttons = b""
	else:
		buttons = b"""
			<p>Colors squares where motion detection is ignored</p>
			<button type="button" class="btn btn-outline-primary" onclick="onClearZoneMasking()" >Clear</button>
			&nbsp;<button type="button" class="btn btn-outline-primary" onclick="onSetZoneMasking()" >Set</button><br>
			&nbsp;<input type="hidden" name="mask" id="mask" value="">"""
	result= Tag(b"""
			%s
			<style> 
				.zoneMask
				{
					-webkit-appearance: none;
					-moz-appearance: none;
					appearance: none;
					background-color: #EFEFEF;
					opacity: 0.14;
				}
				.zoneMask:checked
				{
					background-color: #1460ff;
					opacity: 0.80;
				}
			</style>
			<script>
				var videoStream      = document.getElementById("video-stream");
				var videoStreamWidth = videoStream.offsetWidth;

				function onVideoStreamDisplayed()
				{
					onLoadZoneMasking();
					resizeZoneMasking();
				}

				videoStream.addEventListener('load', onVideoStreamDisplayed);

				if (window.addEventListener) 
				{
					window.addEventListener ("resize", onResizeEvent, true);
				} 

				function onResizeEvent() 
				{
					if(videoStream.offsetWidth != videoStreamWidth)
					{
						videoStreamWidth = videoStream.offsetWidth;
						resizeZoneMasking();
					}
				}

				function resizeZoneMasking()
				{
					var cellWidth  = (videoStream.offsetWidth  / 20) - 2.;
					
					for (id = 0; id < %d; id++)
					{
						var cell = document.getElementById(id);
						cell.style.width  = cellWidth + "px";
						cell.style.height = cellWidth + "px";
					}
				}
			
				var initMask='%s';
				var disabled = %d;
				function check(box)
				{
					if (pressed)
					{
						if (state == -1)
						{
							state = 1-box.checked;
						}
						box.checked = state;
					}
				}

				var pressed=0;
				var state=0;
				document.body.onmousedown = function() {pressed=1;state=-1;}
				document.body.onmouseup   = function() {pressed=0;state=-1;}

				function onLoadZoneMasking()
				{
					var table = document.getElementById("zone_masking");
					var id = 0;
					for (line = 0; line < %d; line ++)
					{
						var row = table.insertRow(line);
						for (column = 0; column < %d; column ++)
						{
							var tag = 'type="checkbox" class="zoneMask" onmousemove="check(this)" id="'+id+'"';
							if (initMask.charAt(id) == "/")
							{
								tag += " checked ";
							}
							if (disabled)
							{
								tag += " disabled ";
							}

							row.insertCell(column).innerHTML = '<input ' + tag + ' />';
							id += 1;
						}
					}
				}
				function onValidZoneMasking()
				{
					var result = ""
					for (id = 0; id < %d; id ++)
					{
						var cell = document.getElementById(id);
						if (cell.checked)
						{
							result += "/";
						}
						else
						{
							result += " ";
						}
					}
					document.getElementById('mask').value = result;
				}
				function onClearZoneMasking()
				{
					for (id = 0; id < %d; id ++)
					{
						var cell = document.getElementById(id);
						cell.checked = 0;
					}
				}
				function onSetZoneMasking()
				{
					for (id = 0; id < %d; id ++)
					{
						var cell = document.getElementById(id);
						cell.checked = 1;
					}
				}
			</script>
"""%(buttons,maxi,config.mask,disabled,height,width,maxi,maxi,maxi))
	return result

@server.httpserver.HttpServer.add_route(b'/motion/config', menu=tools.lang.menu_motion, item=tools.lang.item_motion, available=tools.info.iscamera() and video.video.Camera.is_activated())
async def motion_page(request, response, args):
	""" Motion configuration page """
	zone_config.framesize  = b"%dx%d"%(motion.motioncore.SnapConfig.get().width, motion.motioncore.SnapConfig.get().height)
	zone_config.quality = 30
	webpage.streamingpage.Streaming.set_config(zone_config)

	# Read motion config
	config = motion.motioncore.MotionConfig()

	# Keep activated status
	disabled, action, submit = webpage.mainpage.manage_default_button(request, config, onclick=b"onValidZoneMasking()")

	page = webpage.mainpage.main_frame(request, response, args, tools.lang.motion_detection_configuration,
		Form([
			Switch(text=tools.lang.activated, name=b"activated", checked=config.activated, disabled=disabled),
			webpage.streamingpage.Streaming.get_html(request),
			zone_masking(config, disabled),
			Slider(text=tools.lang.detects_a_movement,          name=b"differences_detection",        min=b"1",  max=b"64", step=b"1",  value=b"%d"%config.differences_detection,         disabled=disabled),
			Slider(text=tools.lang.motion_detection_sensitivity,          name=b"sensitivity",        min=b"0",  max=b"100", step=b"5",  value=b"%d"%config.sensitivity,         disabled=disabled),
			Switch(text=tools.lang.notification_motion, name=b"notify",       checked=config.notify,       disabled=disabled),
			Switch(text=tools.lang.notification_state,  name=b"notify_state", checked=config.notify_state, disabled=disabled),
			Switch(text=tools.lang.suspends_motion_detection,                name=b"suspend_on_presence",     checked=config.suspend_on_presence, disabled=disabled),
			Switch(text=tools.lang.permanent_detection,                      name=b"permanent_detection",     checked=config.permanent_detection, disabled=disabled),
			Switch(text=tools.lang.turn_on_flash,                            name=b"light_compensation",      checked=config.light_compensation,  disabled=disabled),
			submit
		]))
	await response.send_page(page)

@server.httpserver.HttpServer.add_route(b'/motion/onoff', menu=tools.lang.menu_motion, item=tools.lang.item_motion_onoff, available=tools.info.iscamera() and video.video.Camera.is_activated())
async def motion_on_off(request, response, args):
	""" Motion command page """
	config = motion.motioncore.MotionConfig()
	config.load()
	command = request.params.get(b"action",b"none")
	if command == b"on":
		config.activated = True
		config.save()
	elif command == b"off":
		config.activated = False
		config.save()

	page = webpage.mainpage.main_frame(request, response, args, tools.lang.motion_onoff,
		Form([
			Submit(text=tools.lang.motion_off if config.activated else tools.lang.motion_on,  name=b"action", value=b"off" if config.activated else b"on" )
		]))
	await response.send_page(page)
