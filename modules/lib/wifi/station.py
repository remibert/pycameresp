# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Classes used to manage the wifi station """
import time
from tools import jsonconfig,useful
from wifi.hostname import Hostname
import uasyncio

class NetworkConfig(jsonconfig.JsonConfig):
	""" Wifi station configuration class """
	def __init__(self):
		""" Constructor """
		jsonconfig.JsonConfig.__init__(self)
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
		result +="   Ip address :%s\n"%ipaddress
		result +="   Netmask    :%s\n"%netmask
		result +="   Gateway    :%s\n"%gateway
		result +="   Dns        :%s\n"%dns
		result +="   Ssid       :%s\n"%useful.tostrings(self.ssid)
		# result +="   Password   :%s\n"%useful.tostrings(self.wifipassword)
		return result

	def save(self, file = None):
		""" Save wifi configuration """
		result = jsonconfig.JsonConfig.save(self, file=file, partFilename=self.ssid)
		return result

	def listKnown(self):
		""" List all configuration files """
		return jsonconfig.JsonConfig.listAll(self)

	def forget(self):
		""" Forget configuration """
		return jsonconfig.JsonConfig.forget(self, partFilename=self.ssid)

class StationConfig(jsonconfig.JsonConfig):
	""" Wifi station configuration class """
	def __init__(self):
		""" Constructor """
		jsonconfig.JsonConfig.__init__(self)
		self.hostname      = b"esp%05d"%Hostname.getNumber()
		self.activated     = True
		self.fallback      = True
		self.default       = b""

	def __repr__(self):
		""" Display the content of wifi station """
		# Get network address
		result = "%s:\n"%self.__class__.__name__
		result +="   Activated  :%s\n"%useful.tostrings(self.activated)
		result  ="   Hostname   :%s\n"%useful.tostrings(self.hostname)
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
	async def connect(network, maxRetry=15):
		""" Connect to wifi hotspot """
		result = False
		if not Station.wlan.isconnected():
			Station.wlan.active(True)
			Station.configure(network)
			Station.wlan.connect(useful.tobytes(network.ssid), useful.tobytes(network.wifipassword))
			retry = 0
			while not Station.wlan.isconnected() and retry < maxRetry:
				await uasyncio.sleep(1)
				useful.syslog ("   %-2d/%d wait connection to %s"%(retry+1, maxRetry, useful.tostrings(network.ssid)))
				retry += 1

			if Station.wlan.isconnected() == False:
				Station.wlan.active(False)
			else:
				result = True
		else:
			result = True
		return result

	@staticmethod
	def disconnect():
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
	def isFallback():
		""" Indicates if the access point must be started when wifi not reachable """
		Station.reloadConfig()
		return Station.config.fallback

	@staticmethod
	def configure(network):
		""" Configure the wifi """
		# If ip is dynamic
		if  network.dynamic   == True:
			if len(Station.getHostname()) > 0:
				Station.wlan.config(dhcp_hostname= useful.tostrings(Station.getHostname()))
		else:
			try:
				Station.wlan.ifconfig((useful.tostrings(network.ipaddress),useful.tostrings(network.netmask),useful.tostrings(network.gateway),useful.tostrings(network.dns)))
			except Exception as err:
				useful.syslog(err, msg="Cannot configure wifi station")
		try:
			network.ipaddress = useful.tobytes(Station.wlan.ifconfig()[0])
			network.netmask   = useful.tobytes(Station.wlan.ifconfig()[1])
			network.gateway   = useful.tobytes(Station.wlan.ifconfig()[2])
			network.dns       = useful.tobytes(Station.wlan.ifconfig()[3])
		except Exception as err:
			useful.syslog(err, msg="Cannot get ip station")

	@staticmethod
	def reloadConfig():
		""" Reload configuration if it changed """
		if Station.config == None:
			Station.config = StationConfig()
			Station.network = NetworkConfig()
			if Station.config.load() == False:
				Station.config.save()
				useful.syslog("Wifi not initialized")
		else:
			if Station.config.isChanged():
				Station.config.load()
		return Station.config

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
			Station.otherNetworks = []
			Station.wlan.active(True)
			try:
				otherNetworks = Station.wlan.scan()
				for ssid, bssid, channel, rssi, authmode, hidden in sorted(otherNetworks, key=lambda x: x[3], reverse=True):
					useful.syslog("Network detected %s"%useful.tostrings(ssid))
					Station.otherNetworks.append((ssid, channel, authmode))
				Station.lastScan[0] = time.time()
			except Exception as err:
				useful.syslog("No network found")

		return Station.otherNetworks

	@staticmethod
	def isActivated():
		""" Indicates if the wifi station is configured to be activated """
		Station.reloadConfig()
		if Station.config != None:
			return Station.config.activated
		else:
			return False

	@staticmethod
	async def selectNetwork(networkName, maxRetry):
		""" Select the network and try to connect """
		Station.reloadConfig()
		if networkName != b"":
			# Load default network
			if Station.network.load(partFilename=networkName):
				useful.syslog("Try to connect to %s"%useful.tostrings(Station.network.ssid))
				# If the connection failed
				if await Station.connect(Station.network, maxRetry) == True:
					useful.syslog("Connected to %s"%useful.tostrings(Station.network.ssid))
					print(repr(Station.config) + repr(Station.network))
					Station.config.default = networkName
					Station.config.save()
					return True
		return False

	@staticmethod
	async def scanNetworks(maxRetry):
		""" Scan networks known """
		result = False
		# Scan other networks
		if len(Station.scan()) > 0:
			# List known networks
			Station.knownNetworks = Station.network.listKnown()

			# For all known networks
			for networkName in Station.knownNetworks:
				# If the network not already tested
				if networkName != Station.config.default:
					result = await Station.selectNetwork(networkName, maxRetry)
					if result == True:
						break
		return result

	@staticmethod
	async def chooseNetwork(force=False, maxRetry=15):
		""" Choose network within reach """
		result = False
		Station.reloadConfig()

		# Load wifi configuration
		if Station.config.load():
			if Station.config.activated or force:
				result = await Station.selectNetwork(Station.config.default, maxRetry)
				if result == False:
					result = await Station.scanNetworks(maxRetry)
			else:
				useful.syslog("Wifi disabled")
		else:
			Station.config.save()
			useful.syslog("Wifi not initialized")
		return result

	@staticmethod
	async def start(force=False, maxRetry=15):
		""" Start the wifi according to the configuration. Force is used to skip configuration activation flag """
		result = False
		if Station.isActive() == False:
			from network import WLAN, STA_IF
			Station.wlan = WLAN(STA_IF)

			useful.syslog("Start wifi")
			if await Station.chooseNetwork(force, maxRetry) == True:
				result = True
		else:
			if Station.wlan.isconnected():
				useful.syslog("Wifi already started")
				result = True
			else:
				useful.syslog("Wifi started but not connected")
		return result

	@staticmethod
	def stop():
		""" Stop the wifi station """
		useful.syslog("Stop wifi")
		if Station.wlan is not None:
			try:
				Station.wlan.disconnect()
				Station.wlan.active(False)
			except:
				pass
			Station.wlan = None

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

	@staticmethod
	def getHostname():
		""" Returns the host name """
		Station.reloadConfig()
		return Station.config.hostname