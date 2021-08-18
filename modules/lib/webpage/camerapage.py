# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to see the camera streaming """
from server.httpserver import HttpServer
from server.server   import Server
from htmltemplate import *
from webpage import *
from server.httprequest import *
from tools import useful
from video import CameraConfig, Camera
import uasyncio

cameraConfig = CameraConfig()

@HttpServer.addRoute(b'/camera', title=b"Camera", index=110)
async def cameraPage(request, response, args):
	""" Camera streaming page """
	framesizes = []
	Streaming.setConfig(cameraConfig)

	for size in [b"1600x1200",b"1280x1024",b"1024x768",b"800x600",b"640x480",b"400x296",b"320x240",b"240x176",b"160x120"  ]:
		framesizes.append(Option(value=size, text=size, selected= True if cameraConfig.framesize == size else False))
	page = mainFrame(request, response, args, b"Camera",
				Streaming.getHtml(request),
				ComboCmd(framesizes, text=b"Resolution", path=b"camera/configure", name=b"framesize"),
				SliderCmd(           text=b"Quality"   , path=b"camera/configure", name=b"quality",    min=b"10", max=b"63", step=b"1", value=b"%d"%cameraConfig.quality),
				SliderCmd(           text=b"Brightness", path=b"camera/configure", name=b"brightness", min=b"-2", max=b"2" , step=b"1", value=b"%d"%cameraConfig.brightness),
				SliderCmd(           text=b"Contrast"  , path=b"camera/configure", name=b"contrast"  , min=b"-2", max=b"2" , step=b"1", value=b"%d"%cameraConfig.contrast),
				SliderCmd(           text=b"Saturation", path=b"camera/configure", name=b"saturation", min=b"-2", max=b"2" , step=b"1", value=b"%d"%cameraConfig.saturation),
				SwitchCmd(           text=b"H-Mirror"  , path=b"camera/configure", name=b"hmirror"   , checked=cameraConfig.hmirror),
				SwitchCmd(           text=b"V-Flip"    , path=b"camera/configure", name=b"vflip"     , checked=cameraConfig.vflip))
	await response.sendPage(page)

@HttpServer.addRoute(b'/camera/configure')
async def cameraConfigure(request, response, args):
	""" Real time camera configuration """
	Server.slowDown()
	print(useful.tostrings(b"%s=%s"%(request.params[b"name"],request.params[b"value"])))
	cameraConfig.update(request.params)
	Streaming.setConfig(cameraConfig)
	Streaming.activity()
	await response.sendOk()