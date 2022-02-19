# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Classes for exchanging files between the device and the computer """
import time
import os
from binascii import crc32
try:
	import filesystem
except:
	from tools import filesystem

CHUNK_SIZE=512
ACK=b"\x06"
NAK=b"\x15"

class FileError(Exception):
	""" File reader exception """
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
	""" Read formated date 'YYYY/MM/DD hh:mm:ss\x0D\x0A'  """
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
	def __init__(self):
		self.blank    = BlankLineReader()
		self.date     = DateReader()
		self.filename = FilenameReader()
		self.size     = IntReader()
		self.content  = BinaryReader()
		self.blank_content = BlankLineReader()
		self.crc      = IntReader()
		self.crc_computed = 0
		self.read_byte  = self.read_blank

	def read_blank(self, byte):
		""" Read blank line """
		if self.blank.read_byte(byte) is not None:
			self.read_byte = self.read_filename
		return None

	def read_blank_content(self, byte):
		""" Read blank line after content """
		if self.blank_content.read_byte(byte) is not None:
			self.read_byte = self.read_crc
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

	def read_content(self, byte):
		""" Read content """
		if self.content.read_byte(byte) is not None:
			self.read_byte = self.read_crc

	def read_crc(self, byte):
		""" Read crc"""
		if self.crc.read_byte(byte) is not None:
			if self.crc.get() in [self.crc_computed,0]:
				return self.crc_computed
			else:
				return -1

	def read(self, directory, in_file, out_file=None):
		""" Read the file completly """
		result = None
		while result is None:
			if self.read_byte != self.read_content or out_file is None:
				byte = in_file.read(1)
				# pylint:disable=assignment-from-none
				result = self.read_byte(byte)
			else:
				# Start content reception
				out_file.write(ACK)

				# Get size
				size = self.size.get()

				# Create directory
				filename = filesystem.normpath(directory + "/" + self.filename.get())
				filesystem.makedir(filesystem.split(filename)[0], True)

				# Open file
				with open(filename, "wb") as file:
					chunk = bytearray(CHUNK_SIZE)

					while size > 0:
						# Receive content part
						length = in_file.readinto(chunk)

						# Send ack
						out_file.write(ACK)

						# Compute crc
						self.crc_computed = crc32(chunk[:length], self.crc_computed)

						# Write content part received
						file.write(chunk[:length])

						# Decrease the remaining size
						size -= length
				# Set time of file
				try:
					os.utime(filename,(self.date.get(), self.date.get()))
				except:
					pass

				self.read_byte = self.read_blank_content

		if result is not None:
			# If crc is not correct
			if result == -1:
				out_file.write(NAK)
			else:
				out_file.write(ACK)

		return result


class FileWriter:
	""" File writer """
	def write(self, filename, in_file, out_file, directory=None):
		""" Write file """
		result = False

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
			year,month,day,hour,minute,second,_,_ = time.localtime(filesystem.filetime(filename))[:8]
			out_file.write(b"# %04d/%02d/%02d %02d:%02d:%02d\x0D\x0A"%(year,month,day,hour,minute,second))

			# Send the file size
			out_file.write(b"# %d\x0D\x0A"%(size))

			# Wait confirmation to send content file
			if self.wait_ack(in_file):
				crc = 0

				# Open file
				with open(filename_, "rb") as file:
					chunk = bytearray(CHUNK_SIZE)
					while size > 0:
						# Read file part
						length = file.readinto(chunk)

						# Send part
						out_file.write(chunk[:length])

						# Compute the remaining size
						size -= length

						# Compte crc
						crc = crc32(chunk[:length], crc)

						# Wait reception ack
						self.wait_ack(in_file)

				# Send file content terminator
				out_file.write(b"\x0D\x0A")

				# Write crc32 and file terminator
				out_file.write(b"# %d\x0D\x0A"%crc)

				# Waits for confirmation that the file has been received wit success or not
				result = self.wait_ack(in_file, True)
		return result

	def wait_ack(self, in_file, nak=False):
		""" Wait acquittement from file sender """
		result = True
		# If flow control activated
		if in_file is not None:
			result = False
			while True:
				r = in_file.read(1)
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
