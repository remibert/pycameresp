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
		self.lan_problem    = 0
		self.wan_problem    = 0
		self.dns = ""
		self.state = WIFI_OFF
		self.polling_id = 0
		self.access_point_forced = 0


class Wifi:
	""" Class to manage the wifi station and access point """
	context = WifiContext()

	@staticmethod
	def get_dns():
		""" Return the ip address of dns or empty string """
		return Wifi.context.dns

	@staticmethod
	def get_state():
		""" Return the state of wifi """
		return Wifi.context.state

	@staticmethod
	def set_state(state):
		""" Set the state of wifi """
		# pylint:disable=multiple-statements
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
	def is_lan_connected():
		""" Indicates if wifi network available for start server """
		if Wifi.get_state() in [WIFI_CONNECTED, LAN_CONNECTED, WAN_CONNECTED, ACCESS_POINT_FORCED]:
			return True
		elif AccessPoint.is_active() is True:
			return True
		return False

	@staticmethod
	def wan_connected():
		""" Set wan have establish dialog with external server """
		Wifi.lan_connected(False)
		if Wifi.context.wan_problem > 0:
			useful.syslog("Wan connected")
			Wifi.context.wan_problem = 0
		if Wifi.get_state() in [WIFI_CONNECTED, LAN_CONNECTED]:
			Wifi.set_state(WAN_CONNECTED)

	@staticmethod
	def wan_disconnected():
		""" Indicates that wan have probably a problem """
		if Wifi.get_state() in [WIFI_CONNECTED, LAN_CONNECTED, WAN_CONNECTED ]:
			Wifi.context.wan_problem += 1
			useful.syslog("Wan problem %d detected"%Wifi.context.wan_problem)

	@staticmethod
	def lan_connected(changeState=True):
		""" Indicates that lan connection detected """
		if Wifi.context.lan_problem > 0:
			useful.syslog("Lan connected")
			Wifi.context.lan_problem = 0
		if changeState:
			if Wifi.get_state() == WIFI_CONNECTED:
				Wifi.set_state(LAN_CONNECTED)

	@staticmethod
	def lan_disconnected():
		""" Indicates that lan disconnection detected """
		if Wifi.get_state() in [WIFI_CONNECTED, LAN_CONNECTED, WAN_CONNECTED ]:
			Wifi.context.lan_problem += 1
			useful.syslog("Lan problem %d detected"%Wifi.context.lan_problem)

	@staticmethod
	def is_wan_available():
		""" Indicates if wan is connected or established """
		if Wifi.get_state() in [WIFI_CONNECTED, LAN_CONNECTED, WAN_CONNECTED]:
			return True
		return False

	@staticmethod
	def is_lan_available():
		""" Indicates if lan is connected """
		if Wifi.get_state() in [WIFI_CONNECTED, LAN_CONNECTED, WAN_CONNECTED]:
			if Wifi.context.lan_problem < MAX_PROBLEM:
				return True
		return False

	@staticmethod
	def is_wan_connected():
		""" Indicates that wan communication done with success """
		return Wifi.get_state() == WAN_CONNECTED

	@staticmethod
	async def manage():
		""" Manage the wifi """
		Wifi.context.polling_id += 1
		while 1:
			state = Wifi.get_state()

			# If the wifi not started
			if state == WIFI_OFF:
				Wifi.context.dns = ""
				Wifi.context.lan_problem = 0
				Wifi.context.wan_problem = 0
				if Station.is_activated():
					# If wifi station connected
					if await Station.start():
						Wifi.context.dns = Station.get_info()[3]
						Wifi.set_state(WIFI_CONNECTED)
					else:
						Wifi.set_state(WIFI_OTHER_NETWORK)

			# If the network not reached select other network
			elif state in [WIFI_OTHER_NETWORK, ACCESS_POINT_FORCED]:
				if Station.is_activated():
					Station.stop()
					if await Station.choose_network(maxRetry=5) is True:
						Wifi.context.dns = Station.get_info()[3]
						Wifi.context.lan_problem = 0
						Wifi.context.wan_problem = 0
						Wifi.set_state(WIFI_CONNECTED)
					else:
						# Wifi connection failed
						if Station.is_fallback():
							Wifi.set_state(ACCESS_POINT_FORCED)
						else:
							Wifi.set_state(WIFI_CLOSE)
				else:
					Wifi.set_state(WIFI_CLOSE)

			# If the wan reponding
			elif state in [WAN_CONNECTED, LAN_CONNECTED, WIFI_CONNECTED]:
				if Station.is_activated():
					# If many problem notified
					if Wifi.context.lan_problem >= MAX_PROBLEM or Wifi.context.wan_problem >= MAX_PROBLEM:
						Wifi.set_state(WIFI_LOST)
				else:
					Wifi.set_state(WIFI_CLOSE)

			# If wifi lost
			elif state in [WIFI_LOST, WIFI_CLOSE]:
				Station.stop()
				Wifi.set_state(WIFI_OFF)

			# If state unchanged or wifi off
			if state == Wifi.get_state() or Wifi.get_state() == WIFI_OFF:
				# Exit state loop
				break

		# If the accesspoint can activate
		if state == ACCESS_POINT_FORCED and Station.is_fallback():
			Wifi.context.access_point_forced = Wifi.context.polling_id + 4
			forced = True
		else:
			forced = False

		# If the accesspoint can activate
		if forced or AccessPoint.is_activated() is True:
			# If access point inactive
			if AccessPoint.is_active() is False:
				# Start the access point
				AccessPoint.start(forced)
		else:
			# If access point active
			if AccessPoint.is_active() is True:
				# In case of access point forced it is not cut immediatly
				if Wifi.context.access_point_forced <= Wifi.context.polling_id:
					# Stop the access point
					AccessPoint.stop()
