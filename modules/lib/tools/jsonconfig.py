# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Functions for managing the json configuration.
All configuration classes end the name with the word Config.
For each of these classes, a json file with the same name is stored in the config directory of the board. """
# pylint:disable=consider-using-dict-items
# pylint:disable=consider-iterating-dictionary
import time
import json
import re
try:
	import uos
except:
	import os as uos
import tools.logger
import tools.strings
import tools.filesystem
import tools.date


jsonconfig_self  = None
jsonconfig_value = None

class JsonConfig:
	""" Manage json configuration """
	classes = set()
	def __init__(self):
		""" Constructor """
		self.modification_date = 0
		self.last_refresh = 0
		JsonConfig.classes.add(self.__class__)

	def config_root(self):
		""" Configuration root path """
		if tools.filesystem.ismicropython():
			return "/config"
		else:
			return uos.path.expanduser('~') + "/.pycameresp"

	def purify(self, datas):
		""" Remove unwanted items """
		result = datas
		if type(datas) == type(b""):
			result = datas
		elif type(datas) == type([]):
			result = []
			for item in datas:
				result.append(self.purify(item))
		elif type(datas) == type((0,0)):
			result = []
			for item in datas:
				result.append(self.purify(item))
			result = tuple(result)
		elif type(datas) == type({}):
			result = {}
			for key, value in datas.items():
				if key not in ["last_refresh","modification_date"]:
					result[key] = self.purify(value)
		elif isinstance(datas, JsonConfig):
			result = self.purify(datas.__dict__.copy())
			result["__class__"] = datas.__class__.__name__
		return result

	def save(self, file=None, part_filename=""):
		""" Save object in json file """
		try:
			filename = self.get_pathname(tools.strings.tofilename(part_filename))
			str_data = self.to_string()

			file, filename = self.open(file=file, read_write="w", part_filename=part_filename)
			file.write(str_data)
			file.close()

			self.modification_date = uos.stat(filename)[8]
			self.last_refresh = time.time()
			return True
		except Exception as _err:
			str_data = self.to_string()
			tools.logger.syslog(_err, "Cannot save %s "%(filename))
			return False

	def to_string(self):
		""" Convert the configuration to string """
		return json.dumps(self.to_dict(),separators=(',', ':'))

	def to_dict(self):
		""" Convert the configuration to dictionnary """
		return tools.strings.tostrings(self.purify(self.__dict__.copy()))

	def get_pathname(self, part_filename=""):
		""" Get the configuration filename according to the class name """
		return self.config_root()+"/"+self.get_filename(part_filename) + ".json"

	def list_all(self):
		""" List all configuration files """
		result = []
		pattern = self.get_filename() + ".*"
		for fileinfo in tools.filesystem.list_directory(self.config_root()):
			name = fileinfo[0]
			typ  = fileinfo[1]
			if typ & 0xF000 != 0x4000:
				if re.match(pattern, name):
					result.append(tools.strings.tobytes(name[len(self.get_filename()):-len(".json")]))
		return result

	def get_filename(self, part_filename=""):
		""" Return the config filename """
		if self.__class__.__name__[-len("Config"):] == "Config":
			name = self.__class__.__name__[:-len("Config")]
		else:
			name = self.__class__.__name__
		return name + tools.strings.tostrings(part_filename)

	def open(self, file=None, read_write="r", part_filename=""):
		""" Create or open configuration file """
		# pylint:disable=unspecified-encoding
		filename = file
		if tools.filesystem.exists(self.config_root()) is False:
			tools.filesystem.makedir(self.config_root())
		if file is None:
			filename = self.get_pathname(tools.strings.tofilename(part_filename))
			file = open(filename, read_write)
		elif type(file) == type(""):
			file = open(filename, read_write)
		return file, filename

	def update(self, params, show_error=True):
		""" Update object with html request params """
		if b"name" in params and b"value" in params and len(params) == 2:
			setmany = False
			params = {params[b"name"]:params[b"value"]}
		else:
			setmany = True

		for name in self.__dict__.keys():
			# Case of web input is missing when bool is false
			if type(self.__dict__[name]) == type(True):
				name = tools.strings.tobytes(name)
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
			elif type(self.__dict__[name]) == type(0):
				name = tools.strings.tobytes(name)
				if name in params:
					value = 0
					try:
						value = int(params[name])
					except:
						if b"date" in name:
							value = tools.date.html_to_date(params[name])
						elif b"time" in name:
							value = tools.date.html_to_time(params[name])
						else:
							try:
								value = int(eval(params[name]))
							except:
								pass
					params[name] = value
			elif type(self.__dict__[name]) == type(0.):
				name = tools.strings.tobytes(name)
				if name in params:
					value = 0.
					try:
						value = float(params[name])
					except:
						try:
							value = float(eval(params[name]))
						except:
							pass
					params[name] = value

		result = True
		for name, value in params.items():
			res = self.exec(name, value, show_error)
			if res is not True:
				result = res
		return result

	def exec(self, name, value, show_error=True):
		""" Add attribute to current object """
		result = True
		global jsonconfig_self, jsonconfig_value
		name = tools.strings.tostrings(name)
		try:
			try:
				# pylint: disable=exec-used
				jsonconfig_self = self
				exec("a = jsonconfig_self.%s"%name)
				jsonconfig_self  = None
				existing = True
			except Exception as _err:
				if "'NoneType' object" in str(_err):
					result = None
				existing = False

			if existing:
				execval = "jsonconfig_self.%s = jsonconfig_value"%(name)
				# pylint: disable=exec-used
				jsonconfig_value = self.instantiate(value)
				jsonconfig_self  = self
				exec(execval)
				jsonconfig_self  = None
				jsonconfig_value = None
			else:
				if name != "action" and show_error and result is not None:
					print("%s.%s not existing"%(self.__class__.__name__, tools.strings.tostrings(name)))
		except Exception as _err:
			tools.logger.syslog(_err, "Error on %s"%(name))
			result = False
		return result

	def search_class(self, class_name):
		""" Search class with class name """
		for class_ in JsonConfig.classes:
			if class_.__name__ == class_name:
				return class_
		return None

	def instantiate(self, values):
		""" Instantiate all objects with its classes """
		result = values
		if type(values) == type({}):
			class_name = values.setdefault(b"__class__",None)
			instance = None
			if class_name is not None:
				class_ = self.search_class(tools.strings.tostrings(class_name))
				del values[b"__class__"]
				if class_ is not None:
					instance = class_()
					for key, value in values.items():
						instance.exec(key,value)
					result = instance
		elif type(values) == type([]):
			result = []
			for value in values:
				result.append(self.instantiate(value))
		return result

	def load(self, file=None, part_filename="", tobytes=True, errorlog=True):
		""" Load object with the file specified """
		filename = ""
		try:
			filename = self.get_pathname(tools.strings.tofilename(part_filename))
			file, filename = self.open(file=file, read_write="r", part_filename=part_filename)

			data = json.load(file)
			if tobytes:
				data = tools.strings.tobytes(data)
			self.update(data)
			file.close()
			self.last_refresh = time.time()
			return True
		except OSError as _err:
			if _err.args[0] == 2:
				if errorlog:
					tools.logger.syslog("Not existing %s "%(filename))
			else:
				tools.logger.syslog(_err, "Cannot load %s "%(filename))
			return False
		except Exception as _err:
			tools.logger.syslog(_err, "Cannot load %s "%(filename))
			return False

	def forget(self, part_filename=""):
		""" Forget configuration """
		tools.filesystem.remove(self.get_pathname(part_filename=part_filename))

	def is_changed(self, part_filename=""):
		""" Indicates if the configuration changed """
		if self.last_refresh + 31 < time.time():
			try:
				modification_date = uos.stat(self.get_pathname(tools.strings.tofilename(part_filename)))[8]
				if self.modification_date != modification_date:
					self.modification_date = modification_date
					return True
			except:
				pass
		return False

	def load_create(self, file=None, part_filename="", tobytes=True, errorlog=True):
		""" Load and create file if not existing """
		if self.load(file, part_filename, tobytes, errorlog) is False:
			self.save(file, part_filename)

	def refresh(self, file=None, part_filename="", tobytes=True, errorlog=True):
		""" refresh the configuration if it has changed since then """
		if self.is_changed(part_filename):
			self.load(file, part_filename, tobytes, errorlog)
			return True
		return False

	def exists(self, part_filename=""):
		""" Indicates if the configuration file existing """
		return tools.filesystem.exists(self.get_pathname(tools.strings.tofilename(part_filename)))
