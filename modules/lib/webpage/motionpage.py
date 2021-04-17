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
							Title3(text=b"Motion detection configuration"),
							Br(),
							Switch(text=b"Activated", name=b"activated", checked=config.activated, disabled=disabled),
							Slider(text=b"Detect motion when the differences on two successive images is greater than or equal to",          name=b"contigousDetection",        min=b"1",  max=b"100", step=b"1",  value=b"%d"%config.contigousDetection,         disabled=disabled),
							Tag(b'<small style="color:grey">The notification contains the detection difference in field "D=" </small>'),Br(),Br(),
							Edit(text=b"Awake duration on battery",                                name=b"awakeTime",            placeholder=b"Time in seconds it stays awake when on battery power", pattern=b"[0-9]*[0-9]", value=b"%d"%config.awakeTime, disabled=disabled),
							Switch(text=b"Suspend when occupant presence detected",                name=b"suspendOnPresence", checked=config.suspendOnPresence, disabled=disabled),
							Input (text=b"modify" , name=b"modify", type=b"hidden", value=value),
							submit,
						]),
					])
				])
			], title=args["title"], active=args["index"], request=request, response=response)

	await response.sendPage(page)
