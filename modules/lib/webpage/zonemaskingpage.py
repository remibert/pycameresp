# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to see the camera streaming """
from server.httpserver import HttpServer
from htmltemplate import *
from webpage import *
from server.httprequest import *
from tools import useful
from video import CameraConfig, Camera
from webpage import streamingpage
from motion import SnapConfig
import uasyncio

zoneConfig = CameraConfig()

def zoneMasking(config, disabled):
	""" displays an html page to hide certain area of the camera, in order to ignore movements """
	info = SnapConfig.get()
	
	squarex = SnapConfig.get().square_x - 2
	squarey = SnapConfig.get().square_y - 2
	width   = SnapConfig.get().diff_x
	height  = SnapConfig.get().diff_y
	max     = SnapConfig.get().max
	if disabled:
		buttons = b""
	else:
		buttons = b"""
			<p>Color the squares to ignore for motion detection</p>
			<button type="button" class="btn btn-outline-primary" onclick="onClearZoneMasking()" >Clear</button>
			&nbsp;<button type="button" class="btn btn-outline-primary" onclick="onSetZoneMasking()" >Set</button>
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
"""%(buttons,squarex,squarey,config.mask,disabled,height,width,max,max,max))
	return result

@HttpServer.addRoute(b'/zonemasking', title=b"Masking", index=52)
async def zoneMaskingPage(request, response, args):
	""" Camera streaming page """
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

	if action == b"save":
		# Save config with mask modified
		backupConfig.mask = config.mask
		backupConfig.save()

	page = mainFrame(request, response, args, b"Masking", Br(),Streaming.getHtml(request, SnapConfig.get().width, SnapConfig.get().height), zoneMasking(config, disabled), submit)
	await response.sendPage(page)
