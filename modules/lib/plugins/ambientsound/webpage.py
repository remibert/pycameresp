# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" Function define the web page to ambient sound """
# pylint:disable=anomalous-unicode-escape-in-string
# pylint:disable=wrong-import-order
import server.httpserver
from htmltemplate import *
import webpage.mainpage
import plugins.ambientsound.config
import plugins.ambientsound.lang

@server.httpserver.HttpServer.add_route(b'/ambient_sound', menu=plugins.ambientsound.lang.menu_ambientsound, item=plugins.ambientsound.lang.item_time_slots)
async def ambient_sound_page(request, response, args):
	""" Ambient sound configuration page """
	config  = plugins.ambientsound.config.AmbientSoundConfig().get_config()
	time_slot = plugins.ambientsound.config.AmbientTimeConfig()

	# If a new time_slot must be added
	if request.params.get(b"add",None) is not None:
		time_slot.update(request.params, show_error=False)
		if time_slot.start_time < time_slot.end_time:
			config.append(time_slot)
			config.save()
	# If a time_slot must be deleted
	elif request.params.get(b"remove",None) is not None:
		config.remove(request.params.get(b"remove",b"none"))
		config.save()

	# List all time slots
	time_slots = []
	identifier = 0
	while True:
		time_slot_line = config.get(identifier)
		if time_slot_line is not None:
			time_slots.append(
				ListItem(
				[
					Link(text=b"%s - %s "%(
						tools.date.time_to_html(time_slot_line.start_time),
						tools.date.time_to_html(time_slot_line.end_time)),
						href=b"ambient_sound?edit=%d"%identifier),
					Link(text=plugins.ambientsound.lang.remove_button ,
						class_=b"btn position-absolute top-50 end-0 translate-middle-y",
						href=b"ambient_sound?remove=%d"%identifier,
						onclick=b"return window.confirm('%s')"%plugins.ambientsound.lang.remove_dialog)
				]))
		else:
			break
		identifier += 1

	# Build page
	page = webpage.mainpage.main_frame(request, response, args, plugins.ambientsound.lang.title_time_slots,
	[
		Form(
		[
			Edit (text=plugins.ambientsound.lang.field_start, name=b"start_time", type=b"time", required=True, value=tools.date.time_to_html(time_slot.start_time)),
			Edit (text=plugins.ambientsound.lang.field_end,   name=b"end_time",   type=b"time", required=True, value=tools.date.time_to_html(time_slot.end_time)),
			Submit(text=plugins.ambientsound.lang.add_button, name=b"add")
		]),
		List(time_slots)
	])
	await response.send_page(page)
