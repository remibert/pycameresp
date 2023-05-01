""" Parse url and get all content """
# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
import collections
import tools.strings
# url = b"http://user:passsword@192.168.1.28:8080/toto/json.htm?type=command&param=switchlight&idx=4&switchcmd=On&error=mon+error#my_anchor"

class UrlParser:
	""" Parse url """
	def __init__(self, url, http=False):
		""" Parser constructor """
		self.protocol = b""
		self.user     = b""
		self.password = b""
		self.host     = b""
		self.port     = b""
		self.path     = b""
		self.params   = collections.OrderedDict()
		self.anchor   = b""
		self.url      = url
		self.method   = b""
		self.parse(url, http)

	def parse(self, url, http=False):
		""" Parse the url """
		self.protocol = b""
		self.user     = b""
		self.password = b""
		self.host     = b""
		self.port     = b""
		self.path     = b""
		self.params   = collections.OrderedDict()
		self.anchor   = b""
		self.method   = b""
		self.url      = url

		if http:
			spl = url.split(b" ")
			url = b"http://localhost%s"%spl[1]
			self.method = spl[0]

		self.protocol, part_url  = UrlParser.parse_protocol(url)
		self.anchor, part_url    = UrlParser.parse_anchor(part_url)
		user_path_port, params   = UrlParser.parse_path_param(part_url)

		self.params              = UrlParser.parse_params(params)
		user_host, self.path     = UrlParser.parse_host(user_path_port)
		self.path = UrlParser.unquote(self.path)
		user_password, host_port = UrlParser.parse_user_host(user_host)
		self.user, self.password = UrlParser.parse_user_password(user_password)
		self.host, self.port     = UrlParser.parse_host_port(host_port)

	@staticmethod
	def parse_protocol(part_url):
		""" Parse and get the protocol """
		if part_url != b"":
			protocol = b""
			spl = part_url.split(b"://")
			if len(spl) > 1:
				protocol = spl[0]
				part_url = spl[1]
			return protocol, part_url
		else:
			return b"", b""

	@staticmethod
	def parse_anchor(part_url):
		""" Parse and get the anchor """
		if part_url != b"":
			anchor = b""
			spl = part_url.split(b"#")
			if len(spl) > 1:
				anchor = spl[1]
				part_url = spl[0]
			return anchor, part_url
		else:
			return b"", b""

	@staticmethod
	def parse_host(part_url):
		""" Parse and get the host """
		if part_url != b"":
			pos = part_url.find(b"/")
			if pos > 0:
				host = part_url[:pos]
				part_url = part_url[pos:]
			else:
				host = b""
			return host, part_url
		return b"", b""

	@staticmethod
	def parse_user_host(part_url):
		""" Parse and get the user and host """
		if part_url != b"":
			spl = part_url.split(b"@")
			if len(spl) > 1:
				user = spl[0]
				host = spl[1]
			else:
				user = b""
				host = part_url
			return user,host
		return b"", b""

	@staticmethod
	def parse_user_password(user_password):
		""" Parse and get the user and password """
		user     = b""
		password = b""
		if user_password != b"":
			spl = user_password.split(b":")
			if len(spl) > 1:
				user     = spl[0]
				password = spl[1]
		return user,password

	@staticmethod
	def parse_host_port(host_port):
		""" Parse and get the host and port """
		host = b""
		port = b""
		if host_port != b"":
			spl = host_port.split(b":")
			if len(spl) > 1:
				host = spl[0]
				port = spl[1]
			else:
				host = host_port
		return host,port

	@staticmethod
	def parse_path_param(path_param):
		""" Parse and get the path and parameters """
		path = b""
		params = b""
		if path_param != b"":
			spl = path_param.split(b"?")
			if len(spl) > 1:
				path = spl[0]
				params = spl[1]
			else:
				path = path_param
				params = b""
		return path, params

	@staticmethod
	def parse_params(part_url):
		""" Parse and get the parameters """
		params = collections.OrderedDict()
		if part_url != b"":
			pairs = part_url.split(b"&")
			for pair in pairs:
				param = [UrlParser.unquote(x) for x in pair.split(b"=", 1)]
				if len(param) == 1:
					param.append(True)
				name, value = param
				previous_value = params.get(name)
				if previous_value is not None:
					if previous_value == b'0' and value == b'':
						params[name] = b'1'
					else:
						if not isinstance(previous_value, list):
							params[name] = [previous_value]
						params[name].append(value)
				else:
					params[name] = value
		return params

	@staticmethod
	def unquote(url):
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

	@staticmethod
	def quote(text):
		""" Insert in the string the character not supported in an url """
		result = b""
		for char in text:
			if char == 0x2E or char == 0x5F or char == 0x2C or (char >= 0x30 and char < 0x39) or (char >= 0x41 and char < 0x5A) or (char >= 0x61 and char < 0x7A):
				result += char.to_bytes(1,"big")
			elif char == b" ":
				result += b"+"
			else:
				result += b"%%%02X"%char
		return result

	@staticmethod
	def adapt_value(value):
		""" Adapt value to url format """
		if type(value) == type(0):
			value = b"%d"%value
		elif type(value) == type(True):
			if value:
				value = b"1"
			else:
				value = b"0"
		elif type(value) == type(0.):
			value = b"%f"%value
		elif type(value) == type(b""):
			pass
		elif type(value) == type(""):
			value = tools.strings.tobytes(value)
		else:
			value = tools.strings.tobytes(value)
		return value

	def get_params(self):
		""" Get the parameters formated for an url """
		result = b""
		for key, value in self.params.items():
			result += UrlParser.quote(UrlParser.adapt_value(key)) + b"=" + UrlParser.quote(UrlParser.adapt_value(value)) + b"&"
		if len(result) > 1:
			result = result[:-1]
		return result

	def __repr__(self):
		""" Convert parse result intp string """
		result  = b"url      : '%s'\n"%self.url
		result += b"protocol : '%s'\n"%self.protocol
		result += b"host     : '%s'\n"%self.host
		result += b"port     : '%s'\n"%self.port
		result += b"user     : '%s'\n"%self.user
		result += b"password : '%s'\n"%self.password
		result += b"path     : '%s'\n"%self.path
		result += b"params   : %s\n"%tools.strings.tobytes(str(tools.strings.tostrings(self.params)))
		result += b"anchor   : '%s'\n"%self.anchor
		return tools.strings.tostrings(result)
