# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Classes for exchanging files between the device and the computer """
import time
import os
import io
import binascii
try:
	import filesystem
	import strings
except:
	from tools import filesystem, strings
if filesystem.ismicropython():
	# pylint:disable=import-error
	import micropython

CHUNK_SIZE=192 # The chunk is in base 64 so is 256 in length
ACK=b"\x06"
NAK=b"\x15"

def get_b64_size(size):
	""" Calc size in base64 """
	return ((size*8)//24)*4 + (4 if ((size*8) % 24) > 0 else 0)

class FileError(Exception):
	""" File reader exception """
	# pylint:disable=super-init-not-called
	def __init__(self, message = ""):
		""" File exception constructor """
		self.message = message

class Reader:
	""" Abstract reader class """
	def __init__(self):
		self.value = None

	def read_byte(self, byte):
		""" Read one byte """
		return None

	def get(self):
		""" Get the value completly read or None """
		return self.value

	def set(self, value):
		""" Set the value """
		self.value = value

class IntReader(Reader):
	""" Integer reader """
	def __init__(self, terminator=b"\x0A", ignore=b"\x0D#", length=10):
		""" Constructor """
		Reader.__init__(self)
		self.data = b""
		self.terminator = terminator
		self.ignore = ignore
		self.length= length

	def read_byte(self, byte):
		""" Read the integer byte by byte """
		if len(self.data) <= self.length:
			if byte in self.ignore:
				pass
			elif byte in self.terminator:
				if len(self.data) > 0:
					self.value = int(self.data)
					return self.value
				else:
					raise FileError("Integer empty")
			elif byte in b"0123456789 ":
				if byte not in b" ":
					self.data += byte
			else:
				raise FileError("Not an integer")
		else:
			raise FileError("Integer too long")

class DateReader(Reader):
	""" Read formated date 'YYYY/MM/DD hh:mm:ss'  """
	def __init__(self):
		""" Constructor """
		Reader.__init__(self)
		self.year   = IntReader(terminator = b"/", length=4)
		self.month  = IntReader(terminator = b"/", length=2)
		self.day    = IntReader(terminator = b" ", length=2)
		self.hour   = IntReader(terminator = b":", ignore=b" ", length=2)
		self.minute = IntReader(terminator = b":", length=2)
		self.second = IntReader(length=2)
		self.read_byte = self.read_year

	def read_year(self, byte):
		""" Read year """
		if self.year.read_byte(byte) is not None:
			self.read_byte = self.read_month

	def read_month(self, byte):
		""" Read month """
		if self.month.read_byte(byte) is not None:
			self.read_byte = self.read_day

	def read_day(self, byte):
		""" Read day """
		if self.day.read_byte(byte) is not None:
			self.read_byte = self.read_hour

	def read_hour(self, byte):
		""" Read hour """
		if self.hour.read_byte(byte) is not None:
			self.read_byte = self.read_minute

	def read_minute(self, byte):
		""" Read minute """
		if self.minute.read_byte(byte) is not None:
			self.read_byte = self.read_second

	def read_second(self, byte):
		""" Read second """
		if self.second.read_byte(byte) is not None:
			date = [self.year.get(), self.month.get(), self.day.get(), self.hour.get(), self.minute.get(), self.second.get(), 0, 0, 0]
			self.value = time.mktime(tuple(date))
			return self.value

class FilenameReader(Reader):
	""" Read filename """
	def __init__(self, terminator=b"\x0A", ignore=b"\x0D#", length=256):
		""" Constructor """
		Reader.__init__(self)
		self.data = b""
		self.terminator = terminator
		self.ignore = ignore
		self.length= length

	def read_byte(self, byte):
		""" Read filename byte by byte """
		if len(self.data) <= self.length:
			if byte in self.ignore:
				pass
			# Ignore white space in start of line
			elif byte in b" ":
				if len(self.data) > 0:
					self.data += byte
			elif byte in self.terminator:
				if len(self.data) > 0:
					self.value = self.data.decode("utf8")
					return self.value
				else:
					raise FileError("Filename empty")
			elif byte not in b'^<>:;,?"*|':
				self.data += byte
			else:
				raise FileError("Not a filename")
		else:
			raise FileError("Filename too long")

class PatternReader(Reader):
	""" Read file pattern """
	def __init__(self, terminator=b"\x0A", ignore=b"\x0D#", length=256):
		""" Constructor """
		Reader.__init__(self)
		self.data = b""
		self.terminator = terminator
		self.ignore = ignore
		self.length= length

	def read_byte(self, byte):
		""" Read pattern byte by byte """
		if len(self.data) <= self.length:
			if byte in self.ignore:
				pass
			# Ignore white space in start of line
			elif byte in b" ":
				if len(self.data) > 0:
					self.data += byte
			elif byte in self.terminator:
				if len(self.data) > 0:
					self.value = self.data.decode("utf8")
					return self.value
				else:
					raise FileError("Filename empty")
			elif byte not in b'^<>:;,"|':
				self.data += byte
			else:
				raise FileError("Not a pattern")
		else:
			raise FileError("Pattern too long")

class BlankLineReader(Reader):
	""" Read blank line """
	def __init__(self, terminator=b"\x0A", ignore=b"\x0D"):
		""" Constructor """
		Reader.__init__(self)
		self.data = b""
		self.terminator = terminator
		self.ignore = ignore

	def read_byte(self, byte):
		""" Read blank line byte by byte """
		if byte in self.ignore:
			pass
		elif byte in self.terminator:
			self.value = self.data.decode("utf8")
			return self.value
		else:
			self.data += byte

class BinaryReader(Reader):
	""" Read binary """
	def __init__(self, terminator=b"\x0A", ignore=b"\x0D", length=256):
		""" Constructor """
		Reader.__init__(self)
		self.data = b""
		self.terminator = terminator
		self.ignore = ignore
		self.length= length

	def set_length(self, length):
		""" Set the length of binary content """
		self.length = length

	def read_byte(self, byte):
		""" Read filename byte by byte """
		if len(self.data) < self.length:
			self.data += byte
		elif len(self.data) == self.length:
			if byte in self.ignore:
				pass
			elif byte in self.terminator:
				self.value = self.data
				return self.value
			else:
				raise FileError("Bad binary terminator")

class FileReader:
	""" File reader """
	def __init__(self, simulated=False):
		self.blank    = BlankLineReader()
		self.date     = DateReader()
		self.filename = FilenameReader()
		self.size     = IntReader()
		self.content  = BinaryReader()
		self.blank_content = BlankLineReader()
		self.crc      = IntReader()
		self.crc_computed = 0
		self.read_byte  = self.read_blank
		self.start_content = False
		self.simulated = simulated
		self.read_count = 0

	def read_blank(self, byte):
		""" Read blank line """
		if self.blank.read_byte(byte) is not None:
			self.read_byte = self.read_filename
		return None

	def read_filename(self, byte):
		""" Read filename """
		if self.filename.read_byte(byte) is not None:
			self.read_byte = self.read_date
		return None

	def read_date(self, byte):
		""" Read date """
		if self.date.read_byte(byte) is not None:
			self.read_byte = self.read_size
		return None

	def read_size(self, byte):
		""" Read size of content """
		if self.size.read_byte(byte) is not None:
			self.content.set_length(self.size.get())
			self.read_byte = self.read_content
			self.start_content = True

	def read_content(self, byte):
		""" Read content """
		self.read_count += 1
		if self.content.read_byte(byte) is not None:
			self.read_byte = self.read_crc

	def read_blank_content(self, byte):
		""" Read blank line after content """
		if self.blank_content.read_byte(byte) is not None:
			self.read_byte = self.read_crc
		return None

	def read_crc(self, byte):
		""" Read crc"""
		if self.crc.read_byte(byte) is not None:
			if self.crc.get() in [self.crc_computed,0]:
				return self.crc_computed
			else:
				return -1

	def read(self, directory, in_file, out_file=None):
		""" Read the file completly """
		send_ack(out_file,ACK)
		try:
			# Disable the Ctr-C
			if filesystem.ismicropython() and out_file is not None:
				micropython.kbd_intr(-1)

			result = None
			while result is None and self.blank.get() != "exit":
				if self.start_content is False:
					byte = in_file.read(1)
					# pylint:disable=assignment-from-none
					result = self.read_byte(byte)
				else:
					send_ack(out_file,ACK)

					# Create directory
					filename = filesystem.normpath(directory + "/" + self.filename.get())
					filesystem.makedir(filesystem.split(filename)[0], True)

					# Write file
					self.write_file(filename, self.size.get(), in_file, out_file)

					# Set time of file
					try:
						os.utime(filename,(self.date.get(), self.date.get()))
					except:
						pass

					self.read_byte = self.read_blank_content
					self.start_content = False

			if self.blank.get() != "exit":
				if result is not None:
					# If crc is not correct
					if result == -1:
						send_ack(out_file,NAK)
						result = True
					else:
						send_ack(out_file,ACK)
						result = True
			else:
				result = False
		finally:
			# Enable the Ctr-C
			if filesystem.ismicropython() and out_file is not None:
				micropython.kbd_intr(3)
		return result

	def write_file(self, filename, size, in_file, out_file):
		""" Write the file on disk """
		file = None
		try:
			if self.simulated:
				file = io.BytesIO()
			else:
				file = open(filename, "wb")
			chunk = bytearray(get_b64_size(CHUNK_SIZE))

			if size <= 0:
				send_ack(out_file,ACK)
			else:
				while size > 0:
					count = 0
					part = b""
					part_size = get_b64_size(min(size, CHUNK_SIZE))
					while len(part) < part_size:
						size_to_read = get_b64_size(min(size, CHUNK_SIZE)) - len(part)
						# Receive content part
						if filesystem.ismicropython():
							length = in_file.readinto(chunk, size_to_read)
						else:
							chunk = bytearray(size_to_read)
							length = in_file.readinto(chunk)

						part += chunk[:length]
						if length == 0:
							count += 1
							time.sleep(0.01)
							if count > 300:
								raise FileError("Transmission error")

					# Send ack
					send_ack(out_file,ACK)

					# Convert base64 buffer into binary buffer
					bin_buffer = binascii.a2b_base64(part)

					# Compute crc
					self.crc_computed = binascii.crc32(bin_buffer, self.crc_computed)

					# Write content part received
					file.write(bin_buffer)

					# Decrease the remaining size
					size -= len(bin_buffer)
		finally:
			if file is not None:
				file.close()


class FileWriter:
	""" File writer """
	def write(self, filename, in_file, out_file, directory=None):
		""" Write file """
		result = False

		wait_ack(in_file)

		# If file existing
		if filesystem.exists(filename) and filesystem.isfile(filename):
			size = filesystem.filesize(filename)

			# Send blank line
			out_file.write(b"\x0D\x0A")

			# Send the filename
			if directory is not None:
				filename_ = filename.replace(directory, "")
			else:
				filename_ = filename
			out_file.write(b"# %s\x0D\x0A"%filename_.encode("utf8"))

			# Send the file date
			year,month,day,hour,minute,second,_,_ = strings.local_time(filesystem.filetime(filename))[:8]
			out_file.write(b"# %04d/%02d/%02d %02d:%02d:%02d\x0D\x0A"%(year,month,day,hour,minute,second))

			# Send the file size
			out_file.write(b"# %d\x0D\x0A"%(size))

			# Wait confirmation to send content file
			if wait_ack(in_file):
				crc = 0

				# If file empty
				if size <= 0:
					# Wait reception ack
					wait_ack(in_file)
				else:
					# Open file
					with open(filename, "rb") as file:
						chunk = bytearray(CHUNK_SIZE)
						while size > 0:
							# Read file part
							length = file.readinto(chunk)

							# Encode in base64 and send chunk
							out_file.write(binascii.b2a_base64(chunk[:length]).rstrip())

							# Compute the remaining size
							size -= length

							# Compte crc
							crc = binascii.crc32(chunk[:length], crc)

							# Wait reception ack
							wait_ack(in_file)

				# Send file content terminator
				out_file.write(b"\x0D\x0A")

				# Write crc32 and file terminator
				out_file.write(b"# %d\x0D\x0A"%crc)

				# Waits for confirmation that the file has been received wit success or not
				result = wait_ack(in_file, True)
		return result

def wait_ack(in_file, nak=False):
	""" Wait acquittement from file sender """
	result = True
	buffer = b""
	# If flow control activated
	if in_file is not None:
		result = False
		while True:
			r = in_file.read(1)
			buffer += r
			# If aquittement
			if r == ACK:
				result = True
				break
			# If not acquittement and nak can be received
			elif r == NAK and nak:
				result = False
				break
			# If communication failed
			elif r != b"":
				raise FileError("Transmission error")
	return result

def send_ack(out_file, buffer):
	""" Send ack or nak """
	if out_file is not None:
		out_file.write(buffer)

class ImporterCommand:
	""" Importer command """
	def __init__(self, directory):
		""" Constructor """
		self.pattern   = PatternReader()
		self.path      = FilenameReader()
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
			return (self.path.get(), self.pattern.get(), True if self.recursive.get() == 1 else False)

	def write(self, file, recursive, in_file, out_file):
		""" Write download command """
		out_file.write("࿋".encode("utf8"))
		wait_ack(in_file)
		out_file.write(b"# %s\r\n"%file.encode("utf8"))
		out_file.write(b"# %s\r\n"%self.directory.encode("utf8"))
		out_file.write(b"# %d\r\n"%(1 if recursive else 0))
		wait_ack(in_file)

	def read(self, in_file, out_file):
		""" Read the file completly """
		send_ack(out_file, ACK)
		result = None
		while result is None:
			byte = in_file.read(1)
			# pylint:disable=assignment-from-none
			result = self.read_byte(byte)
		send_ack(out_file, ACK)
		return result
