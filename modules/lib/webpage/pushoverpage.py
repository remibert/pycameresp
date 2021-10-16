# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to configure the pushover notifications """
from server.httpserver import HttpServer
from server.pushover   import *
from htmltemplate      import *
from webpage.mainpage  import main_frame, manage_default_button
from tools             import lang

@HttpServer.add_route(b'/pushover', menu=lang.menu_server, item=lang.item_notification)
async def pushover(request, response, args):
	""" Function define the web page to configure the pushover notifications """
	config = PushOverConfig()
	disabled, action, submit = manage_default_button(request, config)
	if action == b"save":
		if config.activated:
			msg = lang.pushover_on
		else:
			msg = lang.pushover_off
		await async_notify(token=config.token, user=config.user, message = msg)
	if disabled:
		typ = b"password"
	else:
		typ = b""
	page = main_frame(request, response, args,lang.notification_configuration,
		Switch(text=lang.activated, name=b"activated", checked=config.activated, disabled=disabled),Br(),
		Edit(text=lang.pushover_user,  name=b"user",  placeholder=lang.enter_pushover_user,  type=typ, value=config.user,  disabled=disabled),
		Edit(text=lang.pushover_token, name=b"token", placeholder=lang.enter_pushover_token, type=typ, value=config.token, disabled=disabled),
		submit,
		Br(), Br(), Link(href=b"https://pushover.net", text=lang.see_pushover_website))

	await response.send_page(page)
