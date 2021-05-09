# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function which sets the internal clock of the card based on an ntp server """

def ntptime():
	""" Return the time from a NTP server """
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

def setdate(offsetTime=+1, dst=True, display=False):
	""" Set the date """
	result = False
	try:
		import time
		year,month,day,hour,minute,second,weekday,yearday = time.localtime(ntptime())[:8]
		startDST = time.mktime((year,3 ,(14-(int(5*year/4+1))%7),1,0,0,0,0,0)) #Time of March change to DST
		endDST   = time.mktime((year,10,( 7-(int(5*year/4+1))%7),1,0,0,0,0,0)) #Time of November change to EST
		now = time.mktime((year,month,day,hour,minute,second,weekday,yearday))
		if dst and now > startDST and now < endDST : # we are before last sunday of october
			newtime = time.localtime(now+(offsetTime*3600)+3600) # DST: UTC+dst*H + 1
		else:
			newtime = time.localtime(now+(offsetTime*3600)) # EST: UTC+dst*H

		year,month,day,hour,minute,second,weekday,yearday = newtime
		import machine
		machine.RTC().datetime((year, month, day, weekday + 1, hour, minute, second, 0))
		if display:
			from tools import useful
			print("Date updated : %s"%(useful.dateToString()))
		result = True
	except Exception as exc:
		print("Cannot set time '%s'"%exc)
	return result


