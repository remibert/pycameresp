# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# Freely inspired by :
#    uping  (MicroPing) for MicroPython
#    copyright (c) 2018 Shawwwn <shawwwn1@gmail.com>
#    License: MIT
   
#    Internet Checksum Algorithm
#    Author: Olav Morken
#    https://github.com/olavmrk/python-ping/blob/master/ping.py
#    @data: bytes

try:
	import utime
	import uselect
	import uctypes
	import usocket
	import ustruct
	import urandom
	import usocket
	import uasyncio
except:
	import time   as utime
	import select as uselect
	import ctypes as uctypes
	import socket as usocket
	import struct as ustruct
	import random as urandom
	import asyncio as uasyncio
import wifi

def ticks_us():
	""" Get tick in microseconds """
	try:
		return utime.ticks_us()
	except:
		return utime.time_ns()//1000

class Packet:
	""" Create ICMP packet for ping """
	ECHO_REQUEST = 8
	ECHO_REPLY   = 0
	def __init__(self, type, code, sequence, size = 64):
		""" Constructor of ICMP packet for ping """
		self.format = b">BBHHHQ"
		self.type       = type #B
		self.code       = code #B
		self.checksum   = 0 #H
		self.identifier = urandom.randint(0, 65535) #H
		self.sequence   = sequence   #H
		self.timestamp  = ticks_us() #Q
		self.size       = size

	def computeChecksum(self, data):
		""" Compute the checksum of packet """
		if len(data) & 0x1: # Odd number of bytes
			data += b'\0'
		checksum = 0
		for pos in range(0, len(data), 2):
			b1 = data[pos]
			b2 = data[pos + 1]
			checksum += (b1 << 8) + b2
		while checksum >= 0x10000:
			checksum = (checksum & 0xffff) + (checksum >> 16)
		checksum = ~checksum & 0xffff
		return checksum

	def serialize(self):
		""" Serialize packet and compute the checksum """
		self.checksum = 0
		self.checksum = self.computeChecksum(self.__getBuffer())
		return self.__getBuffer()
	
	def unserialize(self, resp):
		""" Unserialize packet """
		data = resp[20:]
		data = data[0:ustruct.calcsize(self.format)]
		self.type, self.code, self.checksum, self.identifier, self.sequence, self.timestamp = ustruct.unpack(self.format, data)
		self.ttl = ustruct.unpack("!B",resp[8:9])[0]
	
	def __getBuffer(self):
		""" Create the serialized buffer of data """
		data = ustruct.pack(self.format, self.type, self.code, self.checksum, self.identifier, self.sequence, self.timestamp)
		padding = b"."*(self.size-len(data))
		return data + padding
		
	def isEqual(self, request):
		""" Check if the request is equal to this response """
		if self.identifier == request.identifier and self.sequence == request.sequence:
			return True
		return False
	
	def getTimeElapsed(self):
		""" Get the time elapsed """
		return ticks_us() - self.timestamp
	
	def __repr__(self):
		""" Display the content of data """
		return "type       : %d\n"\
			"code       : %d\n"\
			"checksum   : 0x%04X\n"\
			"identifier : %d\n"\
			"sequence   : %d\n"\
			"timestamp  : %d"%(self.type, self.code, self.checksum, self.identifier, self.sequence, self.timestamp)

def getAddressIp(hostname):
	""" Return the address ip of the hostname """
	try:
		return usocket.getaddrinfo(hostname, 1, usocket.SOCK_DGRAM, usocket.AF_INET)[0][-1][0]
	except:
		return None

async def select(rlist, wlist, xlist, timeout=0):
	""" Asynchronous select """
	while 1:
		r, w, x = uselect.select(rlist, wlist, xlist, 0)
		if r:
			return r,w,x
		else:
			if timeout <= 0:
				return [],[],[]
			else:
				timeout -= 0.1
				await uasyncio.sleep(0.1)

class Ping:
	""" Class used to ping host """
	def __init__(self):
		""" Constructor """
		self.sock = None
	
	def open(self, host):
		""" Open connection to host """
		self.host = host
		self.packetsTransmitted = 0
		self.packetsReceived = 0
		try:
			result = True
			self.close()
			self.sock = usocket.socket(usocket.AF_INET, usocket.SOCK_RAW, 1)
			self.sock.setblocking(0)
			self.addr = usocket.getaddrinfo(self.host, 1, usocket.SOCK_DGRAM, usocket.AF_INET)[0][-1][0]
			self.sock.connect((self.addr, 1))
			if self.quiet == False: print("PING %s (%s)"%(self.host, self.addr))
		except:
			if self.quiet == False : print("Ping open socket failed")
			self.close()
			result = False
		return result
	
	def send(self, seq):
		""" Send ICMP packet """
		result = True
		self.request = Packet(Packet.ECHO_REQUEST, 0, seq)
		try:
			self.sock.send(self.request.serialize())
			self.packetsTransmitted += 1
		except:
			if self.quiet == False: print("Cannot send request to '%s'"%self.host)
			result = False
		return result
	
	def receive(self, seq, sock):
		""" Receive and decode ICMP packet """
		result = False
		if sock:
			resp = self.sock.recv(4096)
			self.response = Packet(Packet.ECHO_REPLY, 0, seq)
			
			self.response.unserialize(resp)
			if self.response.isEqual(self.request):
				if self.quiet == False: print("%u bytes from %s: icmp_seq=%u, ttl=%u, time=%.2f ms" % (len(resp)-20, self.addr, self.response.sequence, self.response.ttl, self.response.getTimeElapsed()/1000))
				self.packetsReceived += 1
				result = True
		else:
			if self.quiet == False: print("Request timeout for icmp_seq %d"%seq)
		return result

	def ping(self, host, count=4, timeout=1, quiet=False):
		""" Do synchronous ping """
		result = True
		self.quiet = quiet
		if self.open(host):
			for seq in range(count):
				if self.send(seq) == False:
					result = False
					break
				else:
					socks, _, _ = uselect.select([self.sock], [], [], timeout)
					if self.receive(seq, socks):
						utime.sleep(timeout)
			self.showResult()
		else:
			result = None
		self.close()
		return self.packetsTransmitted, self.packetsReceived, result

	async def asyncPing(self, host, count=4, timeout=1, quiet=False):
		""" Do an asynchronous ping """
		result = True
		self.quiet = quiet
		if self.open(host):
			for seq in range(count):
				if self.send(seq) == False:
					result = False
					break
				else:
					socks, _, _ = await select([self.sock], [], [], timeout)
					if self.receive(seq, socks):
						await uasyncio.sleep(timeout)
			self.showResult()
		else:
			result = None
		self.close()
		return self.packetsTransmitted, self.packetsReceived, result
	
	def showResult(self):
		""" Show the ping result """
		if self.quiet == False: print("%u packets transmitted, %u packets received" % (self.packetsTransmitted, self.packetsReceived))

	def close(self):
		""" Close socket to server """
		if self.sock:
			self.sock.close()
			self.sock = None

async def asyncPing(host, count=4, timeout=1, quiet=False):
	""" Asynchronous ping of host """
	if wifi.Station.isActive():
		ping_ = Ping()
		return await ping_.asyncPing(host, count, timeout, quiet)
	else:
		return (0,0,None)

def ping(host, count=4, timeout=1, quiet=False):
	""" Ping of host """
	if wifi.Station.isActive():
		ping_ = Ping()
		return ping_.ping(host, count, timeout, quiet)
	else:
		return (0,0,None)
