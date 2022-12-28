# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Device informations """
import sys
import time
import os
from tools import strings,filesystem,lang,date

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

def meminfo():
	""" Get memory informations """
	import gc
	try:
		# pylint: disable=no-member
		alloc = gc.mem_alloc()
		free  = gc.mem_free()
		total = alloc+free
		result = lang.memory_info%(
			strings.size_to_bytes(alloc, 1),
			strings.size_to_bytes(free,  1),
			strings.size_to_bytes(total, 1),
			100-(free*100/total))
	except:
		result = lang.no_information
	return result

def flash_size(mountpoint=None):
	""" Get flash informations """
	import uos
	if mountpoint is None:
		mountpoint = os.getcwd()
	status = uos.statvfs(mountpoint)
	if filesystem.ismicropython():
		free  = status[0]*status[3]
		if free < 0:
			free = 0
		total = status[1]*status[2]
		alloc  = total - free
	else:
		free = status.f_bavail * status.f_frsize
		total = status.f_blocks * status.f_frsize
		alloc = (status.f_blocks - status.f_bfree) * status.f_frsize
	return total, alloc, free


def flashinfo(mountpoint=None):
	""" Get flash informations """
	try:
		total, alloc, free = flash_size(mountpoint=mountpoint)
	except:
		alloc = 1
		free = 1
		total = alloc+free
	percent = 100-(free*100/total)
	total   = strings.size_to_bytes(total, 1)
	free    = strings.size_to_bytes(free,  1)
	alloc   = strings.size_to_bytes(alloc, 1)
	if mountpoint is None:
		mountpoint = b"/"
	else:
		mountpoint = strings.tobytes(mountpoint)
	result = lang.flash_info%(mountpoint, alloc, free, total, percent)
	return result

def deviceinfo():
	""" Get device informations """
	try:
		return b"%s %dMhz"%(strings.tobytes(sys.platform), machine.freq()//1000000)
	except:
		return b"Device information unavailable"

def sysinfo():
	""" Get system informations """
	try:
		result  = b"Device : %s\n"%(deviceinfo())
		result += b"Time   : %s\n"%(date.date_to_bytes())
		result += b"%s : %s\n"%(lang.memory_label, meminfo())
		result += b"%s : %s"%(lang.flash_label, flashinfo("/"))
		return result
	except Exception as err:
		return b"Sysinfo not available"

up_last=None
up_total=0

def uptime_sec():
	""" Get the uptime in seconds """
	global up_last, up_total
	try:
		# pylint: disable=no-member
		up = time.ticks_ms()//1000
	except:
		up = time.time()

	if up_last is None:
		up_last = up

	if up_last > up:
		up_total += (1<<30)//1000

	up_last = up
	up += up_total
	return up

def uptime(text=b"days"):
	""" Tell how long the system has been running """
	try:
		up = uptime_sec()
		seconds = (up)%60
		mins    = (up/60)%60
		hours   = (up/3600)%24
		days    = (up/86400)
		return b"%d %s, %d:%02d:%02d"%(days, text,hours,mins,seconds)
	except:
		return lang.no_information

_last_activity = 0
def get_last_activity():
	""" Get the last activity from user """
	# pylint:disable=global-variable-not-assigned
	global _last_activity
	return _last_activity

def set_last_activity():
	""" Set the last activity from user """
	# pylint:disable=global-variable-not-assigned
	global _last_activity
	_last_activity = uptime_sec()

_issues_counter = 0
def increase_issues_counter():
	""" Increases a issue counter, that may require a reboot if there are too many"""
	# pylint:disable=global-variable-not-assigned
	global _issues_counter
	_issues_counter += 1

def get_issues_counter():
	""" Return the value of the issues counter """
	# pylint:disable=global-variable-not-assigned
	global _issues_counter
	return _issues_counter
