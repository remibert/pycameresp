# Based on https://github.com/cpopp/MicroTelnetServer/blob/master/utelnet/utelnetserver.py
# Add user login
import socket
import errno
from io import IOBase
from server import User
from tools import useful
import sys
import time

try:
	import wifi
	hostname = useful.tobytes(wifi.Station.getHostname())
except:
	hostname = useful.tobytes(sys.platform)
last_client_socket = None
server_socket = None

# Provide necessary functions for dupterm and replace telnet control characters that come in.
class TelnetWrapper(IOBase):
	def __init__(self, socket):
		self.socket = socket
		self.discard_count = 0
		if User.isEmpty():
			self.state = 3
		else:
			self.state = 0

		self.password = b""
		self.login = b""
		self.getlogin()
		
	def readinto(self, b):
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
		if self.state < 3:
			self.getlogin(b)
			b[0] = 0
		return readbytes

	def getlogin(self, b=None):
		global hostname
		result = b
		# Init state
		if self.state == 0:
			message = b"# Telnet on '%s' started #"%hostname
			self.socket.write(b"\r\n%s\r\n%s\r\n%s\r\n"%(b"#"*len(message), message, b"#"*len(message)))
			# If login password not defined
			if User.isEmpty():
				self.state = 3
			else:
				# Display enter password
				self.socket.write(b"Username :")
				self.state = 1
		# Login state
		elif self.state == 1:
			# If validation
			if b[0] == 0x0D or b[0] == 0x0A:
				self.socket.write(b"\r\nPassword :")
				self.state = 2
			# If backspace
			elif b[0] == 0x7F:
				if len(self.login) >= 1:
					self.login = self.login[:-1]
				self.socket.write("\r"+" "*80)
				self.socket.write("\rUsername :" + "*"*len(self.login))
			# If character ignored
			elif b[0] < 0x20 or b[0] > 0x7F:
				pass
			else:
				self.login += bytes([b[0]])
				self.socket.write("\rUsername :" + "*"*len(self.login))
		# Password state
		elif self.state == 2:
			# If validation
			if b[0] == 0x0D or b[0] == 0x0A:
				# If password is a success
				if User.check(self.login, self.password):
					self.state = 3
					self.password = b""
					self.login = b""
					self.socket.write(b"\r\n%s\r\n"%(b"-"*30))
				else:
					self.state = 1
					self.socket.write(b"\n\r\nUsername :")
					self.password = b""
					self.login = b""
			# If backspace
			elif b[0] == 0x7F:
				if len(self.password) >= 1:
					self.password = self.password[:-1]
				self.socket.write("\r"+" "*80)
				self.socket.write("\rPassword :" + "*"*len(self.password))
			# If character ignored
			elif b[0] < 0x20 or b[0] > 0x7F:
				pass
			else:
				self.password += bytes([b[0]])
				self.socket.write("\rPassword :" + "*"*len(self.password))
		return result

	def write(self, data):
		# we need to write all the data but it's a non-blocking socket
		# so loop until it's all written eating EAGAIN exceptions
		if self.state >= 3:
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

# Attach new clients to dupterm and 
# send telnet control characters to disable line mode
# and stop local echoing
def accept_telnet_connect(telnet_server):
	import uos
	global last_client_socket
	
	if last_client_socket:
		# close any previous clients
		uos.dupterm(None)
		last_client_socket.close()
	
	last_client_socket, remote_addr = telnet_server.accept()
	print("Telnet connected from : %s" % remote_addr[0])
	last_client_socket.setblocking(False)
	last_client_socket.setsockopt(socket.SOL_SOCKET, 20, uos.dupterm_notify)
	
	last_client_socket.sendall(bytes([255, 252, 34])) # dont allow line mode
	last_client_socket.sendall(bytes([255, 251, 1])) # turn off local echo
	
	uos.dupterm(TelnetWrapper(last_client_socket))

def stop():
	import uos
	global server_socket, last_client_socket
	uos.dupterm(None)
	if server_socket:
		server_socket.close()
	if last_client_socket:
		last_client_socket.close()

# start listening for telnet connections on port 23
def start(port=23):
	try:
		stop()
		global server_socket
		server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		
		ai = socket.getaddrinfo("0.0.0.0", port)
		addr = ai[0][4]
		
		server_socket.bind(addr)
		server_socket.listen(1)
		server_socket.setsockopt(socket.SOL_SOCKET, 20, accept_telnet_connect)
		
		print("Telnet start %d"%port)

	except Exception as err:
		print("Telnet not available '%s'"%str(err))
