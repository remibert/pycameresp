# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" Function define the web page to display all informations of the board """
import server.httpserver
from htmltemplate      import *
import webpage.mainpage
import wifi.station
import tools.info
import tools.lang
import tools.builddate
import tools.date

@server.httpserver.HttpServer.add_route(b'/', menu=tools.lang.menu_system, item=tools.lang.item_information)
async def index(request, response, args):
	""" Function define the web page to display all informations of the board """
	page = webpage.mainpage.main_frame(request, response, args, tools.lang.device_informations,
		Form([
			Edit(text=tools.lang.date,             value=tools.date.date_to_bytes(),             disabled=True),
			Edit(text=tools.lang.build_date,       value=tools.builddate.date,                      disabled=True),
			Edit(text=tools.lang.uptime,           value=tools.info.uptime(tools.lang.days),              disabled=True),
			Edit(text=tools.lang.device_label,     value=tools.info.deviceinfo(),                   disabled=True),
			Edit(text=tools.lang.memory_label,     value=tools.info.meminfo(),                      disabled=True),
			Edit(text=tools.lang.flash_label,      value=tools.info.flashinfo(),                    disabled=True),
			Edit(text=tools.lang.signal_strength,  value=wifi.station.Station.get_signal_strength_bytes(), disabled=True),
		]))
	await response.send_page(page)
