# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" Function define the web page to configure the awake """
import server.httpserver
from htmltemplate      import *
import webpage.mainpage
import tools.awake
import tools.lang
import tools.features

@server.httpserver.HttpServer.add_route(b'/wakeup', menu=tools.lang.menu_system, item=tools.lang.item_wakeup, available=tools.features.features.awake)
async def wakeup(request, response, args):
	""" Wake uo configuration web page """
	config = tools.awake.AwakeConfig()
	disabled, action, submit = webpage.mainpage.manage_default_button(request, config)

	page = webpage.mainpage.main_frame(request, response, args, tools.lang.gpio_wake_up,
		Form([
			Switch(text=tools.lang.activated,       name=b"activated",     checked=config.activated, disabled=disabled),
			Edit(text=tools.lang.gpio_used_wake_up, name=b"wake_up_gpio",     placeholder=tools.lang.gpio_connected_to_pir, pattern=b"[0-9]*[0-9]", value=b"%d"%config.wake_up_gpio,    disabled=disabled),
			Edit(text=tools.lang.awake_duration_in, name=b"awake_duration",  placeholder=tools.lang.duration_awake,        pattern=b"[0-9]*[0-9]", value=b"%d"%config.awake_duration, disabled=disabled),
			Edit(text=tools.lang.sleep_duration_in, name=b"sleep_duration",  placeholder=tools.lang.duration_sleep,        pattern=b"[0-9]*[0-9]", value=b"%d"%config.sleep_duration, disabled=disabled),
			submit
		]))
	await response.send_page(page)
