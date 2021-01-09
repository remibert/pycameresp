# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to configure the motion detection """
from server.httpserver import HttpServer
from htmltemplate import *
from webpage import *
from motion import MotionConfig

@HttpServer.addRoute(b'/motion', title=b"Motion", index=17, available=useful.iscamera())
async def motion(request, response, args):
	""" Motion configuration page """
	config = MotionConfig()
	config.load()
	action = request.params.get(b"modify",b"none")
	if   action == b"none"  : disabled = True
	elif action == b"modify": disabled = False 
	elif action == b"save"  : 
		disabled = True
		del request.params[b"modify"]
		config.update(request.params)
		config.save()

	if disabled:
		submit = Submit(text=b"Modify")
		value = b'modify'
	else:
		submit = Submit(text=b"Save")
		value = b'save'

	page = mainPage(
		content=[Br(),Container([\
					Card([\
						Form([\
							Br(),
							Switch(text=b"Activated", name=b"activated", checked=config.activated, disabled=disabled),
							Title3(text=b"Images configuration"),
							Edit(text=b"Start detection at image",         name=b"stabilizationCamera",  placeholder=b"Number of images to stabilize the camera",                                        pattern=b"[0-9]*[0-9]", value=b"%d"%config.stabilizationCamera,  disabled=disabled),
							Edit(text=b"Image historic size",              name=b"maxMotionImages",      placeholder=b"Images in motion historic",                                                       pattern=b"[0-9]*[0-9]", value=b"%d"%config.maxMotionImages,      disabled=disabled),
							Edit(text=b"Glitch ignored threshold",         name=b"thresholdGlitch",      placeholder=b"Glitch threshold of image ignored (sometime the camera bug)",                     pattern=b"[0-9]*[0-9]", value=b"%d"%config.thresholdGlitch,      disabled=disabled),
							Edit(text=b"Motion detection threshold",       name=b"thresholdMotion",      placeholder=b"Threshold of minimum image to detect motion",                                     pattern=b"[0-9]*[0-9]", value=b"%d"%config.thresholdMotion,      disabled=disabled),
							Title3(text=b"Detection configuration"),
							Edit(text=b"Minimum difference threshold",     name=b"minRgbDetection",      placeholder=b"Beyond this number of differences, motion detected (0..50)",                      pattern=b"[0-9]*[0-9]", value=b"%d"%config.minRgbDetection,      disabled=disabled),
							Edit(text=b"Maximum difference threshold",     name=b"maxRgbDetection",      placeholder=b"Beyond this number of differences, motion is no longer detected (50..118)",       pattern=b"[0-9]*[0-9]", value=b"%d"%config.maxRgbDetection,      disabled=disabled),
							Edit(text=b"Equivalence range",                name=b"rbgErrorRange",        placeholder=b"If the difference is less than the defined range it is considered equal",         pattern=b"[0-9]*[0-9]", value=b"%d"%config.rbgErrorRange,        disabled=disabled),
							Edit(text=b"Awake duration on battery",        name=b"awakeTime",            placeholder=b"time in seconds awake on battery",                                                pattern=b"[0-9]*[0-9]", value=b"%d"%config.awakeTime,            disabled=disabled),
							Input (text=b"modify" , name=b"modify", type=b"hidden", value=value),
							submit,
						]),
					])
				])
			], title=args["title"], active=args["index"], request=request, response=response)

	await response.sendPage(page)
