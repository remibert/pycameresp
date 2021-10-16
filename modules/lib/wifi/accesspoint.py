# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Classes used to manage the wifi access point """
from wifi.hostname import Hostname
from tools import jsonconfig,useful

class AccessPointConfig(jsonconfig.JsonConfig):
	""" Access point configuration class """
	def __init__(self):
		""" Constructor """
		jsonconfig.JsonConfig.__init__(self)
		self.activated = False
		self.wifi_password = b""
		self.ssid          = b""
		self.authmode      = b"WPA2-PSK"
		self.ip_address    = b"192.168.3.1"
		self.netmask       = b"255.255.255.0"
		self.gateway       = b"192.168.3.1"
		self.dns           = b"192.168.3.1"

	def __repr__(self):
		""" Display accesspoint informations """
		# Get network address
		ip_address, netmask, gateway, dns = AccessPoint.wlan.ifconfig()

		result = "%s:\n"%useful.tostrings(self.__class__.__name__)
		result +="   Ip address :%s\n"%ip_address
		result +="   Netmask    :%s\n"%netmask
		result +="   Gateway    :%s\n"%gateway
		result +="   Dns        :%s\n"%dns
		result +="   Ssid       :%s\n"%useful.tostrings(self.ssid)
		result +="   Password   :%s\n"%useful.tostrings(self.wifi_password)
		result +="   Authmode   :%s\n"%useful.tostrings(self.authmode)
		result +="   Activated  :%s\n"%useful.tostrings(self.activated)
		return result

class AccessPoint:
	""" Class to manage access point """
	config = None
	wlan = None

	@staticmethod
	def open(ssid=None, password=None, authmode=None):
		""" Open access point """
		from wifi import AUTHMODE
		# pylint:disable=multiple-statements
		if ssid     is not None: AccessPoint.config.ssid         = useful.tobytes(ssid)
		if password is not None: AccessPoint.config.wifi_password = useful.tobytes(password)
		if authmode is not None: AccessPoint.config.authmode     = useful.tobytes(authmode)

		authmode = 3
		for authmode_num, authmode_name in AUTHMODE.items():
			if authmode_name == AccessPoint.config.authmode:
				authmode = authmode_num
				break
		AccessPoint.wlan.active(True) # IMPORTANT : Activate before configure
		AccessPoint.wlan.config(\
			essid    = useful.tostrings(AccessPoint.config.ssid),
			password = useful.tostrings(AccessPoint.config.wifi_password),
			authmode = authmode)

	@staticmethod
	def reload_config():
		""" Reload configuration if it changed """
		if AccessPoint.config is None:
			AccessPoint.config = AccessPointConfig()
			if AccessPoint.config.load() is False:
				AccessPoint.config.ssid           = b"esp%05d"%Hostname.get_number()
				AccessPoint.config.wifi_password  = b"Pycam_%05d"%Hostname.get_number()
				AccessPoint.config.save()
				useful.syslog("Access point not initialized")
		else:
			if AccessPoint.config.is_changed():
				AccessPoint.config.load()
		return AccessPoint.config

	@staticmethod
	def close():
		""" Close access point """
		AccessPoint.wlan.active(False)

	@staticmethod
	def is_active():
		""" Indicates if the access point is active or not """
		if AccessPoint.wlan is None:
			return False
		return AccessPoint.wlan.active()

	@staticmethod
	def is_activated():
		""" Indicates if the access point is configured to be activated """
		AccessPoint.reload_config()
		return AccessPoint.config.activated

	@staticmethod
	def get_info():
		""" Get wifi station informations """
		if AccessPoint.wlan is not None and AccessPoint.wlan.active():
			return AccessPoint.wlan.ifconfig()
		return None

	@staticmethod
	def configure(ip_address = None, netmask = None, gateway = None, dns = None):
		""" Configure the access point """
		# pylint:disable=multiple-statements
		if ip_address is not None: AccessPoint.config.ip_address = useful.tobytes(ip_address)
		if netmask    is not None: AccessPoint.config.netmask    = useful.tobytes(netmask)
		if gateway    is not None: AccessPoint.config.gateway    = useful.tobytes(gateway)
		if dns        is not None: AccessPoint.config.dns        = useful.tobytes(dns)

		if AccessPoint.config.ip_address == b"": AccessPoint.config.ip_address = useful.tobytes(AccessPoint.wlan.ifconfig()[0])
		if AccessPoint.config.netmask    == b"": AccessPoint.config.netmask    = useful.tobytes(AccessPoint.wlan.ifconfig()[1])
		if AccessPoint.config.gateway    == b"": AccessPoint.config.gateway    = useful.tobytes(AccessPoint.wlan.ifconfig()[2])
		if AccessPoint.config.dns        == b"": AccessPoint.config.dns        = useful.tobytes(AccessPoint.wlan.ifconfig()[3])

		if AccessPoint.config.ip_address == b"0.0.0.0": AccessPoint.config.ip_address = b""
		if AccessPoint.config.netmask    == b"0.0.0.0": AccessPoint.config.netmask   = b""
		if AccessPoint.config.gateway    == b"0.0.0.0": AccessPoint.config.gateway   = b""
		if AccessPoint.config.dns        == b"0.0.0.0": AccessPoint.config.dns       = b""

		try:
			if AccessPoint.config.ip_address != b"" and \
				AccessPoint.config.netmask   != b"" and \
				AccessPoint.config.gateway   != b"" and \
				AccessPoint.config.dns       != b"":
				AccessPoint.wlan.ifconfig((
					useful.tostrings(AccessPoint.config.ip_address),
					useful.tostrings(AccessPoint.config.netmask),
					useful.tostrings(AccessPoint.config.gateway),
					useful.tostrings(AccessPoint.config.dns)))
		except Exception as err:
			useful.syslog(err, msg="Cannot configure wifi AccessPoint")

	@staticmethod
	def start(force=False):
		""" Start the access point according to the configuration. Force is used to skip configuration activation flag """
		result = False
		if AccessPoint.is_active() is False:
			AccessPoint.reload_config()

			if AccessPoint.config.activated or force:
				useful.syslog("Start AccessPoint")
				from network import WLAN, AP_IF
				AccessPoint.wlan = WLAN(AP_IF)
				AccessPoint.configure()
				AccessPoint.open()
				AccessPoint.configure()
				print(repr(AccessPoint.config))
				result = True
			else:
				useful.syslog("AccessPoint disabled")
		else:
			print("%s already opened"%AccessPoint.__class__.__name__)
			print(repr(AccessPoint.config))
			result = True
		return result

	@staticmethod
	def stop():
		""" Stop access point """
		if AccessPoint.is_active():
			useful.syslog("AccessPoint stopped")
			AccessPoint.close()

	@staticmethod
	def is_ip_on_interface(ipAddr):
		""" Indicates if the address ip is connected to the wifi access point """
		ipInterface = AccessPoint.get_info()
		if ipInterface is not None:
			return useful.issameinterface(useful.tostrings(ipAddr), ipInterface[0], ipInterface[1])
		return False
