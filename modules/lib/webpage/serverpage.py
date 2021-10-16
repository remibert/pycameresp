# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to configure the start of servers """
from server.httpserver import HttpServer
from server.server     import ServerConfig
from htmltemplate      import *
from webpage.mainpage  import main_frame, manage_default_button
from tools.useful      import *
from tools import lang

@HttpServer.add_route(b'/server', menu=lang.menu_server, item=lang.item_server)
async def server(request, response, args):
	""" Function define the web page to configure the start of servers """
	config = ServerConfig()
	disabled, action, submit = manage_default_button(request, config)
	page = main_frame(request, response, args,lang.servers_configuration,
		Switch(text=lang.ftp   , name=b"ftp"   , checked=config.ftp,    disabled=disabled),Br(),
		Switch(text=lang.http  , name=b"http"  , checked=config.http,   disabled=disabled),Br(),
		Switch(text=lang.telnet, name=b"telnet", checked=config.telnet, disabled=disabled),Br(),
		Switch(text=lang.time_synchronization   , name=b"ntp"   , checked=config.ntp,    disabled=disabled),Br(),
		Switch(text=lang.wan_ip   , name=b"wanip"   , checked=config.wanip,    disabled=disabled),Br(),
		Switch(text=lang.notification_reboot_user, name=b"notify", checked=config.notify, disabled=disabled),Br(),
		submit)
	await response.send_page(page)
