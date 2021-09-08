# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to configure the awake """
from server.httpserver import HttpServer
from htmltemplate      import *
from webpage.mainpage  import mainFrame, manageDefaultButton
from tools             import AwakeConfig,lang

@HttpServer.addRoute(b'/wakeup', menu=lang.menu_system, item=lang.item_wakeup)
async def wakeup(request, response, args):
	""" Wake uo configuration web page """
	config = AwakeConfig()
	disabled, action, submit = manageDefaultButton(request, config)

	page = mainFrame(request, response, args, lang.gpio_wake_up, 
		Switch(text=lang.activated,       name=b"activated",     checked=config.activated, disabled=disabled),Br(),
		Edit(text=lang.gpio_used_wake_up, name=b"wakeUpGpio",     placeholder=lang.gpio_connected_to_pir, pattern=b"[0-9]*[0-9]", value=b"%d"%config.wakeUpGpio,    disabled=disabled),
		Edit(text=lang.awake_duration_in, name=b"awakeDuration",  placeholder=lang.duration_awake,        pattern=b"[0-9]*[0-9]", value=b"%d"%config.awakeDuration, disabled=disabled),
		Edit(text=lang.sleep_duration_in, name=b"sleepDuration",  placeholder=lang.duration_sleep,        pattern=b"[0-9]*[0-9]", value=b"%d"%config.sleepDuration, disabled=disabled), 
		Br(),
		submit)
	await response.sendPage(page)
