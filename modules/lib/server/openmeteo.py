# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" These classes are used to get meteo informations.
See https://open-meteo.com """
# pylint:disable=wrong-import-position
import uasyncio
import server.httpclient

async def async_get_meteo(parameters, display=True):
	""" Asyncio get meteo (only in asyncio) """
	return await server.httpclient.HttpClient.request(method=b"GET", url=b"http://api.open-meteo.com:80/v1/forecast?"+parameters)

def get_meteo(parameters):
	""" Get meteo function """
	loop = uasyncio.get_event_loop()
	loop.run_until_complete(async_get_meteo(parameters=parameters))
