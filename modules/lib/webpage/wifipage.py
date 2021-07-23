# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to configure the wifi """
from server.httpserver import HttpServer
from htmltemplate import *
from webpage import *
from tools.useful import *
from tools import useful, jsonconfig
import wifi


def staticIpHtml(config, disabled):
	""" Html to get static ip """
	patternIp = b"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
	return [
			Edit(text=b"Ip address",  name=b"ipaddress", pattern=patternIp, placeholder=b"Enter ip address", value=config.ipaddress, disabled=disabled),
			Edit(text=b"Netmask",     name=b"netmask",   pattern=patternIp, placeholder=b"Enter netmask",    value=config.netmask,   disabled=disabled),
			Edit(text=b"Gateway",     name=b"gateway",   pattern=patternIp, placeholder=b"Enter gateway",    value=config.gateway,   disabled=disabled),
			Edit(text=b"DNS",         name=b"dns",       pattern=patternIp, placeholder=b"Enter DNS",        value=config.dns,       disabled=disabled)]
	
currentNetworks = []
currentConfig  = None
currentNetwork = None

def selectNetwork(increase=0, reparse=False):
	global currentNetworks, currentNetwork
	if reparse:
		currentNetworks = currentNetwork.listKnown()
	current = 0
	for network in currentNetworks:
		searched = useful.tobytes(useful.tofilename(currentNetwork.ssid))
		if searched == network:
			break
		current += 1
	
	if current + increase < 0:
		current = -1
	elif current + increase >= len(currentNetworks):
		current = 0
	else:
		current += increase
	currentNetwork = wifi.NetworkConfig()
	try:
		try:
			partFilename = currentNetworks[current]
		except:
			partFilename = b""
		currentNetwork.load(partFilename = partFilename)
	except Exception as err:
		useful.exception(err)
	return currentNetwork

@HttpServer.addRoute(b'/wifi', title=b"Wifi", index=11)
async def wifiConfig(request, response, args):
	""" Page to configure the wifi station """
	global currentNetworks, currentConfig, currentNetwork
 
	if currentConfig == None:
		currentConfig = wifi.Station.config
		currentNetwork = wifi.Station.network
		currentNetworks = currentNetwork.listKnown()

	config  = currentConfig
	network = currentNetwork

	action  = request.params.get(b"action",b"none")
	forced  = request.params.get(b"forced",b"none")
	current = request.params.get(b"current",b"")
	dynamic = request.params.get(b"dynamic",b"1")

	disabled = False
	# If default page
	if action == b"none" and len(request.params) == 0:
		disabled = True
	# If the dynamic ip switch changed
	elif   action == b"none":
		if dynamic == b"1":
			forced = b"1"
		else:
			forced = b"0"
		action = b"change"
	# If the modify button clicked
	elif action == b"modify":
		pass
	# If the save button clicked
	elif action == b"save":
		network.update(request.params)
		network.save()
		network = selectNetwork(0, True)
		config.default = network.ssid
		config.save()
		forced  = b"none"
		disabled = True
	elif action == b"previous":
		network = selectNetwork(-1)
		forced = b"none"
	elif action == b"next":
		network = selectNetwork(1)
		forced = b"none"
	elif action == b"forget":
		forced = b"none"
		network.forget()
		network = selectNetwork(-1,True)
	elif action == b"default":
		config.default = useful.tostrings(network.ssid)
		config.save()
	if forced == b"none":
		dynamic = network.dynamic
	elif forced == b"1":
		dynamic = True
	else:
		dynamic = False
	
	ssids = []
	
	if action in [b"previous",b"next",b"change",b"forget",b"modify",b"default"]:
		submit = \
			Submit (text=b"Save"  ,     name=b"action",  value=b"save"    , style=b"margin-right:0.5em"), \
			Submit (text=b"&lt;-" ,     name=b"action",  value=b"previous", style=b"margin-right:0.5em"), \
			Submit (text=b"-&gt;" ,     name=b"action",  value=b"next"    , style=b"margin-right:0.5em"), \
			Submit (text=b"Forget",     name=b"action",  value=b"forget"  , style=b"margin-right:0.5em"), \
			Submit (text=b"Set Default",name=b"action",  value=b"default"  , style=b"margin-right:0.5em"), \
			Input  (                    name=b"forced",  value=forced     , type=b"hidden"), \
			Input  (                    name=b"current", value=current    , type=b"hidden")

		if wifi.Station.isActive():
			networks = wifi.Station.scan()
			for net in networks:
				ssids.append(Option(value=net[0]))
	else:
		submit = Submit(text=b"Modify", name=b"action", value=b"modify")

	page = mainFrame(request, response, args, b"Wifi configuration",
		Switch(text=b"Activated", name=b"activated", checked=config.activated, disabled=disabled),Br(),
		Card(
			[
				CardHeader(text= b"Wifi" if useful.tostrings(network.ssid) != useful.tostrings(config.default) else b"Wifi (default)"),
				CardBody([
					ComboBox(ssids, text=b"SSID", placeholder=b"Enter SSID",  name=b"ssid", value=network.ssid, disabled=disabled),
					Edit(text=b"Password",    name=b"wifipassword", placeholder=b"Enter password",      type=b"password",value=network.wifipassword, disabled=disabled),
				])
			]),Br(),
		Card(
			[
				CardHeader([\
					Switch(text=b"Dynamic IP", checked=dynamic, name=b"dynamic", onchange=b"this.form.submit()", disabled=disabled)]),
				CardBody([\
					Edit(text=b"DHCP Hostname" ,   name=b"hostname",  placeholder=b"Hostname not available with static IP",        value=network.hostname,       disabled=disabled) 
					if dynamic else staticIpHtml(network, disabled)])
			]),
		Br(),
		submit)
	await response.sendPage(page)

@HttpServer.addRoute(b'/accesspoint', title=b"Access point", index=12)
async def accessPoint(request, response, args):
	""" Page to configure the access point """
	config = wifi.AccessPointConfig()
	disabled, action, submit = manageDefaultButton(request, config)
	if action == b"save":
		if wifi.AccessPoint.isActive():
			wifi.AccessPoint.config = config
	authmodes = []
	for key, value in wifi.AUTHMODE.items():
		if value==config.authmode:
			authmodes.append(Option(text=value, selected=b"selected", value=value))
		else:
			authmodes.append(Option(text=value, value=value))
	page = mainFrame(request, response, args, b"Access point configuration" if accessPoint else b"Wifi configuration",
		Switch(text=b"Activated", name=b"activated", checked=config.activated, disabled=disabled),Br(),
		Card(
			[
				CardHeader(text=b"Wifi"),
				CardBody([
					Edit(text=b"SSID", placeholder=b"Enter SSID", name=b"ssid", value=config.ssid, disabled=disabled),
					Edit(text=b"Password",    name=b"wifipassword",type=b"password", placeholder=b"Enter password",      value=config.wifipassword, disabled=disabled),
					Select( authmodes,text=b"Authentication mode",name=b"authmode", disabled=disabled),
				]),
			]),Br(),
		Card(
			[
				CardHeader(text=b"Static IP"),
				CardBody(staticIpHtml(config, disabled))
			]),Br(),
		submit)
	await response.sendPage(page)

