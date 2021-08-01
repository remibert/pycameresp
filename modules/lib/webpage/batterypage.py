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

	if action == b'save' or action == b'modify':
		submit = AlertWarning(text=b"On battery servers and motion detection disabled"),submit

	page = mainFrame(request, response, args, b"Battery management", 
		Card(
			[
				CardHeader(text=b"GPIO wake up"),
				CardBody([
					Switch(text=b"Activated",              name=b"activated", checked=config.activated, disabled=disabled),Br(),
					Edit(text=b"GPIO used to wake up",              name=b"wakeUpGpio",           placeholder=b"GPIO connected to passive infrared sensor (PIR)", pattern=b"[0-9]*[0-9]", value=b"%d"%config.wakeUpGpio,   disabled=disabled),
					Edit(text=b"Awake duration in second",                                name=b"awakeTime",            placeholder=b"Time in seconds it stays awake when on battery power", pattern=b"[0-9]*[0-9]", value=b"%d"%config.awakeTime, disabled=disabled),
				])
			]),Br(),
		Card(
			[
				CardHeader(text=b"Battery monitoring"),
				CardBody([
					Switch(text=b"Activated",              name=b"activated", checked=config.activated, disabled=disabled),Br(),
					Edit(text=b"GPIO used to get battery level",       name=b"levelGpio",            placeholder=b"GPIO connect to battery level",                   pattern=b"[0-9]*[0-9]", value=b"%d"%config.levelGpio,    disabled=disabled),
					Edit(text=b"GPIO value for 100%",  name=b"fullBattery",          placeholder=b"GPIO ADC value for battery full (4.2V)",          pattern=b"[0-9]*[0-9]", value=b"%d"%config.fullBattery,  disabled=disabled),
					Edit(text=b"GPIO value for 0%",    name=b"emptyBattery",         placeholder=b"GPIO ADC value for battery empty (3.6V)",         pattern=b"[0-9]*[0-9]", value=b"%d"%config.emptyBattery, disabled=disabled),
				])
			]),Br(),
		Card([
				CardHeader(text=b"Miscellaneous"),
				CardBody([
					Switch(text=b"Force deep sleep if to many successive brown out reset detected",              name=b"activated", checked=config.activated, disabled=disabled),Br(),
					Switch(text=b"Not start servers to save battery",              name=b"activated", checked=config.activated, disabled=disabled),Br(),
				])
			]),Br(),
		submit)
	await response.sendPage(page)
