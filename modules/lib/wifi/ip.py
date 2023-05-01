# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" Ip address tools """
def iptoint(ipaddr):
	""" Convert ip address into integer """
	spl = ipaddr.split(".")
	if len(spl):
		return ((int(spl[0])<<24)+ (int(spl[1])<<16) + (int(spl[2])<<8) + int(spl[3]))
	return 0

def issameinterface(ipaddr, ipinterface, maskinterface):
	""" indicates if the ip address is on the selected interface """
	ipaddr = iptoint(ipaddr)
	ipinterface  = iptoint(ipinterface)
	maskinterface = iptoint(maskinterface)
	if ipaddr & maskinterface == ipinterface & maskinterface:
		return True
	else:
		return False
