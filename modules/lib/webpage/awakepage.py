# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to configure the awake """
from server.httpserver import HttpServer
from htmltemplate      import *
from webpage.mainpage  import main_frame, manage_default_button
from tools             import AwakeConfig,lang

@HttpServer.add_route(b'/wakeup', menu=lang.menu_system, item=lang.item_wakeup)
async def wakeup(request, response, args):
	""" Wake uo configuration web page """
	config = AwakeConfig()
	disabled, action, submit = manage_default_button(request, config)

	page = main_frame(request, response, args, lang.gpio_wake_up,
		Switch(text=lang.activated,       name=b"activated",     checked=config.activated, disabled=disabled),Br(),
		Edit(text=lang.gpio_used_wake_up, name=b"wake_up_gpio",     placeholder=lang.gpio_connected_to_pir, pattern=b"[0-9]*[0-9]", value=b"%d"%config.wake_up_gpio,    disabled=disabled),
		Edit(text=lang.awake_duration_in, name=b"awake_duration",  placeholder=lang.duration_awake,        pattern=b"[0-9]*[0-9]", value=b"%d"%config.awake_duration, disabled=disabled),
		Edit(text=lang.sleep_duration_in, name=b"sleep_duration",  placeholder=lang.duration_sleep,        pattern=b"[0-9]*[0-9]", value=b"%d"%config.sleep_duration, disabled=disabled),
		Br(),
		submit)
	await response.send_page(page)
