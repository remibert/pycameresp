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
from motion import MotionInfo
import uasyncio

zoneConfig = CameraConfig()

def zoneMasking():
	""" displays an html page to hide certain area of the camera, in order to ignore movements """
	info = MotionInfo.get()
	
	squarex = info["diff"]["squarex"] - 2
	squarey = info["diff"]["squarey"] - 2
	width   = info["diff"]["width"]
	height  = info["diff"]["height"]
	max     = info["diff"]["max"]
	return Tag(b"""
			<button type="button" class="btn btn-outline-primary" onclick="onValidZoneMasking()">Valid</button>
			<button type="button" class="btn btn-outline-primary" onclick="onClearZoneMasking()" >Clear</button>
			<button type="button" class="btn btn-outline-primary" onclick="onSetZoneMasking()" >Set</button>

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
					opacity: 0.92;
				}
			</style>
			<script>
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
							var cell = row.insertCell(column);
							cell.innerHTML = '<input type="checkbox" class="zoneMask" onmousemove="check(this)" id="'+id+'"/>';
							id += 1;
						}
					}
				}
				var previousOnload = window.onload;
				window.onload = () =>
				{
					previousOnload();
					onLoadZoneMasking();
				}

				function onValidZoneMasking()
				{
					for (id = 0; id < %d; id ++)
					{
						var cell = document.getElementById(id);
						if (cell.checked)
						{
							console.log(id+":"+cell.checked);
						}
					}
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
"""%(squarex,squarey,height,width,max,max,max)  )

@HttpServer.addRoute(b'/zonemasking', title=b"Zone masking", index=102)
async def zoneMaskingPage(request, response, args):
	""" Camera streaming page """
	zoneConfig.framesize  = b"800x600"
	Streaming.setConfig(zoneConfig)
	page = mainFrame(request, response, args, b"Zone masking", Streaming.getHtml(request), zoneMasking())
	await response.sendPage(page)

