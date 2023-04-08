# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to configure the pushover notifications """
import server.httpserver
import server.pushover
from htmltemplate      import *
import webpage.mainpage
import tools.lang

@server.httpserver.HttpServer.add_route(b'/pushover', menu=tools.lang.menu_server, item=tools.lang.item_notification)
async def pushover(request, response, args):
	""" Function define the web page to configure the pushover notifications """
	config = server.pushover.PushOverConfig()
	disabled, action, submit = webpage.mainpage.manage_default_button(request, config)
	if action == b"save":
		if config.activated:
			msg = tools.lang.pushover_on
		else:
			msg = tools.lang.pushover_off
		await server.pushover.async_notify(token=config.token, user=config.user, message = msg)
	if disabled:
		typ = b"password"
	else:
		typ = b""
	page = webpage.mainpage.main_frame(request, response, args,tools.lang.notification_configuration,
		Form([
			Switch(text=tools.lang.activated, name=b"activated", checked=config.activated, disabled=disabled),
			Edit(text=tools.lang.pushover_user,  name=b"user",  placeholder=tools.lang.enter_pushover_user,  type=typ, value=config.user,  disabled=disabled),
			Edit(text=tools.lang.pushover_token, name=b"token", placeholder=tools.lang.enter_pushover_token, type=typ, value=config.token, disabled=disabled),
			submit,
			Br(), Link(href=b"https://pushover.net", text=tools.lang.see_pushover_website)
		]))

	await response.send_page(page)
