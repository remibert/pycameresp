""" Class used to manage VT100 """
TABSIZE = 4
BACKSPACE        = "\x7F"
LINE_FEED        = "\n"
CARRIAGE_RETURN  = "\r"
ESCAPE           = "\x1B"

# Supported VT100 escape sequences :
#    ESC c                      Reset to Initial State

#    ESC [ Pn ; Pn H            Direct Cursor Addressing
#    ESC [ Pn ; Pn f            same as above
#    ESC [ Pn J                 Erase in Display
#          Pn = None or 0       From Cursor to End of Screen
#               1               From Beginning of Screen to Cursor
#               2               Entire Screen
#    ESC [ Pn K                 Erase in Line
#          Pn = None or 0       From Cursor to End of Line
#               1               From Beginning of Line to Cursor
#               2               Entire Line

#    ESC [ Pn A                 Cursor Up
#    ESC [ Pn B                 Cursor Down
#    ESC [ Pn C                 Cursor Right
#    ESC [ Pn D                 Cursor Left

#    ESC [ Ps ;...; Ps m        Select Graphic Rendition
#    ESC [ Pn ; Pn r            Set Scrolling Region

#    ESC [ Pn S                 Scroll Scrolling Region Up
#    ESC [ Pn T                 Scroll Scrolling Region Down

#    ESC [ 6 n                  Send Cursor Position Report

#REGEXP_ESCAPE_SEQUENCE=r"(\x1b\[|\x9b)[^@-_]*[@-_]|\x1b[@-_]"
def isascii(char):
	""" Indicates if the char is ascii """
	if len(char) == 1:
		if ord(char) >= 0x20 and ord(char) != 0x7F or char == "\t":
			return True
	return False

DEFAULT_BACKCOLOR = 0xFFFFFF
DEFAULT_FORECOLOR = 0x000000
vga_colors = [
	#     30,       31,       32,       33,       34,       35,       36,       37,
	#     40,       41,       42,       43,       44,       45,       46,       47,
	0x000000, 0xAA0000, 0x00AA00, 0xAA5500, 0x0000AA, 0xAA00AA, 0x00AAAA, 0xAAAAAA,
	#     90,       91,       92,       93,       94,       95,       96,       97,
	#    100,      101,      102,      103,      104,      105,      106,      107,
	0x555555, 0xFF5555, 0x55FF55, 0xFFFF55, 0x5555FF, 0xFF55FF, 0x55FFFF, 0xFFFFFF,

	# step = 51
	# for r in range(0,6):
	# 	for g in range(0,6):
	# 		for b in range(0,6):
	# 			rr = (r * step)
	# 			gg = (g * step)
	# 			bb = (b * step)
	# 			color = (rr << 16) | (gg << 8) | (bb)
	# 			print ("0x%06X,"%(color ), end="")
	# 6 × 6 × 6 cube (216 colors): 16 + 36 × r + 6 × g + b (0 ≤ r, g, b ≤ 5)
	0x000000,0x000033,0x000066,0x000099,0x0000CC,0x0000FF,
	0x003300,0x003333,0x003366,0x003399,0x0033CC,0x0033FF,
	0x006600,0x006633,0x006666,0x006699,0x0066CC,0x0066FF,
	0x009900,0x009933,0x009966,0x009999,0x0099CC,0x0099FF,
	0x00CC00,0x00CC33,0x00CC66,0x00CC99,0x00CCCC,0x00CCFF,
	0x00FF00,0x00FF33,0x00FF66,0x00FF99,0x00FFCC,0x00FFFF,
	0x330000,0x330033,0x330066,0x330099,0x3300CC,0x3300FF,
	0x333300,0x333333,0x333366,0x333399,0x3333CC,0x3333FF,
	0x336600,0x336633,0x336666,0x336699,0x3366CC,0x3366FF,
	0x339900,0x339933,0x339966,0x339999,0x3399CC,0x3399FF,
	0x33CC00,0x33CC33,0x33CC66,0x33CC99,0x33CCCC,0x33CCFF,
	0x33FF00,0x33FF33,0x33FF66,0x33FF99,0x33FFCC,0x33FFFF,
	0x660000,0x660033,0x660066,0x660099,0x6600CC,0x6600FF,
	0x663300,0x663333,0x663366,0x663399,0x6633CC,0x6633FF,
	0x666600,0x666633,0x666666,0x666699,0x6666CC,0x6666FF,
	0x669900,0x669933,0x669966,0x669999,0x6699CC,0x6699FF,
	0x66CC00,0x66CC33,0x66CC66,0x66CC99,0x66CCCC,0x66CCFF,
	0x66FF00,0x66FF33,0x66FF66,0x66FF99,0x66FFCC,0x66FFFF,
	0x990000,0x990033,0x990066,0x990099,0x9900CC,0x9900FF,
	0x993300,0x993333,0x993366,0x993399,0x9933CC,0x9933FF,
	0x996600,0x996633,0x996666,0x996699,0x9966CC,0x9966FF,
	0x999900,0x999933,0x999966,0x999999,0x9999CC,0x9999FF,
	0x99CC00,0x99CC33,0x99CC66,0x99CC99,0x99CCCC,0x99CCFF,
	0x99FF00,0x99FF33,0x99FF66,0x99FF99,0x99FFCC,0x99FFFF,
	0xCC0000,0xCC0033,0xCC0066,0xCC0099,0xCC00CC,0xCC00FF,
	0xCC3300,0xCC3333,0xCC3366,0xCC3399,0xCC33CC,0xCC33FF,
	0xCC6600,0xCC6633,0xCC6666,0xCC6699,0xCC66CC,0xCC66FF,
	0xCC9900,0xCC9933,0xCC9966,0xCC9999,0xCC99CC,0xCC99FF,
	0xCCCC00,0xCCCC33,0xCCCC66,0xCCCC99,0xCCCCCC,0xCCCCFF,
	0xCCFF00,0xCCFF33,0xCCFF66,0xCCFF99,0xCCFFCC,0xCCFFFF,
	0xFF0000,0xFF0033,0xFF0066,0xFF0099,0xFF00CC,0xFF00FF,
	0xFF3300,0xFF3333,0xFF3366,0xFF3399,0xFF33CC,0xFF33FF,
	0xFF6600,0xFF6633,0xFF6666,0xFF6699,0xFF66CC,0xFF66FF,
	0xFF9900,0xFF9933,0xFF9966,0xFF9999,0xFF99CC,0xFF99FF,
	0xFFCC00,0xFFCC33,0xFFCC66,0xFFCC99,0xFFCCCC,0xFFCCFF,
	0xFFFF00,0xFFFF33,0xFFFF66,0xFFFF99,0xFFFFCC,0xFFFFFF,

	# for i in range(24):
	# 	color = 8 + i*10
	# 	print("0x%02X%02X%02X,"%(color,color,color))
	# grayscale from black to white in 24 steps
	0x080808, 0x121212, 0x1C1C1C, 0x262626, 0x303030, 0x3A3A3A, 0x444444, 0x4E4E4E,
	0x585858, 0x626262, 0x6C6C6C, 0x767676, 0x808080, 0x8A8A8A, 0x949494, 0x9E9E9E,
	0xA8A8A8, 0xB2B2B2, 0xBCBCBC, 0xC6C6C6, 0xD0D0D0, 0xDADADA, 0xE4E4E4, 0xEEEEEE,
	]

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

class Line:
	""" VT 100 line """
	def __init__(self, width):
		""" VT100 line constructor """
		self.width      = width
		self.line       = ""
		self.forecolors = []
		self.backcolors = []
		self.reverses   = []
		self.htmline    = None
		self.cursor     = None
		self.clear_line()

	def resize(self, width):
		""" Resize the line """
		if width > self.width:
			self.fill(width)
		else:
			self.truncate(width)
		self.width = width
		self.htmline = None

	def fill(self, length):
		""" Fill the end of line if not enough long """
		if length > len(self.line):
			delta = length-len(self.line)
			self.line       += " "*delta
			self.forecolors += [DEFAULT_FORECOLOR]*delta
			self.backcolors += [DEFAULT_BACKCOLOR]*delta
			self.reverses   += [False]*delta
			self.htmline    = None

	def truncate(self, length):
		""" Truncate the line """
		if len(self.line) > length:
			self.line       = self.line      [:length]
			self.forecolors = self.forecolors[:length]
			self.backcolors = self.backcolors[:length]
			self.reverses   = self.reverses  [:length]
			self.htmline    = None

	def clear_line(self):
		""" Clear the content of line """
		self.line       = ""
		self.forecolors = []
		self.backcolors = []
		self.reverses   = []
		self.fill(self.width)

	def replace_char(self, char, forecolor, backcolor, reverse, cursor_column):
		""" Replace character """
		self.htmline = None
		if cursor_column > len(self.line):
			delta = (cursor_column-len(self.line))
			self.line += " "*delta + char
			self.forecolors += [DEFAULT_FORECOLOR]*delta + [forecolor]*len(char)
			self.backcolors += [DEFAULT_BACKCOLOR]*delta + [backcolor]*len(char)
			self.reverses   += [False]*delta             + [reverse]*len(char)
		else:
			self.line       = self.line      [:cursor_column] + char                  + self.line      [cursor_column+1:]
			self.forecolors = self.forecolors[:cursor_column] + [forecolor]*len(char) + self.forecolors[cursor_column+1:]
			self.backcolors = self.backcolors[:cursor_column] + [backcolor]*len(char) + self.backcolors[cursor_column+1:]
			self.reverses   = self.reverses  [:cursor_column] + [reverse  ]*len(char) + self.reverses  [cursor_column+1:]

	def erase_line(self, cursor_column, direction = None):
		""" Erase the line """
		if cursor_column <= self.width and cursor_column >= 0:
			delta = self.width-cursor_column
			# Erase to end of line
			if direction == "0" or direction == "":
				self.line       = self.line      [:cursor_column] + " "*delta
				self.forecolors = self.forecolors[:cursor_column] + [DEFAULT_FORECOLOR]*delta
				self.backcolors = self.backcolors[:cursor_column] + [DEFAULT_BACKCOLOR]*delta
				self.reverses   = self.reverses  [:cursor_column] + [False]*delta
				self.htmline    = None
			# Erase to beginning of line
			elif direction == "1":
				self.line       =  " "*cursor_column                 + self.line      [cursor_column:]
				self.forecolors =  [DEFAULT_FORECOLOR]*cursor_column + self.forecolors[cursor_column:]
				self.backcolors =  [DEFAULT_BACKCOLOR]*cursor_column + self.backcolors[cursor_column:]
				self.reverses   =  [False]*cursor_column             + self.reverses  [cursor_column:]
				self.htmline    = None
			# Erase entire line
			elif direction == "2":
				self.line       = " "*self.width
				self.forecolors += [DEFAULT_FORECOLOR]*self.width
				self.backcolors += [DEFAULT_BACKCOLOR]*self.width
				self.reverses   += [False]*self.width
				self.htmline    = None

	def get(self):
		""" Get the content of line"""
		return self.line

	def to_html(self, cursor=None):
		""" Export line to html with color and reverse video """
		if self.htmline is None or cursor != self.cursor:
			self.cursor = cursor
			previous_forecolor = None
			previous_backcolor = None
			previous_reverse = None
			htmlline = ""
			if cursor is None:
				length = len(self.line.rstrip())
				if length > len(self.line):
					length = len(self.line)
			else:
				length = len(self.line)
			for i in range(length):
				part = ""
				changed = False

				forecolor = self.forecolors[i]
				if forecolor != previous_forecolor:
					changed = True
					previous_forecolor = forecolor

				backcolor = self.backcolors[i]
				if backcolor != previous_backcolor:
					changed = True
					previous_backcolor = backcolor

				reverse = self.reverses[i]
				if reverse != previous_reverse:
					changed = True

				if reverse is True:
					back = forecolor
					fore = backcolor
				else:
					fore = forecolor
					back = backcolor

				if cursor == i:
					back = 0xcFcFcF

				if changed:
					part = '<span style="color:#%06X;background-color:#%06X">'%(fore,back)
					if i > 0:
						part = '</span>' + part
				else:
					part = ""
				char = self.line[i]
				if   char == " ":
					char = "&nbsp;"
				elif char == "<":
					char = "&lt;"
				elif char == ">":
					char = "&gt;"
				elif char == "'":
					char = "&apos;"
				elif char == '"':
					char = "&quot;"
				htmlline += part + char
			htmlline += '</span>'
			self.htmline = htmlline
		return self.htmline

class VT100:
	""" Class which manage the VT100 console """
	def __init__(self, width = 80, height = 20):
		""" Constructor """
		self.width               = width
		self.height              = height
		self.lines               = []

		self.forecolor           = DEFAULT_FORECOLOR
		self.backcolor           = DEFAULT_BACKCOLOR
		self.reverse             = False
		self.region_start        = 0
		self.region_end          = self.height

		self.cursor_line         = 0
		self.cursor_column       = 0
		self.cursor_column_saved = None
		self.cursor_line_saved   = None

		self.escape              = None
		self.modified            = True

		self.set_size(width,height)
		self.cls()
		self.test_number = 0
		self.output              = None

	def reset(self):
		""" Reset to initial state """
		self.forecolor           = DEFAULT_FORECOLOR
		self.backcolor           = DEFAULT_BACKCOLOR
		self.reverse             = False
		self.region_start        = 0
		self.region_end          = self.height

		self.cursor_line         = 0
		self.cursor_column       = 0
		self.cursor_column_saved = None
		self.cursor_line_saved   = None
		self.cls()

	def set_size(self, width, height):
		""" Set the size of console """
		# If size of VT100 display changed
		if self.width != width or self.height != height:
			self.modified = True
			self.width  = width
			self.height = height

			# If lines missing
			if len(self.lines) < self.height:
				# Add empty lines
				count = self.height - len(self.lines)
				for i in range(count):
					self.lines.append(Line(self.width))
			# Resize all lines
			for line in self.lines:
				line.resize(self.width)

			# If too many lines
			if len(self.lines) > self.height:
				# Cut the end of lines
				self.lines = self.lines[:self.height]

			# Fix the cursor position
			self.correct_cursor()

	def correct_cursor(self):
		""" Correct cursor position """
		# If cursor outside the screen by right
		if self.cursor_column >= self.width:
			# Move cursor
			self.cursor_column = self.width-1
		# If cursor outside the screen by bottom
		if self.cursor_line >= self.height:
			# Move cursor
			self.cursor_line = self.height-1

		# If cursor outside the screen by left
		if self.cursor_column < 0:
			# Move cursor
			self.cursor_column = 0
		# If cursor outside the screen by top
		if self.cursor_line < 0:
			# Move cursor
			self.cursor_line = 0

	def get_size(self):
		""" Get the size of console """
		return self.width, self.height

	def cls(self, direction="2"):
		""" Clear screen command """
		# Erase to end of screen
		if direction == "0":
			for i in range(self.cursor_line+1, self.height):
				self.lines[i].clear_line()
			self.lines[self.cursor_line].erase_line(self.cursor_column,"0")
		# Erase to beginning of screen
		elif direction == "1":
			for i in range(0, self.cursor_line):
				self.lines[i].clear_line()
			self.lines[self.cursor_line].erase_line(self.cursor_column,"1")
		# Erase entire screen
		elif direction == "2":
			for line in self.lines:
				line.clear_line()

	def is_modified(self):
		""" Indicates that the console must be refreshed """
		return self.modified

	def set_modified(self):
		""" Force the modification of console """
		self.modified = True

	def treat_char(self, char):
		""" Treat character entered """
		try:
			if ord(char) >= 0x20 and ord(char) != 0x7F:
				if self.cursor_column >= self.width:
					self.cursor_column = 0
					self.auto_scroll(1)
				if self.cursor_line >= self.height:
					self.cursor_line = self.height-1
				self.lines[self.cursor_line].replace_char(char, self.forecolor, self.backcolor, self.reverse, self.cursor_column)
				self.cursor_column += 1
				return True
		except Exception as err:
			return False
		return False

	def to_int(self, value, default=0):
		""" Convert string into integer """
		try:
			result = int(value)
		except:
			result = default
		return result

	def parse_color(self, escape):
		""" Parse vt100 colors """
		result = False
		if len(escape) >= 3:
			# If color modification detected
			if escape[-1] == "m" and escape[1]=="[":
				foreground = None
				background = None
				reverse = None

				data = escape[2:-1]
				values = data.split(';')
				# Case clear
				if len(values) <= 1:
					if len(values[0]) == 0:
						reverse = False
						foreground = DEFAULT_FORECOLOR
						background = DEFAULT_BACKCOLOR
				# Case VT100 large predefined colors
				if len(values) == 3:
					if values[0] == '38' and values[1] == '5':
						color = self.to_int(values[2])
						if color < 256:
							foreground = vga_colors[color]
					elif values[0] == '48' and values[1] == '5':
						color = self.to_int(values[2])
						if color < 256:
							background = vga_colors[color]
				# Case VT100 RGB colors
				elif len(values) == 5:
					if values[0] == '38' and values[1] == '2':
						foreground = ((self.to_int(values[2]) % 256) << 16) | ((self.to_int(values[3])%256) << 8) | ((self.to_int(values[4])%256))
					elif values[0] == '48' and values[1] == '2':
						background = ((self.to_int(values[2]) % 256) << 16) | ((self.to_int(values[3])%256) << 8) | ((self.to_int(values[4])%256))

				# If color not found
				if foreground is None and background is None and reverse is None:
					# Case VT100 reduced predefined colors and reverse
					for value in values:
						value = self.to_int(value)
						if value == 0:
							foreground = DEFAULT_FORECOLOR
							background = DEFAULT_BACKCOLOR
						elif value == 7:
							reverse = True
						elif value >= 30 and value <= 37:
							foreground = vga_colors[value-30]
						elif value == 39:
							foreground = DEFAULT_FORECOLOR
						elif value >= 40 and value <= 47:
							background = vga_colors[value-40]
						elif value == 49:
							background = DEFAULT_BACKCOLOR
						elif value >= 90 and value <= 97:
							foreground = vga_colors[value-90+8]
						elif value >= 100 and value <= 107:
							background = vga_colors[value-100+8]
						elif value == 27:
							reverse = False

				# If color modification detected
				if foreground is not None:
					self.forecolor = foreground
				if background is not None:
					self.backcolor = background
				if reverse is not None:
					self.reverse = reverse
				result = True
		return result

	def parse_erasing_line(self, escape):
		""" Parse vt100 erasing line command """
		if len(escape) >= 3:
			# Erase line
			if escape[-1] == "K":
				if len(escape) == 3:
					self.lines[self.cursor_line].erase_line(self.cursor_column, "")
				elif len(escape) > 3:
					self.lines[self.cursor_line].erase_line(self.cursor_column, escape[2])

	def parse_erasing_screen(self, escape):
		""" Parse vt100 erasing screen command """
		if len(escape) >= 3:
			# Erase screen
			if escape[-1] == "J":
				if len(escape) == 3:
					self.cls("0")
				else:
					self.cls(escape[2])

	def parse_device_attribut(self, escape):
		""" Parse vt100 device attribut """
		if escape == "\x1B[0c":
			self.output = "\x1B[?3;2c" # Respond pycameresp VT

	def parse_cursor(self, escape):
		""" Parse vt100 cursor command """
		try:
			if len(escape) == 2:
				# Cursor down
				if escape[-1] == "D":
					self.cursor_line += 1
					if self.cursor_line >= self.height:
						self.scroll(1,self.height,-1)
						self.cursor_line = self.height-1
				# Cursor up
				elif escape[-1] == "M":
					self.cursor_line -= 1
					if self.cursor_line < 0:
						self.scroll(0,self.height,1)
						self.cursor_line = 0
				# Save cursor position
				elif escape[-1] == "7":
					self.cursor_column_saved = self.cursor_column
					self.cursor_line_saved   = self.cursor_line
				# Restore cursor position
				elif escape[-1] == "8":
					self.cursor_column  = self.cursor_column_saved
					self.cursor_line    = self.cursor_line_saved
			elif len(escape) == 3:
				# Set cursor home
				if escape[1] == "[" and (escape[2] == "f" or escape[2] == "H"):
					self.cursor_column = 0
			elif len(escape) > 3:
				#  Cursor position report
				if escape == "\x1B[6n":
					self.output = "\x1B[%d;%dR"%(self.cursor_line + 1, self.cursor_column + 1)
				# Cursor up pn times - stop at top
				elif escape[-1] == "A":
					move = eval(escape[2:-1])
					self.cursor_line -= move
				# Cursor down pn times - stop at bottom
				elif escape[-1] == "B":
					move = eval(escape[2:-1])
					self.cursor_line += move
				# Cursor right pn times - stop at far right
				elif escape[-1] == "C":
					move = eval(escape[2:-1])
					self.cursor_column += move
				# Cursor left pn times - stop at far left
				elif escape[-1] == "D":
					move = eval(escape[2:-1])
					self.cursor_column -=move
				# Set cursor position - pl Line, pc Column
				elif escape[-1] == "H" or escape[-1] == "f":
					try:
						line, column = escape[2:-1].split(";")
						self.cursor_column = eval(column)-1
						self.cursor_line   = eval(line)-1
					except:
						pass
		except:
			pass
		self.correct_cursor()

	def parse_scroll_region(self, escape):
		""" Parse vt100 scroll region """
		result = False
		if len(escape) >= 3:
			# If scrolling region detected
			if escape[-1] == "r" and escape[1]=="[":
				data = escape[2:-1]
				values = data.split(';')
				if len(values) == 2:
					self.region_start = self.to_int(values[0], 0)-1
					self.region_end   = self.to_int(values[1], self.height)-1
					if self.region_start < 0:
						self.region_start = 0
					elif self.region_start >= self.height:
						self.region_start = self.height
					if self.region_end < 0:
						self.region_end = 0
					elif self.region_end >= self.height:
						self.region_end = self.height
					if self.region_start > self.region_end:
						self.region_end = self.region_start
			# Clear scrolling region
			elif escape == "\x1B[?6l":
				self.region_start = 0
				self.region_end = self.height
			# Scrolling region up
			elif escape[-1] == "S" and escape[1]=="[":
				move = self.to_int(escape[2:-1])
				self.scroll(self.region_start, self.region_end-self.region_start, -move)
			# Scrolling region down
			elif escape[-1] == "T" and escape[1]=="[":
				move = self.to_int(escape[2:-1])
				self.scroll(self.region_start, self.region_end-self.region_start, move)
		return result

	def parse_reset(self, escape):
		""" Parse reset to initial state """
		if escape == "\x1B"+"c":
			self.reset()

	def scroll(self, pos, length, move):
		""" Scroll screen """
		# If position is in the screen
		if pos >= 0 and pos < self.height:
			# If the scroll not null
			if length > 0:
				# If scroll down
				if move > 0:
					# If move greater than the screen
					if move > self.height:
						move = self.height

					# Scroll part
					for i in range(pos + length, pos-1, -1):
						# Move line
						if (i + move) < self.height:
							self.lines[i+move] = self.lines[i]
						# Clear line
						if (i < self.height):
							self.lines[i] = Line(self.width)
				# Else scroll up
				elif move < 0:
					# If move greater than the screen
					if move < (-self.height):
						move = (-self.height)

					# Scroll
					for i in range(pos, pos + length +1):
						# Move line
						if i + move >= pos and i + move < self.height and i < self.height:
							self.lines[i+move] = self.lines[i]
						# Clear line
						if i >= 0 and i < self.height:
							self.lines[i] = Line(self.width)

	def auto_scroll(self, direction):
		""" Automatic scroll """
		self.cursor_line += direction
		# If the scroll is bottom
		if self.cursor_line < 0:
			self.cursor_line = 0
			self.lines.insert(Line(self.width),0)
			self.lines = self.lines[:self.height]
			self.cursor_column = 0
		# If the scroll is top
		elif self.cursor_line >= self.height:
			self.cursor_line = self.height -1
			self.lines = self.lines[1:]
			self.lines.append(Line(self.width))

	def treat_key(self, char):
		""" Treat keys """
		self.output = None
		if self.escape is None:
			if self.treat_char(char) is False:
				if char in "\r":
					self.cursor_column = 0
				elif char in "\n":
					self.cursor_column = 0
					self.auto_scroll(1)
				elif char in "\x08":
					self.cursor_column -= 1
					self.correct_cursor()
				elif char in ESCAPE:
					self.escape = ESCAPE
		else:
			self.escape += char
			if is_key_ended(self.escape):
				escape = self.escape
				self.parse_color         (escape)
				self.parse_erasing_line  (escape)
				self.parse_erasing_screen(escape)
				self.parse_cursor        (escape)
				self.parse_scroll_region (escape)
				self.parse_reset         (escape)
				self.parse_device_attribut(escape)
				self.escape = None
		return self.output

	def to_html(self):
		""" Get the html content of VT100 """
		result = ""
		pos = 0
		for line in self.lines:
			if pos == self.cursor_line:
				cursor = self.cursor_column
			else:
				cursor = None
			pos += 1
			text_line = line.to_html(cursor)
			if pos == self.height:
				result += text_line + "\n"
			else:
				result += text_line + "<br>\n"
		self.modified = False
		return result

	def test_move_abs_cursor(self):
		""" Test the move absolute cursor """
		print("\x1B[2J",end="")
		for i in range(1,self.height+1):
			print("\x1B[%d;%dH#"%(i,i), end="")
		for i in range(1,self.width+1):
			print("\x1B[%d;%dH*"%(0,i), end="")
		for i in range(1,self.width+1):
			print("\x1B[%d;%dH*"%(self.height+1,i), end="")
		for i in range(1,self.height+1):
			print("\x1B[%d;%dH*"%(i,0), end="")
		for i in range(1,self.height+1):
			print("\x1B[%d;%dH*"%(i,self.width+1), end="")

	def test_move_relative_cursor(self):
		""" Test the move relative cursor """
		print("\x1B[%d;%dH"%(3, 7), end="")
		for i in range(10):
			print("\x1B[1C%d\x1B[1D"%i, end="")
		for i in range(10):
			print("\x1B[1B%d\x1B[1D"%i, end="")
		for i in range(10):
			print("\x1B[1D%d\x1B[1D"%i, end="")
		for i in range(10):
			print("\x1B[1A%d\x1B[1D"%i, end="")

	def test_clear_line_part(self):
		""" Test clear line part """
		print("\x1B[%d;%dH"%(self.height//2, self.width//2), end="")
		print("<<<<[]>>>>",end="")
		print("\x1B[5D",end="")
		print("\x1B[K",end="")

		print("\x1B[%d;%dH"%(self.height//2 + 1, self.width//2), end="")
		print("<<<<[]>>>>",end="")
		print("\x1B[5D",end="")
		print("\x1B[0K",end="")

		print("\x1B[%d;%dH"%(self.height//2 + 2, self.width//2), end="")
		print("<<<<[]>>>>",end="")
		print("\x1B[5D",end="")
		print("\x1B[1K",end="")

		print("\x1B[%d;%dH"%(self.height//2 + 3, self.width//2), end="")
		print("<<<<[]>>>>",end="")
		print("\x1B[5D",end="")
		print("\x1B[2K",end="")

	def test_clear_screen_part(self):
		""" Test clear screen part """
		print("\x1B[%d;%dH"%(self.height//2, self.width//2), end="")
		print("<<<<[]>>>>",end="")
		print("\x1B[2D",end="")
		print("\x1B[0J",end="")
		print("\x1B[6D",end="")
		print("\x1B[1J",end="")

	def test_fill_screen(self):
		""" Test fill screen check the automatic line feeld """
		print("\x1B[1;1H", end="")
		for i in range(1680):
			print("%c"%chr((i %96) + 0x20), end="")

	def test_ansi_color(self):
		""" Test ansi color """
		for i in range(11):
			for j in range(10):
				n = 10*i + j
				if (n > 108):
					break
				print("\x1B[%dm %3d\033[m"%(n, n), end="")
			print("\n", end="")

	def test_fill_scroll_screen(self):
		""" Test move cursor with scrolling """
		print("\x1B[2J",end="")
		print("\x1B[1;1H", end="")
		for line in range(self.height):
			print("%c"%(chr(0x41+line))*(self.width),end="")

	def test_scroll_down(self):
		""" Test scrolling down direction """
		print("\x1B[1;1H", end="")
		for i in range(5):
			print("\x1BM",end="") # curseur up, scrolling down

	def test_scroll_up(self):
		""" Test scrolling up direction """
		print("\x1B[%d;1H"%self.height, end="")
		for i in range(5):
			print("\x1BD",end="") # curseur up, scrolling down

	def test_scroll_down_region(self):
		""" Test scroll down region """
		print("\x1B[3;%dr"%(self.height-3), end="")
		for i in range(2):
			print("\x1B[1T", end="")

	def test_scroll_up_region(self):
		""" Test scroll up region """
		print("\x1B[3;%dr"%(self.height-3), end="")
		for i in range(2):
			print("\x1B[1S", end="")

	def test(self):
		""" Unitary test """
		tests= \
		[
			self.test_fill_scroll_screen,
			self.test_scroll_down_region,
			self.test_scroll_down_region,
			self.test_scroll_down_region,
			self.test_scroll_up_region,
			self.test_scroll_up_region,
			self.test_scroll_up_region,
			self.test_fill_scroll_screen,
			self.test_scroll_up,
			self.test_scroll_up,
			self.test_scroll_up,
			self.test_scroll_up,
			self.test_scroll_up,
			self.test_fill_scroll_screen,
			self.test_scroll_down,
			self.test_scroll_down,
			self.test_scroll_down,
			self.test_scroll_down,
			self.test_scroll_down,
			self.test_ansi_color,
			self.test_fill_screen,
			self.test_move_abs_cursor,
			self.test_move_relative_cursor,
			self.test_clear_screen_part,
			self.test_move_abs_cursor,
			self.test_clear_line_part,
		]

		if self.test_number % 1 == 0:
			if self.test_number//1 < len(tests):
				tests[self.test_number//1]()

		self.test_number += 1
