# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# historically based on :
# https://github.com/robert-hh/FTP-Server-for-ESP8266-ESP32-and-PYBD/blob/master/ftp.py
# but I have modified a lot, there must still be some original functions.
""" Ftp server implementation core class """
import socket
import os
import time
import uos
from server import stream
from server.server import Server
from server.user import User
from wifi.accesspoint import AccessPoint
from wifi.station import Station
from tools import useful, fnmatch

MONTHS  = [b"Jan", b"Feb", b"Mar", b"Apr", b"May", b"Jun", b"Jul", b"Aug", b"Sep", b"Oct", b"Nov", b"Dec"]

class FtpServerCore:
	""" Ftp implementation server core """
	portbase = [12345]
	def __init__(self):
		""" Ftp constructor method """
		self.portbase[0] += 1
		self.dataport = self.portbase[0]
		self.pasvsocket = None
		self.addr = b""
		self.user = b""
		self.password = b""
		self.path = b""
		self.cwd = b"/"
		self.fromname = None
		if useful.ismicropython():
			self.root = b""
			self.path_length = 64
		else:
			self.root = useful.tobytes(os.getcwd() + "/")
			self.root = b"/Users/remi/Downloads/ftp/"
			self.path_length = 256
		self.command = b""
		self.payload = b""

		self.datasocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.datasocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.datasocket.bind(socket.getaddrinfo("0.0.0.0", self.dataport)[0][4])
		self.datasocket.listen(1)
		self.datasocket.settimeout(None)
		self.data_addr = None
		self.quit = None
		self.received = None
		self.remoteaddr = None
		self.client = None
		useful.syslog(b"[FTP] Open data %d"%self.dataport)

	def get_ip(self):
		""" Get the ip address of the board """
		if Station.is_ip_on_interface(self.remoteaddr):
			result = useful.tobytes(Station.get_info()[0])
		else:
			result = useful.tobytes(AccessPoint.get_info()[0])
		return result

	def close(self):
		""" Close all ftp connections """
		self.close_pasv()
		if self.datasocket:
			self.datasocket.close()
			self.datasocket = None

	def __del__(self):
		""" Destroy ftp instance """
		self.close()

	def get_file_description(self, filename, typ, size, date, now, full):
		""" Build list of file description """
		if full:
			file_permissions = b"drwxr-xr-x" if (typ & 0xF000 == 0x4000) else b"-rw-r--r--"

			d = time.localtime(date)
			year,month,day,hour,minute,_,_,_ = d[:8]

			if year != now[0] and month != now[1]:
				file_date = b"%s %2d  %4d"%(MONTHS[month-1], day, year)
			else:
				file_date = b"%s %2d %02d:%02d"%(MONTHS[month-1], day, hour, minute)
			description = b"%s    1 owner group %10d %s %s\r\n"%(file_permissions, size, file_date, useful.tobytes(filename))
		else:
			description = useful.tobytes(filename) + b"\r\n"
		return description

	def send_file_list_with_pattern(self, path, stream_, full, now, pattern=None):
		""" Send the list of file with pattern """
		description = b""
		quantity = 0
		counter = 0
		for fileinfo in uos.ilistdir(useful.tostrings(path)):
			filename = fileinfo[0]
			typ = fileinfo[1]
			if len(fileinfo) > 3:
				size = fileinfo[3]
			else:
				size = 0
			if pattern is None:
				accepted = True
			else:
				accepted = fnmatch(useful.tostrings(filename), useful.tostrings(pattern))
			if accepted:
				if quantity > 100:
					date = 0
				else:
					sta = (0,0,0,0,0,0,0,0,0)
					try:
						# If it is a file
						if not (typ & 0xF000 == 0x4000):
							sta = useful.fileinfo(useful.tostrings(useful.abspathbytes(path,useful.tobytes(filename))))
					except Exception:
						pass
					date = sta[8]

				description += self.get_file_description(filename, typ, size, date, now, full)
				counter += 1
				if counter == 20:
					counter = 0
					stream_.write(description)
					description = b""
			quantity += 1
		if description != b"":
			stream_.write(description)

	def send_file_list(self, path, stream_, full):
		""" Send the list of file """
		now = useful.now()
		try:
			self.send_file_list_with_pattern(path, stream_, full, now)
		except Exception as err:
			useful.syslog(err)
			pattern = path.split(b"/")[-1]
			path = path[:-(len(pattern) + 1)]
			if path == b"":
				path = b"/"
			self.send_file_list_with_pattern(path, stream_, full, now, pattern)

	async def send_ok(self):
		""" Send ok to ftp client """
		await self.send_response(250,b"OK")

	async def send_response(self, code, message):
		""" Send response to ftp client """
		useful.syslog(b"[FTP] %d %s"%(code, message))
		await self.client.write(b'%d %s\r\n'%(code,message))

	async def send_error(self, err):
		""" Send error to ftp client """
		showError = False
		if type(err) != type(b""):
			if useful.ismicropython():
				if type(err) != type(OSError):
					showError = True
			else:
				if isinstance(err,FileNotFoundError) or isinstance(err,NotADirectoryError):
					showError = False
				else:
					showError = True
		if showError:
			useful.syslog(err, msg=b"[FTP] cmd='%s' cwd='%s' root='%s' path='%s' payload='%s'"%(self.command, self.cwd, self.root, self.path, self.payload))
		await self.send_response(550, b"Failed")

	async def USER(self):
		""" Ftp command USER """
		if User.get_user() == b"":
			await self.send_response(230, b"User Logged In.")
		else:
			self.user = self.path[1:]
			await self.send_response(331, b"User known, enter password")

	async def PASS(self):
		""" Ftp command PASS """
		self.password = self.path[1:]
		if User.check(self.user, self.password, False):
			await self.send_response(230, b"Logged in.")
		else:
			await self.send_response(430, b"Invalid username or password")

	async def SYST(self):
		""" Ftp command SYST """
		await self.send_response(215, b"UNIX Type: L8")

	async def NOOP(self):
		""" Ftp command NOOP """
		await self.send_response(200, b"OK")

	async def FEAT(self):
		""" Ftp command FEAT """
		await self.send_response(211, b"no-features")

	async def XPWD(self):
		""" Ftp command XPWD """
		await self.PWD()

	async def PWD(self):
		""" Ftp command PWD """
		await self.send_response(257,b'"%s" is current directory.'%self.cwd)

	async def XCWD(self):
		""" Ftp command XCWD """
		await self.CWD()

	async def CWD(self):
		""" Ftp command CWD """
		if len(self.path) <= self.path_length:
			try:
				dd = os.listdir(useful.tostrings(self.root + self.path))
				self.cwd = self.path
				await self.send_response(250,b"CWD command successful.")
			except Exception as err:
				useful.syslog(err)
				await self.send_error(b"Path not existing")
		else:
			await self.send_error(b"Path too long")

	async def CDUP(self):
		""" Ftp command CDUP """
		self.cwd = useful.abspathbytes(self.cwd, b"..")
		await self.send_ok()

	async def TYPE(self):
		""" Ftp command TYPE """
		await self.send_response(200, b"Binary transfer mode active.")

	async def SIZE(self):
		""" Ftp command SIZE """
		size = useful.filesize(useful.tostrings(self.root + self.path))
		await self.send_response(213, b"%d"%(size))

	async def PASV(self):
		""" Ftp command PASV """
		await self.send_response(227, b"Entering Passive Mode (%s,%d,%d)"%(self.addr.replace(b'.',b','), self.dataport>>8, self.dataport%256))
		self.close_pasv()
		self.pasvsocket, self.data_addr = self.datasocket.accept()
		useful.syslog(b"[FTP] PASV Accepted")

	async def PORT(self):
		""" Ftp command PORT """
		items = self.payload.split(b",")
		if len(items) >= 6:
			self.data_addr = b'.'.join(items[:4])
			if self.data_addr == b"127.0.1.1":
				self.data_addr = self.remoteaddr
			self.dataport = int(items[4]) * 256 + int(items[5])
			self.close_pasv()
			self.pasvsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.pasvsocket.settimeout(1000)
			self.pasvsocket.connect((self.data_addr, self.dataport))
			useful.syslog("[FTP] Data connection with: %s"%useful.tostrings(self.data_addr))
			await self.send_response(200, b"OK")
		else:
			await self.send_response(504, b"Fail")

	async def NLST(self):
		""" Ftp command NLST """
		await self.LIST()

	async def LIST(self):
		""" Ftp command LIST """
		if not self.payload.startswith(b"-"):
			place = self.path
		else:
			place = self.cwd
		await self.send_response(150, b"Connection accepted.") # Start list files
		listsocket = stream.Socket(self.pasvsocket)
		useful.syslog("[FTP] List '%s'"%(useful.tostrings(self.root+place)))
		self.send_file_list(self.root + place, listsocket, self.command == b"LIST" or self.payload == b"-l")
		listsocket.close()
		await self.send_response(226, b"Transfert complete.") # End list files
		self.close_pasv()

	async def STAT(self):
		""" Ftp command STAT """
		if self.payload == b"":
			await self.send_response(211, b"Connected to (%s)"%self.remoteaddr[0])
			await self.send_response(211, b"Data address (%s)"%self.addr)
			await self.send_response(211, b"TYPE: Binary STRU: File MODE: Stream")
		else:
			await self.send_response(213,b"Directory listing:")
			useful.syslog("[FTP] List '%s'"%useful.tostrings(self.root+self.path))
			self.send_file_list(self.root + self.path, self.client, True)
			await self.send_response(213, b"Stat end")

	async def RETR(self):
		""" Ftp command RETR """
		await self.send_response(150, b"Start send file")
		useful.syslog("[FTP] Send file '%s'"%useful.tostrings(self.root+self.path))
		filename = self.root + self.path

		if useful.ismicropython():
			buffer_size = 1440
			chunk = bytearray(buffer_size)
			with open(useful.tostrings(filename), "r") as file:
				length = file.readinto(chunk)
				while length > 0:
					# pylint: disable=no-member
					sent = self.pasvsocket.write(chunk[:length])
					length = file.readinto(chunk)
		else:
			with open(useful.tostrings(filename), "rb") as file:
				self.pasvsocket.sendall(file.read())
		await self.send_response(226, b"End send file")
		self.close_pasv()

	def close_pasv(self):
		""" Close PASV connection """
		if self.pasvsocket is not None:
			useful.syslog(b"[FTP] Close PASV")
			self.pasvsocket.close()
			self.pasvsocket = None

	def write_file(self, path, dataclient):
		""" Write ftp received """
		chunk = bytearray(1440)
		with open(useful.tostrings(path), "wb") as file:
			length = dataclient.readinto(chunk)
			while length > 0:
				file.write(chunk, length)
				length = dataclient.readinto(chunk)

	async def STOR(self):
		""" Ftp command STOR """
		await self.send_response(150, b"Start receive file")
		useful.syslog("[FTP] Receive file '%s'"%useful.tostrings(self.root + self.path))
		filename = self.root + self.path

		if useful.ismicropython():
			try:
				self.write_file(filename, self.pasvsocket)
			except Exception as err:
				useful.syslog(err)
				directory, file = useful.split(useful.tostrings(filename))
				useful.makedir(directory, True)
				self.write_file(filename, self.pasvsocket)
		else:
			with open(filename, "wb") as file:
				data = b" "
				while len(data) > 0:
					data = self.pasvsocket.recv(1440)
					file.write(data)
				data = b""
		await self.send_response(226, b"End receive file")
		self.close_pasv()

	async def DELE(self):
		""" Ftp command DELE """
		useful.syslog("[FTP] Delete '%s'"%useful.tostrings(self.root + self.path))
		os.remove(useful.tostrings(self.root + self.path))
		await self.send_ok()

	async def XRMD(self):
		""" Ftp command XRMD """
		await self.RMD()

	async def RMD(self):
		""" Ftp command RMD """
		os.rmdir(useful.tostrings(self.root + self.path))
		await self.send_ok()

	async def XMKD(self):
		""" Ftp command XMKD """
		await self.MKD()

	async def MKD(self):
		""" Ftp command MKD """
		os.mkdir(useful.tostrings(self.root + self.path))
		await self.send_ok()

	async def RNFR(self):
		""" Ftp command RNFR """
		self.fromname = self.path
		await self.send_response(350, b"Rename from")

	async def RNTO(self):
		""" Ftp command RNTO """
		if self.fromname is not None:
			useful.syslog("[FTP] Rename '%s' to '%s'"%(useful.tostrings(self.root + self.fromname), useful.tostrings(self.root + self.path)))
			os.rename(useful.tostrings(self.root + self.fromname), useful.tostrings(self.root + self.path))
			await self.send_ok()
		else:
			await self.send_error(self.fromname)
		self.fromname = None

	async def QUIT(self):
		""" Ftp command QUIT """
		self.quit = True
		await self.send_response(221, b"Bye.")

	async def unsupported_command(self):
		""" Ftp unknown command """
		await self.send_response(502, b"Unsupported command")

	async def receive_command(self):
		""" Ftp command reception """
		Server.slow_down()
		try:
			self.received = await self.client.readline()
		except Exception as err:
			useful.syslog(err)
			useful.syslog(b"[FTP] Reset connection")
			self.quit = True

		if len(self.received) <= 0:
			self.quit = True
		else:
			self.received = self.received.rstrip(b"\r\n")
			if useful.tobytes(self.received[:4]) == b"PASS":
				message = b"PASS ????"
			else:
				message = self.received
			self.command = self.received.split(b" ")[0].upper()
			self.payload = self.received[len(self.command):].lstrip()
			self.path = useful.abspathbytes(self.cwd, self.payload)
			useful.syslog(b"[FTP] '%s' id=%08X cwd='%s' payload='%s' path='%s'"%(message, id(self), self.cwd, self.payload, self.path))

	async def treat_command(self):
		""" Treat ftp command """
		Server.slow_down()
		if self.quit is False:
			try:
				command = useful.tostrings(self.command)
				if hasattr(self, command):
					callback = getattr(self, command)

					if self.command not in [b"USER",b"PASS"]:
						if User.check(self.user, self.password):
							await callback()
						else:
							await self.send_response(430, b"Invalid username or password")
					else:
						await callback()
				else:
					await self.unsupported_command()
			except Exception as err:
				useful.syslog(err)
				await self.send_error(err)

	async def on_connection(self, reader, writer):
		""" Asyncio on ftp connection method """
		Server.slow_down()
		self.remoteaddr = useful.tobytes(writer.get_extra_info('peername')[0])
		self.addr = self.get_ip()
		useful.syslog("[FTP] Connected from %s"%useful.tostrings(self.remoteaddr))
		self.client = stream.Stream(reader, writer)
		try:
			await self.send_response(220, b"Ftp " + useful.tobytes(os.uname()[4]) + b".")
			self.quit = False
			while self.quit is False:
				await self.receive_command()
				await self.treat_command()
		except Exception as err:
			useful.syslog(err)
			await self.send_error(err)
		finally:
			self.close_pasv()
			await self.client.close()
		useful.syslog("[FTP] Disconnected")
