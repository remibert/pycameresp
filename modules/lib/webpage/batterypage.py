# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to configure the battery level detection """
from server.httpserver import HttpServer
from htmltemplate import *
from webpage import *
from tools import BatteryConfig

@HttpServer.addRoute(b'/battery', title=b"Battery", index=200)
async def battery(request, response, args):
	""" Battery configuration web page """
	config = BatteryConfig()
	disabled, action, submit = manageDefaultButton(request, config)

	page = mainFrame(request, response, args, b"Battery management", 
		Card(
			[
				CardHeader(text=b"GPIO wake up"),
				CardBody([
					Switch(text=b"Activated",              name=b"wakeUp", checked=config.wakeUp, disabled=disabled),Br(),
					Edit(text=b"GPIO used to wake up",      name=b"wakeUpGpio", placeholder=b"GPIO connected to passive infrared sensor (PIR)", pattern=b"[0-9]*[0-9]", value=b"%d"%config.wakeUpGpio,   disabled=disabled),
					Edit(text=b"Awake duration in seconds",  name=b"awakeDuration",  placeholder=b"Duration in seconds it stays awake", pattern=b"[0-9]*[0-9]", value=b"%d"%config.awakeDuration, disabled=disabled),
					Edit(text=b"Sleep duration in seconds",  name=b"sleepDuration",  placeholder=b"Duration in seconds to sleep", pattern=b"[0-9]*[0-9]", value=b"%d"%config.sleepDuration, disabled=disabled),
				])
			]),Br(),
		Card(
			[
				CardHeader(text=b"Battery monitoring"),
				CardBody([
					Switch(text=b"Activated",              name=b"monitoring", checked=config.monitoring, disabled=disabled),Br(),
					Edit(text=b"GPIO used to get battery level",       name=b"levelGpio",            placeholder=b"GPIO connect to battery level",                   pattern=b"[0-9]*[0-9]", value=b"%d"%config.levelGpio,    disabled=disabled),
					Edit(text=b"GPIO value for 100%",  name=b"fullBattery",          placeholder=b"GPIO ADC value for battery full (4.2V)",          pattern=b"[0-9]*[0-9]", value=b"%d"%config.fullBattery,  disabled=disabled),
					Edit(text=b"GPIO value for 0%",    name=b"emptyBattery",         placeholder=b"GPIO ADC value for battery empty (3.6V)",         pattern=b"[0-9]*[0-9]", value=b"%d"%config.emptyBattery, disabled=disabled),
					Br(),
					Switch(text=b"Force a deep sleep if several resets due to a power failure",              name=b"brownoutDetection", checked=config.brownoutDetection, disabled=disabled),
				])
			]),Br(),
		submit)
	await response.sendPage(page)
