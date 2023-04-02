# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" These classes are used to manage asynchronous stream. """
from io import BytesIO
from tools import filesystem

class Stream:
	""" Class stream """
	# trace = open("stream.txt","wb")
	trace = None
	def __init__(self, reader, writer):
		self.reader = reader
		self.writer = writer
		self.buffer = b""
		if filesystem.ismicropython():
			self.close      = self.close_mic
			self.awrite     = self.awrite_mic
			self.is_closing = self.is_closing_mic
		else:
			self.close      = self.close_pc
			self.awrite     = self.awrite_pc
			self.is_closing = self.is_closing_pc

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
		if Stream.trace:
			Stream.trace.write(b"\n# read\n")
			Stream.trace.write(data)
			Stream.trace.flush()
		return data

	async def write(self, data):
		""" Write data in the stream """
		result = await self.awrite(data)
		if self.is_closing():
			raise OSError(104,"Closed connection")
		if Stream.trace:
			Stream.trace.write(b"\n# write\n")
			Stream.trace.write(data)
			Stream.trace.flush()
		if result is None:
			result = len(data)
		else:
			result = -1
		return result

	async def awrite_mic(self, data):
		""" Awrite micropython """
		return await self.writer.awrite(data)

	async def awrite_pc(self, data):
		""" Awrite micropython """
		return self.writer.write(data)

	async def close_mic(self):
		""" Close the stream """
		await self.writer.aclose()

	async def close_pc(self):
		""" Close the stream """
		self.writer.close()

	def is_closing_pc(self):
		""" Check if it closed """
		return self.writer.is_closing()

	def is_closing_mic(self):
		""" Check if it closed """
		return False

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
 