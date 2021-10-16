# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to configure the presence detection """
# pylint:disable=consider-using-enumerate
from server.httpserver import HttpServer
from server.dnsclient  import resolve_hostname, is_ip_address
from server.presence   import PresenceConfig
from htmltemplate      import *
from webpage.mainpage  import main_frame, manage_default_button
import wifi
from tools import useful,lang

@HttpServer.add_route(b'/presence', menu=lang.menu_server, item=lang.item_presence)
async def presence(request, response, args):
	""" Presence configuration page """
	config = PresenceConfig()
	def update_config(request, config):
		resolve = False
		if b"resolve" in request.params:
			if request.params[b"resolve"] != b"0":
				resolve = True

		if resolve:
			ip_address, netmask, gateway, dns = wifi.Station.get_info()
			if dns != "":
				for i in range(len(config.smartphones)):
					smartphone = config.smartphones[i]
					try:
						if is_ip_address(useful.tostrings(smartphone)):
							hostname = resolve_hostname(dns, useful.tostrings(smartphone))
							if hostname is not None:
								config.smartphones[i] = useful.tobytes(hostname)
					except:
							pass

	disabled, action, submit = manage_default_button(request, config, update_config)
	if action == b'modify':
		submit = Switch(text=lang.convert_ip_address, name=b"resolve", checked=False, disabled=disabled),submit

	editSmartphones = []
	i = 0
	for smartphone in config.smartphones:
		editSmartphones.append(Edit(text=lang.smartphone_d%(i+1),         name=b"smartphones[%d]"%i,
								placeholder=lang.enter_ip_address_or_dns,
								value=useful.tobytes(config.smartphones[i]),  disabled=disabled))
		i += 1

	page = main_frame(request, response, args,lang.presence_detection_configuration,
		Switch(text=lang.activated, name=b"activated", checked=config.activated, disabled=disabled),Br(),
		editSmartphones,
		Switch(text=lang.notification, name=b"notify", checked=config.notify, disabled=disabled),Br(),
		submit)

	await response.send_page(page)
