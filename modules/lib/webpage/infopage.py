# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to display all informations of the board """
from server.httpserver import HttpServer
from htmltemplate import *
from webpage.mainpage import *
from tools import useful
import sys
import gc
import machine
import esp
from tools import lang


@HttpServer.addRoute(b'/', title=lang.information, index=10)
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
		memAlloc = b"Unvailable"
		memFree  = b"Unvailable"
		memTotal = b"Unvailable"
	try:
		flashUser = useful.sizeToBytes(esp.flash_user_start())
		flashSize = useful.sizeToBytes(esp.flash_size())
	except:
		flashUser = b"Unavailable"
		flashSize = b"Unavailable"

	try:
		frequency = b"%d"%(machine.freq()//1000000)
	except:
		frequency = b"Unvailable"

	try:
		platform = useful.tobytes(sys.platform)
	except:
		platform = b"Unavailable"
  
	try:
		uptime = useful.tobytes(useful.uptime())
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
