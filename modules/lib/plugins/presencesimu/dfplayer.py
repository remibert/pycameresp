# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" Class to drive the dfplayer or yx5300 module """ 
# https://github.com/0xcafed00d/yx5300/blob/master/docs/Serial%20MP3%20Player%20v1.0%20Manual.pdf
from binascii import hexlify
import machine

# Control commands
PLAY_NEXT                     = 0x01
PLAY_PREVIOUS                 = 0x02
RESET                         = 0x0C
PLAY                          = 0x0D
PLAY_TRACK                    = 0x0F
PAUSE                         = 0x0E
STOP                          = 0x16

# Query commands
GET_STATUS    = 0x42

class DFPlayer:
	""" Dfplayer """
	def __init__(self, rx=13, tx=4, display=False):
		""" Open dfplayer instance """
		self.uart = machine.UART(1, baudrate=9600, rx=rx, tx=tx)
		self.display = display

	def __del__(self):
		""" Close dfplayer """
		if self.uart is not None:
			self.uart.close()

	def checksum(self, frame):
		""" Compute the frame checksum """
		result = 0
		for byte in frame:
			result -= byte
		return result

	def send(self, command, param=0, response=False):
		""" Send command to dfplayer """
		buf = bytearray(10)
		buf[0] = 0x7E
		buf[1] = 0xFF
		buf[2] = 6
		buf[3] = command
		buf[4] = 1 if response else 0
		buf[5] = (param & 0xFF00) >> 8
		buf[6] = (param & 0xFF)
		checksum = self.checksum(buf[1:6])
		buf[7] = (checksum & 0xFF00) >> 8
		buf[8] = (checksum & 0xFF)
		buf[9] = 0xEF
		if self.display:
			print("Snd=",hexlify(buf," ").upper().decode("utf8"))
		self.uart.write(buf)
		return buf

	def receive(self):
		""" Receive query response """
		length = self.uart.any()
		if length > 0:
			buf = bytearray(10)
			self.uart.readinto(buf)
			if self.display:
				print("Rcv=",hexlify(buf," ").upper().decode("utf8"))
			return buf[3], buf[5] << 8 | buf[6]
		return None

	def play(self, response=False):
		""" Play """
		if self.display:
			print("Play")
		self.send(PLAY, response=response)

	def play_track(self, folder, track, response=False):
		""" Play """
		if self.display:
			print("Play track")
		self.send(PLAY_TRACK, (folder&0xFF) << 8| track, response=response)

	def stop(self, response=False):
		""" Stop """
		if self.display:
			print("Stop")
		self.send(STOP, response=response)

	def pause(self, response=False):
		""" Pause """
		if self.display:
			print("Pause")
		self.send(PAUSE, response=response)

	def reset(self, response=False):
		""" Reset """
		if self.display:
			print("Reset")
		self.send(RESET, response=response)

	def play_next(self, response=False):
		""" Play next """
		if self.display:
			print("Next")
		self.send(PLAY_NEXT, response=response)

	def play_previous(self, response=False):
		""" Play previous """
		if self.display:
			print("Previous")
		self.send(PLAY_PREVIOUS, response=response)

	def ask_status(self):
		""" Send the status command """
		if self.display:
			print("Ask status")
		self.send(GET_STATUS, response=True)
