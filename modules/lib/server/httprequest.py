# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# historically based on :
# https://github.com/jczic/MicroWebSrv/blob/master/microWebSocket.py
# but I have modified a lot, there must still be some original functions.
""" These classes manage http responses and requests.
The set of request and response are in bytes format.
I no longer use strings, because they are between 20 and 30 times slower.
It may sound a bit more complicated, but it's a lot quick.
"""

import hashlib
import time
from binascii import hexlify, b2a_base64
import collections
import server.stream
from tools import useful

MIMES = {\
	b".txt"   : b"text/plain",
	b".py"    : b"text/plain",
	b".html"  : b"text/html",
	b".css"   : b"text/css",
	b".htm"   : b"text/html",
	b".csv"   : b"text/csv",
	b".js"    : b"application/javascript",
	b".xml"   : b"application/xml",
	b".xhtml" : b"application/xhtml+xml",
	b".json"  : b"application/json",
	b".zip"   : b"application/zip",
	b".pdf"   : b"application/pdf",
	b".ts"    : b"application/typescript",
	b".woff"  : b"font/woff",
	b".woff2" : b"font/woff2",
	b".ttf"   : b"font/ttf",
	b".otf"   : b"font/otf",
	b".jpg"   : b"image/jpeg",
	b".png"   : b"image/png",
	b".gif"   : b"image/gif",
	b".jpeg"  : b"image/jpeg",
	b".svg"   : b"image/svg+xml",
	b".ico"   : b"image/x-icon"
}

class Http:
	""" Http request or reponse """
	def __init__(self, request = True, remoteaddr= b"", port = 0, name=""):
		""" Constructor from http request or response """
		self.port       = port
		self.name       = name
		self.remoteaddr = remoteaddr
		self.path       = b""
		self.method     = b"POST"
		self.headers    = collections.OrderedDict()
		self.params     = collections.OrderedDict()
		self.cookies    = collections.OrderedDict()
		self.parts      = []
		self.status     = 0
		self.content    = None
		self.content_file = None
		self.identifier = None
		self.request    = request

	def __del__(self):
		if self.content_file is not None:
			useful.remove(self.content_file)

	def quote(self, text):
		""" Insert in the string the character not supported in an url """
		result = b""
		for char in text:
			if (ord(char) >= 0x41 and ord(char) < 0x5A) or (ord(char) >= 0x61 and ord(char) < 0x7A):
				result += char
			elif char == b" ":
				result += b"+"
			else:
				result += b"%%%02X"%ord(char)
		return result

	def unquote(self, url):
		""" Remove from a string special character in the url """
		url = url.replace(b'+', b' ')
		spl = url.split(b'%')
		try :
			result = spl[0]
			for part in range(1, len(spl)) :
				try :
					result += bytes([int(spl[part][:2], 16)]) + spl[part][2:]
				except :
					result += b'%' + spl[part]
			return result
		except :
			return url

	def get_expiration(self, expiration):
		""" Get cookie expiration date """
		result = b"; Max-Age=%d"%expiration
		return result

	def get_cookie(self, name):
		""" Get cookie value """
		try:
			return self.cookies.get(name, None)
		except:
			return None

	def set_cookie(self, name, value=None, expiration=None):
		""" Set cookie """
		if value is None:
			if name in self.cookies:
				del self.cookies[name]
		else:
			self.cookies[name] = (value, expiration)

	def get_header(self, name):
		""" Get the http request header """
		try:
			return self.headers.get(name, None)
		except:
			return None

	def set_header(self, name, value):
		""" Set the http request header """
		if value is None:
			del self.headers[name]
		else:
			self.headers[name] = value

	def set_method(self, method):
		""" Set http request method (POST or GET) """
		self.method = method

	def get_path(self):
		""" Get the path of the request or response """
		return self.path

	def set_path(self, path):
		""" Define the past of the request or response """
		self.path = path

	def add_part(self, part):
		""" Add part of the request. Used for multipart request """
		self.parts.append(part)

	def get_status(self):
		""" Get the status value """
		return self.status

	def set_status(self, status):
		""" Set the status value """
		self.status = status

	def set_content(self, content):
		""" Set the content of the request or response (can be an instance of html template) """
		if type(content) == type(""):
			self.content = ContentText(content)
		else:
			self.content = content

	def get_content(self):
		""" Get the content of the request or response """
		return self.content

	def get_id(self):
		""" Get the unique identifier of the request or response. Used for multipart request """
		hash_ = hashlib.sha256()
		ids = b"%d"%time.time()
		hash_.update(ids)
		return hexlify(hash_.digest())[32:]

	async def unserialize(self, streamio):
		""" Unserialize the request or response in the stream """
		data = await streamio.readline()
		if data != b"":
			spl = data.split()
			self.method = spl[0]
			path = spl[1]
			proto = spl[2]
			if self.request is False:
				self.status = path
			paths = path.split(b"?", 1)
			if len(paths) > 1:
				self.unserialize_params(paths[1])
			self.path = self.unquote(paths[0])
			await self.unserialize_headers(streamio)

	def unserialize_params(self, url):
		""" Extract parameters from url """
		if url:
			pairs = url.split(b"&")
			for pair in pairs:
				param = [self.unquote(x) for x in pair.split(b"=", 1)]
				if len(param) == 1:
					param.append(True)
				previousValue = self.params.get(param[0])
				if previousValue is not None:
					if previousValue == b'0' and param[1] == b'':
						self.params[param[0]] = b'1'
					else:
						if not isinstance(previousValue, list):
							self.params[param[0]] = [previousValue]
						self.params[param[0]].append(param[1])
				else:
					self.params[param[0]] = param[1]

	async def read_content(self, streamio):
		""" Read the content of http request """
		length = int(self.headers.get(b"Content-Length","0"))
		# If data small write in memory
		if length < 4096:
			self.content = b""
			while len(self.content) < length:
				self.content += await streamio.read(int(self.headers.get(b"Content-Length","0")))
		# Data too big write in file
		else:
			self.content_file = "%d.tmp"%id(self)
			try:
				content = open(self.content_file, "wb")
				while content.tell() < length:
					content.write(await streamio.read(int(self.headers.get(b"Content-Length","0"))))
			finally:
				content.close()

	def get_content_filename(self):
		""" Copy the content into file """
		if self.content is not None:
			self.content_file = "%d.tmp"%id(self)
			try:
				content = open(self.content_file, "wb")
				content.write(self.content)
			finally:
				content.close()
			self.content = None
		return self.content_file

	async def unserialize_headers(self, streamio):
		""" Extract http header """
		while True:
			header = await streamio.readline()
			if header == b"\r\n":
				if self.method == b"POST":
					await self.read_content(streamio)
					self.unserialize_params(self.content)
				elif self.request is False or self.method == b"PUT":
					await self.read_content(streamio)
				break
			name, value = header.split(b":", 1)
			if name == b"Cookie":
				cookies = value.split(b";")
				for cookie in cookies:
					cookieName,cookieValue=cookie.split(b"=")
					self.cookies[cookieName.strip()] = cookieValue.strip()
			else:
				self.headers[name] = value.strip()

	async def serialize(self, streamio, page=None):
		""" Serialize request or response in the stream """
		io = server.stream.Bufferedio(streamio)
		result = await self.serialize_header(io)
		result += await self.serialize_body(io)
		if page:
			await page.write(io)
		await io.close()
		return result

	async def serialize_header(self, streamio):
		""" Serialize the header of http request or response """
		if self.request:
			result = await streamio.write(b"%s %s %s\r\n"%(self.method, self.path, b"HTTP/1.1"))
		else:
			result = await streamio.write(b"HTTP/1.1 %s NA\r\n"%(self.status))

		try:
			createIdentifier = False
			if len(self.parts) > 0:
				createIdentifier = True
			# If multipart request detected
			if b"multipart" in self.headers[b"Content-Type"] :
				createIdentifier = True
		except:
			pass

		# If identifier required (multipart request)
		if self.identifier is None and createIdentifier:
			self.identifier = self.get_id()

		# Serialize http header
		for header, value in self.headers.items():
			if self.identifier is not None:
				if header == b"Content-Type":
					value += b"; boundary=%s"%self.identifier
			result += await streamio.write(b"%s: %s\r\n"%(header, value))

		# Serialize cookies
		for cookie, value in self.cookies.items():
			if self.request:
				setget = b""
			else:
				setget = b"Set-"
			result += await streamio.write(b"%sCookie: %s=%s%s\r\n"%(setget, cookie, value[0], self.get_expiration(value[1])))
		return result

	async def serialize_body(self, streamio):
		""" Serialize body """
		result = 0
		noEnd = False
		# If content existing
		if self.content is not None:
			try:
				# If content is a bytes string
				if type(self.content) == type(b""):
					result += await streamio.write(b'Content-Type: text/plain\r\n\r\n')
					result += await streamio.write(self.content)
				else:
					# Serialize object
					result += await self.content.serialize(streamio)
					noEnd = True
			except Exception as err:
				# Serialize error detected
				result += await streamio.write(b'Content-Type: text/plain\r\n\r\n')
				result += await streamio.write(useful.tostrings(useful.exception(err)))
		# If multipart detected
		elif len(self.parts) > 0:
			# If the header is a multipart
			if self.headers[b"Content-Type"] == b"multipart/form-data":
				length = 0
				# Set the size of identifier
				for part in self.parts:
					length += 2
					length += await part.get_size(self.identifier)
				length += len(self.identifier)
				length += 6

				# Write multipart identifier
				result += await streamio.write(b"Content-Length: %d\r\n\r\n"%(length))
				result += await streamio.write(b"--%s"%self.identifier)

			# Serialize all parts of the multipart
			for part in self.parts:
				result += await streamio.write(b"\r\n")
				result += await part.serialize(self.identifier, streamio)

			# Terminate multipart request
			if self.headers[b"Content-Type"] != b"multipart/x-mixed-replace":
				result += await streamio.write(b"--")

		if noEnd is False:
			# Terminate serialize request or response
			result += await streamio.write(b"\r\n")
		return result

class ContentText:
	""" Class that contains a text """
	def __init__(self, text, content_type=None):
		""" Constructor """
		self.text = text
		self.content_type = content_type
		if content_type is None:
			self.content_type = b"text/plain"

	async def serialize(self, streamio):
		""" Serialize text content """
		result = await streamio.write(b'Content-Type: %s\r\n\r\n'%(self.content_type))
		result += await streamio.write(self.text)
		return result

class ContentFile:
	""" Class that contains a file """
	def __init__(self, filename, content_type=None, base64=False):
		""" Constructor """
		if type(filename) == type([]):
			self.filenames = filename
		else:
			self.filenames = [filename]
		self.base64 = base64
		if content_type is None:
			global MIMES
			ext = useful.splitext(useful.tostrings(self.filenames[0]))[1]
			self.content_type = MIMES.get(useful.tobytes(ext),b"text/plain")
		else:
			self.content_type = content_type

	async def serialize(self, streamio):
		""" Serialize file """
		found = False
		try:
			f = None
			# print("Begin send %s"%useful.tostrings(self.filename))
			for filename in self.filenames:
				if useful.exists(filename):
					f = open(useful.tostrings(filename), "rb")
					if found is False:
						result = await streamio.write(b'Content-Type: %s\r\n\r\n'%(self.content_type))
					found = True
					if server.stream.Bufferedio.is_enough_memory():
						step = 1440*10
					else:
						step = 512
					buf = bytearray(step)
					f.seek(0,2)
					size = f.tell()
					f.seek(0)

					if self.base64 and step % 3 != 0:
						step = (step//3)*3

					lengthWritten = 0

					while size > 0:
						if size < step:
							buf = bytearray(size)
						length = f.readinto(buf)
						size -= length
						if self.base64:
							lengthWritten += await streamio.write(b2a_base64(buf))
						else:
							lengthWritten += await streamio.write(buf)
					# print("End send %s"%useful.tostrings(self.filename))
					result += lengthWritten
		except Exception as err:
			pass
		finally:
			if f:
				f.close()
		if found is False:
			result = await streamio.write(b'Content-Type: text/plain\r\n\r\n')
			filenames = b""
			for filename in self.filenames:
				filenames += useful.tobytes(filename) + b" "
			result += await streamio.write(b"File %s not found"%useful.tobytes(filename))
		return result

class ContentBuffer:
	""" Class that contains a buffer """
	def __init__(self, filename, buffer, content_type=None):
		""" Constructor """
		self.filename = filename
		self.buffer = buffer
		if content_type is None:
			global MIMES
			ext = useful.splitext(useful.tostrings(filename))[1]
			self.content_type = MIMES.get(useful.tobytes(ext),b"text/plain")
		else:
			self.content_type = content_type

	async def serialize(self, streamio):
		""" Serialize a buffer """
		try:
			b = self.buffer[0]
			result = await streamio.write(b'Content-Type: %s\r\n\r\n'%(self.content_type))
			result += await streamio.write(useful.tobytes(self.buffer))
		except Exception as err:
			result = await streamio.write(b'Content-Type: text/plain\r\n\r\n')
			result += await streamio.write(b"Nothing")
		return result

class PartText:
	""" Class that contains a text, used in multipart request or response """
	def __init__(self, name, value):
		""" Constructor """
		self.name  = name
		self.value = value

	async def serialize(self, identifier, streamio):
		""" Serialize multipart text part """
		result = await streamio.write(b'Content-Disposition: form-data; name="%s"\r\n'%(self.name))
		result += await streamio.write(b'Content-Type: text/plain \r\n')
		result += await streamio.write(b"\r\n%s\r\n"%self.value)
		result += await streamio.write(b"--%s"%identifier)
		return result

	async def get_size(self, identifier):
		""" Get the size of this part """
		result = await self.serialize(identifier, server.stream.Bytesio())
		return result

class PartFile:
	""" Class that contains a file, used in multipart request or response """
	def __init__(self, name, filename, content_type):
		""" Constructor """
		self.name = name
		self.filename = filename
		self.content_type = content_type

	async def serialize_header(self, identifier, streamio):
		""" Serialize multi part header of file """
		result = await streamio.write(b'Content-Disposition: form-data; name="%s"; filename="%s"\r\n'%(self.name, self.filename))
		result += await streamio.write(b'Content-Type: %s\r\n'%self.content_type)
		return result

	async def serialize(self, identifier, streamio):
		""" Serialize multi part file """
		result = await self.serialize_header(identifier, streamio)
		try:
			part = b""
			file = open(useful.tostrings(self.filename),"rb")
			part = file.read()
		finally:
			file.close()
		result += await streamio.write(b"\r\n%s\r\n"%part)
		result +=  await streamio.write(b"--%s"%identifier)
		return result

	async def get_size(self, identifier):
		""" Get the size of multi part file """
		headerSize = await self.serialize_header(identifier, server.stream.Bytesio())
		fileSize = useful.filesize((useful.tostrings(self.filename)))
		return headerSize + fileSize + 4 + len(identifier) + 2

class PartBin(PartFile):
	""" Class that contains a binary data, used in multipart request or response """
	def __init__(self, name, filename, binary, content_type):
		PartFile.__init__(self, name, filename, content_type)
		self.binary = binary

	async def serialize(self, identifier, streamio):
		""" Serialize multi part binary data """
		result = await self.serialize_header(identifier, streamio)
		result += await streamio.write(b"\r\n%s\r\n"%self.binary)
		result +=  await streamio.write(b"--%s"%identifier)
		return result

	async def get_size(self, identifier):
		""" Get the size of multi part binary data """
		headerSize = await self.serialize_header(identifier, server.stream.Bytesio())
		fileSize = len(self.binary)
		return headerSize + fileSize + 4 + len(identifier) + 2

class HttpResponse(Http):
	""" Http response send to web browser client """
	def __init__(self, streamio, remoteaddr= b"", port = 0, name = ""):
		""" Constructor """
		Http.__init__(self, request=False, remoteaddr=remoteaddr, port=port, name=name)
		self.streamio = streamio

	async def send(self, content=None, status=b"200", headers=None):
		""" Send response to client web browser """
		if headers is None:
			headers = {}
		self.set_content(content)
		self.set_status(status)
		if headers is not None:
			for name, value in headers.items():
				self.set_header(name, value)
		return await self.serialize(self.streamio)

	async def send_error(self, status, content=None):
		""" Send error to the client web browser """
		return await self.send(status=status, content=content)

	async def send_ok(self, content=None):
		""" Send ok to the client web browser """
		return await self.send_error(status=b"200", content=content)

	async def send_file(self, filename, mimeType=None, headers=None, base64=False):
		""" Send a file to the client web browser """
		return await self.send(content=ContentFile(filename, mimeType, base64), status=b"200", headers=headers)

	async def send_buffer(self, filename, buffer, mimeType=None, headers=None):
		""" Send a file to the client web browser """
		return await self.send(content=ContentBuffer(filename, buffer, mimeType), status=b"200", headers=headers)

	async def send_page(self, page):
		""" Send a template page to the client web browser """
		self.set_content(None)
		self.set_status(b"200")
		await self.serialize(self.streamio, page)

	async def receive(self, streamio=None):
		""" Receive request from client """
		if streamio is None:
			streamio = self.streamio
		await self.unserialize(streamio)

class HttpRequest(Http):
	""" Http request received from web browser client """
	def __init__(self, streamio, remoteaddr= b"", port = 0, name=""):
		""" Constructor from http request """
		Http.__init__(self, request=True, remoteaddr=remoteaddr, port=port, name=name)
		self.streamio    = streamio

	async def receive(self, streamio=None):
		""" Receive request from client """
		if streamio is None:
			streamio = self.streamio
		await self.unserialize(streamio)

	async def send(self, streamio):
		""" Send request to server """
		if streamio is None:
			streamio = self.streamio
		await self.serialize(streamio)
