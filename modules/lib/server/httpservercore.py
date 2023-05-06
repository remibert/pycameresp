# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
# historically based on :
# https://github.com/jczic/MicroWebSrv/blob/master/microWebSocket.py
# but I have modified a lot, there must still be some original functions.
"""
Http server core, it instanciated only if a connection is done to the asynchronous class HttpServer then if the server not used, it not consum memory
"""
import server.httpserver
import server.httprequest
import server.stream
import tools.logger

class HttpServerCore:
	""" Http server core, it instanciated only if a connection is done to the asynchronous class HttpServer then
	if the server not used, it not consum memory """
	def __init__(self, **kwargs):
		""" Constructor """
		self.port = kwargs.get("port",80)
		self.name = kwargs.get("name","HttpServer")

	async def on_connection(self, reader, writer):
		""" Asynchronous connection call back """
		remoteaddr = writer.get_extra_info('peername')[0]
		stream    = server.stream.Stream(reader, writer)
		request   = server.httprequest.HttpRequest (stream, remoteaddr=remoteaddr, port=self.port, name=self.name)
		response  = server.httprequest.HttpResponse(stream, remoteaddr=remoteaddr, port=self.port, name=self.name)
		try:
			await request.receive()
			function, args = server.httpserver.HttpServer.search_route(request)
			if function is None:
				await response.send_not_found()
			else:
				if await server.httpserver.HttpServer.is_logged(request, response):
					await function(request, response, args)
		except OSError as err:
			# If ECONNRESET or ENOTCONN
			if err.args[0] == 104 or err.args[0] == 128:
				# Ignore error
				pass
			else:
				await response.send_not_found(err)
		except Exception as err:
			tools.logger.syslog(err)
			await response.send_not_found(err)
		finally:
			await stream.close()
