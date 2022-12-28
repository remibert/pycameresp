# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Language selected and regional time """
from tools import region, strings, logger

try:
	exec(b"from electricmeter.em_lang_%s import *"%region.RegionConfig.get().lang)
	logger.syslog("Select electricmeter lang : %s"%strings.tostrings(region.RegionConfig.get().lang))
except Exception as err:
	logger.syslog(err)
	from electricmeter.em_lang_english import *
