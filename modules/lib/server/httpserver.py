# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# historically based on :
# https://github.com/jczic/MicroWebSrv/blob/master/microWebSocket.py
# but I have modified a lot, there must still be some original functions.
""" This class is used to manage an http server.
This class contains few lines of code, this is to save memory.
The core of the server is in the other class HttpServerCore, which is loaded into memory only when connecting an HTTP client.
It takes a little while the first time you connect, but limits memory consumption if not in use.
If you have enough memory (SPIRAM or other), just start the server with the preload option at True. """
import re
from tools import useful

class HttpServer:
	""" Http main class """
	routes = {}
	wildroutes = []
	menus = []
	www_dir = None

	def __init__(self, port=80, loader=None, preload=False, name=""):
		""" Constructor """
		self.server = None
		self.loader = loader
		self.port = port
		self.name = name
		if preload:
			self.preload()
		else:
			useful.syslog("Http waiting on %d"%self.port)

	def preload(self):
		""" Method used to preload page template.
		You must define the content of a callback, which only import the python module with your pages """
		loaded = False

		if self.loader:
			from htmltemplate import WWW_DIR
			useful.syslog("Html load pages")
			self.loader()
			self.loader = None
			HttpServer.www_dir = WWW_DIR
			loaded = True

		if self.server is None:
			useful.syslog("Http start server")
			from server.httpservercore import HttpServerCore
			self.server = HttpServerCore(self.port, self.name)
			loaded = True

		if loaded:
			useful.syslog("Http ready on %d"%self.port)

	@staticmethod
	def add_route(url, **kwargs):
		""" Add a route to select an html page.
		For the server to know the pages, it must imperatively use this decorator """
		def add_route(function):
			if useful.tobytes(url[-1]) == ord(b"*"):
				HttpServer.wildroutes.append([useful.tobytes(url),(function, kwargs)])
			else:
				kwargs["index"] = len(HttpServer.menus)
				HttpServer.routes[useful.tobytes(url)] = (function, kwargs)
			if kwargs.get("available", True):
				if "item" in kwargs and "menu" in kwargs:
					HttpServer.menus.append([kwargs["menu"], kwargs["item"],len(HttpServer.menus), useful.tobytes(url)])
					HttpServer.menus.sort()
			return function
		return add_route

	@staticmethod
	def remove_route(url=None):
		""" Remove a route of html page """
		if url is None:
			HttpServer.routes = {}
			HttpServer.menus = []
		else:
			route = HttpServer.routes.get(url, None)
			if route:
				del HttpServer.routes[url]
				title = route[1].get("title", None)
				if title:
					i = 0
					for item in HttpServer.menus:
						index, route, titl = item
						if titl == title:
							del HttpServer.menus[i]
							break
						i += 1

	@staticmethod
	def get_menus():
		""" Used to get the informations of menu """
		return HttpServer.menus

	@staticmethod
	def search_route(request):
		""" Search route according to the request """
		function, args = None, None

		if request.method == b"PUT":
			directory, file = useful.split(useful.tostrings(request.path))
			found = HttpServer.routes.get(useful.tobytes(directory),None)
			if found:
				function, args = found
			return function, args
		else:
			found = HttpServer.routes.get(request.path,None)
			if found is None:
				for route, func in HttpServer.wildroutes:
					if re.match(useful.tostrings(route), useful.tostrings(request.path)):
						found = func
						break
				if found is None:
					staticRe = re.compile("^/("+useful.tostrings(HttpServer.www_dir)+"/.+|.+)")
					if staticRe.match(useful.tostrings(request.path)):
						function, args = HttpServer.static_pages, {}
				else:
					function, args = found
			else:
				function, args = found
		return function, args

	@staticmethod
	async def static_pages(request, response, args):
		""" Treat the case of static pages """
		path = useful.tobytes(HttpServer.www_dir) + request.path
		path = path.replace(b"//",b"/")

		if b".." in path:
			await response.send_error(status=b"403",content=b"Forbidden")
		else:
			await response.send_file(path, headers=request.headers)

	async def on_connection(self, reader, writer):
		""" Http server connection detected """
		try:
			# Preload the server
			self.preload()

			# Call on connection method
			await self.server.on_connection(reader, writer)
		except Exception as err:
			useful.syslog(err)

def start(loop=None, port=80, loader=None, preload=False, name=""):
	""" Start http server.
	loop : asyncio loop object
	port : tcp/ip port of the server
	preload : True = preload the server at the start, False = load the server at the first connection """
	import uasyncio
	server = HttpServer(port=port, loader=loader, preload=preload, name=name)

	if loop is None:
		loop = uasyncio.get_event_loop()
		run_forever = True
	else:
		run_forever = False

	asyncServer = uasyncio.start_server(server.on_connection, "0.0.0.0",port,backlog=5)

	loop.create_task(asyncServer)
	if run_forever:
		loop.run_forever()
