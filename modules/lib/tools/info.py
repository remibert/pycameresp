# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Device informations """
import sys
import time
import os
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
		total = alloc+free
		result = b"Memory : alloc=%s free=%s total=%s used=%-3.2f%%"%(
			strings.size_to_bytes(alloc, 1),
			strings.size_to_bytes(free,  1),
			strings.size_to_bytes(total, 1),
			100-(free*100/total))
		if display:
			print(strings.tostrings(result))
		else:
			return result
	except:
		return b"Mem unavailable"

def flashinfo(mountpoint=None, display=True):
	""" Get flash informations """
	try:
		import uos
		if mountpoint is None:
			mountpoint = os.getcwd()
		status = uos.statvfs(mountpoint)
		free  = status[0]*status[3]
		if free < 0:
			free = 0
		total = status[1]*status[2]
		alloc  = total - free
		result = b"Disk %s : alloc=%s free=%s total=%s used=%-3.2f%%"%(strings.tobytes(mountpoint),
			strings.size_to_string(alloc, 1),
			strings.size_to_string(free,  1),
			strings.size_to_string(total, 1),
			100-(free*100/total))
		if display:
			print(strings.tostrings(result))
		else:
			return result
	except:
		return b"Flash unavailable"

def sysinfo(display=True, text=""):
	""" Get system informations """
	try:
		result = b"Device : %s%s %dMhz\nTime   : %s\n%s\n%s"%(text, sys.platform, machine.freq()//1000000, strings.date_to_bytes(), meminfo(False), flashinfo("/",False))
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
