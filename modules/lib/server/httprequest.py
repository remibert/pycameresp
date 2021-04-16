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

import collections
import server.stream
from tools import useful
import hashlib
import time
from binascii import hexlify
from tools.useful import log

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
		self.contentFile = None
		self.identifier = None
		self.request    = request

	def __del__(self):
		if self.contentFile != None:
			useful.remove(self.contentFile)

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

	def getExpiration(self, expiration):
		""" Get cookie expiration date """
		result = b"; Max-Age=%d"%expiration
		return result

	def getCookie(self, name):
		""" Get cookie value """
		try:
			return self.cookies.get(name, None)
		except:
			return None

	def setCookie(self, name, value=None, expiration=None):
		""" Set cookie """
		if value == None:
			if name in self.cookies:
				del self.cookies[name]
		else:
			self.cookies[name] = (value, expiration)

	def getHeader(self, name):
		""" Get the http request header """
		try:
			return self.headers.get(name, None)
		except:
			return None

	def setHeader(self, name, value):
		""" Set the http request header """
		if value == None:
			del self.headers[name]
		else:
			self.headers[name] = value

	def setMethod(self, method):
		""" Set http request method (POST or GET) """
		self.method = method

	def getPath(self):
		""" Get the path of the request or response """
		return self.path
	
	def setPath(self, path):
		""" Define the past of the request or response """
		self.path = path

	def addPart(self, part):
		""" Add part of the request. Used for multipart request """
		self.parts.append(part)

	def getStatus(self):
		""" Get the status value """
		return self.status

	def setStatus(self, status):
		""" Set the status value """
		self.status = status
		
	def setContent(self, content):
		""" Set the content of the request or response (can be an instance of html template) """
		if type(content) == type(""):
			self.content = ContentText(content)
		else:
			self.content = content
	
	def getContent(self):
		""" Get the content of the request or response """
		return self.content

	def getId(self):
		""" Get the unique identifier of the request or response. Used for multipart request """
		hash = hashlib.sha256()
		ids = b"%d"%time.time()
		hash.update(ids)
		return hexlify(hash.digest())[32:]

	async def unserialize(self, streamio):
		""" Unserialize the request or response in the stream """
		data = await streamio.readline()
		if data != b"":
			spl = data.split()
			self.method = spl[0]
			path = spl[1]
			proto = spl[2]
			if self.request == False:
				self.status = path
			paths = path.split(b"?", 1)
			if len(paths) > 1:
				self.unserializeParams(paths[1])
			self.path = self.unquote(paths[0])
			await self.unserializeHeaders(streamio)

	def unserializeParams(self, url):
		""" Extract parameters from url """
		if url:
			pairs = url.split(b"&")
			for pair in pairs:
				param = [self.unquote(x) for x in pair.split(b"=", 1)]
				if len(param) == 1:
					param.append(True)
				previousValue = self.params.get(param[0])
				if previousValue is not None:
					if not isinstance(previousValue, list):
						self.params[param[0]] = [previousValue]
					self.params[param[0]].append(param[1])
				else:
					self.params[param[0]] = param[1]

	async def readContent(self, streamio):
		length = int(self.headers.get(b"Content-Length","0"))
		# If data small write in memory
		if length < 4096:
			self.content = b""
			while len(self.content) < length:
				self.content += await streamio.read(int(self.headers.get(b"Content-Length","0")))
		# Data too big write in file
		else:
			self.contentFile = "%d.tmp"%id(self)
			content = open(self.contentFile, "wb")
			while content.tell() < length:
				content.write(await streamio.read(int(self.headers.get(b"Content-Length","0"))))
			content.close()

	def getContentFilename(self):
		""" Copy the content into file """
		if self.content != None:
			self.contentFile = "%d.tmp"%id(self)
			content = open(self.contentFile, "wb")
			content.write(self.content)
			content.close()
			self.content = None
		return self.contentFile

	async def unserializeHeaders(self, streamio):
		""" Extract http header """
		while True:
			header = await streamio.readline()
			if header == b"\r\n":
				if self.method == b"POST":
					await self.readContent(streamio)
					self.unserializeParams(self.content)
				elif self.request == False or self.method == b"PUT":
					await self.readContent(streamio)
				break
			name, value = header.split(b":", 1)
			if name == b"Cookie":
				cookies = value.split(b";")
				for cookie in cookies:
					cookieName,cookieValue=cookie.split(b"=")
					self.cookies[cookieName.strip()] = cookieValue.strip()
			else:
				self.headers[name] = value.strip()

	async def serialize(self, streamio):
		""" Serialize request or response in the stream """
		if self.request:
			result = await self.serializeRequest(streamio)
		else:
			result = await self.serializeResponse(streamio)
		return result
	
	async def serializeRequest(self, streamio):
		""" Serialize request with body """
		result = await streamio.write(b"%s %s %s\r\n"%(self.method, self.path, b"HTTP/1.1"))
		result += await self.serializeBody(streamio)
		return result
	
	async def serializeBody(self, streamio):
		""" Serialize body """
		result = 0
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
		if self.identifier == None and createIdentifier:
			self.identifier = self.getId()

		# Serialize http header
		for header, value in self.headers.items():
			if self.identifier != None:
				if header == b"Content-Type":
					value += b"; boundary=%s"%self.identifier
			result += await streamio.write(b"%s: %s\r\n"%(header, value))
		
		# Serialize cookies
		for cookie, value in self.cookies.items():
			if self.request:
				setget = b""
			else:
				setget = b"Set-"
			result += await streamio.write(b"%sCookie: %s=%s%s\r\n"%(setget, cookie, value[0], self.getExpiration(value[1])))

		noEnd = False
		# If content existing
		if self.content != None:
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
				result += await streamio.write(useful.htmlException(err))
		# If multipart detected
		elif len(self.parts) > 0:
			# If the header is a multipart
			if self.headers[b"Content-Type"] == b"multipart/form-data":
				length = 0
				# Set the size of identifier
				for part in self.parts:
					length += 2
					length += await part.getSize(self.identifier)
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

		if noEnd == False:
			# Terminate serialize request or response
			result += await streamio.write(b"\r\n")
		return result

	async def serializeResponse(self, streamio):
		""" Send response to client web browser """
		result = await streamio.write(b"HTTP/1.1 %s NA\r\n"%(self.status))
		result += await self.serializeBody(streamio)
		return result

class ContentText:
	""" Class that contains a text """
	def __init__(self, text, contentType=None):
		""" Constructor """
		self.text = text
		self.contentType = contentType
		if contentType == None:
			self.contentType = b"text/plain"
	
	async def serialize(self, streamio):
		""" Serialize text content """
		result = await streamio.write(b'Content-Type: %s\r\n\r\n'%(self.contentType))
		result += await streamio.write(self.text)
		return result

class ContentFile:
	""" Class that contains a file """
	def __init__(self, filename, contentType=None):
		""" Constructor """
		self.filename = filename
		if contentType == None:
			global MIMES
			ext = useful.splitext(useful.tostrings(filename))[1]
			self.contentType = MIMES.get(useful.tobytes(ext),b"text/plain")
		else:
			self.contentType = contentType
		
	async def serialize(self, streamio):
		""" Serialize file """
		try:
			with open(useful.tostrings(self.filename), "rb") as f:
				result = await streamio.write(b'Content-Type: %s\r\n\r\n'%(self.contentType))
				step = 1440
				buf = bytearray(step)
				f.seek(0,2)
				size = f.tell()
				f.seek(0)
				while size > 0:
					if size < step:
						buf = bytearray(size)
					length = f.readinto(buf)
					size -= length
					result += await streamio.write(buf)
		except Exception as err:
			result = await streamio.write(b'Content-Type: text/plain\r\n\r\n')
			result += await streamio.write(b"File %s not found"%useful.tobytes(self.filename))
		return result

class ContentBuffer:
	""" Class that contains a buffer """
	def __init__(self, filename, buffer, contentType=None):
		""" Constructor """
		self.filename = filename
		self.buffer = buffer
		if contentType == None:
			global MIMES
			ext = useful.splitext(useful.tostrings(filename))[1]
			self.contentType = MIMES.get(useful.tobytes(ext),b"text/plain")
		else:
			self.contentType = contentType
		
	async def serialize(self, streamio):
		""" Serialize a buffer """
		try:
			b = self.buffer[0]
			result = await streamio.write(b'Content-Type: %s\r\n\r\n'%(self.contentType))
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

	async def getSize(self, identifier):
		""" Get the size of this part """
		result = await self.serialize(identifier, server.stream.Bytesio())
		return result

class PartFile:
	""" Class that contains a file, used in multipart request or response """
	def __init__(self, name, filename, contentType):
		""" Constructor """
		self.name = name
		self.filename = filename
		self.contentType = contentType

	async def serializeHeader(self, identifier, streamio):
		""" Serialize multi part header of file """
		result = await streamio.write(b'Content-Disposition: form-data; name="%s"; filename="%s"\r\n'%(self.name, self.filename))
		result += await streamio.write(b'Content-Type: %s\r\n'%self.contentType)
		return result

	async def serialize(self, identifier, streamio):
		""" Serialize multi part file """
		result = await self.serializeHeader(identifier, streamio)
		result += await streamio.write(b"\r\n%s\r\n"%open(useful.tostrings(self.filename),"rb").read())
		result +=  await streamio.write(b"--%s"%identifier)
		return result
		
	async def getSize(self, identifier):
		""" Get the size of multi part file """
		headerSize = await self.serializeHeader(identifier, server.stream.Bytesio())
		fileSize = useful.filesize((useful.tostrings(self.filename)))
		return headerSize + fileSize + 4 + len(identifier) + 2

class PartBin(PartFile):
	""" Class that contains a binary data, used in multipart request or response """
	def __init__(self, name, filename, binary, contentType):
		PartFile.__init__(self, name, filename, contentType)
		self.binary = binary
	
	async def serialize(self, identifier, streamio):
		""" Serialize multi part binary data """
		result = await self.serializeHeader(identifier, streamio)
		result += await streamio.write(b"\r\n%s\r\n"%self.binary)
		result +=  await streamio.write(b"--%s"%identifier)
		return result

	async def getSize(self, identifier):
		""" Get the size of multi part binary data """
		headerSize = await self.serializeHeader(identifier, server.stream.Bytesio())
		fileSize = len(self.binary)
		return headerSize + fileSize + 4 + len(identifier) + 2

class HttpResponse(Http):
	""" Http response send to web browser client """
	def __init__(self, streamio, remoteaddr= b"", port = 0, name = ""):
		""" Constructor """
		Http.__init__(self, request=False, remoteaddr=remoteaddr, port=port, name=name)
		self.streamio = streamio

	async def send(self, content=None, status=b"200", headers={}):
		""" Send response to client web browser """
		self.setContent(content)
		self.setStatus(status)
		if headers != None:
			for name, value in headers.items():
				self.setHeader(name, value)
		return await self.serialize(self.streamio)

	async def sendError(self, status, content=None):
		""" Send error to the client web browser """
		return await self.send(status=status, content=content)

	async def sendOk(self, content=None):
		""" Send ok to the client web browser """
		return await self.sendError(status=b"200", content=content)

	async def sendFile(self, filename, mimeType=None, headers=None):
		""" Send a file to the client web browser """
		return await self.send(content=ContentFile(filename, mimeType), status=b"200", headers=headers)

	async def sendBuffer(self, filename, buffer, mimeType=None, headers=None):
		""" Send a file to the client web browser """
		return await self.send(content=ContentBuffer(filename, buffer, mimeType), status=b"200", headers=headers)

	async def sendPage(self, page):
		""" Send a template page to the client web browser """
		bytesio = server.stream.Bytesio()
		self.setContent(None)
		self.setStatus(b"200")
		await self.serialize(bytesio)
		await page.write(bytesio)
		await self.streamio.write(bytesio.streamio.getvalue())

	async def receive(self, streamio=None):
		""" Receive request from client """
		if streamio == None:
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
		if streamio == None:
			streamio = self.streamio
		await self.unserialize(streamio)

	async def send(self, streamio):
		""" Send request to server """
		if streamio == None:
			raise 1
			streamio = self.streamio
		await self.serialize(streamio)
