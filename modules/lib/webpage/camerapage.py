# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" Function define the web page to see the camera streaming """
import server.httprequest
from htmltemplate          import *
import webpage.mainpage
import webpage.streamingpage
import video.video
import tools.lang
import tools.info
import tools.tasking

@server.httpserver.HttpServer.add_route(b'/camera', menu=tools.lang.menu_camera, item=tools.lang.item_camera, available=tools.info.iscamera() and video.video.Camera.is_activated())
async def camera_page(request, response, args):
	""" Camera streaming page """
	framesizes = []
	config = video.video.Camera.get_config()
	webpage.streamingpage.Streaming.set_config(config)

	for size in [b"1600x1200",b"1280x1024",b"1024x768",b"800x600",b"640x480",b"400x296",b"320x240",b"240x176",b"160x120"  ]:
		framesizes.append(Option(value=size, text=size, selected= True if config.framesize == size else False))
	page = webpage.mainpage.main_frame(request, response, args, tools.lang.camera,
		Form([
				webpage.streamingpage.Streaming.get_html(request),
				ComboCmd(framesizes, text=tools.lang.resolution,  path=b"camera/configure", name=b"framesize"),
				SliderCmd(           text=tools.lang.quality   ,  path=b"camera/configure", name=b"quality",    min=b"10", max=b"63",  step=b"1", value=b"%d"%config.quality),
				# SliderCmd(           text=tools.lang.brightness,  path=b"camera/configure", name=b"brightness", min=b"-2", max=b"2" ,  step=b"1", value=b"%d"%config.brightness),
				# SliderCmd(           text=tools.lang.contrast  ,  path=b"camera/configure", name=b"contrast"  , min=b"-2", max=b"2" ,  step=b"1", value=b"%d"%config.contrast),
				# SliderCmd(           text=tools.lang.saturation,  path=b"camera/configure", name=b"saturation", min=b"-2", max=b"2" ,  step=b"1", value=b"%d"%config.saturation),
				SliderCmd(           text=tools.lang.flash_level, path=b"camera/configure", name=b"flash_level", min=b"0" , max=b"256", step=b"1", value=b"%d"%config.flash_level),
				SwitchCmd(           text=tools.lang.hmirror   ,  path=b"camera/configure", name=b"hmirror"   , checked=config.hmirror),
				SwitchCmd(           text=tools.lang.vflip     ,  path=b"camera/configure", name=b"vflip"     , checked=config.vflip)
		]))
	await response.send_page(page)

@server.httpserver.HttpServer.add_route(b'/camera/configure')
async def camera_configure(request, response, args):
	""" Real time camera configuration """
	tools.tasking.Tasks.slow_down()
	# print(strings.tostrings(b"%s=%s"%(request.params[b"name"],request.params[b"value"])))
	config = video.video.Camera.get_config()
	config.update(request.params)
	config.save()
	webpage.streamingpage.Streaming.set_config(config)

	webpage.streamingpage.Streaming.activity()
	await response.send_ok()

@server.httpserver.HttpServer.add_route(b'/camera/onoff', menu=tools.lang.menu_camera, item=tools.lang.item_onoff, available=tools.info.iscamera())
async def camera_on_off(request, response, args):
	""" Camera command page """
	config = video.video.Camera.get_config()
	command = request.params.get(b"action",b"none")
	if command == b"on":
		config.activated = True
	elif command == b"off":
		config.activated = False

	if command in [b"on",b"off"]:
		config.save()
		alert = AlertError(text=tools.lang.taken_into_account)
	else:
		alert = None

	page = webpage.mainpage.main_frame(request, response, args, tools.lang.camera_onoff,
		Form([
			Submit(text=tools.lang.camera_off if config.activated else tools.lang.camera_on,  name=b"action", value=b"off" if config.activated else b"on" ), alert
		]))
	await response.send_page(page)
