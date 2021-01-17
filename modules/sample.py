# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
from server.httpserver import HttpServer
from htmltemplate import *
from webpage     import *

# Test simple page with button 
# @HttpServer.addRoute(b'/sample', title=b"Sample", index=1000)
async def samplePage(request, response, args):
	page = mainPage(
		content=\
			[
				Container(
					[
						Title2(text=b'''Sample widgets command'''),
						Br(),
						ButtonCmd(text=b"Click me",  path=b"sample", name=b"myButtom"),
						Br(),
						SliderCmd(min=b"10", max=b"30", step=b"2", value=b"12", text=b"Change slider value", path=b"sample", name=b"mySlider"),
						ComboCmd(\
							[
								Option(value=b"Un"   , text=b"Un"),
								Option(value=b"Deux" , text=b"Deux", selected=True),
								Option(value=b"Trois", text=b"Trois"),
							], path=b"sample", name=b"myCombo", text=b"My combo"),
						SwitchCmd(text=b"My switch", checked=True, path=b"sample", name=b"mySwitch")
						#Paragraph(b'''This page can be easily removed by deleting the <b>sample.py</b> file''')
					])
			], title=args["title"], active=args["index"], request=request, response=response)
	await response.sendPage(page)

# Called when the button pressed
@HttpServer.addRoute(b'/sample/myButtom')
async def buttonPressed(request, response, args):
	print("Button clicked")
	await response.sendOk()

# Called when the slider state changed
@HttpServer.addRoute(b'/sample/mySlider')
async def sliderChanged(request, response, args):
	print("slider changed %s"%request.params[b"value"])
	await response.sendOk()

# Called when the combo state changed
@HttpServer.addRoute(b'/sample/myCombo')
async def comboChanged(request, response, args):
	print("combo changed %s"%request.params[b"value"])
	await response.sendOk()

# Called when the switch state changed
@HttpServer.addRoute(b'/sample/mySwitch')
async def comboChanged(request, response, args):
	print("switch changed %s"%request.params[b"value"])
	await response.sendOk()



