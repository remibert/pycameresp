# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the date time and language """
import server.httpserver
from htmltemplate      import *
import webpage.mainpage
import tools.lang
import tools.region

@server.httpserver.HttpServer.add_route(b'/region', menu=tools.lang.menu_account, item=tools.lang.item_region)
async def region_page(request, response, args):
	""" Function define the web page to manage lang and time """
	config = tools.region.RegionConfig.get()
	disabled, action, submit = webpage.mainpage.manage_default_button(request, config)
	langages = []

	for langage in [b"english",b"french"]:
		if config.lang == langage:
			selected = b"selected"
		else:
			selected = b""
		langages.append(Option(text=langage, selected=selected, value=langage))

	if action == b"save":
		config.save()
		alert = AlertError(text=tools.lang.taken_into_account)
	else:
		alert = None

	page = webpage.mainpage.main_frame(request, response, args, tools.lang.region_configuration,
		Form([
			Edit  (text=tools.lang.utc_offset             , name=b"offset_time",pattern=b"-*[0-9]*[0-9]", placeholder=tools.lang.offset_time_to,        value=b"%d"%config.offset_time,       disabled=disabled),
			Switch(text=tools.lang.daylight_saving_time   , name=b"dst"       ,checked=config.dst,    disabled=disabled),
			Label(text=tools.lang.language),
			Select(langages,name=b"lang", disabled=disabled), submit, alert
		]))
	await response.send_page(page)
