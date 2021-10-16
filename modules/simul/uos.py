# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# pylint: disable=redefined-builtin
""" Simulate uos module """
from os import *

def ilistdir(path_):
	""" List directory """
	result = []
	for filename in listdir(path_):
		fileinfo = stat(path_ + "/" + filename)
		typ = fileinfo[0]
		size = fileinfo[6]

		result.append((filename, typ, 0, size))
	return result

def umount(point):
	""" Unmount """

def mount(card, point):
	""" Mount """

def dupterm(param):
	""" Dup term """

def dupterm_notify(param):
	""" Dupterm notify """
