# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# pylint:disable=consider-using-f-string

""" Manages access to wifi, treats cases of network loss with retry, and manages a fallback on the access point if no network is available """
from wifi.accesspoint import *
from wifi.station import *
from tools import info

WIFI_OFF             = 0
WIFI_OTHER_NETWORK   = 1
WIFI_CONNECTED       = 2
LAN_CONNECTED        = 3
WAN_CONNECTED        = 4
ACCESS_POINT_STARTED = 5
WIFI_LOST            = 6
WIFI_CLOSE           = 7

MAX_PROBLEM = 5

class WifiContext:
	""" Wifi context """
	def __init__(self):
		""" Constructor """
		self.lan_problem    = 0
		self.wan_problem    = 0
		self.dns = ""
		self.state = WIFI_OFF

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
			if state == WIFI_OFF            : logger.syslog("Wifi off")
			if state == WIFI_OTHER_NETWORK  : logger.syslog("Wifi select other network")
			if state == WIFI_CONNECTED      : logger.syslog("Wifi connected")
			if state == LAN_CONNECTED       : logger.syslog("Wifi LAN connected")
			if state == WAN_CONNECTED       : logger.syslog("Wifi WAN connected")
			if state == ACCESS_POINT_STARTED: logger.syslog("Wifi access point started")
			if state == WIFI_LOST           : logger.syslog("Wifi lost connection")
			if state == WIFI_CLOSE          : logger.syslog("Wifi closed")
		Wifi.context.state = state

	@staticmethod
	def is_lan_connected():
		""" Indicates if wifi network available for start server """
		if Wifi.get_state() in [WIFI_CONNECTED, LAN_CONNECTED, WAN_CONNECTED, ACCESS_POINT_STARTED]:
			return True
		elif AccessPoint.is_active() is True:
			return True
		return False

	@staticmethod
	def wan_connected():
		""" Set wan have establish dialog with external server """
		Wifi.lan_connected(False)
		if Wifi.context.wan_problem > 0:
			logger.syslog("WAN connected")
			Wifi.context.wan_problem = 0
		if Wifi.get_state() in [WIFI_CONNECTED, LAN_CONNECTED]:
			Wifi.set_state(WAN_CONNECTED)

	@staticmethod
	def wan_disconnected():
		""" Indicates that wan have probably a problem """
		if Wifi.get_state() in [WIFI_CONNECTED, LAN_CONNECTED, WAN_CONNECTED ]:
			Wifi.context.wan_problem += 1
			logger.syslog("WAN problem %d detected (max=%d) (wifi=%s)"%(Wifi.context.wan_problem,MAX_PROBLEM, strings.tostrings(Station.get_signal_strength_bytes())))

	@staticmethod
	def lan_connected(changeState=True):
		""" Indicates that lan connection detected """
		if Wifi.context.lan_problem > 0:
			logger.syslog("LAN connected")
			Wifi.context.lan_problem = 0
		if changeState:
			if Wifi.get_state() == WIFI_CONNECTED:
				Wifi.set_state(LAN_CONNECTED)

	@staticmethod
	def lan_disconnected():
		""" Indicates that lan disconnection detected """
		if Wifi.get_state() in [WIFI_CONNECTED, LAN_CONNECTED, WAN_CONNECTED ]:
			Wifi.context.lan_problem += 1
			logger.syslog("LAN problem %d detected (max=%d)(wifi=%s)"%(Wifi.context.lan_problem, MAX_PROBLEM, strings.tostrings(Station.get_signal_strength_bytes())))

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
		while 1:
			state = Wifi.get_state()

			# If the wifi not started
			if state == WIFI_OFF:
				Wifi.context.dns = ""

				# If wifi station available
				if Station.is_activated():
					AccessPoint.stop()

					# If wifi station connected
					if await Station.start():
						Wifi.set_state(WIFI_CONNECTED)
					else:
						Wifi.set_state(WIFI_OTHER_NETWORK)
						info.increase_issues_counter()
				# If access point available
				elif AccessPoint.is_activated():
					Wifi.set_state(ACCESS_POINT_STARTED)

			# If the network not reached select other network
			elif state == WIFI_OTHER_NETWORK:
				# If station available
				if Station.is_activated():
					if await Station.choose_network(max_retry=15) is True:
						Wifi.set_state(WIFI_CONNECTED)
					else:
						# Wifi connection failed
						if Station.is_fallback():
							Wifi.set_state(ACCESS_POINT_STARTED)
						else:
							Wifi.set_state(WIFI_CLOSE)
				else:
					Wifi.set_state(WIFI_CLOSE)

			# Start access point if no wifi station detected
			elif state == ACCESS_POINT_STARTED:
				# If access point inactive
				if AccessPoint.is_active() is False:
					# Stop wifi station to avoid some problems
					Station.stop()

					# Start the access point
					AccessPoint.start(Station.is_fallback())
				else:
					# If no activity detected on access point
					if (info.uptime_sec() - info.get_last_activity()) > 3*60:
						# Retry to search network
						if Station.is_activated():
							Wifi.set_state(WIFI_CLOSE)

			# If the wan reponding
			elif state in [WAN_CONNECTED, LAN_CONNECTED, WIFI_CONNECTED]:
				# If connection start
				if state == WIFI_CONNECTED and Wifi.context.dns == "":
					# Initialize context
					Wifi.context.dns = Station.get_info()[3]
					Wifi.context.lan_problem = 0
					Wifi.context.wan_problem = 0

				# If station yet activated
				if Station.is_activated():
					# If too many problem detected
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
