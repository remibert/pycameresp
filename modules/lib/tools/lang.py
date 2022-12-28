# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Language selected and regional time """
import time
import sys
from tools import region, strings, logger

try:
	exec(b"from tools.lang_%s import *"%region.RegionConfig.get().lang)
	logger.syslog("Select lang : %s"%strings.tostrings(region.RegionConfig.get().lang))
except Exception as err:
	logger.syslog(err)
	from tools.lang_english import *

def translate_date(current_date, with_day=True):
	""" Return the date formated according to the lang """
	# pylint:disable=undefined-variable
	# pylint:disable=possibly-unused-variable
	# pylint:disable=used-before-assignment
	# pylint:disable=global-variable-not-assigned
	year, month, day, _, _, _, weekday = time.localtime(current_date)[:7]
	global weekdays, months, date_format, month_format
	weekday = weekdays[weekday]
	month   = months[month-1]
	info = {"weekday":weekday,"month":month,"day":day,"year":year}
	if sys.implementation.name == "micropython":
		return date_format % info
	if with_day:
		return date_format % strings.tobytes(info)
	else:
		return month_format % strings.tobytes(info)
