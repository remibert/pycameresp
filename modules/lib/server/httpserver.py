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

from tools.useful import log
from tools import useful
import re

class HttpServer:
	""" Http main class """
	routes = {}
	wildroutes = []
	menus = []
	wwwDir = None

	def __init__(self, port=80, loader=None, preload=False, name=""):
		""" Constructor """
		self.server = None
		self.loader = loader
		self.port = port
		self.name = name
		if preload:
			self.preload()
		else:
			print("Http waiting on %d"%self.port)

	def preload(self):
		""" Method used to preload page template.
		You must define the content of a callback, which only import the python module with your pages """
		loaded = False

		if self.loader:
			from htmltemplate import WWW_DIR
			print("Html load pages")
			self.loader()
			self.loader = None
			HttpServer.wwwDir = WWW_DIR
			loaded = True

		if self.server == None:
			print("Http start server")
			from server.httpservercore import HttpServerCore
			self.server = HttpServerCore(self.port, self.name)
			loaded = True

		if loaded:
			print("Http ready on %d"%self.port)

	@staticmethod
	def addRoute(url, **kwargs):
		""" Add a route to select an html page.
		For the server to know the pages, it must imperatively use this decorator """
		def addRoute(function):
			if useful.tobytes(url[-1]) == ord(b"*"):
				HttpServer.wildroutes.append([useful.tobytes(url),(function, kwargs)])
			else:
				HttpServer.routes[useful.tobytes(url)] = (function, kwargs)
			if kwargs.get("available", True):
				if "index" in kwargs and "title" in kwargs:
					HttpServer.menus.append([int(kwargs["index"]), useful.tobytes(url), kwargs["title"]])
					HttpServer.menus.sort()
			return function
		return addRoute

	@staticmethod
	def removeRoute(url=None):
		""" Remove a route of html page """
		if url == None:
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
	def getMenus():
		""" Used to get the informations of menu """
		return HttpServer.menus

	@staticmethod
	def searchRoute(request):
		""" Search route according to the request """
		function, args = None, None
		
		if request.method == b"PUT":
			dir, file = useful.split(useful.tostrings(request.path))
			found = HttpServer.routes.get(useful.tobytes(dir),None)
			if found:
				function, args = found
			return function, args
		else:
			found = HttpServer.routes.get(request.path,None)
			if found == None:
				for route, func in HttpServer.wildroutes:
					if re.match(useful.tostrings(route), useful.tostrings(request.path)):
						found = func
						break
				if found == None:
					staticRe = re.compile("^/("+useful.tostrings(HttpServer.wwwDir)+"/.+|.+)")
					if staticRe.match(useful.tostrings(request.path)):
						function, args = HttpServer.staticPages, {}
				else:
					function, args = found
			else:
				function, args = found
		return function, args

	@staticmethod
	async def staticPages(request, response, args):
		""" Treat the case of static pages """
		path = useful.tobytes(HttpServer.wwwDir) + request.path
		path = path.replace(b"//",b"/")
		
		if b".." in path:
			await response.sendError(status=b"403",content=b"Forbidden")
		else:
			await response.sendFile(path, headers=request.headers)

	async def onConnection(self, reader, writer):
		""" Http server connection detected """
		try:
			# Preload the server
			self.preload()

			# Call on connection method
			await self.server.onConnection(reader, writer)
		except Exception as err:
			print(useful.exception(err))

def start(loop=None, port=80, loader=None, preload=False, name=""):
	""" Start http server.
	loop : asyncio loop object
	port : tcp/ip port of the server
	preload : True = preload the server at the start, False = load the server at the first connection """
	import uasyncio
	server = HttpServer(port=port, loader=loader, preload=preload, name=name)

	if loop == None:
		loop = uasyncio.get_event_loop()
		run_forever = True
	else:
		run_forever = False

	asyncServer = uasyncio.start_server(server.onConnection, "0.0.0.0",port,backlog=5)

	loop.create_task(asyncServer)
	if run_forever:
		loop.run_forever()

