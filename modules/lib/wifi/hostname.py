# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Manage the host name """
import tools.strings
import tools.jsonconfig

class HostnameConfig(tools.jsonconfig.JsonConfig):
	""" Hostname configuration class """
	def __init__(self):
		""" Constructor """
		tools.jsonconfig.JsonConfig.__init__(self)
		self.hostname      = b"esp%05d"%Hostname.get_number()

class Hostname:
	""" Manage the host name """
	number = [None]
	hostname = [None]

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
			Hostname.number[0] = tools.strings.compute_hash(mac)
			del wlan
		return Hostname.number[0]

	@staticmethod
	def get_hostname():
		""" Get the hostname of device """
		result = Hostname.get_number()
		if Hostname.hostname[0] is not None:
			result = Hostname.hostname[0]
		return result

	@staticmethod
	def set_hostname(new_hostname):
		""" Set the hostname of device """
		Hostname.hostname[0] = new_hostname
