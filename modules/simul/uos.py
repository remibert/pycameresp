# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET 
# pylint: disable=redefined-builtin
from os import *

def ilistdir(path_):
	result = []
	for filename in listdir(path_):
		fileinfo = stat(path_ + "/" + filename)
		typ = fileinfo[0]
		size = fileinfo[6]
		
		result.append((filename, typ, 0, size))
	return result

def umount(point):
	pass

def mount(card, point):
	pass

def dupterm(param):
	pass

def dupterm_notify(param):
	pass