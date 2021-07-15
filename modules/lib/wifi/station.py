# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Classes used to manage the wifi station """
import sys
from tools import jsonconfig,useful
import time

class NetworkConfig(jsonconfig.JsonConfig):
	""" Wifi station configuration class """
	def __init__(self):
		""" Constructor """
		jsonconfig.JsonConfig.__init__(self)
		self.hostname      = b"Esp32"
		self.wifipassword  = b""
		self.ssid          = b""
		self.ipaddress     = b""
		self.netmask       = b""
		self.gateway       = b""
		self.dns           = b""
		self.dynamic       = True

	def __repr__(self):
		""" Display the content of wifi station """
		# Get network address
		ipaddress, netmask, gateway, dns = Station.wlan.ifconfig()

		result = "%s:\n"%self.__class__.__name__
		result  ="   Hostname   :%s\n"%useful.tostrings(self.hostname)
		result +="   Ip address :%s\n"%ipaddress
		result +="   Netmask    :%s\n"%netmask
		result +="   Gateway    :%s\n"%gateway
		result +="   Dns        :%s\n"%dns
		result +="   Ssid       :%s\n"%useful.tostrings(self.ssid)
		# result +="   Password   :%s\n"%useful.tostrings(self.wifipassword)
		return result

	def listKnown(self):
		""" List all configuration files """
		return self.listAll()

	def forget(self):
		""" Forget configuration """
		return jsonconfig.JsonConfig.forget(self, partFilename=self.ssid)

class StationConfig(jsonconfig.JsonConfig):
	""" Wifi station configuration class """
	def __init__(self):
		""" Constructor """
		jsonconfig.JsonConfig.__init__(self)
		self.activated     = True
		self.default       = b""

	def __repr__(self):
		""" Display the content of wifi station """
		# Get network address
		result = "%s:\n"%self.__class__.__name__
		result +="   Activated  :%s\n"%useful.tostrings(self.activated)
		return result

class Station:
	""" Class to manage wifi station """
	wlan    = None
	config  = None
	network = None
	otherNetworks = []
	knownNetworks = []
	lastScan = [0]

	@staticmethod
	def connect(network, maxRetry=20000):
		""" Connect to wifi hotspot """
		result = False
		if not Station.wlan.isconnected():
			Station.wlan.active(True)
			Station.configure(network)
			Station.wlan.connect(useful.tobytes(network.ssid), useful.tobytes(network.wifipassword))
			from time import sleep
			retry = 0
			count = 0
			while not Station.wlan.isconnected() and retry < maxRetry:
				sleep(0.1)
				retry += 100
				if count % 1000 == 0:
					print ("   %-2d/%d wait connection to %s"%(retry/1000+1, maxRetry/1000, useful.tostrings(network.ssid)))
				count += 100

			if Station.wlan.isconnected() == False:
				Station.wlan.active(False)
			else:
				result = True
		else:
			result = True
		return result

	@staticmethod
	def disconnect(self):
		""" Disconnect the wifi """
		if Station.wlan.isconnected():
			Station.wlan.disconnect()
			Station.wlan.active(False)
	
	@staticmethod
	def isActive():
		""" Indicates if the wifi is active """
		if Station.wlan == None:
			return False
		return Station.wlan.active()

	@staticmethod
	def configure(network):
		""" Configure the wifi """
		# If ip is dynamic
		if  network.dynamic   == True:
			if len(network.hostname) > 0:
				Station.wlan.config(dhcp_hostname= useful.tostrings(network.hostname))
		else:
			try:
				Station.wlan.ifconfig((useful.tostrings(network.ipaddress),useful.tostrings(network.netmask),useful.tostrings(network.gateway),useful.tostrings(network.dns)))
			except Exception as err:
				print("Cannot configure wifi station %s"%useful.exception(err))
		try:
			network.ipaddress = useful.tobytes(Station.wlan.ifconfig()[0])
			network.netmask   = useful.tobytes(Station.wlan.ifconfig()[1])
			network.gateway   = useful.tobytes(Station.wlan.ifconfig()[2])
			network.dns       = useful.tobytes(Station.wlan.ifconfig()[3])
		except Exception as err:
			print("Cannot get ip station %s"%useful.exception(err))

	@staticmethod
	def getInfo():
		""" Get the network information """
		if Station.wlan != None and Station.wlan.isconnected():
			return Station.wlan.ifconfig()
		return None

	@staticmethod
	def getHostname():
		""" Get the hostname """
		if Station.network != None:
			return Station.network.hostname
		else:
			return b""

	@staticmethod
	def isConnected():
		""" Indicates if the wifi is connected """
		if Station.wlan:
			return Station.wlan.isconnected()
		return False

	@staticmethod
	def scan():
		""" Scan other networks """
		if Station.lastScan[0] + 120 < time.time() or len(Station.otherNetworks) == 0:
			Station.lastScan[0] = time.time()
			Station.otherNetworks = []
			Station.wlan.active(True)
			otherNetworks = Station.wlan.scan()
			for ssid, bssid, channel, rssi, authmode, hidden in sorted(otherNetworks, key=lambda x: x[3], reverse=True):
				Station.otherNetworks.append((ssid, channel, authmode))
		return Station.otherNetworks

	@staticmethod
	def isActivated():
		""" Indicates if the wifi station is configured to be activated """
		if Station.config != None:
			return Station.config.activated
		else:
			return False

	@staticmethod
	def chooseNetwork(force=False, maxRetry=20000):
		""" Choose network within reach """
		result = False
		Station.config  = StationConfig()
		Station.network = NetworkConfig()

		# Load wifi configuration
		if Station.config.load():
			if Station.config.activated or force:
				# Load default network
				if Station.network.load(partFilename=Station.config.default):
					
					# If the connection failed
					if Station.connect(Station.network, maxRetry) == False:
						print("Not connected to the default %s"%useful.tostrings(Station.network.ssid))
						# Scan other networks
						Station.scan()

						# List known networks
						Station.knownNetworks = Station.network.listKnown()

						# For all known networks
						for networkName in Station.knownNetworks:
							# If the network not already tested
							if networkName != Station.config.default:
								# Load other
								if Station.network.load(partFilename=networkName):
									print("Try to connect to %s"%useful.tostrings(Station.network.ssid))
									# Connect to the other network found
									if Station.connect(Station.network, maxRetry) == True:
										print("Connected to %s"%useful.tostrings(Station.network.ssid))
										Station.config.default = networkName
										Station.config.save()
										result = True
										break
									else:
										result = result

						# If no other network available
						if result == False:
							print("Retry to connect to default %s"%useful.tostrings(Station.network.ssid))
							# Load default network
							if Station.network.load(partFilename=Station.config.default):
								# If the connection failed
								if Station.connect(Station.network, maxRetry) == True:
									print("Connected to %s"%useful.tostrings(Station.network.ssid))
									result = True
					else:
						result = True
			else:
				print("Wifi disabled")
		else:
			print("Wifi not initialized")
		return result


	@staticmethod
	def start(force, maxRetry=20000):
		""" Start the wifi according to the configuration. Force is used to skip configuration activation flag """
		result = False
		if Station.isActive() == False:
			from network import WLAN, STA_IF
			Station.wlan = WLAN(STA_IF)

			print("Start wifi")
			if Station.chooseNetwork(force, maxRetry) == True:
				print(repr(Station.config) + repr(Station.network))
				result = True
		else:
			print("Wifi already started")
			print(repr(Station.config) + repr(Station.network))
			result = True
		return result

	@staticmethod
	def stop():
		""" Stop the wifi station """
		if Station.isActive() == False:
			print("Wifi stopped")

	@staticmethod
	def isIpOnInterface(ipAddr):
		""" Indicates if the address ip is connected to wifi station """
		ipInterface = Station.getInfo()
		if ipInterface != ("","","",""):
			return useful.issameinterface(useful.tostrings(ipAddr), ipInterface[0], ipInterface[1])
		return False

	@staticmethod
	def getInfo():
		""" Returns the connection informations """
		if Station.wlan:
			if Station.wlan.isconnected():
				return Station.wlan.ifconfig()
		return ("","","","")