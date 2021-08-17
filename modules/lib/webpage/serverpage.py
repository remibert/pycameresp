# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to configure the start of servers """
from server.httpserver import HttpServer
from htmltemplate      import *
from webpage           import *
from tools.useful      import *
from server.server     import ServerConfig

@HttpServer.addRoute(b'/server', title=b"Server", index=13)
async def server(request, response, args):
	""" Function define the web page to configure the start of servers """
	config = ServerConfig()
	disabled, action, submit = manageDefaultButton(request, config)
	page = mainFrame(request, response, args,b"Servers configuration",
		Switch(text=b"Ftp"   , name=b"ftp"   , checked=config.ftp,    disabled=disabled),Br(),
		Switch(text=b'Http'  , name=b"http"  , checked=config.http,   disabled=disabled),Br(),
		Switch(text=b"Telnet", name=b"telnet", checked=config.telnet, disabled=disabled),Br(),
		Switch(text=b"Time synchronization"   , name=b"ntp"   , checked=config.ntp,    disabled=disabled),Br(),
		Switch(text=b"Wan ip"   , name=b"wanip"   , checked=config.wanip,    disabled=disabled),Br(),
		Edit  (text=b"UTC offset" , name=b"offsettime",       pattern=b"-*[0-9]*[0-9]", placeholder=b"Offset time to add to UTC",        value=b"%d"%config.offsettime,       disabled=disabled),
		Switch(text=b"Daylight saving time"   , name=b"dst"   , checked=config.dst,    disabled=disabled),Br(),
		Switch(text=b"Notification (Reboot, User login...)", name=b"notify", checked=config.notify, disabled=disabled),Br(),
		submit)
	await response.sendPage(page)
