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
from tools import fnmatch
from server import stream
from tools import useful
from server.user import User
from wifi.accesspoint import AccessPoint
from wifi.station import Station

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
		self.cwd = b""
		self.path = b""
		self.fromname = None
		if useful.ismicropython():
			self.root = b""
			self.pathLength = 64
		else:
			self.root = useful.tobytes(os.getcwd() + "/")
			self.root = b"/Users/remi/Downloads/ftp/"
			self.pathLength = 256
		self.cwd = b'/'
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
		self.logDebug(b"Open data %d"%self.dataport)

	def log(self, message):
		""" Display log """
		print("%s"%(useful.tostrings(message)))

	def logDebug(self, message):
		""" Display debug log """
		# print("%08X:%d:%s>%s"%(id(self),self.dataport,useful.tostrings(self.path), useful.tostrings(message)))
		# print("%d:%s>%s"%(self.dataport,useful.tostrings(self.path), useful.tostrings(message)))
		# print("%s"%(useful.tostrings(message)))

	def getIp(self):
		""" Get the ip address of the board """
		if Station.isIpOnInterface(self.remoteaddr):
			result = useful.tobytes(Station.getInfo()[0])
		else:
			result = useful.tobytes(AccessPoint.getInfo()[0])
		return result

	def close(self):
		""" Close all ftp connections """
		self.closePasv()
		if self.datasocket:
			self.datasocket.close()
			self.datasocket = None

	def __del__(self):
		""" Destroy ftp instance """
		self.close()

	def getFileDescription(self, filename, typ, size, date, now, full):
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

	def sendFileListWithPattern(self, path, stream_, full, now, pattern=None):
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

				description += self.getFileDescription(filename, typ, size, date, now, full)
				counter += 1
				if counter == 20:
					counter = 0
					stream_.write(description)
					description = b""
			quantity += 1
		if description != b"":
			stream_.write(description)

	def sendFileList(self, path, stream_, full):
		""" Send the list of file """
		now = useful.now()
		try:
			self.sendFileListWithPattern(path, stream_, full, now)
		except Exception as err:
			useful.syslog(err)
			pattern = path.split(b"/")[-1]
			path = path[:-(len(pattern) + 1)]
			if path == b"":
				path = b"/"
			self.sendFileListWithPattern(path, stream_, full, now, pattern)

	async def sendOk(self):
		""" Send ok to ftp client """
		await self.sendResponse(250,b"OK")

	async def sendResponse(self, code, message):
		""" Send response to ftp client """
		self.logDebug(b"%d %s"%(code, message))
		await self.client.write(b'%d %s\r\n'%(code,message))

	async def sendError(self, err):
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
			useful.syslog(err, msg="%s> %-10s %-30s"%(useful.tobytes(self.cwd), self.command, self.payload))
		await self.sendResponse(550, b"Failed")

	async def USER(self):
		""" Ftp command USER """
		if User.getUser() == b"":
			await self.sendResponse(230, b"User Logged In.")
		else:
			self.user = self.path[1:]
			await self.sendResponse(331, b"User known, enter password")

	async def PASS(self):
		""" Ftp command PASS """
		self.password = self.path[1:]
		if User.check(self.user, self.password, False):
			await self.sendResponse(230, b"Logged in.")
		else:
			await self.sendResponse(430, b"Invalid username or password")

	async def SYST(self):
		""" Ftp command SYST """
		await self.sendResponse(215, b"UNIX Type: L8")

	async def NOOP(self):
		""" Ftp command NOOP """
		await self.sendResponse(200, b"OK")

	async def FEAT(self):
		""" Ftp command FEAT """
		await self.sendResponse(211, b"no-features")

	async def XPWD(self):
		""" Ftp command XPWD """
		await self.PWD()

	async def PWD(self):
		""" Ftp command PWD """
		await self.sendResponse(257,b'"%s" is current directory.'%self.cwd)

	async def XCWD(self):
		""" Ftp command XCWD """
		await self.CWD()

	async def CWD(self):
		""" Ftp command CWD """
		if len(self.path) <= self.pathLength:
			try:
				dd = os.listdir(useful.tostrings(self.root + self.path))
				self.cwd = self.path
				await self.sendResponse(250,b"CWD command successful.")
			except Exception as err:
				await self.sendError(b"Path not existing")
		else:
			await self.sendError(b"Path too long")

	async def CDUP(self):
		""" Ftp command CDUP """
		self.cwd = useful.abspathbytes(self.cwd, b"..")
		await self.sendOk()

	async def TYPE(self):
		""" Ftp command TYPE """
		await self.sendResponse(200, b"Binary transfer mode active.")

	async def SIZE(self):
		""" Ftp command SIZE """
		size = useful.filesize(useful.tostrings(self.root + self.path))
		await self.sendResponse(213, b"%d"%(size))

	async def PASV(self):
		""" Ftp command PASV """
		await self.sendResponse(227, b"Entering Passive Mode (%s,%d,%d)"%(self.addr.replace(b'.',b','), self.dataport>>8, self.dataport%256))
		self.closePasv()
		self.pasvsocket, self.data_addr = self.datasocket.accept()
		self.logDebug(b"PASV Accepted")

	async def PORT(self):
		""" Ftp command PORT """
		items = self.payload.split(b",")
		if len(items) >= 6:
			self.data_addr = b'.'.join(items[:4])
			if self.data_addr == b"127.0.1.1":
				self.data_addr = self.remoteaddr
			self.dataport = int(items[4]) * 256 + int(items[5])
			self.closePasv()
			self.pasvsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.pasvsocket.settimeout(1000)
			self.pasvsocket.connect((self.data_addr, self.dataport))
			useful.syslog("Ftp data connection with: %s"%useful.tostrings(self.data_addr))
			await self.sendResponse(200, b"OK")
		else:
			await self.sendResponse(504, b"Fail")

	async def NLST(self):
		""" Ftp command NLST """
		await self.LIST()

	async def LIST(self):
		""" Ftp command LIST """
		if not self.payload.startswith(b"-"):
			place = self.path
		else:
			place = self.cwd
		await self.sendResponse(150, b"Connection accepted.") # Start list files
		listsocket = stream.Socket(self.pasvsocket)
		useful.syslog("Ftp list '%s'"%(useful.tostrings(self.root+place)))
		self.sendFileList(self.root + place, listsocket, self.command == b"LIST" or self.payload == b"-l")
		listsocket.close()
		await self.sendResponse(226, b"Transfert complete.") # End list files
		self.closePasv()

	async def STAT(self):
		""" Ftp command STAT """
		if self.payload == b"":
			await self.sendResponse(211, b"Connected to (%s)"%self.remoteaddr[0])
			await self.sendResponse(211, b"Data address (%s)"%self.addr)
			await self.sendResponse(211, b"TYPE: Binary STRU: File MODE: Stream")
		else:
			await self.sendResponse(213,b"Directory listing:")
			useful.syslog("Ftp list '%s'"%useful.tostrings(self.root+self.path))
			self.sendFileList(self.root + self.path, self.client, True)
			await self.sendResponse(213, b"Stat end")

	async def RETR(self):
		""" Ftp command RETR """
		await self.sendResponse(150, b"Start send file")
		useful.syslog("Ftp send file '%s'"%useful.tostrings(self.root+self.path))
		filename = self.root + self.path

		if useful.ismicropython():
			bufferSize = 1440
			chunk = bytearray(bufferSize)
			with open(useful.tostrings(filename), "r") as file:
				length = file.readinto(chunk)
				while length > 0:
					# pylint: disable=no-member
					sent = self.pasvsocket.write(chunk[:length])
					length = file.readinto(chunk)
		else:
			with open(useful.tostrings(filename), "rb") as file:
				self.pasvsocket.sendall(file.read())
		await self.sendResponse(226, b"End send file")
		self.closePasv()

	def closePasv(self):
		""" Close PASV connection """
		if self.pasvsocket is not None:
			self.logDebug(b"Close PASV")
			self.pasvsocket.close()
			self.pasvsocket = None

	def writeFile(self, path, dataclient):
		""" Write ftp received """
		chunk = bytearray(1440)
		with open(useful.tostrings(path), "wb") as file:
			length = dataclient.readinto(chunk)
			while length > 0:
				file.write(chunk, length)
				length = dataclient.readinto(chunk)

	async def STOR(self):
		""" Ftp command STOR """
		await self.sendResponse(150, b"Start receive file")
		useful.syslog("Ftp receive file '%s'"%useful.tostrings(self.root + self.path))
		filename = self.root + self.path

		if useful.ismicropython():
			try:
				self.writeFile(filename, self.pasvsocket)
			except Exception as err:
				useful.syslog(err)
				directory, file = useful.split(useful.tostrings(filename))
				useful.makedir(directory, True)
				self.writeFile(filename, self.pasvsocket)
		else:
			with open(filename, "wb") as file:
				data = b" "
				while len(data) > 0:
					data = self.pasvsocket.recv(1440)
					file.write(data)
				data = b""
		await self.sendResponse(226, b"End receive file")
		self.closePasv()

	async def DELE(self):
		""" Ftp command DELE """
		useful.syslog("Ftp delete '%s'"%useful.tostrings(self.root + self.path))
		os.remove(useful.tostrings(self.root + self.path))
		await self.sendOk()

	async def XRMD(self):
		""" Ftp command XRMD """
		await self.RMD()

	async def RMD(self):
		""" Ftp command RMD """
		os.rmdir(useful.tostrings(self.root + self.path))
		await self.sendOk()

	async def XMKD(self):
		""" Ftp command XMKD """
		await self.MKD()

	async def MKD(self):
		""" Ftp command MKD """
		os.mkdir(useful.tostrings(self.root + self.path))
		await self.sendOk()

	async def RNFR(self):
		""" Ftp command RNFR """
		self.fromname = self.path
		await self.sendResponse(350, b"Rename from")

	async def RNTO(self):
		""" Ftp command RNTO """
		if self.fromname is not None:
			useful.syslog("Ftp rename '%s' to '%s'"%(useful.tostrings(self.root + self.fromname), useful.tostrings(self.root + self.path)))
			os.rename(useful.tostrings(self.root + self.fromname), useful.tostrings(self.root + self.path))
			await self.sendOk()
		else:
			await self.sendError(self.fromname)
		self.fromname = None

	async def QUIT(self):
		""" Ftp command QUIT """
		self.quit = True
		await self.sendResponse(221, b"Bye.")

	async def unsupportedCommand(self):
		""" Ftp unknown command """
		await self.sendResponse(502, b"Unsupported command")

	async def receiveCommand(self):
		""" Ftp command reception """
		try:
			self.received = await self.client.readline()
		except Exception as err:
			self.logDebug(b"Reset connection")
			self.quit = True

		if len(self.received) <= 0:
			self.quit = True
		else:
			self.received = self.received.rstrip(b"\r\n")
			self.logDebug(self.received)
			self.command = self.received.split(b" ")[0].upper()
			self.payload = self.received[len(self.command):].lstrip()
			self.path = useful.abspathbytes(self.cwd, self.payload)

	async def treatCommand(self):
		""" Treat ftp command """
		if self.quit is False:
			try:
				command = useful.tostrings(self.command)
				if hasattr(self, command):
					callback = getattr(self, command)

					if self.command not in [b"USER",b"PASS"]:
						if User.check(self.user, self.password):
							await callback()
						else:
							await self.sendResponse(430, b"Invalid username or password")
					else:
						await callback()
				else:
					await self.unsupportedCommand()
			except Exception as err:
				await self.sendError(err)

	async def onConnection(self, reader, writer):
		""" Asyncio on ftp connection method """
		self.remoteaddr = useful.tobytes(writer.get_extra_info('peername')[0])
		self.addr = self.getIp()
		useful.syslog("Ftp connected from %s"%useful.tostrings(self.remoteaddr))
		self.client = stream.Stream(reader, writer)
		try:
			await self.sendResponse(220, b"Ftp " + useful.tobytes(os.uname()[4]) + b".")
			self.quit = False
			while self.quit is False:
				await self.receiveCommand()
				await self.treatCommand()
		except Exception as err:
			await self.sendError(err)
		finally:
			self.closePasv()
			await self.client.close()
		useful.syslog("Ftp disconnected")
