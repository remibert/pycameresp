# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Web page sample """
from server.httpserver import HttpServer
from htmltemplate import Br,ButtonCmd,Option,SwitchCmd,Tag,SliderCmd,ComboCmd,Paragraph
from webpage.mainpage     import *
from tools       import useful

@HttpServer.add_route(b'/sample/button')
async def button_pressed(request, response, args):
	""" Called when the button pressed """
	print("Button clicked")
	await response.send_ok()

@HttpServer.add_route(b'/sample/slider')
async def slider_changed(request, response, args):
	""" Called when the slider state changed """
	print("Slider change to %d"%int(request.params[b"value"]))
	await response.send_ok()

@HttpServer.add_route(b'/sample/combo')
async def combo_changed(request, response, args):
	""" Called when the combo state changed """
	print("Number %s selected"%useful.tostrings(request.params[b"value"]))
	await response.send_ok()

@HttpServer.add_route(b'/sample/switch')
async def switch_changed(request, response, args):
	""" Called when the switch state changed """
	print("Switch change to %s"%useful.tostrings(request.params[b"value"]))
	await response.send_ok()

@HttpServer.add_route(b'/sample', menu=b"Sample", item=b"Sample")
async def sample_page(request, response, args):
	""" Test simple page with differents web widgets """
	page = main_frame(request, response, args, b"Sample",
		Tag(b'''
			<p>Example to interact with esp32 via an html page (see the content of file <b>sample.py</b>)</p>
			'''),
			ButtonCmd(text=b"Click on button",  path=b"/sample/button"), Br(),Br(),
			SliderCmd(min=b"10", max=b"30", step=b"2", value=b"12", text=b"Move slider", path=b"/sample/slider"), Br(),
			ComboCmd(\
				[
					Option(value=b"One"   , text=b"One"),
					Option(value=b"Two"   , text=b"Two", selected=True),
					Option(value=b"Three" , text=b"Three"),
				], path=b"/sample/combo", text=b"Select number"), Br(),Br(),
			SwitchCmd(text=b"Change this switch", checked=True, path=b"/sample/switch"),
			Br(),
			Br(),
			Paragraph(b"To eliminate this page delete the <b>sample.py</b> file"))
	await response.send_page(page)
