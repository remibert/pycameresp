""" Micropython firmware flasher for esp32 """
import threading
import queue
import time
import sys
import os.path
from serial import Serial
sys.path.append("../../modules/lib/tools")
# pylint:disable=wrong-import-position
# pylint:disable=import-error
from filesystem import scandir
from strings import get_utf8_length
from exchange import FileReader, PatternReader, FilenameReader, IntReader, FileWriter

class FileDownload:
	""" File downloader """
	def __init__(self, directory):
		""" Constructor """
		self.pattern  = PatternReader()
		self.path     = FilenameReader()
		self.recursive = IntReader()
		self.directory = directory
		self.read_byte   = self.read_pattern

	def read_pattern(self, byte):
		""" Read pattern """
		if self.pattern.read_byte(byte) is not None:
			self.read_byte = self.read_path
		return None

	def read_path(self, byte):
		""" Read path """
		if self.path.read_byte(byte) is not None:
			self.read_byte = self.read_recursive
		return None

	def read_recursive(self, byte):
		""" Read recursive """
		if self.recursive.read_byte(byte) is not None:
			_, filenames = scandir(os.path.normpath(self.directory + "/" + self.path.get()), self.pattern.get(), True if self.recursive.get() == 1 else False)
			return filenames


class ThreadSerial(threading.Thread):
	""" Serial thread """
	def __init__(self, receive_callback):
		""" Constructor """
		threading.Thread.__init__(self)
		self.serial = None
		self.command = queue.Queue()
		self.receive_callback = receive_callback
		self.port = ""
		self.loop = True
		self.buffer = b""

		self.CONNECT = 0
		self.DISCONNECT = 1
		self.WRITE_DATA = 2
		self.WRITE_FILE =3
		self.READ_FILE = 4
		self.QUIT = 5
		self.start()

	def __del__(self):
		""" Destructor """
		self.quit()

	def close(self):
		""" Close serial """
		if self.serial is not None:
			self.serial.close()
			self.serial = None

	def on_connect(self, command, port):
		""" Treat connect command """
		if command == self.CONNECT:
			self.close()
			try:
				if port != "":
					# Open serial console
					self.serial = Serial(port=port, baudrate=115200, timeout=1)

					# Clear input serial buffer
					self.serial.dtr = False
					self.serial.rts = False
					self.serial.reset_input_buffer()
					self.port = port
					self.print("\n\x1B[42;93mSelect %s\x1B[m\n"%self.port)
			except:
				self.close()

	def print(self, message):
		""" Print message to console """
		self.receive_callback(message)

	def on_quit(self, command):
		""" Treat quit command """
		if command == self.QUIT:
			self.loop = False
			self.close()

	def on_disconnect(self, command):
		""" Treat disconnect command """
		if command == self.DISCONNECT:
			self.close()

	def on_write_file(self, command, data):
		""" Treat write file command """
		if command == self.WRITE_FILE:
			file_writer = FileWriter()
			_, filenames = data
			for filename in filenames:
				# self.serial.write("࿊".encode("utf8"))
				file_writer.write(filename, self.serial, self.serial)
			# ࿌
			# self.serial.write("྾".encode("utf8"))

	def on_read_file(self, command, directory):
		""" Treat the read file command """
		if command == self.READ_FILE:
			file_reader = FileReader()
			if file_reader.read(directory, self.serial, self.serial) != -1:
				self.print("  %s\n"%file_reader.filename.get())
			else:
				self.print("  %s bad crc\n"%file_reader.filename.get())

	def on_write(self, command, data):
		""" Treat write command """
		if command == self.WRITE_DATA:
			if self.serial is not None:
				try:
					if len(data) > 32:
						while len(data) > 0:
							data_to_send = data[:8]
							data = data[8:]
							self.serial.write(data_to_send)
							if len(data) > 0:
								for i in range(15):
									time.sleep(0.01)
									if self.serial.in_waiting > 0:
										break
								while self.serial.in_waiting > 0:
									self.receive_callback(self.serial.read(self.serial.in_waiting))
									if self.serial.in_waiting == 0:
										for i in range(15):
											time.sleep(0.01)
											if self.serial.in_waiting > 0:
												break
					else:
						self.serial.write(data)
				except Exception as err:
					self.close()

	def receive(self):
		""" Receive data from serial """
		if self.serial is not None:
			try:
				data = self.serial.read(self.serial.in_waiting or 1)
				self.receive_callback(data)
			except Exception as err:
				self.close()

	def run(self):
		""" Serial thread core """
		while self.loop:
			# If serial port not opened
			if self.serial is None:
				command, data = self.command.get()
				self.on_connect(command, data)
				self.on_quit   (command)
			else:
				# If command awaited
				if self.command.qsize() > 0:
					# read command
					command,data = self.command.get()
					self.on_write      (command, data)
					self.on_write_file (command, data)
					self.on_read_file  (command, data)
					self.on_connect    (command, data)
					self.on_disconnect (command)
					self.on_quit       (command)
				self.receive()

	def send(self, message):
		""" Send message to serial thread """
		self.command.put(message)
		if self.serial is not None:
			try:
				self.serial.cancel_read()
			except:
				pass

	def quit(self):
		""" Send quit command to serial thread """
		self.send((self.QUIT,None))

	def write(self, data):
		""" Send write data command to serial thread """
		self.send((self.WRITE_DATA,data))

	def write_file(self, data):
		""" Send write file command to serial thread """
		self.send((self.WRITE_FILE,data))

	def read_file(self, directory):
		""" Send read file command to serial thread """
		self.send((self.READ_FILE,directory))

	def connect(self, port):
		""" Send connect command to serial thread """
		self.send((self.CONNECT, port))

	def disconnect(self):
		""" Send disconnect command to serial thread """
		self.send((self.DISCONNECT, None))

	def is_disconnected(self):
		""" Indicates if the serial port is disconnected """
		return self.serial is None

class Flasher(threading.Thread):
	""" Micropython firmware flasher for esp32 """
	def __init__(self, stdout, directory):
		""" Constructor with thread on serial port """
		threading.Thread.__init__(self)
		self.command    = queue.Queue()

		self.KEY_PRESSED   = 1
		self.QUIT          = 2
		self.SET_INFO      = 3
		self.DATA_RECEIVED = 4
		self.FLASH         = 5

		self.loop = True
		self.flashing = False
		self.waiting_data = b""
		self.serial_thread = ThreadSerial(self.receive)
		self.stdout = stdout
		self.directory = directory

	def set_directory(self, directory):
		""" Set the working directory for upload and download """
		self.directory = directory

	def run(self):
		""" Thread core """
		while self.loop:
			command, data = self.command.get()
			if command == self.QUIT:
				self.serial_thread.quit()
				self.loop = False
			elif command == self.KEY_PRESSED:
				self.serial_thread.write(data)
			elif command == self.DATA_RECEIVED:
				print(self.decode(data), end="")
			elif command == self.FLASH:
				port, baud, firmware, erase= data
				self.flasher(port, baud, firmware, erase)
			elif command == self.SET_INFO:
				self.serial_thread.connect(data)

	def decode(self, data):
		""" Decode bytes data into string """
		result = ""
		# If data received from serial port
		if type(data) == type(b""):
			last_i = -1

			self.waiting_data += data
			if len(self.waiting_data) > 0:
				i = 0
				while i < len(self.waiting_data):
					length = get_utf8_length(self.waiting_data[i])
					if length >= 1:
						if i + length <= len(self.waiting_data):
							try:
								char = self.waiting_data[i:i+length].decode("utf-8")
								# Special char to upload file
								if char == "࿊":
									self.serial_thread.read_file(self.directory)
									char = ""
								# Special char for download file
								elif char == "࿋":
									char = ""
								i += length
							except:
								char = bytes([self.waiting_data[i]]).decode("latin-1")
								i += 1
							result += char
						else:
							last_i = i
							break
					elif length < 0:
						char = bytes([self.waiting_data[i]]).decode("latin-1")
						result += char
						i += 1
			else:
				pass
			if last_i >= 0:
				self.waiting_data = self.waiting_data[last_i:]
			else:
				self.waiting_data = b""
		else:
			# Else it is standard printing
			result = data
		return result

	def flasher(self, port, baud, firmware, erase):
		""" Flasher of firmware it use the esptool.py command """
		import esptool

		# Disconnect serial link
		self.flashing = True
		self.serial_thread.disconnect()

		try:
			# Waits for the serial link to be available
			for i in range(10):
				if self.serial_thread.is_disconnected() is True:
					break
				time.sleep(0.1)

			# Start flasher
			print("\x1B[48;5;229m\x1B[38;5;243m")
			flash_command = ["--port", port, "--baud", baud, "--chip", "auto", "write_flash", "0x1000", firmware]

			if erase:
				flash_command.append("--erase-all")
			print("\nesptool.py %s" % " ".join(flash_command))
			esptool.main(flash_command)
			print("\n\x1B[42;93mFlashed with success. Remove strap and press reset button\x1B[m")
		except:
			print("\n\x1B[93;101mFlash failed\n\x1B[m")

		# Connect serial link
		self.serial_thread.connect(port)
		self.flashing = False

	def set_info(self, port):
		""" Set the information of the flasher """
		self.command.put((self.SET_INFO, port))

	def flash(self, port, baud, firmware, erase):
		""" Send flash command to flasher thread """
		self.command.put((self.FLASH, (port, baud, firmware, erase)))

	def quit(self):
		""" Send quit command to flasher thread """
		self.command.put((self.QUIT,None))

	def receive(self, data):
		""" Send receive data to flasher thread """
		self.command.put((self.DATA_RECEIVED, data))

	def send_key(self, key):
		""" Send key command to flasher thread """
		# If flashing not in progress (in this case the keys are ignored)
		if self.flashing is False:
			self.command.put((self.KEY_PRESSED, key))
