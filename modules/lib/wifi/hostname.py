# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Manage the host name """
from tools import useful

class Hostname:
	""" Manage the host name """
	number = [None]

	@staticmethod
	def get_number():
		""" Get the unic number of device """
		if Hostname.number[0] is None:
			from network import WLAN, AP_IF
			wlan = WLAN(AP_IF)
			ident = wlan.config("mac")
			mac = ""
			for i in ident:
				mac += "%02X"%i
			Hostname.number[0] = useful.compute_hash(mac)
			del wlan
		return Hostname.number[0]
