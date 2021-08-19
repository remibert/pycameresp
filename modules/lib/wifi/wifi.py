# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Manages access to wifi, treats cases of network loss with retry, and manages a fallback on the access point if no network is available """
from wifi.accesspoint import *
from wifi.station import *
from wifi.hostname import *
from tools import useful

WIFI_OFF            = 0
WIFI_OTHER_NETWORK  = 1
WIFI_CONNECTED      = 2
LAN_CONNECTED       = 3
WAN_CONNECTED       = 4
ACCESS_POINT_FORCED = 5
WIFI_LOST           = 6
WIFI_ABSENT         = 7

class WifiContext:
	""" Wifi context """
	def __init__(self):
		""" Constructor """
		self.problem    = 0
		self.dns = ""
		self.state = WIFI_OFF

class Wifi:
	""" Class to manage the wifi station and access point """
	context = WifiContext()

	@staticmethod
	def getDns():
		""" Return the ip address of dns or empty string """
		return Wifi.context.dns

	@staticmethod
	def getState():
		""" Return the state of wifi """
		return Wifi.context.state

	@staticmethod
	def setState(state):
		""" Set the state of wifi """
		if Wifi.context.state != state:
			if state == WIFI_OFF           : useful.logError("Wifi off")
			if state == WIFI_OTHER_NETWORK : useful.logError("Wifi select other network")
			if state == WIFI_CONNECTED     : useful.logError("Wifi connected")
			if state == LAN_CONNECTED      : useful.logError("Wifi LAN connected")
			if state == WAN_CONNECTED      : useful.logError("Wifi WAN connected")
			if state == ACCESS_POINT_FORCED: useful.logError("Wifi access point forced")
			if state == WIFI_LOST          : useful.logError("Wifi lost connection")
			
		Wifi.context.state = state
		if Wifi.context.state in [WIFI_OFF,WIFI_OTHER_NETWORK,ACCESS_POINT_FORCED,WIFI_LOST]:
			Wifi.context.dns = ""

	@staticmethod
	def isLanConnected():
		""" Indicates if wifi network available for start server """
		if Wifi.getState() in [WIFI_CONNECTED, LAN_CONNECTED, WAN_CONNECTED, ACCESS_POINT_FORCED]:
			return True
		elif AccessPoint.isActive() == True:
			return True
		return False

	@staticmethod
	def connectWan():
		""" Set wan have establish dialog with external server """
		Wifi.context.problem = 0
		if Wifi.getState() == WIFI_CONNECTED:
			Wifi.setState(WAN_CONNECTED)

	@staticmethod
	def disconnectWan():
		""" Indicates that wan have probably a problem """
		if Wifi.getState() in [WIFI_CONNECTED, LAN_CONNECTED, WAN_CONNECTED ]:
			Wifi.context.problem += 1
			useful.logError("Wan problem %d detected"%Wifi.context.problem)

	@staticmethod
	def connectLan():
		""" Indicates that lan connection detected """
		Wifi.context.problem = 0
		if Wifi.getState() in [WIFI_CONNECTED]:
			Wifi.setState(LAN_CONNECTED)

	@staticmethod
	def disconnectLan():
		""" Indicates that lan disconnection detected """
		if Wifi.getState() in [WIFI_CONNECTED, LAN_CONNECTED, WAN_CONNECTED ]:
			Wifi.context.problem += 1
			useful.logError("Lan problem %d detected"%Wifi.context.problem)

	@staticmethod
	def isWanAvailable():
		""" Indicates if wan is connected or established """
		if Wifi.getState() in [WIFI_CONNECTED, LAN_CONNECTED, WAN_CONNECTED]:
			return True
		return False

	@staticmethod
	def isWanConnected():
		""" Indicates that wan communication done with success """
		return Wifi.getState() == WAN_CONNECTED

	@staticmethod
	async def manage():
		""" Manage the wifi """
		while 1:
			state = Wifi.getState()

			# If the wifi not started
			if state == WIFI_OFF:
				if Station.isActivated():
					# If wifi station connected
					if await Station.start():
						Wifi.context.dns = Station.getInfo()[3]
						Wifi.setState(WIFI_CONNECTED)
					else:
						Wifi.setState(WIFI_OTHER_NETWORK)

			# If the network not reached select other network
			elif state == WIFI_OTHER_NETWORK:
				if await Station.chooseNetwork(True, maxRetry=5) == True:
					Wifi.context.dns = Station.getInfo()[3]
					Wifi.setState(WIFI_CONNECTED)
				else:
					# Wifi connection failed
					if Station.isFallback():
						Wifi.setState(ACCESS_POINT_FORCED)

						# Start access point and force it if no wifi station connected
						AccessPoint.start(True)
					else:
						Wifi.setState(WIFI_OFF)

			# If access point forced
			elif state == ACCESS_POINT_FORCED:
				if await Station.chooseNetwork(True, maxRetry=5) == True:
					Wifi.context.dns = Station.getInfo()[3]
					Wifi.setState(WIFI_CONNECTED)

			# If the wan reponding
			elif state in [WAN_CONNECTED, LAN_CONNECTED, WIFI_CONNECTED]:
				# If many wan problem notified
				if Wifi.context.problem > 3:
					Wifi.setState(WIFI_LOST)

			# If wifi lost
			elif state == WIFI_LOST:
				Station.stop()
				Wifi.setState(WIFI_OFF)

			if state == Wifi.getState():
				break
			if Wifi.getState() == WIFI_OFF:
				break

		# If the accesspoint not activated
		if AccessPoint.isActivated() == True and AccessPoint.isActive() == False:
			# Start the access point
			AccessPoint.start()
			
