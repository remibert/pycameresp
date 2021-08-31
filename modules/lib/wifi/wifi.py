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
WIFI_CLOSE          = 7


MAX_PROBLEM = 3

class WifiContext:
	""" Wifi context """
	def __init__(self):
		""" Constructor """
		self.lanProblem    = 0
		self.wanProblem    = 0
		self.dns = ""
		self.state = WIFI_OFF
		self.pollingId = 0
		self.accessPointForced = 0


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
			if state == WIFI_OFF           : useful.syslog("Wifi off")
			if state == WIFI_OTHER_NETWORK : useful.syslog("Wifi select other network")
			if state == WIFI_CONNECTED     : useful.syslog("Wifi connected")
			if state == LAN_CONNECTED      : useful.syslog("Wifi LAN connected")
			if state == WAN_CONNECTED      : useful.syslog("Wifi WAN connected")
			if state == ACCESS_POINT_FORCED: useful.syslog("Wifi access point forced")
			if state == WIFI_LOST          : useful.syslog("Wifi lost connection")
			if state == WIFI_CLOSE         : useful.syslog("Wifi closed")
		Wifi.context.state = state

	@staticmethod
	def isLanConnected():
		""" Indicates if wifi network available for start server """
		if Wifi.getState() in [WIFI_CONNECTED, LAN_CONNECTED, WAN_CONNECTED, ACCESS_POINT_FORCED]:
			return True
		elif AccessPoint.isActive() == True:
			return True
		return False

	@staticmethod
	def wanConnected():
		""" Set wan have establish dialog with external server """
		Wifi.lanConnected(False)
		if Wifi.context.wanProblem > 0:
			useful.syslog("Wan connected")
			Wifi.context.wanProblem = 0
		if Wifi.getState() in [WIFI_CONNECTED, LAN_CONNECTED]:
			Wifi.setState(WAN_CONNECTED)

	@staticmethod
	def wanDisconnected():
		""" Indicates that wan have probably a problem """
		if Wifi.getState() in [WIFI_CONNECTED, LAN_CONNECTED, WAN_CONNECTED ]:
			Wifi.context.wanProblem += 1
			useful.syslog("Wan problem %d detected"%Wifi.context.wanProblem)

	@staticmethod
	def lanConnected(changeState=True):
		""" Indicates that lan connection detected """
		if Wifi.context.lanProblem > 0:
			useful.syslog("Lan connected")
			Wifi.context.lanProblem = 0
		if changeState:
			if Wifi.getState() == WIFI_CONNECTED:
				Wifi.setState(LAN_CONNECTED)

	@staticmethod
	def lanDisconnected():
		""" Indicates that lan disconnection detected """
		if Wifi.getState() in [WIFI_CONNECTED, LAN_CONNECTED, WAN_CONNECTED ]:
			Wifi.context.lanProblem += 1
			useful.syslog("Lan problem %d detected"%Wifi.context.lanProblem)

	@staticmethod
	def isWanAvailable():
		""" Indicates if wan is connected or established """
		if Wifi.getState() in [WIFI_CONNECTED, LAN_CONNECTED, WAN_CONNECTED]:
			return True
		return False

	@staticmethod
	def isLanAvailable():
		""" Indicates if lan is connected """
		if Wifi.getState() in [WIFI_CONNECTED, LAN_CONNECTED, WAN_CONNECTED]:
			if Wifi.context.lanProblem < MAX_PROBLEM:
				return True
		return False

	@staticmethod
	def isWanConnected():
		""" Indicates that wan communication done with success """
		return Wifi.getState() == WAN_CONNECTED

	@staticmethod
	async def manage():
		""" Manage the wifi """
		Wifi.context.pollingId += 1
		while 1:
			state = Wifi.getState()

			# If the wifi not started
			if state == WIFI_OFF:
				Wifi.context.dns = ""
				Wifi.context.lanProblem = 0
				Wifi.context.wanProblem = 0
				if Station.isActivated():
					# If wifi station connected
					if await Station.start():
						Wifi.context.dns = Station.getInfo()[3]
						Wifi.setState(WIFI_CONNECTED)
					else:
						Wifi.setState(WIFI_OTHER_NETWORK)

			# If the network not reached select other network
			elif state in [WIFI_OTHER_NETWORK, ACCESS_POINT_FORCED]:
				if Station.isActivated():
					Station.stop()
					if await Station.chooseNetwork(maxRetry=5) == True:
						Wifi.context.dns = Station.getInfo()[3]
						Wifi.context.lanProblem = 0
						Wifi.context.wanProblem = 0
						Wifi.setState(WIFI_CONNECTED)
					else:
						# Wifi connection failed
						if Station.isFallback():
							Wifi.setState(ACCESS_POINT_FORCED)
						else:
							Wifi.setState(WIFI_CLOSE)
				else:
					Wifi.setState(WIFI_CLOSE)

			# If the wan reponding
			elif state in [WAN_CONNECTED, LAN_CONNECTED, WIFI_CONNECTED]:
				if Station.isActivated():
					# If many problem notified
					if Wifi.context.lanProblem >= MAX_PROBLEM or Wifi.context.wanProblem >= MAX_PROBLEM:
						Wifi.setState(WIFI_LOST)
				else:
					Wifi.setState(WIFI_CLOSE)

			# If wifi lost
			elif state in [WIFI_LOST, WIFI_CLOSE]:
				Station.stop()
				Wifi.setState(WIFI_OFF)

			# If state unchanged or wifi off
			if state == Wifi.getState() or Wifi.getState() == WIFI_OFF:
				# Exit state loop
				break

		# If the accesspoint can activate
		if state == ACCESS_POINT_FORCED and Station.isFallback():
			Wifi.context.accessPointForced = Wifi.context.pollingId + 4
			forced = True
		else:
			forced = False

		# If the accesspoint can activate
		if forced or AccessPoint.isActivated() == True:
			# If access point inactive
			if AccessPoint.isActive() == False:
				# Start the access point
				AccessPoint.start(forced)
		else:
			# If access point active
			if AccessPoint.isActive() == True:
				# In case of access point forced it is not cut immediatly
				if Wifi.context.accessPointForced <= Wifi.context.pollingId:
					# Stop the access point
					AccessPoint.stop()
