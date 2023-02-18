# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to configure the webhook to interact with domoticz or other """
from server.httpserver  import HttpServer
from server.httprequest import HttpRequest
from server.webhook     import *
from htmltemplate       import *
from webpage.mainpage   import main_frame, manage_default_button
from tools              import lang
from tools.info         import iscamera

@HttpServer.add_route(b'/webhook', menu=lang.menu_server, item=lang.item_webhook)
async def webhook(request, response, args):
	""" Function define the web page to configure the webhook  """
	config = WebhookConfig()
	disabled, action, submit = manage_default_button(request, config)
	page = main_frame(request, response, args,lang.webhook_configuration,
		Form([
			Switch(text=lang.activated, name=b"activated", checked=config.activated, disabled=disabled),
			Edit(text=lang.webhook_inhabited_house,   name=b"inhabited_house",   placeholder=lang.url_http_required, value=HttpRequest.to_html(config.inhabited_house),    disabled=disabled),
			Edit(text=lang.webhook_empty_house,       name=b"empty_house",       placeholder=lang.url_http_required, value=config.empty_house,        disabled=disabled),
			Edit(text=lang.webhook_motion_detected,   name=b"motion_detected",   placeholder=lang.url_http_required, value=config.motion_detected,    disabled=disabled) if iscamera() else None,
			Edit(text=lang.webhook_no_motion_detected,name=b"no_motion_detected",placeholder=lang.url_http_required, value=config.no_motion_detected, disabled=disabled) if iscamera() else None,
			submit,
		]))
	await response.send_page(page)
