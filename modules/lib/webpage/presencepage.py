# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" Function define the web page to configure the presence detection """
# pylint:disable=consider-using-enumerate
import server.httpserver
import server.dnsclient
import server.presence
from htmltemplate      import *
import webpage.mainpage
import wifi.wifi
import tools.lang
import tools.strings
import tools.features

@server.httpserver.HttpServer.add_route(b'/presence', menu=tools.lang.menu_server, item=tools.lang.item_presence, available=tools.features.features.presence)
async def presence(request, response, args):
	""" Presence configuration page """
	config = server.presence.PresenceConfig()
	def update_config(request, config):
		resolve = False
		if b"resolve" in request.params:
			if request.params[b"resolve"] != b"0":
				resolve = True

		if resolve:
			ip_address, netmask, gateway, dns = wifi.station.Station.get_info()
			if dns != "":
				for i in range(len(config.smartphones)):
					smartphone = config.smartphones[i]
					try:
						if server.dnsclient.is_ip_address(tools.strings.tostrings(smartphone)):
							hostname = server.dnsclient.resolve_hostname(dns, tools.strings.tostrings(smartphone))
							if hostname is not None:
								config.smartphones[i] = tools.strings.tobytes(hostname)
					except:
							pass

	disabled, action, submit = webpage.mainpage.manage_default_button(request, config, update_config)
	if action == b'modify':
		submit = Switch(text=tools.lang.convert_ip_address, name=b"resolve", checked=False, disabled=disabled),submit

	editSmartphones = []
	i = 0
	for smartphone in config.smartphones:
		editSmartphones.append(Edit(text=tools.lang.smartphone_d%(i+1),         name=b"smartphones[%d]"%i,
								placeholder=tools.lang.enter_ip_address_or_dns,
								value=tools.strings.tobytes(config.smartphones[i]),  disabled=disabled))
		i += 1

	page = webpage.mainpage.main_frame(request, response, args,tools.lang.presence_detection_configuration,
		Form([
			Switch(text=tools.lang.activated, name=b"activated", checked=config.activated, disabled=disabled),
			editSmartphones,
			Switch(text=tools.lang.notification, name=b"notify", checked=config.notify, disabled=disabled),
			submit
		]))

	await response.send_page(page)
