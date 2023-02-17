# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET

""" Client http request """
import wifi
import uasyncio
import server.stream
import server.urlparser
from server.stream import Stream
from server.httprequest import HttpRequest, HttpResponse, ContentText
from tools import logger,strings

class HttpClient:
	""" Http client """
	@staticmethod
	async def read_chunked(streamio, request):
		""" Read http chunked response """
		response = HttpResponse(streamio)
		ack      = HttpResponse(streamio)

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

	@staticmethod
	async def request(method, url, data=None, json=None, headers=None):
		""" Request http to server """
		result = None
		url_parsed = server.urlparser.UrlParser(url)

		# If url supported
		if url_parsed.protocol == b"http" and url_parsed.host is not None and (method == b"POST" or method == b"GET"):
			if wifi.Station.is_active():
				try:
					streamio = None
					if url_parsed.port is None:
						url_parsed.port = 80
					# Open connection
					reader,writer = await uasyncio.open_connection(strings.tostrings(url_parsed.host), url_parsed.port)
					streamio = Stream(reader, writer)
					path = url_parsed.path
					if url_parsed.params is not None:
						path += b"?" + url_parsed.get_params()
					# Create request
					request = HttpRequest(streamio)
					request.set_method(method)
					request.set_path  (path)
					request.set_header(b"Host",url_parsed.host)
					request.set_header(b"Accept",         b"*/*")
					request.set_header(b"Connection",     b"keep-alive")
					if type(headers) == type({}):
						for key, value in headers:
							request.set_header(strings.tobytes(key), strings.tobytes(value))

					if data is not None:
						request.set_header(b"Content-Type",   b"multipart/form-data")
						if data:
							for dat in data:
								request.add_part(dat)
					elif json is not None:
						request.add_part(ContentText(json, content_type = b"application/json"))

					# Send request
					await request.send()

					# Wait response
					result = await HttpClient.read_chunked(streamio, request)
				except Exception as err:
					logger.syslog(err)
				finally:
					if streamio:
						await streamio.close()
			else:
				logger.syslog("Wifi not connected")
		return result
