# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function which sets the internal clock of the card based on an ntp server """
import time
from tools import useful
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
		newtime = time.localtime(currenttime)
		year,month,day,hour,minute,second,weekday,yearday = newtime[:8]

		import machine
		machine.RTC().datetime((year, month, day, weekday + 1, hour, minute, second, 0))
	except Exception as exc:
		useful.syslog("Cannot set time '%s'"%exc)

def calc_local_time(currenttime, offsetTime=+1, dst=True):
	""" Calculate the local time """
	year,month,day,hour,minute,second,weekday,yearday = time.localtime(currenttime)[:8]
	startDST = time.mktime((year,3 ,(14-(int(5*year/4+1))%7),1,0,0,0,0,0)) #Time of March change to DST
	endDST   = time.mktime((year,10,( 7-(int(5*year/4+1))%7),1,0,0,0,0,0)) #Time of November change to EST
	try:
		now = time.mktime((year,month,day,hour,minute,second,weekday,yearday))
	except:
		now = time.mktime((year,month,day,hour,minute,second,weekday,yearday,0))

	if dst and now > startDST and now < endDST : # we are before last sunday of october
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
				useful.syslog("Date updated : %s"%(useful.date_to_string()))
			return currenttime
	return 0
