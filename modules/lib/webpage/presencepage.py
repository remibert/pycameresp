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
	config.load()
	action = request.params.get(b"modify",b"none")
	if   action == b"none"  : disabled = True
	elif action == b"modify": disabled = False 
	elif action == b"save"  : 
		disabled = True
		del request.params[b"modify"]
		if b"resolve" in request.params:
			del request.params[b"resolve"]
			resolve = True
		else:
			resolve = False
		config.update(request.params)

		if resolve:
			wifiConfig = wifi.StationConfig()
			wifiConfig.load()
			if wifiConfig.dns != b"":
				for i in range(len(config.smartphones)):
					smartphone = config.smartphones[i]
					try:
						if isIpAddress(useful.tostrings(smartphone)):
							hostname = getHostname(useful.tostrings(wifiConfig.dns), useful.tostrings(smartphone))
							if hostname != None:
								config.smartphones[i] = useful.tobytes(hostname)
					except:
							pass
		config.save()

	if disabled:
		submit = Submit(text=b"Modify")
		value = b'modify'
	else:
		submit = Switch(text=b"Convert ip address into DNS name", name=b"resolve", checked=False, disabled=disabled),Submit(text=b"Save")
		value = b'save'

	editSmartphones = []
	i = 0
	for smartphone in config.smartphones:
		editSmartphones.append(Edit(text=b"Smartphone %d"%(i+1),         name=b"smartphones[%d]"%i,  
								placeholder=b"Enter ip address or dns name",
								value=useful.tobytes(config.smartphones[i]),  disabled=disabled))
		i += 1

	page = mainPage(
		content=[Br(),Container([\
					Card([\
						Form([\
							Br(),
							Title3(text=b"Presence detection configuration"),
							Br(),
							Switch(text=b"Activated", name=b"activated", checked=config.activated, disabled=disabled),
							editSmartphones,
							Input (text=b"modify" , name=b"modify", type=b"hidden", value=value),
							submit,
						]),
					])
				])
			], title=args["title"], active=args["index"], request=request, response=response)

	await response.sendPage(page)
