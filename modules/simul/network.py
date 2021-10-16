# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Class used to simulate the WLAN class on osx """
AP_IF = 1
STA_IF = 2
class WLAN:
	""" Wlan """
	def __init__(self, typ):
		""" Constructor """
		self.typ = typ
		self._active = False
		self._isconnected = False
		self.ssid =""
		self.password = ""
		self.authmode = 0
		self.dhcp_hostname_ = 0
		self._ifconfig = (("0.0.0.0","0.0.0.0","0.0.0.0","0.0.0.0"))

	def isconnected(self):
		""" Indicates if is connected """
		return self._isconnected

	def active(self, val = None):
		""" Active wlan"""
		if val is not None:
			self._active = val
		return self._active

	def connect(self, ssid, password, authmode=3):
		""" Connect wlan """
		#self._isconnected = False
		self._isconnected = True
		self.password = password
		self.ssid     = ssid
		self.authmode = authmode

	def config(self, dhcp_hostname="", essid="", password="", authmode=3):
		""" Configure wlan """
		self.ssid=essid
		self.dhcp_hostname_=dhcp_hostname
		self.password=password
		self.authmode = authmode
		if dhcp_hostname == "mac":
			return [1,2,3,4,5,6,7,8]

	def ifconfig(self, data=None):
		""" Ifconfig """
		import socket
		ipAddress = socket.gethostbyname(socket.gethostname())
		if data is not None:
			self._ifconfig = (ipAddress, data[1], data[2], data[3])
		else:
			self._ifconfig = (ipAddress, "255.255.255.0","192.168.1.1","192.168.1.1")
		return self._ifconfig

	def scan(self):
		""" Scan """
		if self._active:
			return [\
				(b'WifiMaison4', b'@\xc7)C\xcd\\', 6, -64, 4, False),
				(b'Livebox-1DF2', b'\x84\xa1\xd1\xff\x1d\xf2', 6, -94, 4, False)
				]
		else:
			return []
