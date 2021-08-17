# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Functions for managing the json configuration. 
All configuration classes end the name with the word Config. 
For each of these classes, a json file with the same name is stored in the config directory of the board. """
import json
import uos
from tools import useful
import re

self_config = None
class JsonConfig:
	""" Manage json configuration """
	def __init__(self):
		""" Constructor """
		self.modificationDate = 0

	def configRoot(self):
		""" Configuration root path """
		if useful.ismicropython():
			return "/config"
		else:
			return "config"

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
			useful.exception(err, "Cannot save %s "%(filename))
			return False

	def toString(self):
		""" Convert the configuration to string """
		data = self.__dict__.copy()
		del data["modificationDate"]
		return json.dumps(useful.tostrings(data))

	def getPathname(self, partFilename=""):
		""" Get the configuration filename according to the class name """
		return self.configRoot()+"/"+self.getFilename(partFilename) + ".json"

	def listAll(self):
		""" List all configuration files """
		result = []
		pattern = self.getFilename() + ".*"
		for fileinfo in uos.ilistdir(self.configRoot()):
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
		if useful.exists(self.configRoot()) == False:
			useful.makedir(self.configRoot())
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
					# pylint: disable=exec-used
					exec("a = self_config.%s"%execval)
					existing = True
				except:
					existing = False

				if existing:
					execval = "self_config.%s = %s"%(execval, repr(value))
					# pylint: disable=exec-used
					exec(execval)
				else:
					if name != b"action":
						print("%s.%s not existing"%(self.__class__.__name__, useful.tostrings(name)))
			except Exception as err:
				useful.exception(err, "Error on %s"%(execval))
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
		except OSError as err:
			if err.args[0] == 2:
				useful.logError("Not existing %s "%(filename))
			else:
				useful.exception(err, "Cannot load %s "%(filename))
			return False
		except Exception as err:
			useful.exception(err, "Cannot load %s "%(filename))
			return False

	def forget(self, partFilename=""):
		""" Forget configuration """
		filename = self.getPathname(partFilename=partFilename)
		useful.remove(self.configRoot()+"/"+filename)

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
