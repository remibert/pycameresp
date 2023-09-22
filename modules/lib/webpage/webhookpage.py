# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" Function define the web page to configure the webhook to interact with domoticz or other """
import server.httpserver
import server.httprequest
import server.webhook
from htmltemplate       import *
import webpage.mainpage
import tools.lang
import tools.info
import tools.features

@server.httpserver.HttpServer.add_route(b'/webhook', menu=tools.lang.menu_server, item=tools.lang.item_webhook, available=tools.features.features.webhook)
async def webhook(request, response, args):
	""" Function define the web page to configure the webhook  """
	config = server.webhook.WebhookConfig()
	disabled, action, submit = webpage.mainpage.manage_default_button(request, config)
	page = webpage.mainpage.main_frame(request, response, args,tools.lang.webhook_configuration,
		Form([
			Switch(text=tools.lang.activated, name=b"activated", checked=config.activated, disabled=disabled),
			Edit(text=tools.lang.webhook_inhabited_house,   name=b"inhabited_house",   placeholder=tools.lang.url_http_required, value=server.httprequest.HttpRequest.to_html(config.inhabited_house),    disabled=disabled),
			Edit(text=tools.lang.webhook_empty_house,       name=b"empty_house",       placeholder=tools.lang.url_http_required, value=config.empty_house,        disabled=disabled),
			Edit(text=tools.lang.webhook_motion_detected,   name=b"motion_detected",   placeholder=tools.lang.url_http_required, value=config.motion_detected,    disabled=disabled) if tools.info.iscamera() else None,
			Edit(text=tools.lang.webhook_no_motion_detected,name=b"no_motion_detected",placeholder=tools.lang.url_http_required, value=config.no_motion_detected, disabled=disabled) if tools.info.iscamera() else None,
			submit,
		]))
	await response.send_page(page)
