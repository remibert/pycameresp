# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" Class to compute sourdough bread """
import server.httpserver

@server.httpserver.HttpServer.add_pages()
def page_loader():
	""" Load html pages when connecting to http server """
	# pylint:disable=unused-import
	import plugins.sourdoughbread.webpage
