# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Functions for managing the json configuration.
All configuration classes end the name with the word Config.
For each of these classes, a json file with the same name is stored in the config directory of the board. """
# pylint:disable=consider-using-dict-items
# pylint:disable=consider-iterating-dictionary
import json
import re
import uos
from tools import useful

self_config = None
class JsonConfig:
	""" Manage json configuration """
	def __init__(self):
		""" Constructor """
		self.modification_date = 0

	def config_root(self):
		""" Configuration root path """
		if useful.ismicropython():
			return "/config"
		else:
			return "config"

	def save(self, file = None, part_filename=""):
		""" Save object in json file """
		try:
			filename = self.get_pathname(useful.tofilename(part_filename))
			file, filename = self.open(file=file, read_write="w", part_filename=part_filename)
			data = self.__dict__.copy()
			del data["modification_date"]
			json.dump(useful.tostrings(data),file)
			file.close()
			self.modification_date = uos.stat(filename)[8]
			return True
		except Exception as err:
			useful.syslog(err, "Cannot save %s "%(filename))
			return False

	def to_string(self):
		""" Convert the configuration to string """
		data = self.__dict__.copy()
		del data["modification_date"]
		return json.dumps(useful.tostrings(data))

	def get_pathname(self, part_filename=""):
		""" Get the configuration filename according to the class name """
		return self.config_root()+"/"+self.get_filename(part_filename) + ".json"

	def list_all(self):
		""" List all configuration files """
		result = []
		pattern = self.get_filename() + ".*"
		for fileinfo in uos.ilistdir(self.config_root()):
			name = fileinfo[0]
			typ  = fileinfo[1]
			if typ & 0xF000 != 0x4000:
				if re.match(pattern, name):
					result.append(useful.tobytes(name[len(self.get_filename()):-len(".json")]))
		return result

	def get_filename(self, part_filename=""):
		""" Return the config filename """
		if self.__class__.__name__[-len("Config"):] == "Config":
			name = self.__class__.__name__[:-len("Config")]
		else:
			name = self.__class__.__name__
		return name + useful.tostrings(part_filename)

	def open(self, file=None, read_write="r", part_filename=""):
		""" Create or open configuration file """
		filename = file
		if useful.exists(self.config_root()) is False:
			useful.makedir(self.config_root())
		if file is None:
			filename = self.get_pathname(useful.tofilename(part_filename))
			file = open(filename, read_write)
		elif type(file) == type(""):
			file = open(filename, read_write)
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
				useful.syslog(err, "Error on %s"%(execval))
				result = False
		del self_config
		return result

	def load(self, file = None, part_filename=""):
		""" Load object with the file specified """
		try:
			filename = self.get_pathname(useful.tofilename(part_filename))
			file, filename = self.open(file=file, read_write="r", part_filename=part_filename)
			self.update(useful.tobytes(json.load(file)))
			file.close()
			return True
		except OSError as err:
			if err.args[0] == 2:
				useful.syslog("Not existing %s "%(filename))
			else:
				useful.syslog(err, "Cannot load %s "%(filename))
			return False
		except Exception as err:
			useful.syslog(err, "Cannot load %s "%(filename))
			return False

	def forget(self, part_filename=""):
		""" Forget configuration """
		filename = self.get_pathname(part_filename=part_filename)
		useful.remove(self.config_root()+"/"+filename)

	def is_changed(self, part_filename=""):
		""" Indicates if the configuration changed """
		try:
			modification_date = uos.stat(self.get_pathname(useful.tofilename(part_filename)))[8]
			if self.modification_date != modification_date:
				self.modification_date = modification_date
				return True
		except:
			pass
		return False
