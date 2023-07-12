# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" Class to drive the dfplayer or yx5300 module """ 
# pylint:disable=consider-using-f-string
# https://github.com/0xcafed00d/yx5300/blob/master/docs/Serial%20MP3%20Player%20v1.0%20Manual.pdf
from binascii import hexlify
import machine

# Status
TF_INSERT        = 0x3A  # TF Card was inserted (unsolicited message).
TF_REMOVE        = 0x3B  # TF card was removed (unsolicited message).
PLAY_ENDED       = 0x3D  # Track/file has ended (unsolicited message). Data is the index number of the file just completed.
INIT             = 0x3F  # Initialization complete (unsolicited message). Data is the file store types available (0x02 for TF).
ERR_FILE         = 0x40  # Error file not found. Data is error code (no definition).
ACK_OK           = 0x41  # Message acknowledged ok
STATUS           = 0x42  # Current status. Data high byte is file store (2 for TF); low byte 0=stopped, 1=play, 2=paused.
VOLUME           = 0x43  # Current volume level. Data is volume level [0..30].
EQUALIZER        = 0x44  # Equalizer status. Data is equalizer mode types  0=Normal, 1=Pop, 2=Rock, 3=Jazz, 4=Classic or 5=Base.
TOT_FILES        = 0x48  # TF Total file count
PLAYING          = 0x4C  # Current file playing
FLDR_FILES       = 0x4E  # Total number of files in the folder. Data is the number of files.
TOT_FLDR         = 0x4F  # Total number of folders. Data is the number of folders.

# Command
PLAY_NEXT        = 0x01  # Play next song.
PLAY_PREVIOUS    = 0x02  # Play previous song.
PLAY_WITH_INDEX  = 0x03  # Play song with index number. Data is the index of the file.
VOLUME_UP        = 0x04  # Volume increase by one.
VOLUME_DOWN      = 0x05  # Volume decrease by one.
SET_VOLUME       = 0x06  # Set the volume to level specified. Data is the volume level [0..30].
SET_EQUALIZER    = 0x07  # Set the equalizer to specified level. Data is [0..5] ? 0=Normal, 1=Pop, 2=Rock, 3=Jazz, 4=Classic or 5=Base.
SNG_CYCL_PLAY    = 0x08  # Loop play (repeat) specified track. Data is the track number.
SEL_DEV          = 0x09  # Select file storage device. The only valid choice for data is TF (0x02).
SLEEP_MODE       = 0x0A  # Chip enters sleep mode.
WAKE_UP          = 0x0B  # Chip wakes up from sleep mode.
RESET            = 0x0C  # Chip reset.
PLAY             = 0x0D  # Playback restart.
PAUSE            = 0x0E  # Pause playback.
PLAY_FOLDER_FILE = 0x0F  # Play the file with the specified folder and index number
STOP_PLAY        = 0x16  # Stop playback.
FOLDER_CYCLE     = 0x17  # Loop playback within specified folder. Data is the folder index.
SHUFFLE_PLAY     = 0x18  # Playback shuffle mode. Data is 0 to enable, 1 to disable.
SET_SNGL_CYCL    = 0x19  # Set loop play (repeat) on/off for current file. Data is 0 to enable, 1 to disable.
SET_DAC          = 0x1A  # DAC on/off control (mute sound). Data is 0 to enable DAC, 1 to disable DAC (mute).
PLAY_W_VOL       = 0x22  # Play track at the specified volume. Data hi byte is the track index, low byte is the volume level [0..30].
SHUFFLE_FOLDER   = 0x28  # Playback shuffle mode for folder specified. Data high byte is the folder index.
QUERY_STATUS     = 0x42  # Query Device Status.
QUERY_VOLUME     = 0x43  # Query Volume level.
QUERY_EQUALIZER  = 0x44  # Query current equalizer (disabled in hardware).
QUERY_TOT_FILES  = 0x48  # Query total files in all folders.
QUERY_PLAYING    = 0x4C  # Query which track playing
QUERY_FLDR_FILES = 0x4E  # Query total files in folder. Data is the folder index number.
QUERY_TOT_FLDR   = 0x4F  # Query number of folders.

class DFPlayer:
	""" Dfplayer """
	def __init__(self, rx=13, tx=4, display=False):
		""" Open dfplayer instance """
		self.uart = machine.UART(1, baudrate=9600, rx=rx, tx=tx)
		self.display = display

	def __del__(self):
		""" Close dfplayer """
		if self.uart is not None:
			self.uart.deinit()

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
		# The reception is complicated, because it happens that bytes are lost,
		# and then there is a byte shift on the reception.
		# In this case, the entire reception buffer is emptied
		if self.uart.any() > 0:
			pos = 0
			command = None
			data = None
			fback = None
			flush = False
			buffer = b""
			while self.uart.any() > 0:
				char = self.uart.read(1)
				buffer += char
				if flush is False:
					# Start
					if pos == 0:
						if char[0] == 0x7E:
							pos += 1
						else:
							flush = True
					# Version
					elif pos == 1:
						if char[0] == 0xFF:
							pos += 1
						else:
							flush = True
					# Length
					elif pos == 2:
						if char[0] == 6:
							pos += 1
					# Command
					elif pos == 3:
						command = char[0]
						pos += 1
					# Fback
					elif pos == 4:
						fback = char[0]
						pos += 1
					# Data high
					elif pos == 5:
						data = char[0] << 8
						pos += 1
					# Data low
					elif pos == 6:
						data |= char[0]
						pos += 1
					# Checksum high
					elif pos == 7:
						checksum = char[0] << 8
						pos += 1
					# Checksum low
					elif pos == 8:
						checksum |= char[0]
						pos += 1
					# Stop
					elif pos == 9:
						if char[0] == 0xEF:
							pos += 1
							break
						else:
							flush = True
			if pos == 10:
				if self.display:
					print("Rcv= %02X -> %d"%(command, data))
				return command, data
			else:
				if self.display:
					print("Bad data received ! %s"%(hexlify(buffer," ").upper().decode("utf8")))
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
		self.send(PLAY_FOLDER_FILE, (folder&0xFF) << 8| track, response=response)

	def stop(self, response=False):
		""" Stop """
		if self.display:
			print("Stop")
		self.send(STOP_PLAY, response=response)

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

	def get_status(self):
		""" Send the get status command """
		if self.display:
			print("Get status")
		self.send(QUERY_STATUS, response=True)
