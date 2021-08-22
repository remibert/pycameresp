# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to configure the battery level detection """
from server.httpserver import HttpServer
from htmltemplate import *
from webpage.mainpage import *
from tools import BatteryConfig
from tools import lang

@HttpServer.addRoute(b'/battery', title=lang.battery, index=200)
async def battery(request, response, args):
	""" Battery configuration web page """
	config = BatteryConfig()
	disabled, action, submit = manageDefaultButton(request, config)

	page = mainFrame(request, response, args, lang.battery_management, 
		Card(
			[
				CardHeader(text=lang.gpio_wake_up),
				CardBody([
					Switch(text=lang.activated,              name=b"wakeUp", checked=config.wakeUp, disabled=disabled),Br(),
					Edit(text=lang.gpio_used_to,      name=b"wakeUpGpio", placeholder=lang.gpio_connected_to, pattern=b"[0-9]*[0-9]", value=b"%d"%config.wakeUpGpio,   disabled=disabled),
					Edit(text=lang.awake_duration_in,  name=b"awakeDuration",  placeholder=lang.duration_in_seconds, pattern=b"[0-9]*[0-9]", value=b"%d"%config.awakeDuration, disabled=disabled),
					Edit(text=lang.sleep_duration_in,  name=b"sleepDuration",  placeholder=lang.duration_in_seconds_1, pattern=b"[0-9]*[0-9]", value=b"%d"%config.sleepDuration, disabled=disabled),
				])
			]),Br(),
		Card(
			[
				CardHeader(text=lang.battery_monitoring),
				CardBody([
					Switch(text=lang.activated,              name=b"monitoring", checked=config.monitoring, disabled=disabled),Br(),
					Edit(text=lang.gpio_used_to_2,       name=b"levelGpio",            placeholder=lang.gpio_connect_to,                   pattern=b"[0-9]*[0-9]", value=b"%d"%config.levelGpio,    disabled=disabled),
					Edit(text=lang.gpio_value_for,  name=b"fullBattery",          placeholder=lang.gpio_adc_value,          pattern=b"[0-9]*[0-9]", value=b"%d"%config.fullBattery,  disabled=disabled),
					Edit(text=lang.gpio_value_for_3,    name=b"emptyBattery",         placeholder=lang.gpio_adc_value_4,         pattern=b"[0-9]*[0-9]", value=b"%d"%config.emptyBattery, disabled=disabled),
					Br(),
					Switch(text=lang.force_a_deep,              name=b"brownoutDetection", checked=config.brownoutDetection, disabled=disabled),
				])
			]),Br(),
		submit)
	await response.sendPage(page)
