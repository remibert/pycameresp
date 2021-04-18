# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to configure the battery level detection """
from server.httpserver import HttpServer
from htmltemplate import *
from webpage import *
from tools import BatteryConfig

@HttpServer.addRoute(b'/battery', title=b"Battery", index=19)
async def battery(request, response, args):
	""" Battery configuration web page """
	config = BatteryConfig()
	if config.load() == False:
		config.save()
	action = request.params.get(b"modify",b"none")
	if   action == b"none"  : disabled = True
	elif action == b"modify": disabled = False 
	elif action == b"save"  : 
		disabled = True
		del request.params[b"modify"]
		config.update(request.params)
		config.save()

	if disabled:
		submit = Submit(text=b"Modify")
		value = b'modify'
	else:
		submit = AlertWarning(text=b"On battery servers and motion detection disabled"), Submit(text=b"Save")
		value = b'save'

	page = mainFrame(request, response, args, b"Battery management", 
		Switch(text=b"Activated",              name=b"activated", checked=config.activated, disabled=disabled),
		Edit(text=b"Battery level GPIO",       name=b"levelGpio",            placeholder=b"GPIO connect to battery level",                   pattern=b"[0-9]*[0-9]", value=b"%d"%config.levelGpio,    disabled=disabled),
		Edit(text=b"Battery 100% GPIO value",  name=b"fullBattery",          placeholder=b"GPIO ADC value for battery full (4.2V)",          pattern=b"[0-9]*[0-9]", value=b"%d"%config.fullBattery,  disabled=disabled),
		Edit(text=b"Battery 0% GPIO value",    name=b"emptyBattery",         placeholder=b"GPIO ADC value for battery empty (3.6V)",         pattern=b"[0-9]*[0-9]", value=b"%d"%config.emptyBattery, disabled=disabled),
		Edit(text=b"Wakeup GPIO",              name=b"wakeUpGpio",           placeholder=b"GPIO connected to passive infrared sensor (PIR)", pattern=b"[0-9]*[0-9]", value=b"%d"%config.wakeUpGpio,   disabled=disabled),
		Input (text=b"modify" ,                name=b"modify", type=b"hidden", value=value),
		submit)

	await response.sendPage(page)
