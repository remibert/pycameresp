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
from motion import MotionInfo, MaskingConfig
import uasyncio

zoneConfig = CameraConfig()

def zoneMasking(config, disabled):
	""" displays an html page to hide certain area of the camera, in order to ignore movements """
	info = MotionInfo.get()
	
	squarex = info["diff"]["squarex"] - 2
	squarey = info["diff"]["squarey"] - 2
	width   = info["diff"]["width"]
	height  = info["diff"]["height"]
	max     = info["diff"]["max"]
	if disabled:
		buttons = b""
	else:
		buttons = b"""
			<button type="button" class="btn btn-outline-primary" onclick="onClearZoneMasking()" >Clear</button>
			<button type="button" class="btn btn-outline-primary" onclick="onSetZoneMasking()" >Set</button>
	"""
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
				onLoadZoneMasking();
			</script>
"""%(buttons,squarex,squarey,height,width,max,max,max))
	return result

@HttpServer.addRoute(b'/zonemasking', title=b"Masking", index=52)
async def zoneMaskingPage(request, response, args):
	""" Camera streaming page """
	zoneConfig.framesize  = b"800x600"
	zoneConfig.quality = 30
	Streaming.setConfig(zoneConfig)
	config = MaskingConfig()
	disabled = False
	disabled, action, submit = manageDefaultButton(request, config, onclick=b"onValidZoneMasking()")
 
	page = mainFrame(request, response, args, b"Masking", Streaming.getHtml(request), zoneMasking(config, disabled), submit)
	await response.sendPage(page)

	# framesizes = []
	# Streaming.setConfig(cameraConfig)

	# for size in [b"1600x1200",b"1280x1024",b"1024x768",b"800x600",b"640x480",b"400x296",b"320x240",b"240x176",b"160x120"  ]:
	# 	framesizes.append(Option(value=size, text=size, selected= True if cameraConfig.framesize == size else False))
	# page = mainFrame(request, response, args, b"Camera",
	# 			Streaming.getHtml(request),
	# 			ComboCmd(framesizes, text=b"Resolution", path=b"camera/configure", name=b"framesize"),
	# 			SliderCmd(           text=b"Quality"   , path=b"camera/configure", name=b"quality",    min=b"10", max=b"63", step=b"1", value=b"%d"%cameraConfig.quality),
	# 			SliderCmd(           text=b"Brightness", path=b"camera/configure", name=b"brightness", min=b"-2", max=b"2" , step=b"1", value=b"%d"%cameraConfig.brightness),
	# 			SliderCmd(           text=b"Contrast"  , path=b"camera/configure", name=b"contrast"  , min=b"-2", max=b"2" , step=b"1", value=b"%d"%cameraConfig.contrast),
	# 			SliderCmd(           text=b"Saturation", path=b"camera/configure", name=b"saturation", min=b"-2", max=b"2" , step=b"1", value=b"%d"%cameraConfig.saturation),
	# 			SwitchCmd(           text=b"H-Mirror"  , path=b"camera/configure", name=b"hmirror"   , checked=cameraConfig.hmirror),
	# 			SwitchCmd(           text=b"V-Flip"    , path=b"camera/configure", name=b"vflip"     , checked=cameraConfig.vflip))
	# await response.sendPage(page)
