# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to show an exemple of command button """
from server.httpserver import HttpServer
from htmltemplate import *
from webpage     import *

@HttpServer.addRoute(b'/command', title=b"Command", index=16)
async def command(request, response, args):
	""" Function define the web page to show an exemple of command button """
	page = mainPage(
		content=[Container([\
					Br(),
					Command(text=b"Led on",  path=b"oncommand", id=b"on" , class_=b"btn-success"),
					Br(),
					Br(),
					Command(text=b"Led off", path=b"oncommand", id=b"off", class_=b"btn-warning"),
				])
			], title=args["title"], active=args["index"], request=request, response=response)
	await response.sendPage(page)

@HttpServer.addRoute(b'/oncommand/on')
async def ledOn(request, response, args):
	""" Command switch on the led """
	print("led on")
	await response.sendOk()

@HttpServer.addRoute(b'/oncommand/off')
async def ledOff(request, response, args):
	""" Command switch off the led """
	print("led off")
	await response.sendOk()

