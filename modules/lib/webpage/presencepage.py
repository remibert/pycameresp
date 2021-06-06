# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to configure the presence detection """
from server.httpserver import HttpServer
from server.dnsclient import getHostname, isIpAddress
from htmltemplate import *
from webpage import *
from motion import PresenceConfig
import wifi
from tools import useful

@HttpServer.addRoute(b'/presence', title=b"Presence", index=18, available=useful.iscamera())
async def presence(request, response, args):
	""" Presence configuration page """
	config = PresenceConfig()
	def updateConfig(request, config):
		if b"resolve" in request.params:
			resolve = True
		else:
			resolve = False

		if resolve:
			ipaddress, netmask, gateway, dns = wifi.Station.getInfo()
			if dns != "":
				for i in range(len(config.smartphones)):
					smartphone = config.smartphones[i]
					try:
						if isIpAddress(useful.tostrings(smartphone)):
							hostname = getHostname(dns, useful.tostrings(smartphone))
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
