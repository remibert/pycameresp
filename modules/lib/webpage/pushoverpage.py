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
	config.load()

	action = request.params.get(b"modify",b"none")
	if   action == b"none"  : disabled = True
	elif action == b"modify": disabled = False 
	elif action == b"save"  : 
		disabled = True
		del request.params[b"modify"]
		config.update(request.params)
		config.save()
		await asyncNotify(token=config.token, user=config.user, message = b"Pushover notification %s"%(b"enabled" if config.activated else b"disabled"))

	if disabled:
		submit = Submit(text=b"Modify")
		value = b'modify'
	else:
		submit = Submit(text=b"Save")
		value = b'save'

	page = mainFrame(request, response, args,b"Notification configuration",
		Switch(text=b"Activated", name=b"activated", checked=config.activated, disabled=disabled),
		Edit(text=b"User",  name=b"user",  placeholder=b"Enter pushover user",  type=b"password", value=config.user,  disabled=disabled),
		Edit(text=b"Token", name=b"token", placeholder=b"Enter pushover token", type=b"password", value=config.token, disabled=disabled),
		Input (text=b"modify" , name=b"modify", type=b"hidden", value=value),
		submit,
		Br(), Br(), Link(href=b"https://pushover.net", text=b"See pushover website"))

	await response.sendPage(page)
