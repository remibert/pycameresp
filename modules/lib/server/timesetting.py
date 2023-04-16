# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Function which sets the internal clock of the card based on an ntp server """
import tools.logger
import tools.date

def get_ntp_time():
	""" Return the time from a NTP server """
	try:
		import socket
		import struct
		ntp_query = bytearray(48)
		ntp_query[0] = 0x1B
		addr = socket.getaddrinfo("pool.ntp.org", 123)[0][-1]
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		try:
			s.settimeout(2)
			res = s.sendto(ntp_query, addr)
			msg = s.recv(48)
		finally:
			s.close()
		val = struct.unpack("!I", msg[40:44])[0]
		# (date(2000, 1, 1) - date(1900, 1, 1)).days * 24*60*60
		return val - 3155673600
	except:
		return 0

def set_time(current_time):
	""" Change the current time """
	try:
		newtime = tools.date.local_time(current_time)
		year,month,day,hour,minute,second,weekday,yearday = newtime[:8]

		import machine
		machine.RTC().datetime((year, month, day, weekday + 1, hour, minute, second, 0))
	except Exception as exc:
		tools.logger.syslog("Cannot set time '%s'"%exc)

def calc_local_time(current_time, offset_time=+1, dst=True):
	""" Calculate the local time """
	year,month,day,hour,minute,second,weekday,yearday = tools.date.local_time(current_time)[:8]

	# Get the day of the last sunday of march
	march_end_weekday = tools.date.local_time(tools.date.mktime((year, 3, 31, 0, 0, 0, 0, 0)))[6]
	start_day_dst = 31-((1+march_end_weekday)%7)

	# Get the day of the last sunday of october
	october_end_weekday = tools.date.local_time(tools.date.mktime((year,10, 30, 0, 0, 0, 0, 0)))[6]
	end_day_dst = 30-((1+october_end_weekday)%7)

	start_dst = tools.date.mktime((year,3 ,start_day_dst,1,0,0,0,0))
	end_dst   = tools.date.mktime((year,10,end_day_dst  ,1,0,0,0,0))

	now = tools.date.mktime((year,month,day,hour,minute,second,weekday,yearday))

	if dst and now > start_dst and now < end_dst : # we are before last sunday of october
		return now+(offset_time*3600)+3600 # DST: UTC+dst*H + 1
	else:
		return now+(offset_time*3600) # EST: UTC+dst*H

def set_date(offset_time=+1, dst=True, display=False):
	""" Set the date """
	current_time = get_ntp_time()
	if current_time > 0:
		current_time = calc_local_time(current_time, offset_time, dst)
		if current_time > 0:
			set_time(current_time)
			if display:
				tools.logger.syslog("Date updated : %s"%(tools.date.date_to_string()))
			return current_time
	return 0
