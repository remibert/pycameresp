# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" Function define the web page to sourdough bread """
# pylint:disable=anomalous-unicode-escape-in-string
# pylint:disable=wrong-import-order
import server.httpserver
from htmltemplate import *
import webpage.mainpage
import plugins.sourdoughbread.lang

@server.httpserver.HttpServer.add_route(b'/painlevain', menu=plugins.sourdoughbread.lang.menu_sourdoughbread, item=plugins.sourdoughbread.lang.title_sourdoughbread)
async def sourdough_bread_page(request, response, args):
	""" Sourdough bread compute page """
	flour    = int(request.params.setdefault(b"flour", b"711"))
	leaven   = int(request.params.setdefault(b"leaven",b"250"))
	seed     = int(request.params.setdefault(b"seed",  b"210"))
	humidity = int(request.params.setdefault(b"humidity",b"54"))
	quantity = int(request.params.setdefault(b"quantity",b"4"))

	dry_matter_weight = flour + (leaven // 2) + seed
	humidity_weight   = (dry_matter_weight * humidity // 100)
	water             = humidity_weight - (leaven // 2)
	weight            = dry_matter_weight + humidity_weight
	percent_leaven    = int((leaven/flour) * 100)

	page = webpage.mainpage.main_frame(request, response, args, plugins.sourdoughbread.lang.title_sourdoughbread,
	[
		Form(
		[
			Edit (text=plugins.sourdoughbread.lang.flour,       name=b"flour",  value=b"%d"%flour,  pattern=b"[0-9]*[0-9]", type=b"number"),
			Edit (text=plugins.sourdoughbread.lang.seed,        name=b"seed",   value=b"%d"%seed,   pattern=b"[0-9]*[0-9]", type=b"number"),
			Edit (text=plugins.sourdoughbread.lang.leaven,      name=b"leaven", value=b"%d"%leaven, pattern=b"[0-9]*[0-9]", type=b"number"),
			Slider(text=plugins.sourdoughbread.lang.humidity,   name=b"humidity",        min=b"40", max=b"70", step=b"1",  value=b"%d"%humidity),
			Slider(text=plugins.sourdoughbread.lang.quantity,   name=b"quantity",        min=b"1",  max=b"20", step=b"1",  value=b"%d"%quantity),
			Submit(text=plugins.sourdoughbread.lang.compute,    name=b"compute"),
			Br(),Br(),
			Label(text=b"%s = %d"%(plugins.sourdoughbread.lang.water, water)),
			Br(),
			Label(text=b"%s = %d"%(plugins.sourdoughbread.lang.bread_weight, weight//quantity)),
			Br(),
			Label(text=b"%s = %d"%(plugins.sourdoughbread.lang.weight, weight)),
			Br(),
			Label(text=b"%s = %d&#37;"%(plugins.sourdoughbread.lang.percent_leaven, percent_leaven))
		]),
	])
	await response.send_page(page)
