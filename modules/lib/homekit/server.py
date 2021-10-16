""" Create homekit server """
# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
from homekit.charact   import *
class Server:
	""" Create homekit server """
	UUID_ACCESSORY_INFORMATION        = "3E"
	UUID_PROTOCOL_INFORMATION         = "A2"
	UUID_FAN                          = "40"
	UUID_GARAGE_DOOR_OPENER           = "41"
	UUID_LIGHTBULB                    = "43"
	UUID_LOCK_MANAGEMENT              = "44"
	UUID_LOCK_MECHANISM               = "45"
	UUID_SWITCH                       = "49"
	UUID_OUTLET                       = "47"
	UUID_THERMOSTAT                   = "4A"
	UUID_AIR_QUALITY_SENSOR           = "8D"
	UUID_SECURITY_SYSTEM              = "7E"
	UUID_CARBON_MONOXIDE_SENSOR       = "7F"
	UUID_CONTACT_SENSOR               = "80"
	UUID_DOOR                         = "81"
	UUID_HUMIDITY_SENSOR              = "82"
	UUID_LEAK_SENSOR                  = "83"
	UUID_LIGHT_SENSOR                 = "84"
	UUID_MOTION_SENSOR                = "85"
	UUID_OCCUPANCY_SENSOR             = "86"
	UUID_SMOKE_SENSOR                 = "87"
	UUID_STATLESS_PROGRAMMABLE_SWITCH = "89"
	UUID_TEMPERATURE_SENSOR           = "8A"
	UUID_WINDOW                       = "8B"
	UUID_WINDOW_COVERING              = "8C"
	UUID_BATTERY_SERVICE              = "96"
	UUID_CARBON_DIOXIDE_SENSOR        = "97"
	UUID_FAN_V2                       = "B7"
	UUID_SLAT                         = "B9"
	UUID_FILTER_MAINTENANCE           = "BA"
	UUID_AIR_PURIFIER                 = "BB"
	UUID_HEATER_COOLER                = "BC"
	UUID_HUMIDIFIER_DEHUMIDIFIER      = "BD"
	UUID_SERVICE_LABEL                = "CC"
	UUID_IRRIGATION_SYSTEM            = "CF"
	UUID_VALVE                        = "D0"
	UUID_FAUCET                       = "D7"
	UUID_TELEVISION                   = "D8"
	UUID_INPUT_SOURCE                 = "D9"
	def __init__(self, name, server_uuid):
		""" Constructor homekit server """
		import homekit_
		self.server = homekit_.Server(server_uuid)
		self.name = Charact(Charact.UUID_NAME, Charact.PERM_READ, Charact.TYPE_STRING, name)
		self.add_charact(self.name)

	def __del__(self):
		""" Destructor homekit server """
		self.server.deinit()

	def add_charact(self, charact):
		""" Add characteristic to this homekit server """
		self.server.add_charact(charact.charact)
