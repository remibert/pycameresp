# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Language selected and regional time """
import tools.region
import tools.strings
import tools.logger

try:
	exec(b"from electricmeter.em_lang_%s import *"%tools.region.RegionConfig.get().lang)
	tools.logger.syslog("Select electricmeter lang : %s"%tools.strings.tostrings(tools.region.RegionConfig.get().lang))
except Exception as err:
	tools.logger.syslog(err)
	from electricmeter.em_lang_english import *
