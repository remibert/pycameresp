# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to configure the start of servers """
from server.httpserver import HttpServer
from htmltemplate      import *
from webpage.mainpage  import *
from tools.useful      import *
from server.server     import ServerConfig
from tools import lang

@HttpServer.addRoute(b'/server', title=lang.server, index=13)
async def server(request, response, args):
	""" Function define the web page to configure the start of servers """
	config = ServerConfig()
	disabled, action, submit = manageDefaultButton(request, config)
	page = mainFrame(request, response, args,lang.servers_configuration,
		Switch(text=lang.ftp   , name=b"ftp"   , checked=config.ftp,    disabled=disabled),Br(),
		Switch(text=lang.http  , name=b"http"  , checked=config.http,   disabled=disabled),Br(),
		Switch(text=lang.telnet, name=b"telnet", checked=config.telnet, disabled=disabled),Br(),
		Switch(text=lang.time_synchronization   , name=b"ntp"   , checked=config.ntp,    disabled=disabled),Br(),
		Switch(text=lang.wan_ip   , name=b"wanip"   , checked=config.wanip,    disabled=disabled),Br(),
		Edit  (text=lang.utc_offset , name=b"offsettime",       pattern=b"-*[0-9]*[0-9]", placeholder=lang.offset_time_to,        value=b"%d"%config.offsettime,       disabled=disabled),
		Switch(text=lang.daylight_saving_time   , name=b"dst"   , checked=config.dst,    disabled=disabled),Br(),
		Switch(text=lang.notification_reboot_user, name=b"notify", checked=config.notify, disabled=disabled),Br(),
		submit)
	await response.sendPage(page)
