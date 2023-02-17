# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" These classes are used to get meteo informations.
See https://open-meteo.com """
# pylint:disable=wrong-import-position
from server.httpclient import *
from tools import logger,strings

async def async_get_meteo(parameters, display=True):
	""" Asyncio get meteo (only in asyncio) """
	return await HttpClient.request(method=b"GET", url=b"http://api.open-meteo.com:80/v1/forecast?"+parameters)

def get_meteo(parameters):
	""" Get meteo function """
	loop = uasyncio.get_event_loop()
	loop.run_until_complete(async_get_meteo(parameters=parameters))
