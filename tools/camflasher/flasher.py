""" Micropython firmware flasher for esp32 """
import threading
import tempfile
import queue
import time
import sys
import fileuploader
import streamdevice
import vt100
sys.path.append("../../modules/lib/tools")
# pylint:disable=wrong-import-position
# pylint:disable=import-error
from strings import get_utf8_length

class Flasher(threading.Thread):
	""" Micropython firmware flasher for esp32 """
	DISCONNECTED      = 0
	CONNECTING_TELNET = 1
	TELNET_CONNECTED  = 2
	SERIAL_CONNECTED  = 3
	FLASHING          = 4

	CMD_KEY_PRESSED        = 1
	CMD_QUIT               = 2
	CMD_CONNECT_SERIAL     = 3
	CMD_CONNECT_TELNET     = 4
	CMD_DISCONNECT         = 5
	CMD_DATA_RECEIVED      = 6
	CMD_FLASH              = 7
	CMD_UPLOAD_FROM_SERVER = 8
	CMD_UPLOAD_FILES       = 10

	def __init__(self, stdout, directory):
		""" Constructor with thread on serial port """
		threading.Thread.__init__(self)
		self.command    = queue.Queue()
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
			if command == self.CMD_QUIT:
				self.stream_thread.quit()
				self.loop = False
			elif command == self.CMD_KEY_PRESSED:
				self.stream_thread.write(data)
			elif command == self.CMD_DATA_RECEIVED:
				print(self.decode(data), end="")
			elif command == self.CMD_FLASH:
				self.flasher(data)
			elif command == self.CMD_CONNECT_SERIAL:
				self.stream_thread.connect_serial(data)
			elif command == self.CMD_CONNECT_TELNET:
				self.stream_thread.connect_telnet(data)
			elif command == self.CMD_UPLOAD_FROM_SERVER:
				self.stream_thread.upload_from_server(data)
			elif command == self.CMD_UPLOAD_FILES:
				self.stream_thread.upload_files(data)
			elif command == self.CMD_DISCONNECT:
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
								# Special char to download file
								if char == "࿊":
									self.stream_thread.download_file(self.directory)
									char = ""
								# Special char for upload file
								elif char == "࿋":
									self.stream_thread.upload_file(self.directory)
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

	def print(self, message, end="\n"):
		""" Print message """
		print(message, end)

	def flasher(self, data):
		""" Flasher of firmware it use the esptool.py command """
		import esptool
		port, baud, rts_dtr, firmware, erase, address, chip = data

		# Disconnect serial link
		self.flashing = True
		self.stream_thread.disconnect()

		try:
			# Waits for the serial link to be available
			for i in range(10):
				if self.stream_thread.is_disconnected() is True:
					break
				time.sleep(0.1)

			print("\x1B[1;1f\x1B[2J")
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
				flash_command = ["--port", port, "--baud", baud, "--chip", chip, "write_flash", address, firmware]
				if erase:
					flash_command.append("--erase-all")
				print("esptool.py %s" % " ".join(flash_command))
				esptool.main(flash_command)
				print("\n"+vt100.COLOR_OK+"Flashed with success. Remove strap and press reset button"+vt100.COLOR_NONE)
		except Exception as err:
			print("\n"+vt100.COLOR_FAILED+"Flash failed"+vt100.COLOR_NONE)

		# Connect serial link
		self.stream_thread.connect_serial((port, rts_dtr))
		self.flashing = False

	def get_state(self):
		""" Get the current state of the stream """
		result = self.CMD_DISCONNECT
		state = self.stream_thread.get_state()
		if self.flashing:
			result = self.FLASHING
		elif state == self.stream_thread.SERIAL_CONNECTED:
			result = self.SERIAL_CONNECTED
		elif state == self.stream_thread.TELNET_CONNECTED:
			result = self.TELNET_CONNECTED
		elif state == self.stream_thread.DISCONNECTED:
			result = self.DISCONNECTED
		elif state == self.stream_thread.CONNECTING_TELNET:
			result = self.CONNECTING_TELNET
		return result

	def connect_serial(self, port, rts_dtr):
		""" Connect serial link """
		self.command.put((self.CMD_CONNECT_SERIAL, (port, rts_dtr)))

	def connect_telnet(self, host, port):
		""" Connect telnet link """
		self.command.put((self.CMD_CONNECT_TELNET, (host, port)))

	def disconnect(self):
		""" Disconnect link """
		self.command.put((self.CMD_DISCONNECT, None))

	def flash(self, params):
		""" Send flash command to flasher thread """
		self.command.put((self.CMD_FLASH, params))

	def quit(self):
		""" Send quit command to flasher thread """
		self.command.put((self.CMD_QUIT,None))

	def receive(self, data):
		""" Send receive data to flasher thread """
		self.command.put((self.CMD_DATA_RECEIVED, data))

	def upload_from_server(self, filename):
		""" Send upload zip file from server """
		self.command.put((self.CMD_UPLOAD_FROM_SERVER, filename))

	def upload_files(self, filenames):
		""" Send upload files """
		self.command.put((self.CMD_UPLOAD_FILES, filenames))


	def send_key(self, key):
		""" Send key command to flasher thread """
		# If flashing not in progress (in this case the keys are ignored)
		if self.flashing is False:
			self.command.put((self.CMD_KEY_PRESSED, key))
