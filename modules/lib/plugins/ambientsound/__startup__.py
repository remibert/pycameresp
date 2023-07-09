# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" Ambient sound that plays sounds in the absence of the occupants of a dwelling """
import server.httpserver

@server.httpserver.HttpServer.add_pages()
def page_loader():
	""" Load html pages when connecting to http server """
	# pylint:disable=unused-import
	import plugins.ambientsound.webpage

def startup(**kwargs):
	""" Startup """
	import plugins.ambientsound.ambientsound
	plugins.ambientsound.ambientsound.AmbientSound.start(**kwargs)
