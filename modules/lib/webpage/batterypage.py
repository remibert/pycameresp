# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" Function define the web page to configure the battery level detection """
import server.httpserver
from htmltemplate      import *
import webpage.mainpage
import tools.battery
import tools.lang

@server.httpserver.HttpServer.add_route(b'/battery', menu=tools.lang.menu_system, item=tools.lang.item_battery)
async def battery(request, response, args):
	""" Battery configuration web page """
	config = tools.battery.BatteryConfig()
	disabled, action, submit = webpage.mainpage.manage_default_button(request, config)

	page = webpage.mainpage.main_frame(request, response, args, tools.lang.battery_management,
		Form([
			Switch(text=tools.lang.activated,          name=b"activated", checked=config.activated, disabled=disabled),
			Edit(text=tools.lang.gpio_used_battery,    name=b"level_gpio",            placeholder=tools.lang.gpio_connected_to_battery,    pattern=b"[0-9]*[0-9]", value=b"%d"%config.level_gpio,    disabled=disabled),
			Edit(text=tools.lang.gpio_value_for_full,  name=b"full_battery",          placeholder=tools.lang.gpio_adc_value_full,          pattern=b"[0-9]*[0-9]", value=b"%d"%config.full_battery,  disabled=disabled),
			Edit(text=tools.lang.gpio_value_for_empty, name=b"empty_battery",         placeholder=tools.lang.gpio_adc_value_empty,         pattern=b"[0-9]*[0-9]", value=b"%d"%config.empty_battery, disabled=disabled),
			Switch(text=tools.lang.force_a_deep,       name=b"brownout_detection", checked=config.brownout_detection, disabled=disabled),
			submit
		]))
	await response.send_page(page)
