# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Automatic starter if loaded in the device """
from electricmeter import create_electric_meter
from server.httpserver import HttpServer

def page_loader():
	""" Load html pages when connecting to http server """
	# pylint:disable=unused-import
	import electricmeter.webpage

def startup(loop):
	""" Startup """
	create_electric_meter(loop, gpio=21)
	HttpServer.add_page_loader(page_loader)
