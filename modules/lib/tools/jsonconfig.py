# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Functions for managing the json configuration. 
All configuration classes end the name with the word Config. 
For each of these classes, a json file with the same name is stored in the config directory of the board. """
import json
import sys
import uos
from tools import useful
import re
CONFIG_ROOT="config"

class JsonConfig:
	""" Manage json configuration """
	def __init__(self):
		""" Constructor """
		self.modificationDate = 0

	def save(self, file = None, partFilename=""):
		""" Save object in json file """
		try:
			filename = self.getPathname(useful.tofilename(partFilename))
			file, filename = self.open(file=file, readWrite="w", partFilename=partFilename)
			data = self.__dict__.copy()
			del data["modificationDate"]
			json.dump(useful.tostrings(data),file)
			file.close()
			return True
		except Exception as err:
			print("Cannot save %s (%s)"%(filename,err))
			return False

	def getPathname(self, partFilename=""):
		""" Get the configuration filename according to the class name """
		return CONFIG_ROOT+"/"+self.getFilename(partFilename) + ".json"

	def listAll(self):
		""" List all configuration files """
		result = []
		pattern = self.getFilename() + ".*"
		for fileinfo in uos.ilistdir(CONFIG_ROOT):
			name = fileinfo[0]
			typ  = fileinfo[1]
			if typ & 0xF000 != 0x4000:
				if re.match(pattern, name):
					result.append(useful.tobytes(name[len(self.getFilename()):-len(".json")]))
		return result

	def getFilename(self, partFilename=""):
		""" Return the config filename """
		if self.__class__.__name__[-len("Config"):] == "Config":
			name = self.__class__.__name__[:-len("Config")]
		else:
			name = self.__class__.__name__
		return name + useful.tostrings(partFilename)

	def open(self, file=None, readWrite="r", partFilename=""):
		""" Create or open configuration file """
		filename = file
		if useful.exists(CONFIG_ROOT) == False:
			useful.makedir(CONFIG_ROOT)
		if file == None:
			filename = self.getPathname(useful.tofilename(partFilename))
			file = open(filename, readWrite)
		elif type(file) == type(""):
			file = open(filename, readWrite)
		return file, filename

	def update(self, params):
		""" Update object with html request params """
		global self_config
		if b"name" in params and b"value" in params and len(params) == 2:
			setmany = False
			params = {params[b"name"]:params[b"value"]}
		else:
			setmany = True
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
					if setmany:
						params[name] = False
			# Case of web input is integer but string with number received
			elif type(self.__dict__[name]) == type(0) or type(self.__dict__[name]) == type(0.):
				name = useful.tobytes(name)
				if name in params:
					try:
						params[name] = int(params[name])
					except:
						params[name] = 0
		result = True
		for name, value in params.items():
			execval = useful.tostrings(name)
			try:
				try:
					exec("a = self_config.%s"%execval)
					existing = True
				except:
					existing = False

				if existing:
					execval = "self_config.%s = %s"%(execval, repr(value))
					exec(execval)
				# else:
				# 	print("%s not in object "%name)
			except Exception as err:
				print("Error on %s (%s)"%(execval, err))
				result = False
		del self_config
		return result

	def load(self, file = None, partFilename=""):
		""" Load object with the file specified """
		try:
			filename = self.getPathname(useful.tofilename(partFilename))
			file, filename = self.open(file=file, readWrite="r", partFilename=partFilename)
			self.update(useful.tobytes(json.load(file)))
			file.close()
			return True
		except Exception as err:
			print("Cannot load %s (%s)"%(filename,err))
			return False

	def forget(self, partFilename=""):
		""" Forget configuration """
		filename = self.getPathname(partFilename=partFilename)
		useful.remove(CONFIG_ROOT+"/"+filename)

	def isChanged(self, partFilename=""):
		""" Indicates if the configuration changed """
		try:
			modificationDate = uos.stat(self.getPathname(useful.tofilename(partFilename)))[8]
			if self.modificationDate != modificationDate:
				self.modificationDate = modificationDate
				return True
		except:
			pass
		return False
