# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to see the camera streaming """
from server.httpserver     import HttpServer
from server.server         import Server
from htmltemplate          import *
from webpage.mainpage      import mainFrame
from webpage.streamingpage import *
from server.httprequest    import *
from tools                 import useful, lang
from video                 import Camera
import uasyncio

@HttpServer.addRoute(b'/camera', menu=lang.menu_camera, item=lang.item_camera, available=useful.iscamera() and Camera.isActivated())
async def cameraPage(request, response, args):
	""" Camera streaming page """
	framesizes = []
	config = Camera.getConfig()
	Streaming.setConfig(config)

	for size in [b"1600x1200",b"1280x1024",b"1024x768",b"800x600",b"640x480",b"400x296",b"320x240",b"240x176",b"160x120"  ]:
		framesizes.append(Option(value=size, text=size, selected= True if config.framesize == size else False))
	page = mainFrame(request, response, args, lang.camera,
				Streaming.getHtml(request),
				ComboCmd(framesizes, text=lang.resolution, path=b"camera/configure", name=b"framesize"),
				SliderCmd(           text=lang.quality   , path=b"camera/configure", name=b"quality",    min=b"10", max=b"63", step=b"1", value=b"%d"%config.quality),
				SliderCmd(           text=lang.brightness, path=b"camera/configure", name=b"brightness", min=b"-2", max=b"2" , step=b"1", value=b"%d"%config.brightness),
				SliderCmd(           text=lang.contrast  , path=b"camera/configure", name=b"contrast"  , min=b"-2", max=b"2" , step=b"1", value=b"%d"%config.contrast),
				SliderCmd(           text=lang.saturation, path=b"camera/configure", name=b"saturation", min=b"-2", max=b"2" , step=b"1", value=b"%d"%config.saturation),
				SwitchCmd(           text=lang.hmirror   , path=b"camera/configure", name=b"hmirror"   , checked=config.hmirror),
				SwitchCmd(           text=lang.vflip     , path=b"camera/configure", name=b"vflip"     , checked=config.vflip))
	await response.sendPage(page)

@HttpServer.addRoute(b'/camera/configure')
async def cameraConfigure(request, response, args):
	""" Real time camera configuration """
	Server.slowDown()
	# print(useful.tostrings(b"%s=%s"%(request.params[b"name"],request.params[b"value"])))
	config = Camera.getConfig()
	config.update(request.params)
	config.save()
	Streaming.setConfig(config)
	
	Streaming.activity()
	await response.sendOk()

@HttpServer.addRoute(b'/camera/onoff', menu=lang.menu_camera, item=lang.item_onoff, available=useful.iscamera())
async def cameraOnOff(request, response, args):
	""" Camera command page """
	config = Camera.getConfig()
	command = request.params.get(b"action",b"none") 
	if command == b"on":
		config.activated = True
	elif command == b"off":
		config.activated = False

	if command in [b"on",b"off"]:
		config.save()
		alert = Br(), Br(), AlertError(text=lang.taken_into_account)
	else:
		alert = None

	page = mainFrame(request, response, args, lang.camera_onoff,
		Submit(text=lang.camera_off if config.activated else lang.camera_on,  name=b"action", value=b"off" if config.activated else b"on" ), alert)
	await response.sendPage(page)
