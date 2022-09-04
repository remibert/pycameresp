# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to display all informations of the board """
import sys
import gc
import machine
from server.httpserver import HttpServer
from htmltemplate      import *
from webpage.mainpage  import main_frame
from wifi.station      import Station
from tools             import info, lang, builddate, strings

@HttpServer.add_route(b'/', menu=lang.menu_system, item=lang.item_information)
async def index(request, response, args):
	""" Function define the web page to display all informations of the board """
	try:
		# pylint: disable=no-member
		allocated = gc.mem_alloc()
		freed     = gc.mem_free()
		mem_alloc = strings.size_to_bytes(allocated)
		mem_free  = strings.size_to_bytes(freed)
		mem_total = strings.size_to_bytes(allocated + freed)
	except:
		mem_alloc = lang.unavailable
		mem_free  = lang.unavailable
		mem_total = lang.unavailable
	try:
		_, flash_allocated, flash_free = info.flash_size()
		flash_allocated = strings.size_to_bytes(flash_allocated)
		flash_free      = strings.size_to_bytes(flash_free)
	except:
		flash_allocated = lang.unavailable
		flash_free      = lang.unavailable

	try:
		frequency = b"%d"%(machine.freq()//1000000)
	except:
		frequency = lang.unavailable

	try:
		platform = strings.tobytes(sys.platform)
	except:
		platform = lang.unavailable

	signal_strength = Station.get_signal_strength_bytes()

	try:
		uptime = strings.tobytes(info.uptime(lang.days))
	except:
		uptime = b""

	date = strings.date_to_bytes()

	page = main_frame(request, response, args, lang.device_informations,
		Edit(text=lang.date,             value=date,            disabled=True),
		Edit(text=lang.build_date,       value=builddate.date,  disabled=True),
		Edit(text=lang.uptime,           value=uptime,          disabled=True),
		Edit(text=lang.platform,         value=platform,        disabled=True),
		Edit(text=lang.frequency,        value=frequency,       disabled=True),
		Edit(text=lang.memory_free,      value=mem_free,        disabled=True),
		Edit(text=lang.memory_allocated, value=mem_alloc,       disabled=True),
		Edit(text=lang.memory_total,     value=mem_total,       disabled=True),
		Edit(text=lang.flash_free,       value=flash_free,      disabled=True),
		Edit(text=lang.flash_allocated,  value=flash_allocated, disabled=True),
		Edit(text=lang.signal_strength,  value=signal_strength, disabled=True),
		)

	await response.send_page(page)
