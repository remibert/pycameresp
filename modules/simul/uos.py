# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET 
from os import *

def ilistdir(path):
	result = []
	for filename in listdir(path):
		fileinfo = stat(path + "/" + filename)
		typ = fileinfo[0]
		size = fileinfo[6]
		
		result.append((filename, typ, 0, size))
	return result