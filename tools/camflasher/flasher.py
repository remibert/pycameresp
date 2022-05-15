""" Micropython firmware flasher for esp32 """
import threading
import tempfile
import queue
import time
import sys
import fileuploader
import streamdevice
sys.path.append("../../modules/lib/tools")
# pylint:disable=wrong-import-position
# pylint:disable=import-error
from strings import get_utf8_length

class Flasher(threading.Thread):
	""" Micropython firmware flasher for esp32 """
	def __init__(self, stdout, directory):
		""" Constructor with thread on serial port """
		threading.Thread.__init__(self)
		self.command    = queue.Queue()

		self.KEY_PRESSED     = 1
		self.QUIT            = 2
		self.CONNECT_SERIAL  = 3
		self.CONNECT_TELNET  = 4
		self.DISCONNECT      = 5
		self.DATA_RECEIVED   = 6
		self.FLASH           = 7
		self.UPLOAD_FILE     = 8

		self.loop = True
		self.flashing = False
		self.waiting_data = b""
		self.stream_thread = streamdevice.StreamThread(self.receive, stdout)
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
				self.stream_thread.quit()
				self.loop = False
			elif command == self.KEY_PRESSED:
				self.stream_thread.write(data)
			elif command == self.DATA_RECEIVED:
				print(self.decode(data), end="")
			elif command == self.FLASH:
				port, baud, rts_dtr, firmware, erase= data
				self.flasher(port, baud, rts_dtr, firmware, erase)
			elif command == self.CONNECT_SERIAL:
				self.stream_thread.connect_serial(data)
			elif command == self.CONNECT_TELNET:
				self.stream_thread.connect_telnet(data)
			elif command == self.UPLOAD_FILE:
				self.stream_thread.upload(data)
			elif command == self.DISCONNECT:
				self.stream_thread.disconnect()

	def decode(self, data):
		""" Decode bytes data into string """
		result = ""
		bad_char = False
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
									self.stream_thread.read_file(self.directory)
									char = ""
								# Special char for download file
								elif char == "࿋":
									self.stream_thread.write_file(self.directory)
									char = ""
								i += length
							except:
								char = ""#bytes([self.waiting_data[i]]).decode("latin-1")
								bad_char = True
								i += 1
							result += char
						else:
							last_i = i
							break
					elif length < 0:
						# char = bytes([self.waiting_data[i]]).decode("latin-1")
						char = ""
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

		if bad_char:
			result = ""
		return result

	def is_flashing(self):
		""" Indicates if the firmware flash is in progress """
		return self.flashing

	def print(self, message, end="\n"):
		""" Print message """
		print(message, end)

	def flasher(self, port, baud, rts_dtr, firmware, erase):
		""" Flasher of firmware it use the esptool.py command """
		import esptool

		# Disconnect serial link
		self.flashing = True
		self.stream_thread.disconnect()

		try:
			# Waits for the serial link to be available
			for i in range(10):
				if self.stream_thread.is_disconnected() is True:
					break
				time.sleep(0.1)

			if type(firmware) == type((0,)):
				firmware = firmware[0]
				uploader = fileuploader.PythonUploader(self.print)
				content = uploader.download_last_release(fileuploader.GITHUB_HOST, fileuploader.PYCAMERESP_PATH, firmware)
				if content is not None:
					directory = tempfile.TemporaryDirectory()
					firmware = "%s/%s"%(directory.name, firmware)
					file = open(firmware, "wb")
					file.write(content)
					file.close()
				else:
					print("\n\x1B[93;101mFirmware download failed\n\x1B[m")
					firmware = None

			print("\x1B[48;5;229m\x1B[38;5;243m")
			if firmware is not None:
				# Start flasher
				flash_command = ["--port", port, "--baud", baud, "--chip", "auto", "write_flash", "0x1000", firmware]
				if erase:
					flash_command.append("--erase-all")
				print("\nesptool.py %s" % " ".join(flash_command))
				esptool.main(flash_command)
				print("\n\x1B[42;93mFlashed with success. Remove strap and press reset button\x1B[m")
		except Exception as err:
			print("\n\x1B[93;101mFlash failed\n\x1B[m")

		# Connect serial link
		self.stream_thread.connect_serial((port, rts_dtr))
		self.flashing = False

	def get_state(self):
		""" Get the current state of the stream """
		return self.stream_thread.get_state()

	def connect_serial(self, port, rts_dtr):
		""" Connect serial link """
		self.command.put((self.CONNECT_SERIAL, (port, rts_dtr)))

	def connect_telnet(self, host, port):
		""" Connect telnet link """
		self.command.put((self.CONNECT_TELNET, (host, port)))

	def disconnect(self):
		""" Disconnect link """
		self.command.put((self.DISCONNECT, None))

	def flash(self, port, baud, rts_dtr, firmware, erase):
		""" Send flash command to flasher thread """
		self.command.put((self.FLASH, (port, baud, rts_dtr, firmware, erase)))

	def quit(self):
		""" Send quit command to flasher thread """
		self.command.put((self.QUIT,None))

	def receive(self, data):
		""" Send receive data to flasher thread """
		self.command.put((self.DATA_RECEIVED, data))

	def upload(self, filename):
		""" Send upload command to serial thread """
		self.command.put((self.UPLOAD_FILE, filename))

	def send_key(self, key):
		""" Send key command to flasher thread """
		# If flashing not in progress (in this case the keys are ignored)
		if self.flashing is False:
			self.command.put((self.KEY_PRESSED, key))
