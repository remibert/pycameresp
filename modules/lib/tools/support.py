# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" List the supported configuration according to the hardware """

import sys

def telnet():
	""" Indicates if telnet is supported by this hardware """
	if sys.platform == "rp2":
		return False
	return True

def hostname():
	""" Indicates if hostname can be used by this hardware """
	return True

def static_ip_accesspoint():
	""" Indicates if static ip on access point can be used by this hardware """
	if sys.platform == "rp2":
		return False
	return True

def battery():
	""" Indicates if battery setup supported """
	if sys.platform == "rp2":
		return False
	return True

def counter():
	""" Indicates if hardware counter supported """
	if sys.platform == "rp2":
		return False
	return True
