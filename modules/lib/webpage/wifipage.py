# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to configure the wifi """
from server.httpserver        import HttpServer
from htmltemplate.htmlclasses import *
from webpage.mainpage         import mainFrame, manageDefaultButton
from tools.useful             import *
from tools                    import useful,lang
import wifi

def staticIpHtml(config, disabled):
	""" Html to get static ip """
	patternIp = br"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
	return [
			Edit(text=lang.ip_address,  name=b"ipaddress", pattern=patternIp, placeholder=lang.enter_ip_address, value=config.ipaddress, disabled=disabled),
			Edit(text=lang.netmask,     name=b"netmask",   pattern=patternIp, placeholder=lang.enter_netmask,    value=config.netmask,   disabled=disabled),
			Edit(text=lang.gateway,     name=b"gateway",   pattern=patternIp, placeholder=lang.enter_gateway,    value=config.gateway,   disabled=disabled),
			Edit(text=lang.dns,         name=b"dns",       pattern=patternIp, placeholder=lang.enter_dns,        value=config.dns,       disabled=disabled)]
	
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
		useful.syslog(err)
	return currentNetwork

@HttpServer.addRoute(b'/wifi', menu=lang.menu_network, item=lang.item_wifi)
async def wifiConfig(request, response, args):
	""" Page to configure the wifi station """
	global currentNetworks, currentConfig, currentNetwork

	patternDns = rb"^([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])(\.([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]))*$"

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
		config.update(request.params)
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
			Submit (text=lang.save  ,     name=b"action",  value=b"save"    , style=b"margin-right:0.5em"), \
			Submit (text=lang.lt ,        name=b"action",  value=b"previous", style=b"margin-right:0.5em"), \
			Submit (text=lang.gt ,        name=b"action",  value=b"next"    , style=b"margin-right:0.5em"), \
			Submit (text=lang.forget,     name=b"action",  value=b"forget"  , style=b"margin-right:0.5em"), \
			Submit (text=lang.set_default,name=b"action",  value=b"default" , style=b"margin-right:0.5em"), \
			Input  (                      name=b"forced",  value=forced     , type=b"hidden"), \
			Input  (                      name=b"current", value=current    , type=b"hidden")

		if wifi.Station.isActive():
			networks = wifi.Station.scan()
			for net in networks:
				ssids.append(Option(value=net[0]))
	else:
		submit = Submit(text=lang.modify, name=b"action", value=b"modify")

	page = mainFrame(request, response, args, lang.wifi_configuration,
		Switch(text=lang.activated, name=b"activated", checked=config.activated, disabled=disabled),Br(),
		Edit(text=lang.hostname ,   name=b"hostname",  placeholder=lang.hostname_not_available, pattern=patternDns, value=config.hostname, disabled=disabled), 
		Switch(text=lang.fallback_to_the, name=b"fallback", checked=config.fallback, disabled=disabled),Br(),
		Card(
			[
				CardHeader(text= lang.wifi if useful.tostrings(network.ssid) != useful.tostrings(config.default) else lang.wifi_default),
				CardBody([
					ComboBox(ssids, text=lang.ssid, placeholder=lang.enter_ssid,  name=b"ssid", value=network.ssid, disabled=disabled),
					Edit(text=lang.password,    name=b"wifipassword", placeholder=lang.enter_password,      type=b"password",value=network.wifipassword, disabled=disabled),
				])
			]),Br(),
		Card(
			[
				CardHeader([\
					Switch(text=lang.dynamic_ip, checked=dynamic, name=b"dynamic", onchange=b"this.form.submit()", disabled=disabled)]),
				CardBody([\
					None if dynamic else staticIpHtml(network, disabled)])
			]),
		Br(),
		submit)
	await response.sendPage(page)

@HttpServer.addRoute(b'/accesspoint', menu=lang.menu_network, item=lang.item_access_point)
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
	# pylint: disable=missing-parentheses-for-call-in-test
	# pylint: disable=using-constant-test
	page = mainFrame(request, response, args, lang.access_point_configuration if accessPoint else b"Wifi configuration",
		Switch(text=lang.activated, name=b"activated", checked=config.activated, disabled=disabled),Br(),
		Card(
			[
				CardHeader(text=lang.wifi),
				CardBody([
					Edit(text=lang.ssid, placeholder=lang.enter_ssid, name=b"ssid", value=config.ssid, disabled=disabled),
					Edit(text=lang.password,    name=b"wifipassword",type=b"password", placeholder=lang.enter_password,      value=config.wifipassword, disabled=disabled),
					Select(authmodes,text=lang.authentication_mode,name=b"authmode", disabled=disabled),
				]),
			]),Br(),
		Card(
			[
				CardHeader(text=lang.static_ip),
				CardBody(staticIpHtml(config, disabled))
			]),Br(),
		submit)
	await response.sendPage(page)

