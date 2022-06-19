# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
import sys

try:
	from PyQt6.QtCore import QSettings
except:
	from PyQt5.QtCore import QSettings


# Settings
SETTINGS_FILENAME  = "CamFlasher.ini"
FONT_FAMILY        = "camflasher.font.family"
FONT_SIZE          = "camflasher.font.size"
WORKING_DIRECTORY  = "camflasher.working_directory"
WIN_GEOMETRY       = "camflasher.window.geometry"
FIRMWARE_FILENAMES = "camflasher.firmware.filenames"
TELNET_HOSTS       = "camflasher.telnet.host"
DEVICE_RTS_DTR     = "camflasher.device.rts_dtr"
FIELD_COLORS       = "camflasher.colors"
TYPE_LINK          = "camflasher.link.type"

def get_settings():
	""" Return the QSettings class according to the os """
	if sys.platform == "darwin":
		result = QSettings()
	elif sys.platform == "win32":
		if uname() == "7":
			result = QSettings(SETTINGS_FILENAME, QSettings.IniFormat)
		else:
			result = QSettings(SETTINGS_FILENAME)
	else:
		result = QSettings()
	return result