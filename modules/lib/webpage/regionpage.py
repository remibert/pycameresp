# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the date time and language """
from server.httpserver import HttpServer
from htmltemplate      import *
from webpage.mainpage  import mainFrame, manageDefaultButton
from tools             import useful,lang

@HttpServer.addRoute(b'/region', title=lang.region, index=90)
async def regionPage(request, response, args):
	""" Function define the web page to manage lang and time """
	config = lang.RegionConfig()
	disabled, action, submit = manageDefaultButton(request, config)
	langages = []
	for langage in [b"english",b"french"]:
		if config.lang == langage:
			selected = b"selected"
		else:
			selected = b""
		langages.append(Option(text=langage, selected=selected, value=langage))

	page = mainFrame(request, response, args, lang.region_configuration,
		Edit  (text=lang.utc_offset             , name=b"offsettime",pattern=b"-*[0-9]*[0-9]", placeholder=lang.offset_time_to,        value=b"%d"%config.offsettime,       disabled=disabled),
		Switch(text=lang.daylight_saving_time   , name=b"dst"       ,checked=config.dst,    disabled=disabled),Br(),
		Select(langages,text=lang.language,name=b"lang", disabled=disabled), Br(), submit)
	await response.sendPage(page)

