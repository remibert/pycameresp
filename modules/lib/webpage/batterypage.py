# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to configure the battery level detection """
from server.httpserver import HttpServer
from htmltemplate      import *
from webpage.mainpage  import mainFrame, manageDefaultButton
from tools             import BatteryConfig,lang

@HttpServer.addRoute(b'/battery', menu=lang.menu_system, item=lang.item_battery)
async def battery(request, response, args):
	""" Battery configuration web page """
	config = BatteryConfig()
	disabled, action, submit = manageDefaultButton(request, config)

	page = mainFrame(request, response, args, lang.battery_management, 
		Switch(text=lang.activated,          name=b"activated", checked=config.activated, disabled=disabled),Br(),
		Edit(text=lang.gpio_used_battery,    name=b"levelGpio",            placeholder=lang.gpio_connected_to_battery,    pattern=b"[0-9]*[0-9]", value=b"%d"%config.levelGpio,    disabled=disabled),
		Edit(text=lang.gpio_value_for_full,  name=b"fullBattery",          placeholder=lang.gpio_adc_value_full,          pattern=b"[0-9]*[0-9]", value=b"%d"%config.fullBattery,  disabled=disabled),
		Edit(text=lang.gpio_value_for_empty, name=b"emptyBattery",         placeholder=lang.gpio_adc_value_empty,         pattern=b"[0-9]*[0-9]", value=b"%d"%config.emptyBattery, disabled=disabled),
		Br(),
		Switch(text=lang.force_a_deep,       name=b"brownoutDetection", checked=config.brownoutDetection, disabled=disabled), 
		Br(),
		submit)
	await response.sendPage(page)