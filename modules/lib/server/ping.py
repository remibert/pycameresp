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
""" Ping network class """
import time
import random
import socket
import struct
import uselect
import uasyncio
import wifi

def ticks_us():
	""" Get tick in microseconds """
	try:
		# pylint: disable=no-member
		return time.ticks_us()
	except:
		return time.time_ns()//1000

class Packet:
	""" Create ICMP packet for ping """
	ECHO_REQUEST = 8
	ECHO_REPLY   = 0
	def __init__(self, typ, code, sequence, size = 64):
		""" Constructor of ICMP packet for ping """
		self.format = b">BBHHHQ"
		self.type       = typ #B
		self.code       = code #B
		self.checksum   = 0 #H
		self.identifier = random.randint(0, 65535) #H
		self.sequence   = sequence   #H
		self.timestamp  = ticks_us() #Q
		self.size       = size
		self.ttl = None

	def compute_checksum(self, data):
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
		self.checksum = self.compute_checksum(self.__get_buffer())
		return self.__get_buffer()

	def unserialize(self, resp):
		""" Unserialize packet """
		data = resp[20:]
		data = data[0:struct.calcsize(self.format)]
		self.type, self.code, self.checksum, self.identifier, self.sequence, self.timestamp = struct.unpack(self.format, data)
		self.ttl = struct.unpack("!B",resp[8:9])[0]

	def __get_buffer(self):
		""" Create the serialized buffer of data """
		data = struct.pack(self.format, self.type, self.code, self.checksum, self.identifier, self.sequence, self.timestamp)
		padding = b"."*(self.size-len(data))
		return data + padding

	def is_equal(self, request):
		""" Check if the request is equal to this response """
		if self.identifier == request.identifier and self.sequence == request.sequence:
			return True
		return False

	def get_time_elapsed(self):
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
				timeout -= 0.25
				await uasyncio.sleep(0.25)

class Ping:
	""" Class used to ping host """
	def __init__(self):
		""" Constructor """
		self.sock = None
		self.ttl = None
		self.host = None
		self.packets_transmitted = 0
		self.packets_received = 0
		self.addr = None
		self.request = None
		self.quiet = None
		self.response = None

	def open(self, host):
		""" Open connection to host """
		self.host = host
		self.packets_transmitted = 0
		self.packets_received = 0
		try:
			result = True
			self.close()
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, 1)
			self.sock.setblocking(0)
			self.addr = socket.getaddrinfo(self.host, 1, socket.SOCK_DGRAM, socket.AF_INET)[0][-1][0]
			self.sock.connect((self.addr, 1))
			if self.quiet is False:
				print("PING %s (%s)"%(self.host, self.addr))
		except:
			if self.quiet is False :
				print("Ping open socket failed")
			self.close()
			result = False
		return result

	def send(self, seq):
		""" Send ICMP packet """
		result = True
		self.request = Packet(Packet.ECHO_REQUEST, 0, seq)
		try:
			self.sock.send(self.request.serialize())
			self.packets_transmitted += 1
		except:
			if self.quiet is False:
				print("Cannot send request to '%s'"%self.host)
			result = False
		return result

	def receive(self, seq, sock):
		""" Receive and decode ICMP packet """
		result = False
		if sock:
			resp = self.sock.recv(256)
			self.response = Packet(Packet.ECHO_REPLY, 0, seq)

			self.response.unserialize(resp)
			if self.response.is_equal(self.request):
				if self.quiet is False:
					print("%u bytes from %s: icmp_seq=%u, ttl=%u, time=%.2f ms" % (len(resp)-20, self.addr, self.response.sequence, self.response.ttl, self.response.get_time_elapsed()/1000))
				self.packets_received += 1
				result = True
		else:
			if self.quiet is False:
				print("Request timeout for icmp_seq %d"%seq)
		return result

	def ping(self, host, count=4, timeout=1, quiet=False):
		""" Do synchronous ping """
		result = True
		self.quiet = quiet
		if self.open(host):
			for seq in range(count):
				if self.send(seq) is False:
					result = False
					break
				else:
					socks, _, _ = uselect.select([self.sock], [], [], timeout)
					if self.receive(seq, socks):
						time.sleep(timeout)
			self.show_result()
		else:
			result = None
		self.close()
		return self.packets_transmitted, self.packets_received, result

	async def async_ping(self, host, count=4, timeout=1, quiet=False):
		""" Do an asynchronous ping """
		result = True
		self.quiet = quiet
		if self.open(host):
			for seq in range(count):
				if self.send(seq) is False:
					result = False
					break
				else:
					socks, _, _ = await select([self.sock], [], [], timeout)
					if self.receive(seq, socks):
						await uasyncio.sleep(timeout)
			self.show_result()
		else:
			result = None
		self.close()
		return self.packets_transmitted, self.packets_received, result

	def show_result(self):
		""" Show the ping result """
		if self.quiet is False:
			print("%u packets transmitted, %u packets received" % (self.packets_transmitted, self.packets_received))

	def close(self):
		""" Close socket to server """
		if self.sock:
			self.sock.close()
			self.sock = None

async def async_ping(host, count=4, timeout=1, quiet=False):
	""" Asynchronous ping of host """
	if wifi.Station.is_active():
		ping_ = Ping()
		return await ping_.async_ping(host, count, timeout, quiet)
	else:
		return (0,0,None)

def ping(host, count=4, timeout=1, quiet=False):
	""" Ping of host """
	if wifi.Station.is_active():
		ping_ = Ping()
		return ping_.ping(host, count, timeout, quiet)
	else:
		return (0,0,None)
