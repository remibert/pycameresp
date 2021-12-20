""" Micropython firmware flasher for esp32 """
import threading
from serial import Serial
import useful

class Flasher(threading.Thread):
	""" Micropython firmware flasher for esp32 """
	def __init__(self):
		""" Constructor with thread on serial port """
		threading.Thread.__init__(self)
		self.port     = None
		self.firmware = None
		self.erase    = False
		self.stop     = False
		self.serial   = None

	def run(self):
		""" Thread core """
		from time import sleep
		while True:
			if self.stop:
				break
			self.flasher()
			if self.stop:
				break
			self.console()
			sleep(1)

	def flasher(self):
		""" Flasher of firmware it use the esptool.py command """
		if self.port is not None and self.port != "" and self.firmware is not None:
			from traceback import format_exc
			import esptool
			try:
				print("\x1B[100;97m")
				flash_command = ["--port", self.port, "--baud", "460800", "--chip", "esp32", "write_flash", "-z", "0x1000", self.firmware]

				if self.erase:
					flash_command.append("--erase-all")

				print("esptool.py %s\n" % " ".join(flash_command))

				esptool.main(flash_command)

				print("\n\x1B[42;93mFirmware successfully flashed.\x1B[m\n")

				print("\x1B[93;101mPress reset button on device\x1B[m")
			except:
				print("\x1B[93;101mFirmware flash failed : \n%s\x1B[m"%format_exc())
			self.firmware = None

	def set_info(self, port=None, firmware=None, erase=None):
		""" Set the information of the flasher """
		self.port     = port
		self.firmware = firmware
		self.erase    = erase

	def cancel(self):
		""" Cancel thread """
		self.stop = True

	def console(self):
		""" Show the console """
		if self.port is not None and self.firmware is None:
			import sys
			port = self.port
			try:
				self.serial = Serial(port=self.port, baudrate=115200, timeout=1)
				self.serial.reset_input_buffer()
				try:
					while self.firmware is None and self.stop is False and port == self.port:
						sys.stdout.write(useful.read_utf8(self.serial))
				except Exception as err:
					pass
				finally:
					self.serial.close()
			except Exception as err:
				print("\x1B[93;101mCannot open serial port\x1B[m")
