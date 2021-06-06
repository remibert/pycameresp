# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to configure the pushover notifications """
from server.httpserver import HttpServer
from htmltemplate import *
from webpage import *
from server.pushover import *

@HttpServer.addRoute(b'/pushover', title=b"Pushover", index=15)
async def pushover(request, response, args):
	""" Function define the web page to configure the pushover notifications """
	config = PushOverConfig()
	disabled, action, submit = manageDefaultButton(request, config)
	if action == b"save":
		await asyncNotify(token=config.token, user=config.user, message = b"pushover notification %s"%(b"on" if config.activated else b"off"))
	page = mainFrame(request, response, args,b"Notification configuration",
		Switch(text=b"Activated", name=b"activated", checked=config.activated, disabled=disabled),Br(),
		Edit(text=b"User",  name=b"user",  placeholder=b"Enter pushover user",  type=b"password", value=config.user,  disabled=disabled),
		Edit(text=b"Token", name=b"token", placeholder=b"Enter pushover token", type=b"password", value=config.token, disabled=disabled),
		submit,
		Br(), Br(), Link(href=b"https://pushover.net", text=b"See pushover website"))

	await response.sendPage(page)
