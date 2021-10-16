# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" These classes are used to manage asynchronous stream. """

import sys
from io import BytesIO
if sys.implementation.name == "micropython":
	class Stream:
		""" Class stream """
		def __init__(self, reader, writer):
			self.reader = reader
			self.writer = writer
			self.buffer = b""

		async def readline(self):
			""" The firt time, this method completely reads the stream.
			It then returns only the requested row. This significantly increases read performance. """
			pos = self.buffer.find(b"\r\n")
			if pos == -1:
				self.buffer += await self.reader.read(1440)
				pos = self.buffer.find(b"\r\n")
			if pos == -1:
				result = self.buffer
				self.buffer = b""
			else:
				result = self.buffer[:pos+2]
				self.buffer = self.buffer[pos+2:]
			return result

		async def read(self, length):
			""" Read data from the stream """
			if len(self.buffer) < length:
				data = await self.reader.read(length - len(self.buffer))
				self.buffer += data

			data = self.buffer[:length]
			self.buffer = self.buffer[length:]
			return data

		async def write(self, data):
			""" Write data in the stream """
			result = await self.writer.awrite(data)
			if result is None:
				result = len(data)
			else:
				result = -1
			return result

		async def close(self):
			""" Close the stream """
			await self.writer.aclose()
else:
	trace = None
	#~ trace = open("stream.txt","wb")
	class Stream:
		""" Class stream """
		def __init__(self, reader, writer):
			self.reader = reader
			self.writer = writer
			self.buffer = b""

		async def readline(self):
			""" The firt time, this method completely reads the stream.
			It then returns only the requested row. This significantly increases read performance. """
			pos = self.buffer.find(b"\r\n")
			if pos == -1:
				self.buffer += await self.reader.read(1440)
				pos = self.buffer.find(b"\r\n")
			if pos == -1:
				result = self.buffer
				self.buffer = b""
			else:
				result = self.buffer[:pos+2]
				self.buffer = self.buffer[pos+2:]
			return result

		async def read(self, length):
			""" Read data from the stream """
			if len(self.buffer) < length:
				data = await self.reader.read(length - len(self.buffer))
				self.buffer += data

			data = self.buffer[:length]
			l = len(data)
			self.buffer = self.buffer[length:]
			return data

		async def write(self, data):
			""" Write data in the stream """
			# print("<-      %s"%data[:-1])
			result = self.writer.write(data)
			if self.writer.is_closing():
				raise OSError(104,"Error")
			if trace:
				trace.write(data)
				trace.flush()

			if result is None:
				result = len(data)
			return result

		async def close(self):
			""" Close the stream """
			self.writer.close()


class Socket:
	""" Class stream which wrap socket """
	def __init__(self, socket):
		""" Constructor """
		self.socket = socket

	def read(self):
		""" Read data from the stream """
		data = self.socket.readlines()
		return data

	def write(self, data):
		""" Write data in the stream """
		length = self.socket.sendall(data)
		if length is None:
			length = len(data)
		return length

	def close(self):
		""" Close the stream """
		self.socket.close()


class Bytesio:
	""" Class stream which wrap BytesIO """
	def __init__(self):
		""" Constructor """
		self.streamio = BytesIO()

	async def read(self):
		""" Read data from the stream """
		return self.streamio.read()

	async def write(self, data):
		""" Write data in the stream """
		return self.streamio.write(data)

	async def close(self):
		""" Close the stream """
		self.streamio.close()


class Bufferedio:
	""" Bufferized bytes io stream """
	memorysize = [None]
	""" Class used to buffered stream write """
	def __init__(self, streamio, part=1440*20):
		""" Constructor """
		self.buffered = BytesIO()

		if Bufferedio.is_enough_memory():
			self.part = part
		else:
			self.part = None

		self.streamio = streamio

	@staticmethod
	def is_enough_memory():
		""" Indicate if it has enough memory """
		if Bufferedio.memorysize[0] is None:
			import gc
			try:
				# pylint: disable=no-member
				Bufferedio.memorysize[0]  = gc.mem_free()
			except:
				Bufferedio.memorysize[0]  = 256*1024

		if Bufferedio.memorysize[0] < 200*1024:
			return False
		return True

	async def read(self):
		""" Read data from the stream """
		return self.streamio.read()

	async def write(self, data):
		""" Write data in the stream """
		if self.part is None:
			result = len(data)
			await self.streamio.write(data)
		else:
			result = self.buffered.write(data)
			if self.buffered.tell() > self.part:
				await self.streamio.write(self.buffered.getvalue())
				self.buffered = BytesIO()
		return result

	async def close(self):
		""" Close the stream """
		try:
			if self.buffered.tell() > 0:
				await self.streamio.write(self.buffered.getvalue())
		finally:
			self.buffered.close()
 