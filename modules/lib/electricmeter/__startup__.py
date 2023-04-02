# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Automatic starter if loaded in the device """
from server.httpserver import HttpServer

@HttpServer.add_pages()
def page_loader():
	""" Load html pages when connecting to http server """
	# pylint:disable=unused-import
	import electricmeter.webpage

def startup(**kwargs):
	""" Startup """
	import electricmeter
	electricmeter.ElectricMeter.start(**kwargs)
