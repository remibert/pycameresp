# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to configure the wifi """
from server.httpserver import HttpServer
from htmltemplate import *
from webpage import *
from tools.useful import *
import wifi

def configureWifi(title=b"",config=None,accessPoint=False,disabled=False,active=0,request=None,response=None):
	""" Content of wifi page """
	if accessPoint:
		authmodes = []

		for key, value in wifi.AUTHMODE.items():
			if value==config.authmode:
				authmodes.append(Option(text=value, selected=b"selected", value=value))
			else:
				authmodes.append(Option(text=value, value=value))
		authentication = Select( authmodes,text=b"Authentication mode",name=b"authmode", disabled=disabled)
		ssid = Edit(text=b"SSID", placeholder=b"Enter SSID", name=b"ssid", value=config.ssid, disabled=disabled)
	else:
		authentication = None
		ssids = []
		if disabled == False:
			if wifi.Station.isActive():
				networks = wifi.Station.scan()
				for network in networks:
					ssids.append(Option(value=network[0]))
		ssid = ComboBox(ssids, text=b"SSID", placeholder=b"Enter SSID",  name=b"ssid", value=config.ssid, disabled=disabled)
	patternIp = b"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
	if disabled:
		submit = Submit(text=b"Modify")
		value = b'modify'
	else:
		submit = Submit(text=b"Save")
		value = b'save'
	page = mainPage(
		content=[Br(),Container([\
					Card([\
						Form([\
							Br(),
							Title3(text=b"Access point configuration" if accessPoint else b"Wifi configuration"),
							Br(),
							Switch(text=b"Activated", name=b"activated", checked=config.activated, disabled=disabled),
							ssid,
							Edit(text=b"Password",    name=b"wifipassword",type=b"password", placeholder=b"Enter password",      value=config.wifipassword, disabled=disabled),
							authentication,
							Edit(text=b"Ip address",  name=b"ipaddress", pattern=patternIp, placeholder=b"Enter ip address or leave blank", value=config.ipaddress, disabled=disabled),
							Edit(text=b"Netmask",     name=b"netmask",   pattern=patternIp, placeholder=b"Enter netmask or leave blank",    value=config.netmask,   disabled=disabled),
							Edit(text=b"Gateway",     name=b"gateway",   pattern=patternIp, placeholder=b"Enter gateway or leave blank",    value=config.gateway,   disabled=disabled),
							Edit(text=b"DNS",         name=b"dns",       pattern=patternIp, placeholder=b"Enter DNS or leave blank",        value=config.dns,       disabled=disabled),
							Input(text=b"modify",     name=b"modify",    type=b"hidden", value=value),
							submit,
						])
					])
				])
			], title=title, active=active, request=request, response=response)
	return page

@HttpServer.addRoute(b'/wifi', title=b"Wifi", index=11)
async def wifiConfig(request, response, args):
	""" Page to configure the wifi station """
	config = wifi.StationConfig()
	config.load()

	action = request.params.get(b"modify",b"none")
	if   action == b"none"  : disabled = True
	elif action == b"modify": disabled = False 
	elif action == b"save"  : 
		disabled = True
		del request.params[b"modify"]
		config.update(request.params)
		config.save()
		if wifi.Station:
			wifi.Station.config = config
	elif action == b"modify":
		disabled = False

	page = configureWifi(title=args["title"], config=config, accessPoint=False, disabled=disabled, active=args["index"], request=request, response=response)
	await response.sendPage(page)

@HttpServer.addRoute(b'/accesspoint', title=b"Access point", index=12)
async def accessPoint(request, response, args):
	""" Page to configure the access point """
	config = wifi.AccessPointConfig()
	config.load()

	action = request.params.get(b"modify",b"none")
	if   action == b"none"  : disabled = True
	elif action == b"modify": disabled = False 
	elif action == b"save"  : 
		disabled = True
		del request.params[b"modify"]
		config.update(request.params)
		config.save()
		if wifi.AccessPoint.isActive():
			wifi.AccessPointconfig = config

	page = configureWifi(title=args["title"], config=config, accessPoint=True, disabled=disabled, active=args["index"], request=request, response=response)
	await response.sendPage(page)

