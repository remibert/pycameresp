# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" Function define the web page to configure the start of servers """
import server.httpserver
import server.server
from htmltemplate      import *
import webpage.mainpage
import tools.lang
import tools.support

@server.httpserver.HttpServer.add_route(b'/server', menu=tools.lang.menu_server, item=tools.lang.item_server)
async def server_page(request, response, args):
	""" Function define the web page to configure the start of servers """
	config = server.server.ServerConfig()
	disabled, action, submit = webpage.mainpage.manage_default_button(request, config)
	page = webpage.mainpage.main_frame(request, response, args,tools.lang.servers_configuration,
		Form([
			Switch(text=tools.lang.telnet, name=b"telnet", checked=config.telnet, disabled=disabled) if tools.support.telnet() and tools.features.features.telnet else None,
			Switch(text=tools.lang.ftp   , name=b"ftp"   , checked=config.ftp,    disabled=disabled) if tools.features.features.ftp else None,
			Switch(text=tools.lang.http  , name=b"http"  , checked=config.http,   disabled=disabled) if tools.features.features.http else None,
			Switch(text=tools.lang.time_synchronization   , name=b"ntp"   , checked=config.ntp,    disabled=disabled) if tools.features.features.ntp else None,
			Switch(text=tools.lang.wan_ip   , name=b"wanip"   , checked=config.wanip,    disabled=disabled) if tools.features.features.wanip else None,
			Switch(text=tools.lang.notification_reboot_user, name=b"notify", checked=config.notify, disabled=disabled) if tools.features.features.pushover or tools.features.features.webhook or tools.features.features.mqtt_client else None,
			submit
		]))
	await response.send_page(page)
