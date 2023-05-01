# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" Language selected and regional time """
import tools.jsonconfig

region_config = None

class RegionConfig(tools.jsonconfig.JsonConfig):
	""" Language selected and regional time """
	def __init__(self):
		""" Constructor """
		tools.jsonconfig.JsonConfig.__init__(self)
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
		region_config.refresh()
		return region_config
