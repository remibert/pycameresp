# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to configure the presence detection """
from server.httpserver import HttpServer
from server.dnsclient import resolveHostname, isIpAddress
from server.presence import PresenceConfig
from htmltemplate import *
from webpage import *
import wifi
from tools import useful

@HttpServer.addRoute(b'/presence', title=b"Presence", index=60, available=useful.iscamera())
async def presence(request, response, args):
	""" Presence configuration page """
	config = PresenceConfig()
	def updateConfig(request, config):
		resolve = False
		if b"resolve" in request.params:
			if request.params[b"resolve"] != b"0":
				resolve = True

		if resolve:
			ipaddress, netmask, gateway, dns = wifi.Station.getInfo()
			if dns != "":
				for i in range(len(config.smartphones)):
					smartphone = config.smartphones[i]
					try:
						if isIpAddress(useful.tostrings(smartphone)):
							hostname = resolveHostname(dns, useful.tostrings(smartphone))
							if hostname != None:
								config.smartphones[i] = useful.tobytes(hostname)
					except:
							pass

	disabled, action, submit = manageDefaultButton(request, config, updateConfig)
	if action == b'modify':
		submit = Switch(text=b"Convert ip address into DNS name", name=b"resolve", checked=False, disabled=disabled),submit

	editSmartphones = []
	i = 0
	for smartphone in config.smartphones:
		editSmartphones.append(Edit(text=b"Smartphone %d"%(i+1),         name=b"smartphones[%d]"%i,  
								placeholder=b"Enter ip address or dns name",
								value=useful.tobytes(config.smartphones[i]),  disabled=disabled))
		i += 1

	page = mainFrame(request, response, args,b"Presence detection configuration",
		Switch(text=b"Activated", name=b"activated", checked=config.activated, disabled=disabled),Br(),
		editSmartphones,
		Switch(text=b"Notification", name=b"notify", checked=config.notify, disabled=disabled),Br(),
		submit)

	await response.sendPage(page)
