# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Classes used to manage the wifi access point """
import sys
from tools import jsonconfig
from tools import useful

class AccessPointConfig(jsonconfig.JsonConfig):
	""" Access point configuration class """
	def __init__(self):
		""" Constructor """
		jsonconfig.JsonConfig.__init__(self)
		self.activated = True
		self.wifipassword  = b""
		self.ssid          = b""
		self.authmode      = b"WPA2-PSK"
		self.ipaddress     = b"192.168.3.1"
		self.netmask       = b"255.255.255.0"
		self.gateway       = b"192.168.3.1"
		self.dns           = b"192.168.3.1"

	def __repr__(self):
		""" Display accesspoint informations """
		# Get network address
		ipaddress, netmask, gateway, dns = AccessPoint.wlan.ifconfig()

		result = "%s:\n"%useful.tostrings(self.__class__.__name__)
		result +="   Ip address :%s\n"%ipaddress
		result +="   Netmask    :%s\n"%netmask
		result +="   Gateway    :%s\n"%gateway
		result +="   Dns        :%s\n"%dns
		result +="   Ssid       :%s\n"%useful.tostrings(self.ssid)
		result +="   Password   :%s\n"%useful.tostrings(self.wifipassword)
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
		from time import sleep
		if ssid     != None: AccessPoint.config.ssid         = useful.tobytes(ssid)
		if password != None: AccessPoint.config.wifipassword = useful.tobytes(password)
		if authmode != None: AccessPoint.config.authmode     = useful.tobytes(authmode)

		authmode = 3
		for authmodeNum, authmodeName in AUTHMODE.items():
			if authmodeName == AccessPoint.config.authmode:
				authmode = authmodeNum
				break
		AccessPoint.wlan.active(True) # IMPORTANT : Activate before configure
		AccessPoint.wlan.config(\
			essid    = useful.tostrings(AccessPoint.config.ssid),
			password = useful.tostrings(AccessPoint.config.wifipassword),
			authmode = authmode)

	@staticmethod
	def close():
		""" Close access point """
		AccessPoint.wlan.active(False)

	@staticmethod
	def isActive():
		""" Indicates if the access point is active or not """
		if AccessPoint.wlan == None:
			return False
		return AccessPoint.wlan.active()

	@staticmethod
	def isActivated():
		""" Indicates if the access point is configured to be activated """
		if AccessPoint.config != None:
			return AccessPoint.config.activated
		else:
			return False

	@staticmethod
	def getInfo():
		if AccessPoint.wlan != None and AccessPoint.wlan.active():
			return AccessPoint.wlan.ifconfig()
		return None

	@staticmethod
	def configure(ipaddress = None, netmask = None, gateway = None, dns = None):
		""" Configure the access point """
		if ipaddress != None: AccessPoint.config.ipaddress = useful.tobytes(ipaddress)
		if netmask   != None: AccessPoint.config.netmask   = useful.tobytes(netmask)
		if gateway   != None: AccessPoint.config.gateway   = useful.tobytes(gateway)
		if dns       != None: AccessPoint.config.dns       = useful.tobytes(dns)

		if AccessPoint.config.ipaddress == b"": AccessPoint.config.ipaddress = useful.tobytes(AccessPoint.wlan.ifconfig()[0])
		if AccessPoint.config.netmask   == b"": AccessPoint.config.netmask   = useful.tobytes(AccessPoint.wlan.ifconfig()[1])
		if AccessPoint.config.gateway   == b"": AccessPoint.config.gateway   = useful.tobytes(AccessPoint.wlan.ifconfig()[2])
		if AccessPoint.config.dns       == b"": AccessPoint.config.dns       = useful.tobytes(AccessPoint.wlan.ifconfig()[3])

		if AccessPoint.config.ipaddress == b"0.0.0.0": AccessPoint.config.ipaddress = b""
		if AccessPoint.config.netmask   == b"0.0.0.0": AccessPoint.config.netmask   = b""
		if AccessPoint.config.gateway   == b"0.0.0.0": AccessPoint.config.gateway   = b""
		if AccessPoint.config.dns       == b"0.0.0.0": AccessPoint.config.dns       = b""

		try:
			if AccessPoint.config.ipaddress != b"" and \
				AccessPoint.config.netmask   != b"" and \
				AccessPoint.config.gateway   != b"" and \
				AccessPoint.config.dns       != b"":
				AccessPoint.wlan.ifconfig((
					useful.tostrings(AccessPoint.config.ipaddress),
					useful.tostrings(AccessPoint.config.netmask),
					useful.tostrings(AccessPoint.config.gateway),
					useful.tostrings(AccessPoint.config.dns)))
		except Exception as err:
			print("Cannot configure wifi AccessPoint %s"%useful.exception(err))

	@staticmethod
	def start(force):
		""" Start the access point according to the configuration. Force is used to skip configuration activation flag """
		result = False
		if AccessPoint.isActive() == False:
			config = AccessPointConfig()

			if not config.load():
				from network import WLAN, AP_IF
				config.activated    = True
				wlan = WLAN(AP_IF)
				ident = wlan.config("mac")
				config.ssid          = b"Esp_%02X%02X%02X"%(ident[0],ident[1],ident[2])
				config.wifipassword  = b"Pycam_%02X%02X%02X"%(ident[0],ident[1],ident[2])
				config.save()
			else:
				wlan = None

			if config.activated or force:
				print("Start AccessPoint")
				from network import WLAN, AP_IF
				AccessPoint.config = config
				if wlan == None:
					AccessPoint.wlan = WLAN(AP_IF)
				else:
					AccessPoint.wlan = wlan
				AccessPoint.configure()
				AccessPoint.open()
				AccessPoint.configure()
				print(repr(AccessPoint.config))
				result = True
			else:
				print("AccessPoint disabled")
		else:
			print("%s already opened"%AccessPoint.__class__.__name__)
			print(repr(AccessPoint.config))
			result = True
		return result

	@staticmethod
	def stop():
		""" Stop access point """
		if AccessPoint.isActive():
			AccessPoint.close()

	@staticmethod
	def isIpOnInterface(ipAddr):
		""" Indicates if the address ip is connected to the wifi access point """
		ipInterface = AccessPoint.getInfo()
		if ipInterface != None:
			return useful.issameinterface(useful.tostrings(ipAddr), ipInterface[0], ipInterface[1])
		return False