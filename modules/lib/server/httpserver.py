# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
# historically based on :
# https://github.com/jczic/MicroWebSrv/blob/master/microWebSocket.py
# but I have modified a lot, there must still be some original functions.
# pylint:disable=consider-using-f-string
""" This class is used to manage an http server.
This class contains few lines of code, this is to save memory.
The core of the server is in the other class HttpServerCore, which is loaded into memory only when connecting an HTTP client.
It takes a little while the first time you connect, but limits memory consumption if not in use.
If you have enough memory (SPIRAM or other), just start the server with the preload option at True. """
import re
import server.server
import tools.logger
import tools.filesystem
import tools.strings
import tools.tasking

class HttpServerInstance(tools.tasking.ServerInstance):
	""" Instance of server Http """
	def __init__(self, **kwargs):
		""" Constructor """
		tools.tasking.ServerInstance.__init__(self, **kwargs)
		self.server = None
		self.kwargs = kwargs

	def preload(self):
		""" Method used to preload page template.
		You must define the content of a callback, which only import the python module with your pages """
		started = False
		if HttpServer.preload():
			started = True

		if self.server is None:
			tools.logger.syslog("Http '%s' started"%self.kwargs.get("name",""))
			from server.httpservercore import HttpServerCore
			self.server = HttpServerCore(**self.kwargs)
			started = True

		if started:
			tools.logger.syslog("Http '%s' ready on %d"%(self.kwargs.get("name",""), self.kwargs.get("port",0)))

	async def on_connection(self, reader, writer):
		""" Http server connection detected """
		try:
			# Preload the server
			self.preload()

			# Call on connection method
			await self.server.on_connection(reader, writer)
		except Exception as err:
			tools.logger.syslog(err)

class HttpServer:
	""" Http main class """
	routes       = {}
	wildroutes   = []
	menus        = []
	www_dir      = None
	pages        = []
	loaded       = [False]
	config       = None
	login_checker= None

	@staticmethod
	def call_preload(loader):
		""" Call preload html page callback """
		if loader is not None:
			if tools.filesystem.ismicropython():
				ModuleNotFound = ImportError
			else:
				ModuleNotFound = ModuleNotFoundError
			try:
				loader()
			except ModuleNotFound as err:
				tools.logger.syslog("Preload html page : %s"%str(err))
			except Exception as err:
				tools.logger.syslog(err)

	@staticmethod
	def preload():
		""" Method used to preload page template.
		You must define the content of a callback, which only import the python module with your pages """
		result = False
		if HttpServer.loaded[0] is False:
			from htmltemplate import WWW_DIR
			tools.logger.syslog("Html load pages")
			if len(HttpServer.pages) > 0:
				for loader in HttpServer.pages:
					HttpServer.call_preload(loader)
			HttpServer.www_dir = WWW_DIR
			result = True
			HttpServer.loaded[0] = True
		return result

	@staticmethod
	def add_pages():
		""" Add an html page loader which will be called when connecting to the http server """
		def add_pages(function):
			HttpServer.pages.append(function)
			return function
		return add_pages

	@staticmethod
	def add_route(url, **kwargs):
		""" Add a route to select an html page.
		For the server to know the pages, it must imperatively use this decorator """
		def add_route(function):
			if tools.strings.tobytes(url[-1]) == ord(b"*"):
				HttpServer.wildroutes.append([tools.strings.tobytes(url),(function, kwargs)])
			else:
				kwargs["index"] = len(HttpServer.menus)
				HttpServer.routes[tools.strings.tobytes(url)] = (function, kwargs)
			if kwargs.get("available", True):
				if "item" in kwargs and "menu" in kwargs:
					HttpServer.menus.append([kwargs["menu"], kwargs["item"],len(HttpServer.menus), tools.strings.tobytes(url)])
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
	def set_login_checker():
		""" Change the default login checker """
		def setter(checker):
			HttpServer.login_checker = checker
		return setter

	@staticmethod
	async def is_logged(request, response):
		""" Check the login """
		if HttpServer.login_checker is not None:
			return await HttpServer.login_checker(request, response)
		return True

	@staticmethod
	def search_route(request):
		""" Search route according to the request """
		function, args = None, None

		if request.method == b"PUT":
			directory, file = tools.filesystem.split(tools.strings.tostrings(request.path))
			found = HttpServer.routes.get(tools.strings.tobytes(directory),None)
			if found:
				function, args = found
			return function, args
		else:
			found = HttpServer.routes.get(request.path,None)
			if found is None:
				for route, func in HttpServer.wildroutes:
					if re.match(tools.strings.tostrings(route), tools.strings.tostrings(request.path)):
						found = func
						break
				if found is None:
					staticRe = re.compile("^/("+tools.strings.tostrings(HttpServer.www_dir)+"/.+|.+)")
					if staticRe.match(tools.strings.tostrings(request.path)):
						function, args = HttpServer.static_pages, {}
				else:
					function, args = found
			else:
				function, args = found
		return function, args

	@staticmethod
	async def static_pages(request, response, args):
		""" Treat the case of static pages """
		path = tools.strings.tobytes(HttpServer.www_dir) + request.path
		path = path.replace(b"//",b"/")
		if b".." in path:
			await response.send_error(status=b"403",content=b"Forbidden")
		else:
			await response.send_file(path, headers=request.headers)

	@staticmethod
	def init():
		""" Initialize http server """
		if HttpServer.config is None:
			HttpServer.config = server.server.ServerConfig()
			HttpServer.config.load_create()
		else:
			HttpServer.config.refresh()

	@staticmethod
	def start(**kwargs):
		""" Start http server instance on selected port """
		HttpServer.init()
		# If http activated
		if HttpServer.config.http:
			kwargs["port"] = kwargs.get("http_port",80)
			kwargs["name"] = kwargs.get("name","Http")
			kwargs["backlog"] = kwargs.get("backlog",5)
			tools.tasking.Tasks.create_server(HttpServerInstance(**kwargs))
		else:
			tools.logger.syslog("Http server disabled in config")
