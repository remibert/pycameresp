""" Dns client class """
# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# DNS spec https://www2.cs.duke.edu/courses/fall16/compsci356/DNS/DNS-primer.pdf
import struct
import random
import socket
import re

class DnsHeader:
	""" DNS packet header """
	def __init__(self, ident, flag, query, answer, autority=0, additional=0):
		""" DNS header contructor """
		self.ident      = ident
		self.flag       = flag
		self.query      = query
		self.answer     = answer
		self.autority   = autority
		self.additional = additional
		self.format     = "!HHHHHH"

	def serialize(self):
		""" Serialize DNS header """
		return struct.pack(self.format, self.ident, self.flag, self.query, self.answer, self.autority, self.additional)

	def unserialize(self, data):
		""" Unserialize DNS header """
		length = struct.calcsize(self.format)
		self.ident, self.flag, self.query, self.answer, self.autority, self.additional = struct.unpack(self.format, data[:length])
		return length

	def __repr__(self):
		""" Display content """
		return "Header : ident=0x%04X flag=0x%04X query=%d answer=%d autority=%d additional=%d"%(self.ident, self.flag, self.query, self.answer, self.autority, self.additional)

	def encode_name(self, name):
		""" Encode DNS name """
		result = ""
		spl = split_ip_address(name)
		# Ip address detected
		if type(spl) == type([]):
			spl.reverse()
			spl.append("in-addr")
			spl.append("arpa")
		else:
			spl = name.split(".")

		for item in spl:
			result += chr(len(item))
			result += item
		return result + chr(0)

	def decode_name(self, data, pos):
		""" Decode DNS name """
		result = ""
		while pos < len(data):
			length = data[pos]
			pos += 1
			if length == 0:
				break
			elif length & 0xC0 == 0xC0:
				offset = data[pos] + (length & 0x3F << 8)
				pos += 1
				part, pos2 = self.decode_name(data, offset)
				result = result + "." + part
			else:
				part = data[pos:pos+length]
				pos += length
				result = result + "." + part.decode("utf8")
		return result.strip("."), pos

class DnsQuery:
	""" DNS query packet """
	def __init__(self, header, qname, qtype=0x000C, qclass=0x0001):
		""" DNS query constructor """
		self.header = header
		self.name = qname
		self.qtype = qtype
		self.qclass = qclass
		self.format = "!HH"

	def serialize(self):
		""" Serialize query """
		data = self.header.serialize()
		data += self.header.encode_name(self.name).encode("latin-1")
		data += struct.pack(self.format,self.qtype, self.qclass)
		return data

	def unserialize(self, data):
		""" Unserialize query """
		pos = self.header.unserialize(data)
		self.name, pos = self.header.decode_name(data, pos)
		self.qtype, self.qclass = struct.unpack(self.format, data[pos:pos+struct.calcsize(self.format)])
		return pos + struct.calcsize(self.format)

	def __repr__(self):
		""" Display result """
		return repr(self.header) + "\n  Query  : name='%s' type=%04X class=%04X"%(self.name, self.qtype, self.qclass)

class DnsAnswer:
	""" DNS answer packet """
	def __init__(self):
		""" DNS answer constructor """
		self.query  = DnsQuery(DnsHeader(0,0,0, 0), "")
		self.format = "!HHHLH"
		self.info = 0
		self.name = ""
		self.atype = 0
		self.aclass = 0
		self.timetolive = 0
		self.length = 0

	def unserialize(self, data):
		""" Unserialize answer """
		pos = self.query.unserialize(data)
		self.info, self.atype, self.aclass, self.timetolive, self.length = struct.unpack(self.format, data[pos:pos+struct.calcsize(self.format)])
		pos += struct.calcsize(self.format)
		if self.atype == 1:
			self.name = "%d.%d.%d.%d"%(data[pos],data[pos+1],data[pos+2],data[pos+3])
		else:
			self.name, posname = self.query.header.decode_name(data, pos)

	def __repr__(self):
		""" Display result """
		return repr(self.query) + "\n  Answer : info=%04X type=%04X class=%04X time=%d length=%d name='%s'"%(self.info, self.atype, self.aclass, self.timetolive, self.length,self.name)

def dns_exchange(dnsIp, dnsQuery, dnsAnswer):
	""" Exchange DNS query and wait answer """
	result = None
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		sock.settimeout(1)
		query = dnsQuery.serialize()
		sock.sendto(query, (dnsIp, 53))
		answer = sock.recv(1024)
		try:
			dnsAnswer.unserialize(answer)
			if dnsQuery.header.ident == dnsAnswer.query.header.ident:
				result = dnsAnswer.name
		except:
			pass
	finally:
		sock.close()
	return result

def resolve_hostname(dnsIp, ipAddress):
	""" Resolve hostname with ip address """
	return dns_exchange(dnsIp, DnsQuery(DnsHeader(random.randint(0, 65535), 0x0100, 1, 0), ipAddress, 0xC), DnsAnswer())

def resolve_ip_address(dnsIp, hostname):
	""" Resolve ip address with hostname """
	return dns_exchange(dnsIp, DnsQuery(DnsHeader(random.randint(0, 65535), 0x0100, 1, 0), hostname, 1), DnsAnswer())

def split_ip_address(url):
	""" Split ip address """
	if is_ip_address(url):
		return url.split(".")
	else:
		return url

def is_ip_address(url):
	""" Indicates if the url is an ip address """
	# Ip address detected
	if re.match(r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)", url):
		return True
	return False
