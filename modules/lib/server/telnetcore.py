# Based on https://github.com/cpopp/MicroTelnetServer/blob/master/utelnet/utelnetserver.py
# Add user login
# pylint:disable=consider-using-f-string
# pylint:disable=consider-using-enumerate
""" Telnet class """
import sys
import errno
from io import IOBase
import time
from server.user import User
from tools import strings

class TelnetLogin:
	""" Class to manage the username and password """
	count_failed = [0]
	def __init__(self, output):
		""" Constructor """
		self.output = output
		if User.is_empty():
			self.footer()
			self.state = 2
		else:
			self.state = 0
		self.clean()
		self.header()
		self.refresh()

	def header(self):
		""" Show header """
		try:
			import wifi
			hostname = strings.tobytes(wifi.Station.get_hostname())
		except:
			hostname = strings.tobytes(sys.platform)
		message = b"# Telnet on '%s' started #"%hostname
		self.output.write(b"\r\n%s\r\n%s\r\n%s\r\n"%(b"#"*len(message), message, b"#"*len(message)))

	def footer(self):
		""" Show footer """
		self.output.write(b"\r\n%s\r\n"%(b"-"*30))

	def clean(self):
		""" Clean the login """
		self.input_buffer = b""
		self.input_char   = b""
		self.password     = b""
		self.login        = b""

	def input(self, b):
		""" Input value """
		# pylint:disable=attribute-defined-outside-init
		result = None
		self.input_char += b[0].to_bytes(1,"little")

		# Check if the character is complete
		if strings.is_key_ended(self.input_char):
			# If escape sequence detected
			if self.input_char[0] == 0x1B:
				# Ignore escape sequence
				self.input_char = b""
			# If return detected
			elif self.input_char[0] == 0x0D:
				result = self.input_buffer
				self.input_buffer = b""
				self.input_char = b""
			# If tabulation sequence detected
			elif self.input_char[0] == 0x09:
				# Ignore escape sequence
				self.input_char = b""
			# If line feed detected
			elif self.input_char[0] == 0x0A:
				self.input_char = b""
			# If delete detected
			elif self.input_char[0] == 0x7F or self.input_char[0] == 0x08:
				if len(self.input_buffer) > 0:
					self.input_buffer = strings.tobytes(strings.tostrings(self.input_buffer)[:-1])
				self.input_char = b""
			# Else other character
			else:
				self.input_buffer += self.input_char
				self.input_char = b""
		return result

	def refresh(self):
		""" Refresh the line displayed """
		if self.state == 0:
			self.output.write(strings.tostrings(b"\x1B[2K\rUsername : %s"%self.input_buffer))
		elif self.state == 1:
			self.output.write(strings.tostrings(b"\x1B[2K\rPassword : %s"%(b"*"*len(strings.tostrings(self.input_buffer)))))

	def valid(self, buffer):
		""" Valid data entered """
		result = False
		# pylint:disable=attribute-defined-outside-init
		if self.state == 0:
			self.login = buffer
			self.state += 1
			self.output.write("\n")
		elif self.state == 1:
			self.password = buffer
			self.state += 1
			self.output.write("\r\n")
			# If password is a success
			if User.check(self.login, self.password, display=False):
				if self.count_failed[0] >> 2:
					time.sleep(15)
				self.output.write(b"Login successful\r\n")
				self.footer()
				self.state += 1
				self.count_failed[0] = 0
				result = True
			else:
				self.count_failed[0] += 1
				duration = 3 + (30*(self.count_failed[0] >> 2))
				time.sleep(duration)
				self.output.write(b"Login failed\r\n")
				self.state = 0
			self.clean()
		return result

	def manage(self, character):
		""" Manage the login """
		result = False
		buffer = self.input(character)
		if buffer is not None:
			result = self.valid(buffer)
		self.refresh()
		return result

	def is_logged(self):
		""" Indicates if the login successful """
		return self.state >= 2

# Provide necessary functions for dupterm and replace telnet control characters that come in.
class TelnetWrapper(IOBase):
	""" Telnet wrapper class """
	def __init__(self, sock):
		# pylint: disable=super-init-not-called
		self.socket = sock
		self.discard_count = 0
		self.login = TelnetLogin(sock)

	def readinto(self, b):
		""" Read into the buffer """
		readbytes = 0
		for i in range(len(b)):
			try:
				byte = 0
				# discard telnet control characters and
				# null bytes
				while(byte == 0):
					byte = self.socket.recv(1)[0]
					if byte == 0xFF:
						self.discard_count = 2
						byte = 0
					elif self.discard_count > 0:
						self.discard_count -= 1
						byte = 0
				b[i] = byte
				readbytes += 1
			except (IndexError, OSError) as e:
				if type(e) == IndexError or len(e.args) > 0 and e.args[0] == errno.EAGAIN:
					if readbytes == 0:
						return None
					else:
						return readbytes
				else:
					raise
		if self.login.is_logged() is False:
			self.login.manage(b)
			b[0] = 0
		return readbytes

	def write(self, data):
		""" Write data """
		# we need to write all the data but it's a non-blocking socket
		# so loop until it's all written eating EAGAIN exceptions
		if self.login.is_logged():
			while len(data) > 0:
				try:
					written_bytes = self.socket.write(data)
					data = data[written_bytes:]
				except OSError as e:
					if len(e.args) > 0 and e.args[0] == errno.EAGAIN:
						# can't write yet, try again
						pass
					else:
						# something else...propagate the exception
						raise

	def close(self):
		self.socket.close()
