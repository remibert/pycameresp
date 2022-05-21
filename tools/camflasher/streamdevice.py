""" Stream class to communicate with the device """
import threading
import queue
import time
import sys
import telnetlib
import os.path
import serial
import fileuploader
sys.path.append("../../modules/lib/tools")
# pylint:disable=wrong-import-position
# pylint:disable=import-error
from exchange import FileReader, FileWriter, ImporterCommand
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

		self.CONNECT_SERIAL    = 0
		self.CONNECT_TELNET    = 1
		self.DISCONNECT = 2
		self.WRITE_DATA = 3
		self.WRITE_FILE = 4
		self.READ_FILE  = 5
		self.UPLOAD_FILE= 6
		self.QUIT       = 7
		self.stdout = stdout

		self.DISCONNECTED = 0
		self.CONNECT_IN_PROGRESS = 1
		self.CONNECTED = 2
		self.state = self.DISCONNECTED

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
		if command == self.CONNECT_SERIAL:
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

					self.print("\n\x1B[42;93mConnect serial link %s\x1B[m"%self.port)
			except Exception as err:
				self.close()

	def on_connect_telnet(self, command, data):
		""" Treat telnet connection command """
		if command == self.CONNECT_TELNET:
			host, port = data
			self.close()
			try:
				if host != "":
					# Open serial console
					self.stream = StreamTelnet(host=host, port=port, stdout=self.stdout)
					self.port = port
					self.host = host

					self.print("\n\x1B[42;93mConnect telnet on %s:%d\x1B[m"%(self.host, self.port))
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
		if command == self.QUIT:
			self.loop = False
			self.close()

	def on_disconnect(self, command):
		""" Treat disconnect command """
		if command == self.DISCONNECT:
			if self.state in [self.CONNECTED, self.CONNECT_IN_PROGRESS]:
				self.print("\n\x1B[42;93mDisconnected\x1B[m")
			self.close()

	def on_write_file(self, command, directory):
		""" Treat write file command """
		if command == self.WRITE_FILE:
			try:
				command = ImporterCommand(directory)
				path, pattern, recursive = command.read(self.stream, self.stream)
				target_dir = os.path.normpath(directory + "/" + path + "/" + pattern)
				if isdir(target_dir):
					target_dir += "/*"
				directory_, pattern_ = os.path.split(target_dir)

				# If directory can be parsed
				if directory_.find(os.path.normpath(directory)) == 0 and os.path.exists(directory_):
					_, filenames = scandir(directory_, pattern_, recursive)

					for filename in filenames:
						file_writer = FileWriter()
						filename = filename.replace("\\","/")
						filename_ = filename.replace(directory, "")
						if file_writer.write(filename, self.stream, self.stream, directory) is True:
							self.print("  %s"%filename_)
						else:
							self.print("  %s bad crc"%filename_)
				else:
					self.print("'%s' not found"%(os.path.normpath(path + "/" + pattern)))

				self.stream.write(b"exit\r\n")
			except Exception as err:
				self.print("Importer error")

	def on_read_file(self, command, directory):
		""" Treat the read file command """
		if command == self.READ_FILE:
			try:
				file_reader = FileReader()
				if file_reader.read(directory, self.stream, self.stream) != -1:
					self.print("  %s"%file_reader.filename.get())
				else:
					self.print("  %s bad crc"%file_reader.filename.get())
			except Exception as err:
				self.print("Exporter error")

	def on_upload(self, command, filename):
		""" Treat upload command to device """
		if command == self.UPLOAD_FILE:
			uploader = fileuploader.PythonUploader(self.print)
			uploader.upload(self.stream, fileuploader.GITHUB_HOST, fileuploader.PYCAMERESP_PATH, filename)

	def on_write(self, command, data):
		""" Treat write command """
		if command == self.WRITE_DATA:
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
				self.print("\n\x1B[93;101mConnection lost\x1B[m")
				self.close()

	def run(self):
		""" Serial thread core """
		current = 0
		while self.loop:
			if self.state == self.DISCONNECTED:
				command, data = self.command.get()
				self.on_connect(command, data)
				self.on_quit   (command)
				self.state = self.CONNECT_IN_PROGRESS
			elif self.state == self.CONNECT_IN_PROGRESS:
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
							self.print("\x1B[42;93mConnected waiting for answer\x1B[m")
						self.state = self.CONNECTED
					else:
						progress = [" |*-----|"," |-*----|"," |--*---|"," |---*--|", " |----*-|", " |-----*|"]
						self.print(progress[current%len(progress)], end="\r")
						current += 1
						time.sleep(0.1)
				else:
					self.state = self.DISCONNECTED
			elif self.state == self.CONNECTED:
				# If command awaited
				if self.command.qsize() > 0:
					# read command
					command,data = self.command.get()
					self.on_write      (command, data)
					self.on_write_file (command, data)
					self.on_read_file  (command, data)
					self.on_connect    (command, data)
					self.on_upload     (command, data)
					self.on_disconnect (command)
					self.on_quit       (command)
				self.receive()

	def send(self, message):
		""" Send message to serial thread """
		self.command.put(message)
		if self.stream is not None:
			try:
				self.stream.cancel_read()
			except:
				pass

	def quit(self):
		""" Send quit command to serial thread """
		self.send((self.QUIT,None))

	def write(self, data):
		""" Send write data command to serial thread """
		self.send((self.WRITE_DATA,data))

	def write_file(self, directory):
		""" Send write file command to serial thread """
		self.send((self.WRITE_FILE,directory))

	def read_file(self, directory):
		""" Send read file command to serial thread """
		self.send((self.READ_FILE,directory))

	def connect_serial(self, data):
		""" Send serial connect command to serial thread """
		self.send((self.CONNECT_SERIAL, data))

	def connect_telnet(self, data):
		""" Send telnet connect command to serial thread """
		self.send((self.CONNECT_TELNET, data))

	def disconnect(self):
		""" Send disconnect command to serial thread """
		self.send((self.DISCONNECT, None))

	def upload(self, filename):
		""" Send upload command to serial thread """
		self.send((self.UPLOAD_FILE, filename))

	def is_disconnected(self):
		""" Indicates if the serial port is disconnected """
		return self.stream is None

	def get_state(self):
		""" Get the current state of the stream """
		return self.state
