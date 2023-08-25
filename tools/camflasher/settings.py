""" Settings for camflasher """
# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
import sys
import platform
from PyQt6.QtCore import QSettings

# Settings
SETTINGS_FILENAME  = "CamFlasher.ini"
FONT_FAMILY        = "camflasher.font.family"
FONT_SIZE          = "camflasher.font.size"
WORKING_DIRECTORY  = "camflasher.working_directory"
WIN_GEOMETRY       = "camflasher.window.geometry"
TELNET_HOSTS       = "camflasher.telnet.host"
DEVICE_RTS_DTR     = "camflasher.device.rts_dtr"
DEVICE_CONFIGURE   = "camflasher.device.configure"
FIELD_COLORS       = "camflasher.colors"
TYPE_LINK          = "camflasher.link.type"

FIRMWARE_1_FILENAME = "camflasher.flash.firmware_1"
FIRMWARE_2_FILENAME = "camflasher.flash.firmware_2"
FIRMWARE_3_FILENAME = "camflasher.flash.firmware_3"

FIRMWARE_1_ADDRESS  = "camflasher.flash.adress_1"
FIRMWARE_2_ADDRESS  = "camflasher.flash.adress_2"
FIRMWARE_3_ADDRESS  = "camflasher.flash.adress_3"

FLASH_OPTIONS       = "camflasher.flash.options"

def get_settings():
	""" Return the QSettings class according to the os """
	if sys.platform == "darwin":
		result = QSettings()
	elif sys.platform == "win32":
		if platform.uname() == "7":
			result = QSettings(SETTINGS_FILENAME, QSettings.IniFormat)
		else:
			result = QSettings(SETTINGS_FILENAME)
	else:
		result = QSettings()
	return result
