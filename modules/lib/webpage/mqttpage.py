# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" Function define the web page to configure the mqtt broker """
import server.httpserver
import server.mqttclient
from htmltemplate       import *
import webpage.mainpage
import tools.lang

@server.httpserver.HttpServer.add_route(b'/mqtt', menu=tools.lang.menu_server, item=tools.lang.item_mqtt)
async def mqttpage(request, response, args):
	""" Function define the web page to configure the mqtt """
	config = server.mqttclient.MqttConfig()
	disabled, action, submit = webpage.mainpage.manage_default_button(request, config)
	page = webpage.mainpage.main_frame(request, response, args,tools.lang.mqtt_configuration,
		Form([
			Switch(text=tools.lang.activated,    name=b"activated", checked=config.activated, disabled=disabled),
			Edit(text=tools.lang.mqtt_host,      name=b"host",     value=config.host, disabled=disabled),
			Edit(text=tools.lang.mqtt_port,      name=b"port",     value=b"%d"%config.port, type=b"number", step=b"1", required=True, min=b"1024",  max=b"65536", disabled=disabled),
			Edit(text=tools.lang.mqtt_username,  name=b"username", value=config.username, disabled=disabled),
			Edit(text=tools.lang.mqtt_username,  name=b"password", value=config.password, type=b"password", disabled=disabled),
			submit,
		]))
	await response.send_page(page)
