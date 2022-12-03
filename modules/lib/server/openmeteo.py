# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" These classes are used to get meteo informations.
See https://open-meteo.com """
# pylint:disable=wrong-import-position
import uasyncio
import json
from server.stream import *
from server.httprequest import *
import wifi
from tools import logger,strings

class Meteo:
	""" Class that manages a push over notification """
	def __init__(self, host, port):
		""" Constructor
		host : hostname b"api.open-meteo.com"
		port : port of pushover (80) """
		self.host  = host
		self.port  = port

	async def get(self, parameters, display=True):
		""" Get meteo """
		result = None
		if wifi.Station.is_active():
			try:
				streamio = None
				# Open pushover connection
				reader,writer = await uasyncio.open_connection(strings.tostrings(self.host), self.port)
				streamio = Stream(reader, writer)

				# Create multipart request
				request = HttpRequest(streamio)
				request.set_method(b"GET")
				request.set_path  (b"/v1/forecast"+parameters)
				request.set_header(b"Host",self.host)
				request.set_header(b"Accept",         b"*/*")
				request.set_header(b"Connection",     b"keep-alive")

				response = await read_chunked(streamio, request)
				result = strings.tostrings(response.get_content())
				with open("res.json","wb") as file:
					file.write(response.get_content())
				result = json.loads(result)

			except Exception as err:
				logger.syslog(err)
			finally:
				if streamio:
					await streamio.close()
		else:
			logger.syslog("Get meteo not sent : wifi not connected", display=display)
		return result

async def read_chunked(streamio, request):
	""" Read http chunked response """
	response = HttpResponse(streamio)
	ack      = HttpResponse(streamio)
	await request.send()

	while True:
		await response.receive()
		# print(response.get_content())
		if response.status == b"200":
			if response.headers.get(b"Transfer-Encoding",b"") == b"chunked":
				if response.chunk_size == 0:
					break
				else:
					await ack.send_ok()
			else:
				break
		else:
			break
	return response

async def async_get_meteo(parameters, display=True):
	""" Asyncio get meteo (only in asyncio) """
	meteo = Meteo(host=b"api.open-meteo.com", port=80)
	return await meteo.get(parameters, display=display)

def get_meteo(parameters):
	""" Get meteo function """
	loop = uasyncio.get_event_loop()
	loop.run_until_complete(async_get_meteo(parameters=parameters))
