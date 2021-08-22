# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to see the camera streaming """
from server.httpserver import HttpServer
from htmltemplate import *
from webpage.mainpage import *
from webpage.streamingpage import *
from server.httprequest import *
from tools import useful
from video import CameraConfig, Camera
from motion import SnapConfig, MotionConfig
from tools import lang
import uasyncio

zoneConfig = CameraConfig()

def zoneMasking(config, disabled):
	""" displays an html page to hide certain area of the camera, in order to ignore movements """
	info = SnapConfig.get()
	
	squarex = SnapConfig.get().square_x - 2
	squarey = SnapConfig.get().square_y - 2
	width   = SnapConfig.get().diff_x
	height  = SnapConfig.get().diff_y
	maxi     = SnapConfig.get().max
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
					width: %dpx;
					height: %dpx;
				}
				.zoneMask:checked
				{
					background-color: #1460ff;
					opacity: 0.80;
				}
			</style>
			<script>
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
					var table = document.getElementById("zoneMasking");
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
				onLoadZoneMasking();
			</script>
"""%(buttons,squarex,squarey,config.mask,disabled,height,width,maxi,maxi,maxi))
	return result

@HttpServer.addRoute(b'/motion', title=lang.motion, index=51, available=useful.iscamera())
async def motion(request, response, args):
	""" Motion configuration page """
	zoneConfig.framesize  = b"%dx%d"%(SnapConfig.get().width, SnapConfig.get().height)
	zoneConfig.quality = 30
	Streaming.setConfig(zoneConfig)
 
	# Read motion config and keep it
	backupConfig = MotionConfig()
	backupConfig.load()

	config = MotionConfig()

	# Keep activated status
	activated = config.activated
	disabled, action, submit = manageDefaultButton(request, config, onclick=b"onValidZoneMasking()")

	page = mainFrame(request, response, args, lang.motion_detection_configuration, 
		Switch(text=lang.activated, name=b"activated", checked=config.activated, disabled=disabled),
		Streaming.getHtml(request, SnapConfig.get().width, SnapConfig.get().height), 
		zoneMasking(config, disabled), Br(),
		Slider(text=lang.detects_a_movement,          name=b"differencesDetection",        min=b"1",  max=b"64", step=b"1",  value=b"%d"%config.differencesDetection,         disabled=disabled),
		Slider(text=lang.motion_detection_sensitivity,          name=b"sensitivity",        min=b"1",  max=b"100", step=b"1",  value=b"%d"%config.sensitivity,         disabled=disabled),
		Switch(text=lang.notification, name=b"notify", checked=config.notify, disabled=disabled),Br(),
		Switch(text=lang.suspends_motion_detection,                name=b"suspendOnPresence", checked=config.suspendOnPresence, disabled=disabled),Br(),
		submit)
	await response.sendPage(page)
