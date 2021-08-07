# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Manage the host name """
from tools import useful

class Hostname:
	""" Manage the host name """
	hostname = [None]
	number = [None]

	@staticmethod
	def get():
		""" Return the current host name """
		if Hostname.hostname[0] == None:
			Hostname.hostname[0]         = b"Esp_%05d"%Hostname.getNumber()
		return Hostname.hostname[0]

	@staticmethod
	def getNumber():
		""" Get the unic number of device """
		if Hostname.number[0] == None:
			from network import WLAN, AP_IF
			wlan = WLAN(AP_IF)
			ident = wlan.config("mac")
			mac = ""
			for i in ident:
				mac += "%02X"%i
			Hostname.number[0] = useful.computeHash(mac)
		return Hostname.number[0]

	@staticmethod
	def set(hostname):
		""" Change the default host name """
		Hostname.hostname[0] = hostname
