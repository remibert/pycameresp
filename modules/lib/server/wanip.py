# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Get the wan ip address """
import uasyncio
import random
from server.stream import *
from server.httprequest import *
from tools import logger,strings

async def request(host, port, path):
	""" Asynchronous request to ip server """
	result = None
	try:
		streamio = None
		reader,writer = await uasyncio.open_connection(strings.tostrings(host), port)
		streamio = Stream(reader, writer)
		req = HttpRequest(None)
		req.set_path(strings.tobytes(path))
		req.set_header(b"HOST",strings.tobytes(host))
		req.set_method(b"GET")
		req.set_header(b"Accept"         ,b"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
		req.set_header(b"User-Agent"     ,b"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.3 Safari/605.1.15")
		req.set_header(b"Accept-Language",b"fr-FR,fr;q=0.9")
		req.set_header(b"Accept-Encoding",b"gzip, deflate")
		req.set_header(b"Connection"     ,b"keep-alive")
		await req.send(streamio)
		response = HttpResponse(streamio)
		await response.receive(streamio)
		if response.status == b"200":
			result = response.get_content().strip()

	except Exception as err:
		logger.syslog(err)
	finally:
		if streamio:
			await streamio.close()
	return result

async def get_wan_ip_async():
	""" Get the wan ip address with asynchronous method """
	hosts =[
		("alma.ch"              ,"/myip.cgi"),
		("api.infoip.io"        ,"/ip"),
		("api.ipify.org"        ,"/"),
		("checkip.amazonaws.com","/"),
		("l2.io"                ,"/ip"),
		("whatismyip.akamai.com","/")
	]
	host, path = hosts[random.randrange(0,len(hosts))]
	resp = await request(host,80,path)
	if resp:
		return resp.decode("utf-8")
	return None
