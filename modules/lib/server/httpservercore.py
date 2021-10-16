# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# historically based on :
# https://github.com/jczic/MicroWebSrv/blob/master/microWebSocket.py
# but I have modified a lot, there must still be some original functions.
"""
Http server core, it instanciated only if a connection is done to the asynchronous class HttpServer then if the server not used, it not consum memory
"""
from server.httpserver import HttpServer
from server.httprequest import HttpRequest, HttpResponse
from server.stream import Stream
from tools import useful

class HttpServerCore:
	""" Http server core, it instanciated only if a connection is done to the asynchronous class HttpServer then
	if the server not used, it not consum memory """
	def __init__(self, port, name):
		""" Constructor """
		self.port = port
		self.name = name

	async def on_connection(self, reader, writer):
		""" Asynchronous connection call back """
		remoteaddr = writer.get_extra_info('peername')[0]
		stream    = Stream(reader, writer)
		request   = HttpRequest (stream, remoteaddr=remoteaddr, port=self.port, name=self.name)
		response  = HttpResponse(stream, remoteaddr=remoteaddr, port=self.port, name=self.name)
		try:
			await request.receive()
			# print(request.path)
			function, args = HttpServer.search_route(request)
			if function is None:
				await response.send_error(status=b"404", content=b"Page not found")
			else:
				await function(request, response, args)
		except OSError as err:
			# If ECONNRESET or ENOTCONN
			if err.args[0] == 104 or err.args[0] == 128:
				# Ignore error
				pass
			else:
				await response.send_error(status=b"404", content=useful.tobytes(useful.exception(err)))
		except Exception as err:
			await response.send_error(status=b"404", content=useful.tobytes(useful.exception(err)))
		finally:
			await stream.close()
