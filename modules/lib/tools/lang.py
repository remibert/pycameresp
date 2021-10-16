# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Language selected and regional time """
from tools.jsonconfig import *

region_config = None

class RegionConfig(JsonConfig):
	""" Language selected and regional time """
	def __init__(self):
		""" Constructor """
		JsonConfig.__init__(self)
		self.lang        = b"english"
		self.offset_time  = 1
		self.dst         = True
		self.current_time = 0

	@staticmethod
	def get():
		""" Return region configuration """
		global region_config
		if region_config is None:
			region_config = RegionConfig()
			if region_config.load() is False:
				region_config.save()

		if region_config.is_changed():
			region_config.load()
		return region_config

try:
	exec(b"from tools.lang_%s import *"%RegionConfig.get().lang)
except Exception as err:
	from tools import useful
	useful.syslog(err)
	from tools.lang_english import *
