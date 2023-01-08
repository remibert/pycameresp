# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Date and time utilities """
import sys
import time

def local_time(date_=None):
	""" Safe local time, it return 2000/1/1 00:00:00 if date can be extracted """
	try:
		year,month,day,hour,minute,second,weekday,yearday = time.localtime(date_)[:8]
	except:
		year,month,day,hour,minute,second,weekday,yearday = 2000,1,1,0,0,0,0,0
	return year,month,day,hour,minute,second,weekday,yearday

def date_to_string(date_ = None):
	""" Get a string with the current date """
	return date_to_bytes(date_).decode("utf8")

def date_to_bytes(date_ = None):
	""" Get a bytes with the current date """
	year,month,day,hour,minute,second = local_time(date_)[:6]
	return b"%04d/%02d/%02d  %02d:%02d:%02d"%(year,month,day,hour,minute,second)

def date_ms_to_string():
	""" Get a string with the current date with ms """
	current = time.time_ns()
	ms = (current // 1_000_000)%1000
	current //= 1_000_000_000
	year,month,day,hour,minute,second = local_time(current)[:6]
	return "%04d/%02d/%02d %02d:%02d:%02d.%03d"%(year,month,day,hour,minute,second,ms)

def mktime(t):
	""" Portable mktime """
	year,month,day,hour,minute,second,weekday,yearday = t
	if sys.implementation.name == "micropython":
		result = time.mktime((year, month, day, hour, minute, second, weekday, yearday))
	else:
		result = time.mktime((year, month, day, hour, minute, second, weekday, yearday, 0))
	return result

def html_to_date(date_, separator=b"-"):
	""" Convert html date into time integer """
	result = 0
	try:
		year, month, day = date_.split(separator)
		year  = int( year.lstrip(b"0"))
		month = int(month.lstrip(b"0"))
		day   = int(  day.lstrip(b"0"))
		result = mktime((year, month, day, 1,0,0, 0,0))
	except:
		result = (time.time() // 86400) * 86400
	return result

def date_to_html(date_ = None, separator=b"-"):
	""" Get a html date with the current date """
	year,month,day = local_time(date_)[:3]
	return b"%04d%s%02d%s%02d"%(year,separator,month,separator,day)


def html_to_time(time_, separator=b":"):
	""" Convert html time string into time integer """
	result = 0
	try:
		hour, minute, second = time_.split(separator)
		hour   = int(  hour.lstrip(b"0"))
		minute = int(minute.lstrip(b"0"))
		second = int(second.lstrip(b"0"))
		result = hour * 3600 + minute * 60 * second
	except:
		try:
			hour, minute = time_.split(separator)
			hour   = int(  hour.lstrip(b"0"))
			minute = int(minute.lstrip(b"0"))
			result = hour * 3600 + minute * 60
		except:
			pass
	return result

def time_to_html(t = None, seconds=False):
	""" Convert time into date bytes """
	if t is None:
		t = time.time()
	t %= 86400
	result =  b"%02d:%02d:%02d"%(t//3600, (t%3600)//60, t%60)
	if seconds is False:
		result = result[:-3]
	return result

def date_to_filename(date_ = None):
	""" Get a filename with a date """
	filename = date_to_string(date_)
	filename = filename.replace("  "," ")
	filename = filename.replace(" ","_")
	filename = filename.replace("/","-")
	filename = filename.replace(":","-")
	return filename

def date_to_path(date_=None):
	""" Get a path with year/month/day/hour """
	year,month,day,hour,minute = local_time(date_)[:5]
	return b"%04d/%02d/%02d/%02dh%02d"%(year,month,day,hour,minute)
