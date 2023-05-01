# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" Automatic starter if loaded in the device """
import server.httpserver

@server.httpserver.HttpServer.add_pages()
def page_loader():
	""" Load html pages when connecting to http server """
	# pylint:disable=unused-import
	import electricmeter.webpage

def startup(**kwargs):
	""" Startup """
	import electricmeter.meter
	electricmeter.meter.ElectricMeter.start(**kwargs)
