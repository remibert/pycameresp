# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to configure the start of servers """
from server.httpserver import HttpServer
from htmltemplate import *
from webpage import *
from tools.useful import *
from server import *

def configureServerPage(request, response, args, config=None,disabled=False):
	""" Content of server page """
	if disabled:
		submit = Submit(text=b"Modify")
		value = b'modify'
	else:
		submit = Submit(text=b"Save")
		value = b'save'
	page = mainFrame(request, response, args,b"Servers configuration",
		Switch(text=b"Ftp"   , name=b"ftp"   , checked=config.ftp,    disabled=disabled),
		Switch(text=b'Http'  , name=b"http"  , checked=config.http,   disabled=disabled),
		Switch(text=b"Telnet", name=b"telnet", checked=config.telnet, disabled=disabled),
		Switch(text=b"Time synchronization"   , name=b"ntp"   , checked=config.ntp,    disabled=disabled),
		Edit  (text=b"UTC offset" , name=b"offsettime",       pattern=b"-*[0-9]*[0-9]", placeholder=b"Offset time to add to UTC",        value=b"%d"%config.offsettime,       disabled=disabled),
		Switch(text=b"Daylight saving time"   , name=b"dst"   , checked=config.dst,    disabled=disabled),
		Input (text=b"modify", name=b"modify", type=b"hidden", value=value),
		submit)
	return page

@HttpServer.addRoute(b'/server', title=b"Server", index=13)
async def server(request, response, args):
	""" Function define the web page to configure the start of servers """
	config = ServerConfig()
	config.load()
	action = request.params.get(b"modify",b"none")
	if   action == b"none"  : disabled = True
	elif action == b"modify": disabled = False 
	elif action == b"save"  : 
		disabled = True
		del request.params[b"modify"]
		config.update(request.params)
		config.save()

	page = configureServerPage(request, response, args, config=config, disabled=disabled)
	await response.sendPage(page)
