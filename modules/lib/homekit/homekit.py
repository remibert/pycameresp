class Homekit:
	@staticmethod
	def start():
		import homekit_
		homekit_.start()

	@staticmethod
	def stop():
		import homekit_
		homekit_.stop()

	@staticmethod
	def addAccessory(accessory):
		import homekit_
		homekit_.add_accessory(accessory.accessory)

	@staticmethod
	def init():
		import homekit_
		homekit_.init()

	@staticmethod
	def deinit():
		import homekit_
		homekit_.deinit()
	
	@staticmethod
	def setSetupId(setup_id):
		import homekit_
		homekit_.set_setup_id(setup_id)

	@staticmethod
	def setSetupCode(setup_code):
		import homekit_
		homekit_.set_setup_code(setup_code)

class Accessory:
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
	def __init__(self, cid, name="Esp", manufacturer="Espressif", model="Esp32", serial_number="00112233445566", fw_rev="1.0.0", hw_rev="1.0.0", product_vers="1.0"):
		import homekit_
		self.accessory = homekit_.Accessory(cid=cid, name=name, manufacturer=manufacturer, model=model, serial_number=serial_number, fw_rev=fw_rev, hw_rev=hw_rev, product_vers=product_vers)

	def __del__(self):
		self.accessory.deinit()

	def addServer(self, server):
		"""  Add the serve to the accessory object """
		self.accessory.add_server(server.server)

	def setIdentifyCallback(self, callback):
		""" Set identify callback. In a real accessory, something like LED blink should be implemented got visual identification """
		self.accessory.set_identify_callback(callback)

	def setProductData(self, data):
		""" Set product data. 8 bytes product data assigned to the Product Plan. """
		self.accessory.set_product_data(data)

class Server:
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
	def __init__(self, serverUuid):
		import homekit_
		self.server = homekit_.Server(serverUuid)

	def __del__(self):
		self.server.deinit()

	def addCharact(self, charact):
		self.server.add_charact(charact.charact)

class Charact:
	""" Class to manage Apple characteristics """
	# UUID of characteristic
	UUID_ADMINISTRATOR_ONLY_ACCESS                = "1"
	UUID_BRIGHTNESS                               = "8"
	UUID_COOLING_THRESHOLD_TEMPERATURE            = "D"
	UUID_CURRENT_DOOR_STATE                       = "E"
	UUID_CURRENT_HEATING_COOLING_STATE            = "F"
	UUID_CURRENT_RELATIVE_HUMIDITY                = "10"
	UUID_CURRENT_TEMPERATURE                      = "11"
	UUID_FIRMWARE_REVISION                        = "52"
	UUID_HARDWARE_REVISION                        = "53"
	UUID_HEATING_THRESHOLD_TEMPERATURE            = "12"
	UUID_HUE                                      = "13"
	UUID_IDENTIFY                                 = "14"
	UUID_LOCK_CONTROL_POINT                       = "19"
	UUID_LOCK_CURRENT_STATE                       = "1D"
	UUID_LOCK_LAST_KNOWN_ACTION                   = "1C"
	UUID_LOCK_MANAGEMENT_AUTO_SECURITY_TIMEOUT    = "1A"
	UUID_LOCK_TARGET_STATE                        = "1E"
	UUID_LOGS                                     = "1F"
	UUID_MANUFACTURER                             = "20"
	UUID_MODEL                                    = "21"
	UUID_MOTION_DETECTED                          = "22"
	UUID_NAME                                     = "23"
	UUID_OBSTRUCTION_DETECTED                     = "24"
	UUID_ON                                       = "25"
	UUID_OUTLET_IN_USE                            = "26"
	UUID_ROTATION_DIRECTION                       = "28"
	UUID_ROTATION_SPEED                           = "29"
	UUID_SATURATION                               = "2F"
	UUID_SERIAL_NUMBER                            = "30"
	UUID_TARGET_DOOR_STATE                        = "32"
	UUID_TARGET_HEATING_COOLING_STATE             = "33"
	UUID_TARGET_RELATIVE_HUMIDITY                 = "34"
	UUID_TARGET_TEMPERATURE                       = "35"
	UUID_TEMPERATURE_DISPLAY_UNITS                = "36"
	UUID_VERSION                                  = "37"
	UUID_AIR_PARTICULATE_DENSITY                  = "64"
	UUID_AIR_PARTICULATE_SIZE                     = "65"
	UUID_SECURITY_SYSTEM_CURRENT_STATE            = "66"
	UUID_SECURITY_SYSTEM_TARGET_STATE             = "67"
	UUID_BATTERY_LEVEL                            = "68"
	UUID_CARBON_MONOXIDE_DETECTED                 = "69"
	UUID_CONTACT_SENSOR_STATE                     = "6A"
	UUID_CURRENT_AMBIENT_LIGHT_LEVEL              = "6B"
	UUID_CURRENT_HORIZONTAL_TILT_ANGLE            = "6C"
	UUID_CURRENT_POSITION                         = "6D"
	UUID_CURRENT_VERTICAL_TILT_ANGLE              = "6E"
	UUID_HOLD_POSITION                            = "6F"
	UUID_LEAK_DETECTED                            = "70"
	UUID_OCCUPANCY_DETECTED                       = "71"
	UUID_POSITION_STATE                           = "72"
	UUID_PROGRAMMABLE_SWITCH_EVENT                = "73"
	UUID_STATUS_ACTIVE                            = "75"
	UUID_SMOKE_DETECTED                           = "76"
	UUID_STATUS_FAULT                             = "77"
	UUID_STATUS_JAMMED                            = "78"
	UUID_STATUS_LOW_BATTERY                       = "79"
	UUID_STATUS_TAMPERED                          = "7A"
	UUID_TARGET_HORIZONTAL_TILT_ANGLE             = "7B"
	UUID_TARGET_POSITION                          = "7C"
	UUID_TARGET_VERTICAL_TILT_ANGLE               = "7D"
	UUID_STATUS_SECURITY_SYSTEM_ALARM_TYPE        = "8E"
	UUID_CHARGING_STATE                           = "8F"
	UUID_CARBON_MONOXIDE_LEVEL                    = "90"
	UUID_CARBON_MONOXIDE_PEAK_LEVEL               = "91"
	UUID_CARBON_DIOXIDE_DETECTED                  = "92"
	UUID_CARBON_DIOXIDE_LEVEL                     = "93"
	UUID_CARBON_DIOXIDE_PEAK_LEVEL                = "94"
	UUID_AIR_QUALITY                              = "95"
	UUID_ACCESSORY_FLAGS                          = "A6"
	UUID_LOCK_PHYSICAL_CONTROLS                   = "A7"
	UUID_CURRENT_AIR_PURIFIER_STATE               = "A9"
	UUID_CURRENT_SLAT_STATE                       = "AA"
	UUID_SLAT_TYPE                                = "C0"
	UUID_FILTER_LIFE_LEVEL                        = "AB"
	UUID_FILTER_CHANGE_INDICATION                 = "AC"
	UUID_RESET_FILTER_INDICATION                  = "AD"
	UUID_TARGET_AIR_PURIFIER_STATE                = "A8"
	UUID_TARGET_FAN_STATE                         = "BF"
	UUID_CURRENT_FAN_STATE                        = "AF"
	UUID_ACTIVE                                   = "B0"
	UUID_SWING_MODE                               = "B6"
	UUID_CURRENT_TILT_ANGLE                       = "C1"
	UUID_TARGET_TILT_ANGLE                        = "C2"
	UUID_OZONE_DENSITY                            = "C3"
	UUID_NITROGEN_DIOXIDE_DENSITY                 = "C4"
	UUID_SULPHUR_DIOXIDE_DENSITY                  = "C5"
	UUID_PM_2_5_DENSITY                           = "C6"
	UUID_PM_10_DENSITY                            = "C7"
	UUID_VOC_DENSITY                              = "C8"
	UUID_SERVICE_LABEL_INDEX                      = "CB"
	UUID_SERVICE_LABEL_NAMESPACE                  = "CD"
	UUID_COLOR_TEMPERATURE                        = "CE"
	UUID_CURRENT_HEATER_COOLER_STATE              = "B1"
	UUID_TARGET_HEATER_COOLER_STATE               = "B2"
	UUID_CURRENT_HUMIDIFIER_DEHUMIDIFIER_STATE    = "B3"
	UUID_TARGET_HUMIDIFIER_DEHUMIDIFIER_STATE     = "B4"
	UUID_WATER_LEVEL                              = "B5"
	UUID_RELATIVE_HUMIDITY_DEHUMIDIFIER_THRESHOLD = "C9"
	UUID_RELATIVE_HUMIDITY_HUMIDIFIER_THRESHOLD   = "CA"
	UUID_PROGRAM_MODE                             = "D1"
	UUID_IN_USE                                   = "D2"
	UUID_SET_DURATION                             = "D3"
	UUID_REMAINING_DURATION                       = "D4"
	UUID_VALVE_TYPE                               = "D5"
	UUID_IS_CONFIGURED                            = "D6"
	UUID_PRODUCT_DATA                             = "220"
	
	# Type of characteristic
	TYPE_INT    = 0
	TYPE_BOOL   = 1
	TYPE_FLOAT  = 2
	TYPE_UINT32 = 3
	TYPE_STRING = 4
	TYPE_UINT8  = 5

	# Permissions of characteristic
	PERM_READ   = (1 << 0)
	PERM_WRITE  = (1 << 1)
	PERM_EVENT  = (1 << 2)
	PERM_RWE    = (1 << 0) | (1 << 1) | (1 << 2)
	
	# Unit of characteristic
	UNIT_CELSIUS    = "celsius"
	UNIT_PERCENTAGE = "percentage"
	UNIT_ARCDEGREES = "arcdegrees"
	UNIT_LUX        = "lux"
	UNIT_SECONDS    = "seconds"

	def __init__(self, uuid, typ, perm, value):
		""" Create homekit characteristic """
		import homekit_
		self.charact = homekit_.Charact(uuid, typ, perm, value)

	def __del__(self):
		""" Destructor of characteristic """
		self.charact.deinit()

	def setUnit(self, unit):
		""" Set characteristic unit """
		self.charact.set_unit(unit)

	def setDescription(self, description):
		""" Set characteristic description """
		self.charact.set_description(description)

	def setConstraints(self, mini, maxi):
		""" Set characteristic constraints (min, max) """
		self.charact.set_constraints(mini, maxi)

	def setValue(self, value):
		""" Set characteristic value """
		self.charact.set_value(value)

	def getValue(self):
		""" Get characteristic value """
		return self.charact.get_value()
	
	def setStep(self, step):
		""" Set characteristic step """
		self.charact.set_step(step)

	def setReadCallback(self, callback):
		""" Set the read callback """
		self.charact.set_read_callback(callback)

	def setWriteCallback(self, callback):
		""" Set the write callback """
		self.charact.set_write_callback(callback)
