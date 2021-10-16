# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to configure the battery level detection """
from server.httpserver import HttpServer
from htmltemplate      import *
from webpage.mainpage  import main_frame, manage_default_button
from tools             import BatteryConfig,lang

@HttpServer.add_route(b'/battery', menu=lang.menu_system, item=lang.item_battery)
async def battery(request, response, args):
	""" Battery configuration web page """
	config = BatteryConfig()
	disabled, action, submit = manage_default_button(request, config)

	page = main_frame(request, response, args, lang.battery_management,
		Switch(text=lang.activated,          name=b"activated", checked=config.activated, disabled=disabled),Br(),
		Edit(text=lang.gpio_used_battery,    name=b"level_gpio",            placeholder=lang.gpio_connected_to_battery,    pattern=b"[0-9]*[0-9]", value=b"%d"%config.level_gpio,    disabled=disabled),
		Edit(text=lang.gpio_value_for_full,  name=b"full_battery",          placeholder=lang.gpio_adc_value_full,          pattern=b"[0-9]*[0-9]", value=b"%d"%config.full_battery,  disabled=disabled),
		Edit(text=lang.gpio_value_for_empty, name=b"empty_battery",         placeholder=lang.gpio_adc_value_empty,         pattern=b"[0-9]*[0-9]", value=b"%d"%config.empty_battery, disabled=disabled),
		Br(),
		Switch(text=lang.force_a_deep,       name=b"brownout_detection", checked=config.brownout_detection, disabled=disabled),
		Br(),
		submit)
	await response.send_page(page)
