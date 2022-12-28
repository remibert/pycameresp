# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to see the camera streaming """
from server.httpserver     import HttpServer
from htmltemplate          import *
from webpage.mainpage      import main_frame, manage_default_button
from webpage.streamingpage import *
from video                 import CameraConfig, Camera
from motion                import SnapConfig, MotionConfig
import uasyncio
from tools                 import lang, info

zone_config = CameraConfig()

def zone_masking(config, disabled):
	""" displays an html page to hide certain area of the camera, in order to ignore movements """
	_ = SnapConfig.get()

	width   = SnapConfig.get().diff_x
	height  = SnapConfig.get().diff_y
	maxi    = SnapConfig.get().max
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

@HttpServer.add_route(b'/motion/config', menu=lang.menu_motion, item=lang.item_motion, available=info.iscamera() and Camera.is_activated())
async def motion(request, response, args):
	""" Motion configuration page """
	zone_config.framesize  = b"%dx%d"%(SnapConfig.get().width, SnapConfig.get().height)
	zone_config.quality = 30
	Streaming.set_config(zone_config)

	# Read motion config
	config = MotionConfig()

	# Keep activated status
	disabled, action, submit = manage_default_button(request, config, onclick=b"onValidZoneMasking()")

	page = main_frame(request, response, args, lang.motion_detection_configuration,
		Form([
			Switch(text=lang.activated, name=b"activated", checked=config.activated, disabled=disabled),
			Streaming.get_html(request),
			zone_masking(config, disabled),
			Slider(text=lang.detects_a_movement,          name=b"differences_detection",        min=b"1",  max=b"64", step=b"1",  value=b"%d"%config.differences_detection,         disabled=disabled),
			Slider(text=lang.motion_detection_sensitivity,          name=b"sensitivity",        min=b"0",  max=b"100", step=b"5",  value=b"%d"%config.sensitivity,         disabled=disabled),
			Switch(text=lang.notification_motion, name=b"notify",       checked=config.notify,       disabled=disabled),
			Switch(text=lang.notification_state,  name=b"notify_state", checked=config.notify_state, disabled=disabled),
			Switch(text=lang.suspends_motion_detection,                name=b"suspend_on_presence", checked=config.suspend_on_presence, disabled=disabled),
			Switch(text=lang.permanent_detection,                      name=b"permanent_detection", checked=config.permanent_detection, disabled=disabled),
			Switch(text=lang.turn_on_flash,                            name=b"light_compensation",  checked=config.light_compensation,  disabled=disabled),
			submit
		]))
	await response.send_page(page)

@HttpServer.add_route(b'/motion/onoff', menu=lang.menu_motion, item=lang.item_motion_onoff, available=info.iscamera() and Camera.is_activated())
async def motion_on_off(request, response, args):
	""" Motion command page """
	config = MotionConfig()
	config.load()
	command = request.params.get(b"action",b"none")
	if command == b"on":
		config.activated = True
		config.save()
	elif command == b"off":
		config.activated = False
		config.save()

	page = main_frame(request, response, args, lang.motion_onoff,
		Form([
			Submit(text=lang.motion_off if config.activated else lang.motion_on,  name=b"action", value=b"off" if config.activated else b"on" )
		]))
	await response.send_page(page)
