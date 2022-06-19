# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Stream class to communicate with the device """
import os
import os.path
import threading
import queue
import time
import sys
import telnetlib
import tempfile
import zipfile
import serial
import fileuploader
import vt100
sys.path.append("../../modules/lib/tools")
# pylint:disable=wrong-import-position
# pylint:disable=import-error
from exchange import FileReader, FileWriter, UploadCommand
from filesystem import scandir, isdir

class FileLogger:
	""" Class to save and display all log """
	def __init__(self, stdout, name):
		""" Constructor """
		if "-file" in sys.argv:
			self.file = open("%s.log"%name,"w")
		else:
			self.file = None

		if "-stdout" in sys.argv:
			self.stdout = stdout
		else:
			self.stdout = None

	def write(self, data):
		""" Write data in the file or display """
		if self.stdout is not None:
			self.stdout.write(data)
			self.stdout.flush()

		if self.file is not None:
			self.file.write(data)
			self.file.flush()

	def is_activated(self):
		""" Indicates if the logger is activated """
		return self.file is not None or self.stdout is not None

class StreamLogger:
	""" Log all data exchanged """
	def __init__(self, stdout, name):
		""" Constructor """
		self.received = b""
		self.writer = FileLogger(stdout, name)

	def write(self, data):
		""" Write buffer to logger """
		self.log("<-", self.received)
		self.received = b""
		self.log("->", data)

	def insert_sep(self, string, sep, period):
		""" Add separator in string """
		return sep.join([string[i*period:(i+1)*period] for i in range(len(string)//period)])

	def log(self, direction, buffer):
		""" Log exchange on serial link """
		if buffer != b"":
			if self.writer.is_activated():
				message = ""
				for i in buffer:
					if i >= 0x20 and  i < 0x7F:
						message += chr(i)
					else:
						message += '.'
				self.writer.write("# %s\n"%message)
				data = self.insert_sep(buffer.hex().upper(), " ", 2)
				self.writer.write("('%s',%-5d,'%s'),\n"%(direction, len(buffer),data))

	def read(self, data):
		""" Read data from logger """
		if len(data) == 0:
			self.log("<-", self.received)
			self.received = b""
		else:
			self.received += data
		return data

class StreamSerial(serial.Serial):
	""" Stream serial with log exchange """
	def __init__(self, *args, **params):
		if "stdout" in params:
			stdout = params["stdout"]
			del params["stdout"]
		else:
			stdout = None
		self.logger = StreamLogger(stdout, self.__class__.__name__)
		serial.Serial.__init__(*((self,) + args), **params)

	def write(self, data):
		""" Write buffer to serial link """
		self.logger.write(data)
		return serial.Serial.write(self, data)

	def read(self, size=1):
		""" Read length from serial link """
		data = serial.Serial.read(self, size)
		self.logger.read(data)
		return data

	def get_in_waiting(self):
		""" Get the number of bytes in the input buffer """
		return self.in_waiting

	def is_opened(self):
		""" Indicates if the serial link is opened """
		return True

class StreamTelnet:
	""" Stream telnet with log exchange """
	def __init__(self, *args, **params):
		self.host = params["host"]
		self.port = params["port"]
		self.telnet = telnetlib.Telnet()
		self.logger = StreamLogger(params["stdout"], self.__class__.__name__)
		self.check = 0
		self.received = b""

	def write(self, data):
		""" Write buffer to serial link """
		self.logger.write(data)
		return self.telnet.write(data)

	def read(self, size=1):
		""" Read length from serial link """
		data = self.telnet.read_very_eager()
		self.logger.read(data)
		self.received += data
		result = self.received[:size]
		self.received = self.received[size:]
		return result

	def cancel_read(self):
		""" Cancel the read """

	def reset_input_buffer(self):
		""" Reset the input buffer """
		self.received = b""

	def get_in_waiting(self):
		""" Get the number of bytes in the input buffer """
		if len(self.received) == 0:
			if self.telnet.sock_avail():
				return 1
			else:
				time.sleep(0.1)
				return 0
		else:
			return len(self.received)

	def close(self):
		""" Close telnet connection """
		if self.telnet is not None:
			self.telnet.close()

	def readinto(self, buffer):
		""" Read bytes into buffer """
		size = len(buffer)
		data = self.read(size)
		buffer[0:len(data)] = data
		return len(data)

	def is_opened(self):
		""" Indicates if telnet connected """
		try:
			self.telnet.open(self.host,self.port, timeout=1)
			return True
		except Exception as err:
			return False

class StreamThread(threading.Thread):
	""" Thread of the communication stream with the device """
	DISCONNECTED      = 0
	CONNECTING_TELNET = 1
	TELNET_CONNECTED  = 2
	SERIAL_CONNECTED  = 3

	CMD_CONNECT_SERIAL     = 0
	CMD_CONNECT_TELNET     = 1
	CMD_DISCONNECT         = 2
	CMD_WRITE_DATA         = 3
	CMD_UPLOAD_FILE        = 4
	CMD_DONWLOAD_FILE      = 5
	CMD_UPLOAD_FROM_SERVER = 6
	CMD_UPLOAD_FILES       = 8
	CMD_QUIT               = 9
	def __init__(self, receive_callback, stdout):
		""" Constructor """
		threading.Thread.__init__(self)
		self.stream = None
		self.command = queue.Queue()
		self.receive_callback = receive_callback
		self.port = ""
		self.host = ""
		self.loop = True
		self.buffer = b""
		self.drop_directory = ""
		self.drop_filenames = []
		self.stdout = stdout
		self.state = self.DISCONNECTED
		self.zip_extract = False
		self.start()

	def __del__(self):
		""" Destructor """
		self.quit()

	def close(self):
		""" Close serial """
		if self.stream is not None:
			self.stream.close()
			self.state = self.DISCONNECTED
			self.stream = None

	def on_connect_serial(self, command, data):
		""" Treat serial connection """
		if command == self.CMD_CONNECT_SERIAL:
			port, rts_dtr = data
			self.close()
			try:
				if port != "":
					# Open serial console
					self.stream = StreamSerial(port=port, baudrate=115200, timeout=0.2, stdout=self.stdout)

					# Select RTS/DTR
					if rts_dtr is True:
						self.stream.dtr = True
						self.stream.rts = True
					else:
						self.stream.dtr = False
						self.stream.rts = False

					# Clear input serial buffer
					self.stream.reset_input_buffer()
					self.port = port

					self.print("\n"+vt100.COLOR_OK+"Connect serial link %s"%self.port+vt100.COLOR_NONE)
			except Exception as err:
				self.close()

	def on_connect_telnet(self, command, data):
		""" Treat telnet connection command """
		if command == self.CMD_CONNECT_TELNET:
			host, port = data
			self.close()
			try:
				if host != "":
					# Open serial console
					self.stream = StreamTelnet(host=host, port=port, stdout=self.stdout)
					self.port = port
					self.host = host

					self.print("\n"+vt100.COLOR_OK+"Connect telnet on %s:%d"%(self.host, self.port)+vt100.COLOR_NONE)
			except Exception as err:
				self.close()

	def on_connect(self, command, data):
		""" Treat connect command """
		self.on_connect_serial(command, data)
		self.on_connect_telnet(command, data)

	def print(self, message, end="\n"):
		""" Print message to console """
		self.receive_callback(message + end)

	def on_quit(self, command):
		""" Treat quit command """
		if command == self.CMD_QUIT:
			self.loop = False
			self.close()

	def on_disconnect(self, command):
		""" Treat disconnect command """
		if command == self.CMD_DISCONNECT:
			if self.state in [self.TELNET_CONNECTED, self.CONNECTING_TELNET]:
				self.print("\n"+vt100.COLOR_OK+"Disconnected"+vt100.COLOR_NONE)
			self.close()

	def on_upload_file(self, command, directory):
		""" Treat write file command """
		if command == self.CMD_UPLOAD_FILE:
			if len(self.drop_filenames) > 0:
				self.uploader_drop(directory)
			else:
				self.uploader_file(directory)

	def uploader_file(self, directory):
		""" Uploader file """
		try:
			command = UploadCommand(directory)
			device_dir, pattern, recursive = command.read(self.stream, self.stream)
			computer_dir = os.path.normpath(directory + "/" + device_dir + "/" + pattern)
			if isdir(computer_dir):
				computer_dir += "/*"
			directory_, pattern_ = os.path.split(computer_dir)

			# If directory can be parsed
			if directory_.find(os.path.normpath(directory)) == 0 and os.path.exists(directory_):
				_, filenames = scandir(directory_, pattern_, recursive)
				for filename in filenames:
					if not self.is_fileignored(filename):
						file_writer = FileWriter()
						filename = filename.replace("\\","/")
						device_filename = filename.replace(directory, "")
						file_writer.write(filename, self.stream, self.stream, device_filename, self.print)
			else:
				self.print("'%s' not found"%(os.path.normpath(device_dir + "/" + pattern)))

			self.stream.write(b"exit\r\n")
		except Exception as err:
			self.print("Upload error")

	def uploader_drop(self, directory):
		""" Uploader from drop file """
		try:
			command = UploadCommand(self.drop_directory)
			path, pattern, recursive = command.read(self.stream, self.stream)
			file_writer = FileWriter()
			for filename in self.drop_filenames:
				filename_ = os.path.join(self.drop_directory,filename)
				drop_filename = filename[len(self.drop_directory):]
				if drop_filename[0] == "/" or drop_filename[0] == "\\":
					drop_filename = drop_filename[1:]
				drop_filename = drop_filename.replace("\\","/")

				# If the content of zip must be extracted
				if self.zip_extract and os.path.splitext(filename_)[1].lower() == ".zip":
					with zipfile.ZipFile(filename_,"r") as zip_file:
						for file in zip_file.infolist():
							zip_content = tempfile.NamedTemporaryFile(delete=False)
							zip_content.write(zip_file.read(file.filename))
							zip_content.close()
							try:
								file_writer.write(zip_content.name, self.stream, self.stream, file.filename, self.print)
							finally:
								os.unlink(zip_content.name)
				else:
					file_writer.write(filename_, self.stream, self.stream, drop_filename, self.print)
			self.stream.write(b"exit\r\n")
			self.drop_filenames = []
			self.zip_extract = False
		except Exception as err:
			self.print("Upload error")

	def on_download_file(self, command, directory):
		""" Treat the read file command """
		if command == self.CMD_DONWLOAD_FILE:
			try:
				file_reader = FileReader()
				file_reader.read(directory, self.stream, self.stream, self.print)
			except Exception as err:
				self.print("Download error")

	def on_upload_from_server(self, command, filename):
		""" Treat upload command to device """
		if command == self.CMD_UPLOAD_FROM_SERVER:
			uploader = fileuploader.PythonUploader(self.print)
			prompt = uploader.wait_prompt(device=self.stream)
			if prompt == "=>":
				self.stream.write(b"quit\x0D")
				time.sleep(0.4)
				prompt = uploader.wait_prompt(device=self.stream)
			if prompt == ">>>":
				uploader.upload_from_server(self.stream, fileuploader.GITHUB_HOST, fileuploader.PYCAMERESP_PATH, filename)
				self.stream.write(b"from shell import sh\x0D")
				self.stream.write(b"sh()\x0D")

	def is_fileignored(self, filename):
		""" Indicates that the filename is ignored """
		if os.path.split(filename)[1] in [".DS_Store",".gitignore"]:
			return True
		else:
			return False

	def create_upload_list(self, filenames):
		""" Create list with dropped filenames """
		drop_filenames = []
		for filename in filenames:
			if isdir(filename):
				_, files = scandir(filename, "*", True)
				for f in files:
					if not self.is_fileignored(f):
						drop_filenames.append(os.path.normpath(f))
			else:
				drop_filenames.append(os.path.normpath(filename))

		if len(filenames) == 1:
			drop_directory = os.path.split(os.path.normpath(filenames[0]))[0]
		else:
			if len(drop_filenames) > 1:
				drop_directory = os.path.normpath(os.path.commonprefix(drop_filenames))
			else:
				drop_directory = os.path.normpath(os.path.split(os.path.normpath(filenames[0]))[0])
		return drop_directory, drop_filenames

	def on_upload_files(self, command, filenames):
		""" Treat upload command to device """
		if command == self.CMD_UPLOAD_FILES:
			filenames, zip_extract = filenames
			uploader = fileuploader.PythonUploader(self.print)
			prompt = uploader.wait_prompt(device=self.stream)
			if prompt == ">>>":
				drop_directory, drop_filenames = self.create_upload_list(filenames)
				uploader.upload_files(self.stream, drop_filenames, drop_directory, zip_extract)
			elif prompt == "=>":
				self.zip_extract = zip_extract
				self.drop_directory, self.drop_filenames = self.create_upload_list(filenames)
				current = self.drop_filenames[0]
				drop_filename = current[len(self.drop_directory):]
				if drop_filename[0] == "/" or drop_filename[0] == "\\":
					drop_filename = drop_filename[1:]
				drop_filename = drop_filename.replace("\\","/")
				self.stream.write(("upload %s\x0d"%drop_filename).encode("utf8"))

	def on_write(self, command, data):
		""" Treat write command """
		if command == self.CMD_WRITE_DATA:
			if self.stream is not None:
				try:
					if len(data) > 32:
						while len(data) > 0:
							data_to_send = data[:8]
							data = data[8:]
							self.stream.write(data_to_send)
							if len(data) > 0:
								for i in range(15):
									time.sleep(0.01)
									if self.stream.get_in_waiting() > 0:
										break
								while self.stream.get_in_waiting() > 0:
									self.receive_callback(self.stream.read(self.stream.get_in_waiting()))
									if self.stream.get_in_waiting() == 0:
										for i in range(15):
											time.sleep(0.01)
											if self.stream.get_in_waiting() > 0:
												break
					else:
						self.stream.write(data)
				except Exception as err:
					self.close()

	def receive(self):
		""" Receive data from serial """
		if self.stream is not None:
			try:
				data = self.stream.read(self.stream.get_in_waiting() or 1)
				self.receive_callback(data)
			except Exception as err:
				self.print("\n"+vt100.COLOR_FAILED+"Connection lost"+vt100.COLOR_NONE)
				self.close()

	def run(self):
		""" Serial thread core """
		current = 0
		while self.loop:
			if self.state == self.DISCONNECTED:
				command, data = self.command.get()
				self.on_connect(command, data)
				self.on_quit   (command)
				self.state = self.CONNECTING_TELNET
			elif self.state == self.CONNECTING_TELNET:
				# If command awaited
				if self.command.qsize() > 0:
					# read command
					command,data = self.command.get()
					self.on_connect    (command, data)
					self.on_disconnect (command)
					self.on_quit       (command)
				if self.stream is not None:
					if self.stream.is_opened():
						if isinstance(self.stream, StreamTelnet):
							self.print(vt100.COLOR_OK+"Connected waiting for answer"+vt100.COLOR_NONE)
							self.state = self.TELNET_CONNECTED
						else:
							self.state = self.SERIAL_CONNECTED
					else:
						progress = [" |*-----|"," |-*----|"," |--*---|"," |---*--|", " |----*-|", " |-----*|"]
						self.print(progress[current%len(progress)], end="\r")
						current += 1
						time.sleep(0.1)
				else:
					self.state = self.DISCONNECTED
			elif self.state in [self.TELNET_CONNECTED, self.SERIAL_CONNECTED]:
				# If command awaited
				if self.command.qsize() > 0:
					# read command
					command,data = self.command.get()
					self.on_write               (command, data)
					self.on_upload_file         (command, data)
					self.on_download_file       (command, data)
					self.on_connect             (command, data)
					self.on_upload_from_server  (command, data)
					self.on_upload_files        (command, data)
					self.on_disconnect          (command)
					self.on_quit                (command)
				self.receive()

	def send(self, message):
		""" Send message to stream thread """
		self.command.put(message)
		if self.stream is not None:
			try:
				self.stream.cancel_read()
			except:
				pass

	def quit(self):
		""" Send quit command to stream thread """
		self.send((self.CMD_QUIT,None))

	def write(self, data):
		""" Send write data command to stream thread """
		self.send((self.CMD_WRITE_DATA,data))

	def upload_file(self, directory):
		""" Send upload file command to stream thread """
		self.send((self.CMD_UPLOAD_FILE,directory))

	def download_file(self, directory):
		""" Send download file command to stream thread """
		self.send((self.CMD_DONWLOAD_FILE,directory))

	def connect_serial(self, data):
		""" Send serial connect command to stream thread """
		self.send((self.CMD_CONNECT_SERIAL, data))

	def connect_telnet(self, data):
		""" Send telnet connect command to stream thread """
		self.send((self.CMD_CONNECT_TELNET, data))

	def disconnect(self):
		""" Send disconnect command to stream thread """
		self.send((self.CMD_DISCONNECT, None))

	def upload_from_server(self, filename):
		""" Send upload file on python prompt to stream thread """
		self.send((self.CMD_UPLOAD_FROM_SERVER, filename))

	def upload_files(self, filenames):
		""" Send upload files on python prompt to stream thread """
		self.send((self.CMD_UPLOAD_FILES, filenames))

	def is_disconnected(self):
		""" Indicates if the serial port is disconnected """
		return self.stream is None

	def get_state(self):
		""" Get the current state of the stream """
		return self.state
