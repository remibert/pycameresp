# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Class to manage wifi and access point """
from wifi.accesspoint import *
from wifi.station import *
from wifi.hostname import *
from tools import useful

AUTHMODE = {0: b"open", 1: b"WEP", 2: b"WPA-PSK", 3: b"WPA2-PSK", 4: b"WPA/WPA2-PSK"}

async def start(force = False):
	""" Start wifi station and access point """
	from wifi.accesspoint import AccessPoint
	from wifi.station     import Station
	result2 = AccessPoint.start(force)
	result1 = await Station.start(force)
	if result1 == False and result2 == False:
		# If the wifi station cannot be connected
		if Station.isActivated():
			# Force the access point
			print("Access point start forced")
			result2 = AccessPoint.start(True)
	return result1 or result2

def stop():
	""" Stop wifi station and access point """
	from wifi.accesspoint import AccessPoint
	from wifi.station     import Station
	AccessPoint.stop()
	Station.stop()


