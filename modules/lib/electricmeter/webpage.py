# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to view recent motion detection """
# pylint:disable=anomalous-unicode-escape-in-string
# pylint:disable=wrong-import-order
# import time
# import uos
import json
from server.httpserver      import HttpServer
from htmltemplate           import *
from webpage.mainpage       import main_frame, manage_default_button
from tools                  import date, strings, lang
from electricmeter.config   import RateConfig, TimeSlotConfig, RatesConfig, TimeSlotsConfig, GeolocationConfig
from electricmeter          import electricmeter, em_lang


@HttpServer.add_route(b'/hourly', menu=em_lang.menu_electricmeter, item=em_lang.item_hour)
async def hourly_page_page(request, response, args):
	""" Daily consumption graph hour by hour """
	geolocation = GeolocationConfig.get_config()
	day  = date.html_to_date(request.params.get(b"day",b""))

	if   request.params.get(b"direction",b"") == b"next":
		day += 86400
	elif request.params.get(b"direction",b"") == b"previous":
		day -= 86400

	step = int(request.params.get(b"step",b"30"))
	steps = []
	for s in [1,2,5,10,15,30]:
		if s == step:
			selected = True
		else:
			selected = False
		steps.append(Option(text=b"%d %s"%(s, em_lang.step_minutes), value=b"%d"%s, selected=selected))

	unit = request.params.get(b"unit",b"power")

	with  open(WWW_DIR + "electricmeter.html", "rb") as file:
		content = file.read()

	page_content = [\
		Div(
			[
				Div([
					Button(type=b"submit", text=b"&lt;-", name=b"direction",  value=b"previous"),Space(),
					Input (type=b"date",   class_=b"form-label", name=b"day", value= date.date_to_html(day), event=b'onchange="this.form.submit()"'),Space(),
					Button(type=b"submit", text=b"-&gt;", name=b"direction",  value=b"next")],
					class_=b'col-md-4'),
				Div(
					[Select(steps, spacer=b"", text=em_lang.step_minutes, name=b"step",                 event=b'onchange="this.form.submit()"')],
					class_=b'col-md-4'),
				Div(
					[Select(
						[
							Option(text=em_lang.type_price, value=b"price", selected= True if unit == b"price" else False),
							Option(text=em_lang.type_power, value=b"power", selected= True if unit == b"power" else False),
						], spacer=b"", text=em_lang.step_minutes, name=b"unit",                 event=b'onchange="this.form.submit()"')],
					class_=b'col-md-4')
			],
			class_=b"row"),

		Tag(content%(b"hourly",
			step,
			date.date_to_html(day),
			lang.translate_date(day),
			unit,
			em_lang.power_consumed,
			geolocation.latitude,
			geolocation.longitude,
			b""))
	]
	page = main_frame(request, response, args,em_lang.title_electricmeter + em_lang.item_hour.lower(),Form(page_content))
	await response.send_page(page)


@HttpServer.add_route(b'/hourly_datas')
async def hourly_page_datas(request, response, args):
	""" Send pulses of hours and rates """
	day    = date.html_to_date(request.params.get(b"day",b""))
	result = {"pulses":None}
	result["rates"] = strings.tostrings(TimeSlotsConfig.get_cost(day))
	try:
		result["pulses"] = electricmeter.HourlyCounter.get_datas(day)
		await response.send_buffer(b"pulses", buffer=strings.tobytes(json.dumps(result)), mime_type=b"application/json")
	except Exception as err:
		await response.send_not_found(err)


@HttpServer.add_route(b'/power_datas')
async def power_page_datas(request, response, args):
	""" Send current power consumed """
	try:
		power = {"power":electricmeter.HourlyCounter.get_power()}
		await response.send_buffer(b"pulses", buffer=strings.tobytes(json.dumps(power)), mime_type=b"application/json")
	except Exception as err:
		await response.send_not_found(err)


@HttpServer.add_route(b'/daily', menu=em_lang.menu_electricmeter, item=em_lang.item_day)
async def daily_page(request, response, args):
	""" Consumption graph day by day """
	geolocation = GeolocationConfig.get_config()
	y,m = date.local_time()[:2]
	year   = int(request.params.get(b"year",b"%d"%y))
	month  = int(request.params.get(b"month",b"%d"%m))
	day  = date.html_to_date(b"%04d-%02d-01"%(year, month))
	unit = request.params.get(b"unit",b"power")
	temperature = request.params.get(b"temperature")
	if temperature is None or temperature == b"0":
		with_temperature = b"false"
		temperature = None
	else:
		with_temperature = b"true"

	months_combo = []
	month_id = 1
	for m in lang.months:
		months_combo.append(Option(text=m, value=b"%d"%month_id, selected= True if month_id == month else False))
		month_id += 1

	with  open(WWW_DIR + "electricmeter.html", "rb") as file:
		content = file.read()

	page_content = [\
		Div(
			[
				Div([
					Edit (name=b"year", spacer=b"", type=b"number", step=b"1",  required=True, value=b"%d"%year, event=b'onchange="this.form.submit()"'),
					],
					class_=b'col-md-3'),
				Div([
					Select(months_combo, spacer=b"", name=b"month", event=b'onchange="this.form.submit()"')],
					class_=b'col-md-3 mb-2'),
				Div(
					[Select(
						[
							Option(text=em_lang.type_price, value=b"price", selected= True if unit == b"price" else False),
							Option(text=em_lang.type_power, value=b"power", selected= True if unit == b"power" else False),
						], spacer=b"", text=em_lang.step_minutes, name=b"unit",                 event=b'onchange="this.form.submit()"')],
					class_=b'col-md-3'),
				Div(
					Switch(text=em_lang.temperature, name=b"temperature", checked=temperature, event=b'onchange="this.form.submit()"'),
					class_=b'col-md-3')
			],
			class_=b"row"),

		Tag(content%(b"daily", 86400, date.date_to_html(day), lang.translate_date(day, False), unit, em_lang.power_consumed, geolocation.latitude, geolocation.longitude, with_temperature))
	]
	page = main_frame(request, response, args, em_lang.title_electricmeter + em_lang.item_day.lower(),Form(page_content))
	await response.send_page(page)


@HttpServer.add_route(b'/daily_datas')
async def daily_datas(request, response, args):
	""" Send pulses of month and rates """
	await electricmeter.MonthlyCounter.refresh()
	month    = date.html_to_date(request.params.get(b"month",b""))
	result = {"time_slots":None}
	result["rates"] = strings.tostrings(TimeSlotsConfig.get_cost(month))
	try:
		result["time_slots"] = electricmeter.DailyCounter.get_datas(month)
		await response.send_buffer(b"pulses", buffer=strings.tobytes(json.dumps(result)), mime_type=b"application/json")
	except Exception as err:
		await response.send_not_found(err)


@HttpServer.add_route(b'/monthly', menu=em_lang.menu_electricmeter, item=em_lang.item_month)
async def monthly_page(request, response, args):
	""" Consumption graph month by month """
	geolocation = GeolocationConfig.get_config()
	y = date.local_time()[0]
	year   = int(request.params.get(b"year",b"%d"%y))
	month  = date.html_to_date(b"%04d-01-01"%(year))
	unit = request.params.get(b"unit",b"power")

	with  open(WWW_DIR + "electricmeter.html", "rb") as file:
		content = file.read()

	page_content = [\
		Div(
			[
				Div([
					Edit (name=b"year", spacer=b"", type=b"number", step=b"1",  required=True, value=b"%d"%year, event=b'onchange="this.form.submit()"'),
					],
					class_=b'col-md-6'),
				Div(
					[Select(
						[
							Option(text=em_lang.type_price, value=b"price", selected= True if unit == b"price" else False),
							Option(text=em_lang.type_power, value=b"power", selected= True if unit == b"power" else False),
						], spacer=b"", text=em_lang.step_minutes, name=b"unit",                 event=b'onchange="this.form.submit()"')],
					class_=b'col-md-6')
			],
			class_=b"row"),

		Tag(content%(b"monthly", 86400, date.date_to_html(month), lang.translate_date(month, False), unit, em_lang.power_consumed, geolocation.latitude, geolocation.longitude, b""))
	]
	page = main_frame(request, response, args, em_lang.title_electricmeter + em_lang.item_month.lower(),Form(page_content))
	await response.send_page(page)


@HttpServer.add_route(b'/monthly_datas')
async def monthly_datas(request, response, args):
	""" Send pulses of month and rates """
	await electricmeter.MonthlyCounter.refresh()
	year   = date.html_to_date(request.params.get(b"year",b""))
	result = {"time_slots":None}
	result["rates"] = strings.tostrings(TimeSlotsConfig.get_cost(year))
	try:
		result["time_slots"] = electricmeter.MonthlyCounter.get_datas(year)
		await response.send_buffer(b"pulses", buffer=strings.tobytes(json.dumps(result)), mime_type=b"application/json")
	except Exception as err:
		await response.send_not_found(err)


@HttpServer.add_route(b'/rate', menu=em_lang.menu_electricmeter, item=em_lang.item_rate)
async def rate_page(request, response, args):
	""" Electric rate configuration page """
	rates   = RatesConfig.get_config()
	current = RateConfig()
	# If new rate added
	if request.params.get(b"add",None) is not None:
		current.update(request.params, show_error=False)
		rates.append(current)
		rates.save()
	# If a rate must be deleted
	elif request.params.get(b"remove",None) is not None:
		rates.remove(request.params.get(b"remove",b"none"))
		rates.save()
	# If a rate must be edited
	elif request.params.get(b"edit",None) is not None:
		current.update(rates.get(request.params.get(b"edit",b"none")))

	# List all rates
	rate_items = []
	identifier = 0
	while True:
		rate = rates.get(identifier)
		if rate is not None:
			rate_items.append(
					ListItem(
					[
						Link(text=b" %s : %f %s %s %s "%(rate[b"name"], rate[b"price"], rate[b"currency"], em_lang.from_the, lang.translate_date(rate[b"validity_date"])), href=b"rate?edit=%d"%identifier ),
						Link(text=em_lang.remove_button , class_=b"btn position-absolute top-50 end-0 translate-middle-y", href=b"rate?remove=%d"%identifier, onclick=b"return window.confirm('%s')"%em_lang.remove_dialog)
					]))
		else:
			break
		identifier += 1

	# Build page
	page = main_frame(request, response, args, em_lang.title_rate,
		[
			Form([
				Edit  (text=em_lang.name,          name=b"name",          placeholder=em_lang.field_rate,     required=True, value=current.name),
				Edit  (text=em_lang.validy_date,   name=b"validity_date", type=b"date",                    required=True, value=b"%04d-%02d-%02d"%date.local_time(current.validity_date)[:3]),
				Edit  (text=em_lang.price,         name=b"price",         type=b"number", step=b"0.0001",  required=True, value=b"%f"%current.price),
				Edit  (text=em_lang.currency,      name=b"currency",      placeholder=em_lang.field_currency, required=True, value=current.currency),
				Submit(text=em_lang.add_button,    name=b"add")
			]),
			List(rate_items)
		])
	await response.send_page(page)


@HttpServer.add_route(b'/time_slots', menu=em_lang.menu_electricmeter, item=em_lang.item_time_slots)
async def time_slots_page(request, response, args):
	""" Electric time slots configuration page """
	time_slots = TimeSlotsConfig.get_config()
	rates   = RatesConfig.get_config()
	current = TimeSlotConfig()

	# If new time_slot added
	if request.params.get(b"add",None) is not None:
		current.update(request.params, show_error=False)
		time_slots.append(current)
		time_slots.save()
	# If a time_slot must be deleted
	elif request.params.get(b"remove",None) is not None:
		time_slots.remove(request.params.get(b"remove",b"none"))
		time_slots.save()
	# If a rate must be edited
	elif request.params.get(b"edit",None) is not None:
		current.update(time_slots.get(request.params.get(b"edit",b"none")))

	# List all rates names
	rates_combo = []
	names       = {}
	identifier  = 0
	while True:
		rate = rates.get(identifier)
		if rate is not None:
			if rate[b"name"] not in names:
				rates_combo.append(Option(text=rate[b"name"], value=rate[b"name"], selected=b"selected" if current.rate == rate[b"name"] else b""))
		else:
			break
		names[rate[b"name"]] = b""
		identifier += 1

	# List all rates
	time_slots_items = []
	identifier = 0
	while True:
		time_slot = time_slots.get(identifier)
		if time_slot is not None:
			time_slots_items.append(
					ListItem(
					[
						Label(text=b"&nbsp;&nbsp;&nbsp;&nbsp;", style=b"background-color: %s"%time_slot[b"color"]),
						Space(),Space(),
						Link(text=b"%s - %s : %s "%(date.time_to_html(time_slot[b"start_time"]), date.time_to_html(time_slot[b"end_time"]), time_slot[b"rate"]),href=b"time_slots?edit=%d"%identifier),
						Link(text=em_lang.remove_button , class_=b"btn position-absolute top-50 end-0 translate-middle-y", href=b"time_slots?remove=%d"%identifier, onclick=b"return window.confirm('%s')"%em_lang.remove_dialog)
					]))
		else:
			break
		identifier += 1

	# Build page
	page = main_frame(request, response, args, em_lang.title_time_slots,
		[
			Form([
				Edit (text=em_lang.field_start,      name=b"start_time", type=b"time", required=True, value=date.time_to_html(current.start_time)),
				Edit (text=em_lang.field_end,        name=b"end_time",   type=b"time", required=True, value=date.time_to_html(current.end_time)),
				Label(text=em_lang.field_time_rate),
				Select(rates_combo,name=b"rate",                                    required=True),
				Edit (text=em_lang.field_color,      name=b"color", type=b"color",     required=True, value=current.color),
				Submit(text=em_lang.add_button,      name=b"add")
			]),
			List(time_slots_items)
		])
	await response.send_page(page)


@HttpServer.add_route(b'/geolocation', menu=em_lang.menu_electricmeter, item=em_lang.item_geolocation)
async def geolocation_page(request, response, args):
	""" Determines the geolocation of the device """
	config = GeolocationConfig.get_config()
	disabled, action, submit = manage_default_button(request, config)

	page = main_frame(request, response, args, em_lang.item_geolocation,
		Form([
			Edit  (text=em_lang.latitude,  name=b"latitude",  type=b"number", step=b"0.0001", required=True, min=b"-90.",  max=b"90." , value=b"%.3f"%config.latitude, disabled=disabled),
			Edit  (text=em_lang.longitude, name=b"longitude", type=b"number", step=b"0.0001", required=True, min=b"-180.", max=b"180.", value=b"%.3f"%config.longitude,disabled=disabled),
			submit, None
		]))
	await response.send_page(page)
