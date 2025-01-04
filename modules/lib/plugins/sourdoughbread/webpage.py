# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" Function define the web page to sourdough bread """
# pylint:disable=anomalous-unicode-escape-in-string
# pylint:disable=wrong-import-order
import server.httpserver
import tools.jsonconfig
from htmltemplate import *
import webpage.mainpage
import plugins.sourdoughbread.lang

class SourdoughBreadConfig(tools.jsonconfig.JsonConfig):
	""" Sourdough bread configuration """
	def __init__(self):
		""" Constructor """
		tools.jsonconfig.JsonConfig.__init__(self)
		self.flour    = 1000
		self.leaven   = 250
		self.seed     = 320
		self.humidity = 75
		self.quantity = 4

@server.httpserver.HttpServer.add_route(b'/painlevain', menu=plugins.sourdoughbread.lang.menu_sourdoughbread, item=plugins.sourdoughbread.lang.title_sourdoughbread)
async def sourdough_bread_page(request, response, args):
	""" Sourdough bread compute page """
	config = SourdoughBreadConfig()

	if request.params.setdefault(b"reset",None) is not None:
		config.save()

	if request.params.setdefault(b"compute",None) is None:
		if config.load() is False:
			config.save()
	else:
		config.update(request.params, False)
		config.save()

	dry_matter_weight = config.flour + (config.leaven // 2)
	humidity_weight   = (dry_matter_weight * config.humidity // 100)
	water             = humidity_weight - (config.leaven // 2)
	weight            = dry_matter_weight + humidity_weight + config.seed
	try:
		percent_leaven = int((config.leaven/config.flour) * 100)
	except:
		percent_leaven = 0

	page = webpage.mainpage.main_frame(request, response, args, plugins.sourdoughbread.lang.title_sourdoughbread,
	[
		Form(
		[
			Edit  (text=plugins.sourdoughbread.lang.flour,      name=b"flour",  value=b"%d"%config.flour,  pattern=b"[0-9+\-*/\s]+", type=b"text"),
			Edit  (text=plugins.sourdoughbread.lang.seed,       name=b"seed",   value=b"%d"%config.seed,   pattern=b"[0-9+\-*/\s]+", type=b"text"),
			Edit  (text=plugins.sourdoughbread.lang.leaven,     name=b"leaven", value=b"%d"%config.leaven, pattern=b"[0-9+\-*/\s]+", type=b"text"),
			Slider(text=plugins.sourdoughbread.lang.humidity,   name=b"humidity",        min=b"40", max=b"80", step=b"1",  value=b"%d"%config.humidity),
			Slider(text=plugins.sourdoughbread.lang.quantity,   name=b"quantity",        min=b"1",  max=b"20", step=b"1",  value=b"%d"%config.quantity),
			Submit(text=plugins.sourdoughbread.lang.compute,    name=b"compute"), b"&nbsp;",
			Submit(text=plugins.sourdoughbread.lang.reset,      name=b"reset"),
			Br(),Br(),
			Label(text=b"%s = %d"%(plugins.sourdoughbread.lang.water, water)),
			Br(),
			Label(text=b"%s = %d"%(plugins.sourdoughbread.lang.bread_weight, weight//config.quantity)),
			Br(),
			Label(text=b"%s = %d"%(plugins.sourdoughbread.lang.weight, weight)),
			Br(),
			Label(text=b"%s = %d&#37;"%(plugins.sourdoughbread.lang.percent_leaven, percent_leaven))
		]),
	])
	await response.send_page(page)
