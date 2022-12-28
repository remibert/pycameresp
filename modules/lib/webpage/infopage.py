# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to display all informations of the board """
from server.httpserver import HttpServer
from htmltemplate      import *
from webpage.mainpage  import main_frame
from wifi.station      import Station
from tools             import info, lang, builddate, date

@HttpServer.add_route(b'/', menu=lang.menu_system, item=lang.item_information)
async def index(request, response, args):
	""" Function define the web page to display all informations of the board """
	page = main_frame(request, response, args, lang.device_informations,
		Form([
			Edit(text=lang.date,             value=date.date_to_bytes(),             disabled=True),
			Edit(text=lang.build_date,       value=builddate.date,                      disabled=True),
			Edit(text=lang.uptime,           value=info.uptime(lang.days),              disabled=True),
			Edit(text=lang.device_label,     value=info.deviceinfo(),                   disabled=True),
			Edit(text=lang.memory_label,     value=info.meminfo(),                      disabled=True),
			Edit(text=lang.flash_label,      value=info.flashinfo(),                    disabled=True),
			Edit(text=lang.signal_strength,  value=Station.get_signal_strength_bytes(), disabled=True),
		]))
	await response.send_page(page)
