# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
from tools.jsonconfig import *

class LangConfig(JsonConfig):
	""" Langue selected """
	def __init__(self):
		""" Constructor """
		JsonConfig.__init__(self)
		self.lang = b"english"

config = LangConfig()
if config.load() == False:
	config.save()

exec(b"from tools.lang_%s import *"%config.lang)
