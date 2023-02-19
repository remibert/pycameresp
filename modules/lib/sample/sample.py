# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Web page sample """
from server.httpserver import HttpServer
from htmltemplate import Br,ButtonCmd,Option,SwitchCmd,Tag,SliderCmd,ComboCmd,Paragraph
from webpage.mainpage     import *
from tools       import strings

@HttpServer.add_route(b'/sample/button')
async def button_pressed(request, response, args):
	""" Called when the button pressed """
	print("Button clicked")
	await response.send_ok()

@HttpServer.add_route(b'/sample/slider')
async def slider_changed(request, response, args):
	""" Called when the slider state changed """
	# pylint:disable=consider-using-f-string
	print("Slider change to %d"%int(request.params[b"value"]))
	await response.send_ok()

@HttpServer.add_route(b'/sample/combo')
async def combo_changed(request, response, args):
	""" Called when the combo state changed """
	# pylint:disable=consider-using-f-string
	print("Number %s selected"%strings.tostrings(request.params[b"value"]))
	await response.send_ok()

@HttpServer.add_route(b'/sample/switch')
async def switch_changed(request, response, args):
	""" Called when the switch state changed """
	# pylint:disable=consider-using-f-string
	print("Switch change to %s"%strings.tostrings(request.params[b"value"]))
	await response.send_ok()

@HttpServer.add_route(b'/sample', menu=b"Sample", item=b"Sample")
async def sample_page(request, response, args):
	""" Test simple page with differents web widgets """
	page = main_frame(request, response, args, b"Sample",
		Form([
			Tag(b'''
			<p>Example to interact with esp32 via an html page (see the content of file <b>sample.py</b>)</p>
			'''),
			ButtonCmd(text=b"Click on button",  path=b"/sample/button"),
			SliderCmd(min=b"10", max=b"30", step=b"2", value=b"12", text=b"Move slider", path=b"/sample/slider"),
			ComboCmd(\
				[
					Option(value=b"One"   , text=b"One"),
					Option(value=b"Two"   , text=b"Two", selected=True),
					Option(value=b"Three" , text=b"Three"),
				], path=b"/sample/combo", text=b"Select number"),
			SwitchCmd(text=b"Change this switch", checked=True, path=b"/sample/switch"),
			Br(),
			Paragraph(b"To eliminate this page delete the <b>sample.py</b> file")
		]))
	await response.send_page(page)
