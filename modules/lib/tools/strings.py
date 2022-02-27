# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Strings utilities """
import binascii
import time

def local_time(date=None):
	""" Safe local time, it return 2000/1/1 00:00:00 if date can be extracted """
	try:
		year,month,day,hour,minute,second,weekday,yearday = time.localtime(date)[:8]
	except:
		year,month,day,hour,minute,second,weekday,yearday = 2000,1,1,0,0,0,0,0
	return year,month,day,hour,minute,second,weekday,yearday

def date_to_string(date = None):
	""" Get a string with the current date """
	return date_to_bytes(date).decode("utf8")

def date_to_bytes(date = None):
	""" Get a bytes with the current date """
	year,month,day,hour,minute,second,weekday,yearday = local_time(date)[:8]
	return b"%04d/%02d/%02d  %02d:%02d:%02d"%(year,month,day,hour,minute,second)

def date_ms_to_string():
	""" Get a string with the current date with ms """
	ms = (time.time_ns() // 1000000)%1000
	year,month,day,hour,minute,second,weekday,yearday = local_time(None)[:8]
	return "%04d/%02d/%02d %02d:%02d:%02d.%03d"%(year,month,day,hour,minute,second,ms)

def date_to_filename(date = None):
	""" Get a filename with a date """
	filename = date_to_string(date)
	filename = filename.replace("  "," ")
	filename = filename.replace(" ","_")
	filename = filename.replace("/","-")
	filename = filename.replace(":","-")
	return filename

def date_to_path(date=None):
	""" Get a path with year/month/day/hour """
	year,month,day,hour,minute,second,weekday,yearday = local_time(date)[:8]
	return b"%04d/%02d/%02d/%02dh%02d"%(year,month,day,hour,minute)

def size_to_string(size, largeur=6):
	""" Convert a size in a string with k, m, g, t..."""
	return size_to_bytes(size, largeur).decode("utf8")

def size_to_bytes(size, largeur=6):
	""" Convert a size in a bytes with k, m, g, t..."""
	if size > 1073741824*1024:
		return  b"%*.2fT"%(largeur, size / (1073741824.*1024.))
	elif size > 1073741824:
		return  b"%*.2fG"%(largeur, size / 1073741824.)
	elif size > 1048576:
		return b"%*.2fM"%(largeur, size / 1048576.)
	elif size > 1024:
		return b"%*.2fK"%(largeur, size / 1024.)
	else:
		return b"%*dB"%(largeur, size)

def tobytes(datas, encoding="utf8"):
	""" Convert data to bytes """
	result = datas
	if type(datas) == type(""):
		result = datas.encode(encoding)
	elif type(datas) == type([]):
		result = []
		for item in datas:
			result.append(tobytes(item, encoding))
	elif type(datas) == type((0,0)):
		result = []
		for item in datas:
			result.append(tobytes(item, encoding))
		result = tuple(result)
	elif type(datas) == type({}):
		result = {}
		for key, value in datas.items():
			result[tobytes(key,encoding)] = tobytes(value, encoding)
	return result

def tostrings(datas, encoding="utf8"):
	""" Convert data to strings """
	result = datas
	if type(datas) == type(b""):
		result = datas.decode(encoding)
	elif type(datas) == type([]):
		result = []
		for item in datas:
			result.append(tostrings(item, encoding))
	elif type(datas) == type((0,0)):
		result = []
		for item in datas:
			result.append(tostrings(item, encoding))
		result = tuple(result)
	elif type(datas) == type({}):
		result = {}
		for key, value in datas.items():
			result[tostrings(key,encoding)] = tostrings(value, encoding)
	return result

def tofilename(filename):
	""" Replace forbid characters in filename """
	filename = tostrings(filename)
	if len(filename) > 0:
		for char in "<>:/\\|?*":
			filename = filename.replace(char,"_%d_"%ord(char))
	return filename

def isascii(char):
	""" Indicates if the char is ascii """
	if len(char) == 1:
		if ord(char) >= 0x20 and ord(char) != 0x7F or char == "\t":
			return True
	return False

def isupper(char):
	""" Indicates if the char is upper """
	if len(char) == 1:
		if ord(char) >= 0x41 and ord(char) <= 0x5A:
			return True
	return False

def islower(char):
	""" Indicates if the char is lower """
	if len(char) == 1:
		if ord(char) >= 0x61 and ord(char) < 0x7A:
			return True
	return False

def isdigit(char):
	""" Indicates if the char is a digit """
	if len(char) == 1:
		if ord(char) >= 0x31 and ord(char) <= 0x39:
			return True
		return False

def isalpha(char):
	""" Indicates if the char is alpha """
	return isupper(char) or islower(char) or isdigit(char)

def isspace(char):
	""" Indicates if the char is a space, tabulation or new line """
	if char == " " or char == "\t" or char == "\n" or char == "\r":
		return True
	return False

def ispunctuation(char):
	""" Indicates if the char is a punctuation """
	if  (ord(char) >= 0x21 and ord(char) <= 0x2F) or \
		(ord(char) >= 0x3A and ord(char) <= 0x40) or \
		(ord(char) >= 0x5B and ord(char) <= 0x60) or \
		(ord(char) >= 0x7B and ord(char) <= 0x7E):
		return True
	else:
		return False

def get_length_utf8(key):
	""" Get the length utf8 string """
	if len(key) > 0:
		char = key[0]
		if char <= 0x7F:
			return 1
		elif char >= 0xC2 and char <= 0xDF:
			return 2
		elif char >= 0xE0 and char <= 0xEF:
			return 3
		elif char >= 0xF0 and char <= 0xF4:
			return 4
		return 1
	else:
		return 0

def is_key_ended(key):
	""" Indicates if the key completly entered """
	if len(key) == 0:
		return False
	else:
		char = key[-1]
		if len(key) == 1:
			if char == 0x1B:
				return False
			elif get_length_utf8(key) == len(key):
				return True
		elif len(key) == 2:
			if key[0] == b"\x1B" and key[1] == b"\x1B":
				return False
			elif key[0] == b"\x1B":
				if  key[1] == b"[" or key[1] == b"(" or \
					key[1] == b")" or key[1] == b"#" or \
					key[1] == b"?" or key[1] == b"O":
					return False
				else:
					return True
			elif get_length_utf8(key) == len(key):
				return True
		else:
			if key[-1] >= ord("A") and key[-1] <= ord("Z"):
				return True
			elif key[-1] >= ord("a") and key[-1] <= ord("z"):
				return True
			elif key[-1] == b"~":
				return True
			elif key[0] != b"\x1B" and get_length_utf8(key) == len(key):
				return True
	return False

def dump(buff, withColor=True):
	""" dump buffer """
	if withColor:
		string = "\x1B[7m"
	else:
		string = ""
	if type(buff) == type(b"") or type(buff) == type(bytearray()):
		for i in buff:
			if isascii(chr(i)):
				string += chr(i)
			else:
				string += "\\x%02x"%i
	else:
		for i in buff:
			if isascii(i):
				string += i
			else:
				string += "\\x%02x"%ord(i)
	if withColor:
		string += "\x1B[m"
	return string

def dump_line (data, line = None, width = 0):
	""" dump a data data in hexadecimal on one line """
	size = len(data)
	fill = 0

	# Calculation of the filling length
	if width > size:
		fill = width-size

	# Displaying values in hex
	line.write(binascii.hexlify(data, " ").upper())

	# Filling of vacuum according to the size of the dump
	line.write(b'   '*fill)

	# Display of ASCII codes
	line.write(b' |')

	for i in data:
		if i >= 0x20 and  i < 0x7F:
			line.write(i.to_bytes(1,"big"))
		else:
			line.write(b'.')

	# Filling of vacuum according to the size of the dump
	line.write(b' '*fill)

	# End of data ascii
	line.write(b'|')

def compute_hash(string):
	""" Compute hash
	>>> print(compute_hash("1234"))
	49307
	>>> print(compute_hash(b"1234"))
	49307
	"""
	string = tostrings(string)
	hash_ = 63689
	for char in string:
		hash_ = hash_ * 378551 + ord(char)
	return hash_ % 65536

try:
	# pylint: disable=no-name-in-module

	from time import ticks_ms
	def ticks():
		""" Count tick elapsed from start """
		return ticks_ms()
except:
	def ticks():
		""" Count tick elapsed from start """
		return (int)(time.time() * 1000)

def ticks_to_string():
	""" Create a string with tick in seconds """
	tick = ticks()
	return "%d.%03d s"%(tick/1000, tick%1000)

def get_utf8_length(data):
	""" Get the length of utf8 character """
	# 0XXX XXXX one byte
	if data <= 0x7F:
		length = 1
	# 110X XXXX  two length
	else:
		# first byte
		if ((data & 0xE0) == 0xC0):
			length = 2
		# 1110 XXXX  three bytes length
		elif ((data & 0xF0) == 0xE0):
			length = 3
		# 1111 0XXX  four bytes length
		elif ((data & 0xF8) == 0xF0):
			length = 4
		# 1111 10XX  five bytes length
		elif ((data & 0xFC) == 0xF8):
			length = 5
		# 1111 110X  six bytes length
		elif ((data & 0xFE) == 0xFC):
			length = 6
		else:
			# not a valid first byte of a UTF-8 sequence
			length = -1
	return length
