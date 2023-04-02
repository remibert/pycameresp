# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to configure the mqtt broker """
from server.httpserver  import HttpServer
from server.mqttclient     import *
from htmltemplate       import *
from webpage.mainpage   import main_frame, manage_default_button
from tools              import lang

@HttpServer.add_route(b'/mqtt', menu=lang.menu_server, item=lang.item_mqtt)
async def mqttpage(request, response, args):
	""" Function define the web page to configure the mqtt """
	config = MqttConfig()
	disabled, action, submit = manage_default_button(request, config)
	page = main_frame(request, response, args,lang.mqtt_configuration,
		Form([
			Switch(text=lang.activated,    name=b"activated", checked=config.activated, disabled=disabled),
			Edit(text=lang.mqtt_host,      name=b"host",     value=config.host, disabled=disabled),
			Edit(text=lang.mqtt_port,      name=b"port",     value=b"%d"%config.port, type=b"number", step=b"1", required=True, min=b"1024",  max=b"65536", disabled=disabled),
			Edit(text=lang.mqtt_username,  name=b"username", value=config.username, disabled=disabled),
			Edit(text=lang.mqtt_username,  name=b"password", value=config.password, type=b"password", disabled=disabled),
			submit,
		]))
	await response.send_page(page)
