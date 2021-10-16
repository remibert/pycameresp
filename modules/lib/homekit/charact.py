""" Class to manage Apple characteristics """
# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
class Charact:
	""" Class to manage Apple characteristics """
	# UUID of characteristic
	UUID_ADMINISTRATOR_ONLY_ACCESS                = "1"
	UUID_AUDIO_FEEDBACK                           = "5"
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
	UUID_INPUT_SOURCE_TYPE                        = "DB"
	UUID_INPUT_DEVICE_TYPE                        = "DC"
	UUID_CLOSED_CAPTIONS                          = "DD"
	UUID_POWER_MODE_SELECTION                     = "DF"
	UUID_CONFIGURED_NAME                          = "E3"
	UUID_IDENTIFIER                               = "E6"
	UUID_ACTIVE_IDENTIFIER                        = "E7"
	UUID_SLEEP_DISCOVERY_MODE                     = "E8"
	UUID_CURRENT_MEDIA_STATE                      = "E0"
	UUID_PICTURE_MODE                             = "E2"
	UUID_REMOTE_KEY                               = "E1"
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
	PERM_RE     = (1 << 0) | (1 << 2)
	PERM_SPECIAL_READ   = (1 << 6)

	# Unit of characteristic
	UNIT_CELSIUS    = "celsius"
	UNIT_PERCENTAGE = "percentage"
	UNIT_ARCDEGREES = "arcdegrees"
	UNIT_LUX        = "lux"
	UNIT_SECONDS    = "seconds"

	def __init__(self, uuid, typ, perms, value):
		""" Create homekit characteristic """
		import homekit_
		self.charact = homekit_.Charact(uuid, typ, perms, value)

	def __del__(self):
		""" Destructor of characteristic """
		self.charact.deinit()

	def set_unit(self, unit):
		""" Set characteristic unit """
		self.charact.set_unit(unit)

	def set_description(self, description):
		""" Set characteristic description """
		self.charact.set_description(description)

	def set_constraint(self, mini, maxi, step):
		""" Set characteristic constraints (min, max) """
		self.charact.set_constraint(mini, maxi)
		self.charact.set_step(step)

	def set_value(self, value):
		""" Set characteristic value """
		self.charact.set_value(value)

	def get_value(self):
		""" Get characteristic value """
		return self.charact.get_value()

	def set_read_callback(self, callback):
		""" Set the read callback """
		self.charact.set_read_callback(callback)

	def set_write_callback(self, callback):
		""" Set the write callback """
		self.charact.set_write_callback(callback)

def charact_int_create(uuid, perm, value):
	""" Create integer characteristic """
	return Charact(uuid, perm, Charact.TYPE_INT, value)

def charact_float_create(uuid, perm, value):
	""" Create float characteristic """
	return Charact(uuid, perm, Charact.TYPE_FLOAT, value)

def charact_uint8_create(uuid, perm, value):
	""" Create unsigned int 8 bits characteristic """
	return Charact(uuid, perm, Charact.TYPE_UINT8, value)

def charact_string_create(uuid, perm, value):
	""" Create string characteristic """
	return Charact(uuid, perm, Charact.TYPE_STRING, value)

def charact_bool_create(uuid, perm, value):
	""" Create bool characteristic """
	return Charact(uuid, perm, Charact.TYPE_BOOL, value)

def charact_uint32_create(uuid, perm, value):
	""" Create unsigned integer 32 bits characteristic """
	return Charact(uuid, perm, Charact.TYPE_UINT32, value)
