""" Micropython firmware flasher for esp32 """
import sys
import time
import threading
import select
import queue
import os
from serial import Serial

class WaitableEvent:
	""" Class handling an event that can be added to a select.
		Implementation based on https://lat.sk/2015/02/multiple-event-waiting-python-3 """
	def __init__(self):
		""" Constructor """
		self.read_fd, self.write_fd = os.pipe()

	def wait(self, timeout=None):
		""" Wait the event, return True if set else return False """
		read_fds, _, _ = select.select([self.read_fd], [], [], timeout)
		return self.read_fd in read_fds

	def is_set(self):
		""" Indicates an event set or not """
		return self.wait(0)

	def clear(self):
		""" Clear the event """
		if self.is_set():
			os.read(self.read_fd, 1)

	def flush(self):
		""" Clear all event """
		while self.is_set():
			self.clear()

	def set(self):
		""" Set the event """
		if not self.is_set():
			os.write(self.write_fd, b'1')

	def fileno(self):
		""" Return the file number of the read side of the pipe, allows this object to be used with select.select(). """
		return self.read_fd

class Flasher(threading.Thread):
	""" Micropython firmware flasher for esp32 """
	def __init__(self):
		""" Constructor with thread on serial port """
		threading.Thread.__init__(self)
		self.port     = ""
		self.key_press_event    = WaitableEvent()
		self.keys    = queue.Queue()
		self.quit_event = WaitableEvent()
		self.changed_event = WaitableEvent()
		self.baud     = None
		self.firmware = None
		self.erase    = False
		self.stop     = False
		self.serial   = None
		self.length   = None
		self.buffer   = None

	def run(self):
		""" Thread core """
		while self.quit_event.is_set() is False:
			self.flasher()
			self.console()

	def flasher(self):
		""" Flasher of firmware it use the esptool.py command """
		if self.quit_event.is_set() is False:
			if self.port is not None and self.baud is not None and self.port != "" and self.firmware is not None:
				from traceback import format_exc
				import esptool
				try:
					print("\x1B[48;5;229m\x1B[38;5;243m")
					flash_command = ["--port", self.port, "--baud", self.baud, "--chip", "auto", "write_flash", "0x1000", self.firmware]

					if self.erase:
						flash_command.append("--erase-all")
					print("\nesptool.py %s" % " ".join(flash_command))
					esptool.main(flash_command)
					print("\n\x1B[42;93mFlashed with success. Remove strap and press reset button\x1B[m")
				except:
					print("\x1B[93;101mFirmware flash failed : \n%s\x1B[m"%format_exc())
				self.firmware = None

	def set_info(self, port=None, baud=None, firmware=None, erase=None):
		""" Set the information of the flasher """
		self.port     = port
		self.baud     = baud
		self.firmware = firmware
		self.erase    = erase
		self.changed_event.set()

	def cancel(self):
		""" Cancel thread """
		self.quit_event.set()

	def get_utf8_length(self, data):
		""" Get the length of utf8 character """
		# 0XXX XXXX one byte
		if data[0] <= 0x7F:
			length = 1
		# 110X XXXX  two length
		else:
			# first byte
			if ((data[0] & 0xE0) == 0xC0):
				length = 2
			# 1110 XXXX  three bytes length
			elif ((data[0] & 0xF0) == 0xE0):
				length = 3
			# 1111 0XXX  four bytes length
			elif ((data[0] & 0xF8) == 0xF0):
				length = 4
			# 1111 10XX  five bytes length
			elif ((data[0] & 0xFC) == 0xF8):
				length = 5
			# 1111 110X  six bytes length
			elif ((data[0] & 0xFE) == 0xFC):
				length = 6
			else:
				# not a valid first byte of a UTF-8 sequence
				length = 1
		return length

	def wait_event(self):
		""" Wait event from serial link or key board pressed """
		read_fds,_,_ = select.select([self.serial.fileno(), self.key_press_event.fileno(), self.quit_event.fileno(), self.changed_event.fileno()],[],[],1000000)
		# If character received from serial
		if self.serial.fileno() in read_fds:
			char = self.serial.read(1)
			# If no utf8 charactere began
			if self.length is None:
				self.length = self.get_utf8_length(char)
				if self.length == 1:
					sys.stdout.write(char)
					self.length = None
				else:
					self.buffer = char
			# Else continu the utf8 read
			else:
				self.buffer += char
				# If utf8 completly read
				if len(self.buffer) == self.length:
					sys.stdout.write(self.buffer)
					self.length = None
		# If key event detected
		if self.key_press_event.fileno() in read_fds:
			key = self.keys.get()
			self.key_press_event.clear()
			self.serial.write(key)
		# If changed event detected
		if self.changed_event.fileno() in read_fds:
			self.changed_event.clear()

	def send_key(self, key):
		""" Send key pressed to serial link """
		self.keys.put_nowait(key)
		self.key_press_event.set()

	def flush_key(self):
		""" Flush all key pressed """
		self.key_press_event.flush()
		with self.keys.mutex:
			self.keys.queue.clear()

	def console(self):
		""" Show the console """
		if self.quit_event.is_set() is False:
			if self.port is not None and self.firmware is None:
				if self.port != "":
					port = self.port

					# Clear all key bufferized before open console
					self.flush_key()
					try:
						# Open serial console
						self.serial = Serial(port=self.port, baudrate=115200, timeout=1)

						# Clear input serial buffer
						self.serial.reset_input_buffer()
						try:
							# While serial not changed
							while self.firmware is None and port == self.port and self.quit_event.is_set() is False:
								self.wait_event()
						except Exception as err:
							pass
						finally:
							self.serial.close()
					except Exception as err:
						print("\x1B[93;101mCannot open serial port\x1B[m")
						self.port = ''
						time.sleep(0.5)
				else:
					print("\x1B[93;101mPlease connect the device\x1B[m")
					self.port = ''
					time.sleep(0.5)
			else:
				time.sleep(0.5)
