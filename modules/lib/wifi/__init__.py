# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Class to manage wifi and access point """
from wifi.accesspoint import *
from wifi.station import *
from tools import useful

AUTHMODE = {0: b"open", 1: b"WEP", 2: b"WPA-PSK", 3: b"WPA2-PSK", 4: b"WPA/WPA2-PSK"}

def start(force = False):
	from wifi.accesspoint import AccessPoint
	from wifi.station     import Station
	result2 = AccessPoint.start(force)
	result1 = Station.start(force)
	return result1 or result2

def stop():
	from wifi.accesspoint import AccessPoint
	from wifi.station     import Station
	AccessPoint.stop()
	Station.stop()


