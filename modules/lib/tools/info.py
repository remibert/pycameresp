# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Device informations """
import sys
import time
from tools import strings,filesystem
try:
	import machine
except:
	pass

def temperature():
	""" Get the internal temperature in celcius and farenheit """
	try:
		import esp32
		farenheit = esp32.raw_temperature()
		celcius = (farenheit-32)/1.8
		return (celcius, farenheit)
	except:
		return (0,0)

def iscamera():
	""" Indicates if the board is esp32cam """
	try:
		import camera
		return camera.isavailable()
	except:
		if filesystem.ismicropython():
			return False
		else:
			return True

def meminfo(display=True):
	""" Get memory informations """
	import gc
	try:
		# pylint: disable=no-member
		alloc = gc.mem_alloc()
		free  = gc.mem_free()
		result = b"Mem alloc=%s free=%s total=%s"%(strings.size_to_bytes(alloc, 1), strings.size_to_bytes(free, 1), strings.size_to_bytes(alloc+free, 1))
		if display:
			print(strings.tostrings(result))
		else:
			return result
	except:
		return b"Mem unavailable"

def flashinfo(display=True):
	""" Get flash informations """
	try:
		import esp
		result = b"Flash user=%s size=%s"%(strings.size_to_bytes(esp.flash_user_start(), 1), strings.size_to_bytes(esp.flash_size(), 1))
		if display:
			print(strings.tostrings(result))
		else:
			return result
	except:
		return b"Flash unavailable"

def sysinfo(display=True, text=""):
	""" Get system informations """
	try:
		result = b"%s%s %dMhz, %s, %s, %s"%(text, sys.platform, machine.freq()//1000000, strings.date_to_bytes(), meminfo(False), flashinfo(False))
		if display:
			print(strings.tostrings(result))
		else:
			return result
	except:
		return b"Sysinfo not available"

up_last=0
up_total=0

def uptime(text="days"):
	""" Tell how long the system has been running """
	global up_last, up_total
	try:
		# pylint: disable=no-member
		up = time.ticks_ms()
	except:
		up = time.time() * 1000

	if up_last > up:
		up_total += 1^30

	up_last = up
	up += up_total

	_       = (up%1000)
	seconds = (up/1000)%60
	mins    = (up/1000/60)%60
	hours   = (up/1000/3600)%24
	days    = (up/1000/86400)
	return "%d %s, %d:%02d:%02d"%(days, strings.tostrings(text),hours,mins,seconds)
