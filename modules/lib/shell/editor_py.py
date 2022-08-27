# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# pylint:disable=consider-iterating-dictionary
""" Syntax highlight for python in the editor """
PYTHON_KEYWORDS = b"and as assert break class continue def del elif else except exec finally for from global if import in is lambda None not or pass print raise return try while self as join abs apply bool buffer callable chr cmp coerce compile complex delattr dir dict divmod eval execfile filter float getattr globals hasattr hash hex id input int intern isinstance issubclass len list locals long map max min oct open ord pow range raw_input reduce reload repr round setattr slice str tuple type unichr unicode vars xrange zip with yield True False async await"

NO_COLOR       = b"\x1B[m"
STRING_COLOR   = b"\x1B[31m"
COMMENT_COLOR  = b"\x1B[32m"
NUMBER_COLOR   = b"\x1B[33m"
KEYWORD_COLOR  = b"\x1B[1;34m"
CLASS_COLOR    = b"\x1B[1;35m"
FUNCTION_COLOR = b"\x1B[1;36m"

class Colorizer:
	""" Syntax highlight for python """
	def __init__(self):
		""" Constructor """
		keywords = PYTHON_KEYWORDS.split(b" ")
		keywords.sort()
		self.lexicon = {}
		for keyword in keywords:
			self.lexicon.setdefault(keyword[0],[]).append(keyword)

	def colorize(self, text, out):
		""" Colorize python file """
		STATE_UNDEFINED      = 0
		STATE_KEYWORD        = 1
		STATE_NUMBER         = 2
		STATE_COMMENT        = 3
		STATE_DECIMAL        = 4
		STATE_EXPONENT       = 5
		STATE_BINARY         = 6
		STATE_OCTAL          = 7
		STATE_HEXA           = 8
		STATE_STRING         = 9
		STATE_STRING_CONTENT = 10
		STATE_STRING_ESCAPE  = 11
		STATE_FUNCTION       = 12
		STATE_CLASS          = 13
		state = STATE_UNDEFINED
		pos = 0
		lastpos = 0
		j = 0
		previous_char = 0
		for char in text:
			charactere = char.to_bytes(1,"big")
			# If nothind detected
			if   state == STATE_UNDEFINED:
				word  = b""
				keywords = None
				pos = -1
				# If a keyword start
				if char in self.lexicon.keys():
					if not (0x41 <= previous_char <= 0x5A or 0x61 <= previous_char <= 0x7A or 0x30 <= previous_char <= 0x39 or previous_char == 0x5F):
						pos = j
						state = STATE_KEYWORD
						word  = charactere
						keywords = self.lexicon[char]
				# If decimal number started
				elif 0x31 <= char <= 0x39:
					if 0x41 <= previous_char <= 0x5A or 0x61 <= previous_char <= 0x7A or 0x30 <= previous_char <= 0x39 or previous_char == 0x5F:
						pass
					else:
						state = STATE_DECIMAL
						word = charactere
						pos = j
				# If base number started
				elif char == 0x30:
					if 0x41 <= previous_char <= 0x5A or 0x61 <= previous_char <= 0x7A or 0x30 <= previous_char <= 0x39 or previous_char == 0x5F:
						pass
					else:
						state = STATE_NUMBER
						word = charactere
						pos = j
				# If comment detected
				elif char == 0x23:
					pos = j
					state = STATE_COMMENT
					out.write(text[lastpos:j]+COMMENT_COLOR+text[j:]+NO_COLOR)
					lastpos = len(text)
					break
				# If string detected
				elif char == 0x22 or char == 0x27:
					state = STATE_STRING
					word = charactere
					pos = j
			# If keyword started
			elif state == STATE_KEYWORD:
				# If a keyword continue
				if 0x41 <= char <= 0x5A or 0x61 <= char <= 0x7A or char == 0x5F:
					tmp_word = word + charactere
					count = 0
					for kwd in keywords:
						if kwd.find(word) == 0:
							count += 1
					if count > 0:
						word = tmp_word
				else:
					# If special string detected
					if (char == 0x27 or char == 0x22) and len(word) == 1:
						# Byte string
						if word[0] == 0x62 or word[0] == 0x42:
							word = charactere
							pos = j
							state = STATE_STRING
						# Regular string
						elif word[0] == 0x52 or word[0] == 0x72:
							word = charactere
							pos = j
							state = STATE_STRING
						# Unicode string
						elif word[0] == 0x55 or word[0] == 0x75:
							word = charactere
							pos = j
							state = STATE_STRING
						else:
							word  = b""
							state = STATE_UNDEFINED
							keywords = None
					else:
						if word in keywords:
							out.write(text[lastpos:pos]+KEYWORD_COLOR+word+NO_COLOR)
							if word == b"def":
								state = STATE_FUNCTION
								lastpos = j
								word  = charactere
								keywords = None
							elif word == b"class":
								state = STATE_CLASS
								lastpos = j
								word  = charactere
								keywords = None
							else:
								lastpos = j
								word  = b""
								state = STATE_UNDEFINED
								keywords = None
						else:
							word  = b""
							state = STATE_UNDEFINED
							keywords = None
			# If function name
			elif state == STATE_FUNCTION:
				if 0x41 <= char <= 0x5A or 0x61 <= char <= 0x7A or 0x30 <= char <= 0x39 or char == 0x5F or char == 0x20 or char == 0x09:
					word += charactere
				else:
					out.write(text[lastpos:pos]+FUNCTION_COLOR+word+NO_COLOR)
					lastpos = j
					state = STATE_UNDEFINED
					word  = b""
					keywords = None
			# If class name
			elif state == STATE_CLASS:
				if 0x41 <= char <= 0x5A or 0x61 <= char <= 0x7A or 0x30 <= char <= 0x39 or char == 0x5F or char == 0x20 or char == 0x09:
					word += charactere
				else:
					out.write(text[lastpos:pos]+CLASS_COLOR+word+NO_COLOR)
					lastpos = j
					state = STATE_UNDEFINED
					word  = b""
					keywords = None
			# If decimal detected
			elif state == STATE_DECIMAL:
				if char >= 0x30 and char <= 0x39:
					word += charactere
				elif char == 0x2E:
					if b"." not in word:
						word += charactere
					else:
						state = STATE_UNDEFINED
				elif char == 0x45 or char == 0x65:
					word += charactere
					state = STATE_EXPONENT
				else:
					out.write(text[lastpos:pos]+NUMBER_COLOR+word+NO_COLOR)
					lastpos = j
					state = STATE_UNDEFINED
			# If decimal with exponent
			elif state == STATE_EXPONENT:
				if char >= 0x30 and char <= 0x39:
					word += charactere
				elif char == 0x2B or char == 0x2D:
					if b"+" in word or b"-" in word:
						out.write(text[lastpos:pos]+NUMBER_COLOR+word+NO_COLOR)
						lastpos = j
						state = STATE_UNDEFINED
					else:
						word += charactere
				else:
					out.write(text[lastpos:pos]+NUMBER_COLOR+word+NO_COLOR)
					lastpos = j
					state = STATE_UNDEFINED
			# If number detected
			elif state == STATE_NUMBER:
				# If hexa number detected
				if char == 0x58 or char == 0x78:
					word += charactere
					state = STATE_HEXA
				# If octal number detected
				elif char == 0x4F or char == 0x6F:
					word += charactere
					state = STATE_OCTAL
				# If binary number detected
				elif char == 0x42 or char == 0x62:
					word += charactere
					state = STATE_BINARY
				else:
					if char == 0x2E:
						state = STATE_DECIMAL
						word += charactere
					elif 0x30 <= char <= 0x39 or 0x41 <= char <= 0x46 or 0x61 <= char <= 0x66 or char == 0x5F:
						state = STATE_UNDEFINED
						word  = b""
					else:
						out.write(text[lastpos:pos]+NUMBER_COLOR+word+NO_COLOR)
						lastpos = j
						state = STATE_UNDEFINED
			# If hexa number
			elif state == STATE_HEXA:
				# If hexa detected
				if 0x30 <= char <= 0x39 or 0x41 <= char <= 0x46 or 0x61 <= char <= 0x66:
					word += charactere
				# If not hexa detected
				elif 0x47 <= char <= 0x5A or 0x67 <= char <= 0x7A:
					state = STATE_UNDEFINED
				# If the number ended
				else:
					out.write(text[lastpos:pos]+NUMBER_COLOR+word+NO_COLOR)
					lastpos = j
					state = STATE_UNDEFINED
			# If octal number
			elif state == STATE_OCTAL:
				# If hexa detected
				if 0x30 <= char <= 0x37:
					word += charactere
				# If the number ended
				else:
					out.write(text[lastpos:pos]+NUMBER_COLOR+word+NO_COLOR)
					lastpos = j
					state = STATE_UNDEFINED
			# If binary number
			elif state == STATE_BINARY:
				# If hexa detected
				if 0x30 <= char <= 0x31:
					word += charactere
				# If the number ended
				else:
					out.write(text[lastpos:pos]+NUMBER_COLOR+word+NO_COLOR)
					lastpos = j
					state = STATE_UNDEFINED
			# If string started
			elif state == STATE_STRING:
				if char == word[0]:
					word += charactere
					if len(word) == 3:
						state = STATE_STRING_CONTENT
				else:
					if len(word) == 2:
						out.write(text[lastpos:pos]+STRING_COLOR+word+NO_COLOR)
						lastpos = j
						state = STATE_UNDEFINED
					elif char == 0x5C:
						word += charactere
						state = STATE_STRING_ESCAPE
					else:
						word += charactere
						state = STATE_STRING_CONTENT
			# If escape in string
			elif state == STATE_STRING_ESCAPE:
				word += charactere
				state = STATE_STRING_CONTENT
			# If string content
			elif state == STATE_STRING_CONTENT:
				# String terminated maybe
				if word[0] == char:
					word += charactere
					if len(word) >= 6:
						if word[:3] == b'"""' or word[:3] == b"'''":
							if word[:3] == word[-3:]:
								out.write(text[lastpos:pos]+STRING_COLOR+word+NO_COLOR)
								lastpos = j+1
								state = STATE_UNDEFINED
						elif word[0] == word[-1]:
							out.write(text[lastpos:pos]+STRING_COLOR+word+NO_COLOR)
							lastpos = j+1
							state = STATE_UNDEFINED
					elif len(word) >= 2:
						if word[0] == word[-1]:
							out.write(text[lastpos:pos]+STRING_COLOR+word+NO_COLOR)
							lastpos = j+1
							state = STATE_UNDEFINED
				elif char == 0x5C:
					word += charactere
					state = STATE_STRING_ESCAPE
				else:
					word += charactere

			previous_char = char
			j += 1

		if state in [STATE_NUMBER, STATE_HEXA, STATE_OCTAL, STATE_BINARY, STATE_DECIMAL, STATE_EXPONENT]:
			out.write(text[lastpos:pos]+NUMBER_COLOR+word+NO_COLOR)
		elif state == STATE_KEYWORD:
			if word in keywords:
				out.write(text[lastpos:pos]+KEYWORD_COLOR+word+NO_COLOR)
			else:
				out.write(text[lastpos:])
		elif lastpos < len(text):
			out.write(text[lastpos:])
