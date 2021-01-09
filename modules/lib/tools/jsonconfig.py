# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Functions for managing the json configuration. 
All configuration classes end the name with the word Config. 
For each of these classes, a json file with the same name is stored in the config directory of the board. """
import json
import sys
from tools import useful
CONFIG_ROOT="config"

def save(self, file = None):
	""" Save object in json file """
	filename = file
	try:
		if useful.exists(CONFIG_ROOT) == False:
			useful.makedir(CONFIG_ROOT)
		if file == None:
			filename = self.__class__.__name__ + ".json"
			file = open(CONFIG_ROOT+"/"+filename, "w")
		elif type(file) == type(""):
			file = open(CONFIG_ROOT+"/"+filename, "w")
		json.dump(useful.tostrings(self.__dict__),file)
		file.close()
		return True
	except Exception as err:
		print("Cannot save %s (%s)"%(filename,err))
		return False

def update(self, params):
	""" Update object with params """
	global self_config
	self_config = self
	for name in self.__dict__.keys():
		# Case of web input is missing when bool is false
		if type(self.__dict__[name]) == type(True):
			name = useful.tobytes(name)
			if name in params:
				if type(params[name]) == type(""):
					if params[name] == "":
						params[name] = True
					elif params[name] == "1" or params[name].lower() == "true":
						params[name] = True
					elif params[name] == "0" or params[name].lower() == "false":
						params[name] = False
				elif type(params[name]) == type(b""):
					if params[name] == b"":
						params[name] = True
					elif params[name] == b"1" or params[name].lower() == b"true":
						params[name] = True
					elif params[name] == b"0" or params[name].lower() == b"false":
						params[name] = False
			else:
				params[name] = False
		# Case of web input is integer but string with number received
		elif type(self.__dict__[name]) == type(0) or type(self.__dict__[name]) == type(0.):
			name = useful.tobytes(name)
			if name in params:
				try:
					params[name] = int(params[name])
				except:
					params[name] = 0

	for name, value in params.items():
		execval = name
		try:
			execval = "self_config.%s = %s"%((useful.tostrings(name)), repr(value))
			exec(execval)
		except Exception as err:
			print("Error on %s (%s)"%(execval, err))
	del self_config

def load(self, file = None):
	""" Load object with the file specified """
	filename = file
	try:
		if useful.exists(CONFIG_ROOT) == False:
			useful.makedir(CONFIG_ROOT)
		if file == None:
			filename = self.__class__.__name__ + ".json"
			file = open(CONFIG_ROOT+"/"+filename)
		elif type(file) == type(""):
			file = open(CONFIG_ROOT+"/"+filename)
		self.update(useful.tobytes(json.load(file)))
		file.close()
		return True
	except Exception as err:
		print("Cannot load %s (%s)"%(filename,err))
		return False
