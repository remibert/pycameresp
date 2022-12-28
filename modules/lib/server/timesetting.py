# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Function which sets the internal clock of the card based on an ntp server """
from tools import logger, strings, date

def get_ntp_time():
	""" Return the time from a NTP server """
	try:
		import socket
		import struct
		NTP_QUERY = bytearray(48)
		NTP_QUERY[0] = 0x1B
		addr = socket.getaddrinfo("pool.ntp.org", 123)[0][-1]
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		try:
			s.settimeout(2)
			res = s.sendto(NTP_QUERY, addr)
			msg = s.recv(48)
		finally:
			s.close()
		val = struct.unpack("!I", msg[40:44])[0]
		# (date(2000, 1, 1) - date(1900, 1, 1)).days * 24*60*60
		NTP_DELTA = 3155673600
		return val - NTP_DELTA
	except:
		return 0

def set_time(currenttime):
	""" Change the current time """
	try:
		newtime = date.local_time(currenttime)
		year,month,day,hour,minute,second,weekday,yearday = newtime[:8]

		import machine
		machine.RTC().datetime((year, month, day, weekday + 1, hour, minute, second, 0))
	except Exception as exc:
		logger.syslog("Cannot set time '%s'"%exc)

def calc_local_time(currenttime, offsetTime=+1, dst=True):
	""" Calculate the local time """
	year,month,day,hour,minute,second,weekday,yearday = date.local_time(currenttime)[:8]

	# Get the day of the last sunday of march
	march_end_weekday = date.local_time(date.mktime((year, 3, 31, 0, 0, 0, 0, 0)))[6]
	start_day_dst = 31-((1+march_end_weekday)%7)

	# Get the day of the last sunday of october
	october_end_weekday = date.local_time(date.mktime((year,10, 30, 0, 0, 0, 0, 0)))[6]
	end_day_dst = 30-((1+october_end_weekday)%7)

	start_DST = date.mktime((year,3 ,start_day_dst,1,0,0,0,0))
	end_DST   = date.mktime((year,10,end_day_dst  ,1,0,0,0,0))

	now = date.mktime((year,month,day,hour,minute,second,weekday,yearday))

	if dst and now > start_DST and now < end_DST : # we are before last sunday of october
		return now+(offsetTime*3600)+3600 # DST: UTC+dst*H + 1
	else:
		return now+(offsetTime*3600) # EST: UTC+dst*H

def set_date(offsetTime=+1, dst=True, display=False):
	""" Set the date """
	currenttime = get_ntp_time()
	if currenttime > 0:
		currenttime = calc_local_time(currenttime, offsetTime, dst)
		if currenttime > 0:
			set_time(currenttime)
			if display:
				logger.syslog("Date updated : %s"%(date.date_to_string()))
			return currenttime
	return 0
