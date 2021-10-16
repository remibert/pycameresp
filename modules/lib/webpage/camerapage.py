# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to see the camera streaming """
from server.server         import Server
from server.httprequest    import *
from htmltemplate          import *
from webpage.mainpage      import main_frame
from webpage.streamingpage import *
from video                 import Camera
import uasyncio
from tools                 import useful, lang

@HttpServer.add_route(b'/camera', menu=lang.menu_camera, item=lang.item_camera, available=useful.iscamera() and Camera.is_activated())
async def camera_page(request, response, args):
	""" Camera streaming page """
	framesizes = []
	config = Camera.get_config()
	Streaming.set_config(config)

	for size in [b"1600x1200",b"1280x1024",b"1024x768",b"800x600",b"640x480",b"400x296",b"320x240",b"240x176",b"160x120"  ]:
		framesizes.append(Option(value=size, text=size, selected= True if config.framesize == size else False))
	page = main_frame(request, response, args, lang.camera,
				Streaming.get_html(request),
				ComboCmd(framesizes, text=lang.resolution,  path=b"camera/configure", name=b"framesize"),
				SliderCmd(           text=lang.quality   ,  path=b"camera/configure", name=b"quality",    min=b"10", max=b"63",  step=b"1", value=b"%d"%config.quality),
				SliderCmd(           text=lang.brightness,  path=b"camera/configure", name=b"brightness", min=b"-2", max=b"2" ,  step=b"1", value=b"%d"%config.brightness),
				SliderCmd(           text=lang.contrast  ,  path=b"camera/configure", name=b"contrast"  , min=b"-2", max=b"2" ,  step=b"1", value=b"%d"%config.contrast),
				SliderCmd(           text=lang.saturation,  path=b"camera/configure", name=b"saturation", min=b"-2", max=b"2" ,  step=b"1", value=b"%d"%config.saturation),
				SliderCmd(           text=lang.flash_level, path=b"camera/configure", name=b"flash_level", min=b"0" , max=b"256", step=b"1", value=b"%d"%config.flash_level),
				SwitchCmd(           text=lang.hmirror   ,  path=b"camera/configure", name=b"hmirror"   , checked=config.hmirror),
				SwitchCmd(           text=lang.vflip     ,  path=b"camera/configure", name=b"vflip"     , checked=config.vflip))
	await response.send_page(page)

@HttpServer.add_route(b'/camera/configure')
async def camera_configure(request, response, args):
	""" Real time camera configuration """
	Server.slow_down()
	# print(useful.tostrings(b"%s=%s"%(request.params[b"name"],request.params[b"value"])))
	config = Camera.get_config()
	config.update(request.params)
	config.save()
	Streaming.set_config(config)

	Streaming.activity()
	await response.send_ok()

@HttpServer.add_route(b'/camera/onoff', menu=lang.menu_camera, item=lang.item_onoff, available=useful.iscamera())
async def camera_on_off(request, response, args):
	""" Camera command page """
	config = Camera.get_config()
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

	page = main_frame(request, response, args, lang.camera_onoff,
		Submit(text=lang.camera_off if config.activated else lang.camera_on,  name=b"action", value=b"off" if config.activated else b"on" ), alert)
	await response.send_page(page)
