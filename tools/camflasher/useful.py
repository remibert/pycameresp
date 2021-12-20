""" Functions useful """

def decode(data):
	""" Decode bytes into string """
	if type(data) == type(""):
		result = data
	else:
		try:
			result = data.decode("utf8")
		except:
			result = data.decode("latin-1")
	return result



def get_len_utf8(key):
	""" Get the length utf8 string """
	if len(key) > 0:
		char = ord(key[0])
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
			if char == "\x1B":
				return False
			elif get_len_utf8(key) == len(key):
				return True
		elif len(key) == 2:
			if key[0] == "\x1B" and key[1] == "\x1B":
				return False
			elif key[0] == "\x1B":
				if  key[1] == "[" or key[1] == "(" or \
					key[1] == ")" or key[1] == "#" or \
					key[1] == "?" or key[1] == "O":
					return False
				else:
					return True
			elif get_len_utf8(key) == len(key):
				return True
		else:
			if ord(key[-1]) >= ord("A") and ord(key[-1]) <= ord("Z"):
				return True
			elif ord(key[-1]) >= ord("a") and ord(key[-1]) <= ord("z"):
				return True
			elif ord(key[-1]) == "~":
				return True
			elif ord(key[0]) != "\x1B" and get_len_utf8(key) == len(key):
				return True
	return False

def read_utf8(stream):
	""" Read utf8 charactere """
	data = stream.read(1)
	result = data
	if len(data) > 0:
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

			# successor length should have the form 10XX XXXX
			if length > 1:
				for _ in range(length):
					result += stream.read(1)
	return result
