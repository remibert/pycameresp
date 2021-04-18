# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
from server.httpserver import HttpServer
from htmltemplate import *
from webpage     import *
from tools       import useful

# Test simple page with button 
@HttpServer.addRoute(b'/sample', title=b"Sample", index=1000)
async def samplePage(request, response, args):
	page = mainFrame(request, response, args, b'''Widgets sample command''',
		ButtonCmd(text=b"Click on button",  path=b"/sample/button"), Br(),Br(),
		SliderCmd(min=b"10", max=b"30", step=b"2", value=b"12", text=b"Move slider", path=b"/sample/slider"), Br(),
		ComboCmd(\
			[
				Option(value=b"One"   , text=b"One"),
				Option(value=b"Two"   , text=b"Two", selected=True),
				Option(value=b"Three" , text=b"Three"),
			], path=b"/sample/combo", text=b"Select number"), Br(),Br(),
		SwitchCmd(text=b"Change this switch", checked=True, path=b"/sample/switch"))
	await response.sendPage(page)

# Called when the button pressed
@HttpServer.addRoute(b'/sample/button')
async def buttonPressed(request, response, args):
	print("Button clicked")
	await response.sendOk()

# Called when the slider state changed
@HttpServer.addRoute(b'/sample/slider')
async def sliderChanged(request, response, args):
	print("Slider change to %d"%int(request.params[b"value"]))
	await response.sendOk()

# Called when the combo state changed
@HttpServer.addRoute(b'/sample/combo')
async def comboChanged(request, response, args):
	print("Number %s selected"%useful.tostrings(request.params[b"value"]))
	await response.sendOk()

# Called when the switch state changed
@HttpServer.addRoute(b'/sample/switch')
async def comboChanged(request, response, args):
	print("Switch change to %s"%useful.tostrings(request.params[b"value"]))
	await response.sendOk()



