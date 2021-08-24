# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to display all informations of the board """
import sys
import gc
import machine
import esp
from server.httpserver import HttpServer
from htmltemplate      import *
from webpage.mainpage  import mainFrame
from tools             import useful, lang


@HttpServer.addRoute(b'/', title=lang.information, index=20)
async def index(request, response, args):
	""" Function define the web page to display all informations of the board """
	try:
		# pylint: disable=no-member
		allocated = gc.mem_alloc()
		freed     = gc.mem_free()
		memAlloc = useful.sizeToBytes(allocated)
		memFree  = useful.sizeToBytes(freed)
		memTotal = useful.sizeToBytes(allocated + freed)
	except:
		memAlloc = lang.unavailable
		memFree  = lang.unavailable
		memTotal = lang.unavailable
	try:
		flashUser = useful.sizeToBytes(esp.flash_user_start())
		flashSize = useful.sizeToBytes(esp.flash_size())
	except:
		flashUser = lang.unavailable
		flashSize = lang.unavailable

	try:
		frequency = b"%d"%(machine.freq()//1000000)
	except:
		frequency = lang.unavailable

	try:
		platform = useful.tobytes(sys.platform)
	except:
		platform = lang.unavailable
  
	try:
		uptime = useful.tobytes(useful.uptime(lang.days))
	except:
		uptime = b""

	date = useful.dateToBytes()

	page = mainFrame(request, response, args, lang.device_informations,
		Edit(text=lang.date,             value=date,      disabled=True),
		Edit(text=lang.uptime,           value=uptime,    disabled=True),
		Edit(text=lang.platform,         value=platform,  disabled=True),
		Edit(text=lang.frequency,        value=frequency, disabled=True),
		Edit(text=lang.memory_free,      value=memFree,   disabled=True),
		Edit(text=lang.memory_allocated, value=memAlloc,  disabled=True),
		Edit(text=lang.memory_total,     value=memTotal,  disabled=True),
		Edit(text=lang.flash_user,       value=flashUser, disabled=True),
		Edit(text=lang.flash_size,       value=flashSize, disabled=True))

	await response.sendPage(page)
