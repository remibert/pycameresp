# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
# pylint: disable=redefined-builtin
""" Simulate uos module """
from os import *

def ilistdir(path_):
	""" List directory """
	result = []
	try:
		for filename in listdir(path_):
			try:
				fileinfo = stat(path_ + "/" + filename)
				typ = fileinfo[0]
				size = fileinfo[6]
				result.append((filename, typ, 0, size))
			except:
				pass
	except:
		pass
	return result

def umount(point):
	""" Unmount """

def mount(card, point):
	""" Mount """

def dupterm(param):
	""" Dup term """

def dupterm_notify(param):
	""" Dupterm notify """

def statvfs(path_):
	""" Simulate statvfs """
	import os
	try:
		return os.statvfs(path_)
	except:
		class StatVfsSimulated:
			""" StatVfsSimulated """
			def __init__(self):
				self.f_bsize = 1024
				self.f_frsize = 12
				self.f_blocks = 12333
				self.f_bfree = 1244
				self.f_bavail = 123
				self.f_files = 1234
				self.f_ffree = 123
				self.f_favail = 144
				self.f_flag = 0
				self.f_namemax = 1123
				self.f_fsid = 122
		return StatVfsSimulated()
