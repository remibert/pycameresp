# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Language selected and regional time """
from tools.jsonconfig import *

regionConfig = None

class RegionConfig(JsonConfig):
	""" Language selected and regional time """
	def __init__(self):
		""" Constructor """
		JsonConfig.__init__(self)
		self.lang        = b"english"
		self.offsettime  = 1
		self.dst         = True
		self.currentTime = 0

	@staticmethod
	def get():
		""" Return region configuration """
		global regionConfig
		if regionConfig == None:
			regionConfig = RegionConfig()
			if regionConfig.load() == False:
				regionConfig.save()
		
		if regionConfig.isChanged():
			regionConfig.load()
		return regionConfig

try:
	exec(b"from tools.lang_%s import *"%RegionConfig.get().lang)
except Exception as err:
	from tools import useful
	useful.syslog(err)
	from tools.lang_english import *
	
