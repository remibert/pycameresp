# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to display all informations of the board """
from server.httpserver import HttpServer
from htmltemplate import *
from webpage import *
from tools import useful
from tools.useful import log
import sys
import gc

try:
	import machine
	import esp
except:
	pass

@HttpServer.addRoute(b'/', title=b"Information", index=10)
async def index(request, response, args):
	""" Function define the web page to display all informations of the board """
	try:
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

	date = useful.dateToBytes()

	page = mainPage(
		content=[Br(),Container([\
					Card([\
						Form([\
							Br(),
							Title3(text=b"Device informations"),
							Br(),
							Edit(text=b"Date",             value=date,      disabled=True),
							Edit(text=b"Platform",         value=platform,  disabled=True),
							Edit(text=b"Frequency",        value=frequency, disabled=True),
							Edit(text=b"Memory free",      value=memFree,   disabled=True),
							Edit(text=b"Memory allocated", value=memAlloc,  disabled=True),
							Edit(text=b"Memory total",     value=memTotal,  disabled=True),
							Edit(text=b"Flash user",       value=flashUser, disabled=True),
							Edit(text=b"Flash size",       value=flashSize, disabled=True),
						])
					])
				])
			], title=args["title"], active=args["index"], request=request, response=response)

	await response.sendPage(page)
