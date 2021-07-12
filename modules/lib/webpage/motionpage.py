# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to configure the motion detection """
from server.httpserver import HttpServer
from htmltemplate import *
from webpage import *
from motion import MotionConfig

@HttpServer.addRoute(b'/motion', title=b"Motion", index=51, available=useful.iscamera())
async def motion(request, response, args):
	""" Motion configuration page """
	config = MotionConfig()
	disabled, action, submit = manageDefaultButton(request, config)
	page = mainFrame(request, response, args,b"Motion detection configuration",
		Switch(text=b"Activated", name=b"activated", checked=config.activated, disabled=disabled),Br(),
		Slider(text=b"Detect motion when the differences on two successive images is greater or equal to",          name=b"contigousDetection",        min=b"1",  max=b"100", step=b"1",  value=b"%d"%config.contigousDetection,         disabled=disabled),
		Tag(b'<small style="color:grey">The notification contains the detection difference in field "D=" </small>'),Br(),Br(),
		Edit(text=b"Awake duration on battery",                                name=b"awakeTime",            placeholder=b"Time in seconds it stays awake when on battery power", pattern=b"[0-9]*[0-9]", value=b"%d"%config.awakeTime, disabled=disabled),
		Switch(text=b"Notification", name=b"notify", checked=config.notify, disabled=disabled),Br(),
		Switch(text=b"Suspend when occupant presence detected",                name=b"suspendOnPresence", checked=config.suspendOnPresence, disabled=disabled),Br(),
		submit)
	await response.sendPage(page)
