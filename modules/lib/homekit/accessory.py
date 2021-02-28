# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
from homekit.server import *

class Accessory:
	""" Homekit accessory class """
	CID_NONE                = 0
	CID_OTHER               = 1
	CID_BRIDGE              = 2
	CID_FAN                 = 3
	CID_GARAGE_DOOR_OPENER  = 4
	CID_LIGHTING            = 5
	CID_LOCK                = 6
	CID_OUTLET              = 7
	CID_SWITCH              = 8
	CID_THERMOSTAT          = 9
	CID_SENSOR              = 10
	CID_SECURITY_SYSTEM     = 11
	CID_DOOR                = 12
	CID_WINDOW              = 13
	CID_WINDOW_COVERING     = 14
	CID_PROGRAMMABLE_SWITCH = 15
	CID_RESERVED            = 16
	CID_IP_CAMERA           = 17
	CID_VIDEO_DOORBELL      = 18
	CID_AIR_PURIFIER        = 19
	CID_HEATER              = 20
	CID_AIR_CONDITIONER     = 21
	CID_HUMIDIFIER          = 22
	CID_DEHUMIDIFIER        = 23
	def __init__(self, cid, **kwargs):
		""" Create accessory. 
			Parameters : name(string), manufacturer(string), model(string), serialNumber(string), firmwareRevision(string), hardwareRevision(string), productVersion(string), productData (string with 8 bytes required)"""
		import homekit_
		self.accessory = homekit_.Accessory(\
			cid              = cid, \
			name             = kwargs.get("name"            , "NoName"), \
			manufacturer     = kwargs.get("manufacturer"    , "Manufacturer"), \
			model            = kwargs.get("model"           , "ESP32"), \
			serialNumber     = kwargs.get("serialNumber"    , "0000000000"), \
			firmwareRevision = kwargs.get("firmwareRevision", "1.0"), \
			hardwareRevision = kwargs.get("hardwareRevision", "1.0"), \
			productVersion   = kwargs.get("productVersion"  , "1.0"))
		self.accessory.setProductData(kwargs.get("productData","01234568"))

	def __del__(self):
		""" Destroy homekit accessory """
		self.accessory.deinit()

	def addServer(self, server):
		"""  Add the serve to the accessory object """
		self.accessory.addServer(server.server)

	def setIdentifyCallback(self, callback):
		""" Set identify callback. In a real accessory, something like LED blink should be implemented got visual identification """
		self.accessory.setIdentifyCallback(callback)

	def setProductData(self, data):
		""" Set product data. 8 bytes product data assigned to the Product Plan. """
		self.accessory.setProductData(data)


