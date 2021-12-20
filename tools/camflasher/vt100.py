""" Class used to manage VT100 """
import useful

TABSIZE = 4
BACKSPACE        = "\x7F"
LINE_FEED        = "\n"
CARRIAGE_RETURN  = "\r"
ESCAPE           = "\x1B"


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

class Line:
	""" VT 100 line """
	def __init__(self):
		""" VT100 line constructor """
		self.clear_line()

	def clear_line(self):
		""" Clear the content of line """
		self.line = ""
		self.forecolors = []
		self.backcolors = []
		self.reverses = []
		self.htmline = None

	def set_data(self, lst, data, cursor_column):
		""" Set data into the line at the cursor position"""
		if len(lst) > 0:
			lst = lst[:cursor_column] + data
			if cursor_column < len(lst)-1:
				lst += lst[cursor_column+1:]
		else:
			if type(lst) == type(""):
				lst += data
			else:
				lst.append(data)
		return lst

	def replace_char(self, char, forecolor, backcolor, reverse, cursor_column):
		""" Replace character """
		# pylint:disable=attribute-defined-outside-init
		self.htmline = None
		if len(self.line) > 0:
			line = self.line[:cursor_column] + char
			if cursor_column < len(line) - 1:
				self.line = line + self.line[cursor_column+1:]
			else:
				self.line = line
		else:
			self.line = char

		if len(self.forecolors) > 0:
			line = self.forecolors[:cursor_column] + [forecolor]*len(char)
			if cursor_column < len(line) - 1:
				self.forecolors = line + self.forecolors[cursor_column+1:]
			else:
				self.forecolors = line
		else:
			self.forecolors = [forecolor]*len(char)

		if len(self.backcolors) > 0:
			line = self.backcolors[:cursor_column] + [backcolor]*len(char)
			if cursor_column < len(line) - 1:
				self.backcolors = line + self.backcolors[cursor_column+1:]
			else:
				self.backcolors = line
		else:
			self.backcolors = [backcolor]*len(char)

		if len(self.reverses) > 0:
			line = self.reverses[:cursor_column] + [reverse]*len(char)
			if cursor_column < len(line) - 1:
				self.reverses = line + self.reverses[cursor_column+1:]
			else:
				self.reverses = line
		else:
			self.reverses = [reverse]*len(char)

	def erase_line(self, cursor_column, direction = None):
		""" Erase the line """
		# pylint:disable=attribute-defined-outside-init
		if direction == 1:
			self.line       = self.line      [cursor_column:]
			self.forecolors = self.forecolors[cursor_column:]
			self.backcolors = self.backcolors[cursor_column:]
			self.reverses   = self.reverses  [cursor_column:]
			self.htmline    = None
		elif direction == -1:
			self.line       = self.line      [:cursor_column]
			self.forecolors = self.forecolors[:cursor_column]
			self.backcolors = self.backcolors[:cursor_column]
			self.reverses   = self.reverses  [:cursor_column]
			self.htmline    = None

	def get(self):
		""" Get the content of line"""
		return self.line

	def to_html(self, width):
		""" Export line to html with color and reverse video """
		# pylint:disable=attribute-defined-outside-init
		if self.htmline is None:
			previous_forecolor = None
			previous_backcolor = None
			previous_reverse = None
			htmlline = ""
			length = min(width,len(self.line))
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

				if changed:
					part = '<span style="color:#%06X;background-color:#%06X">'%(fore,back)
					if i > 0:
						part = '</span>' + part
				else:
					part = ""
				htmlline += part + self.line[i]
			htmlline += '</span><br>'
			self.htmline = htmlline
		return self.htmline


class VT100:
	""" Class which manage the VT100 console """
	def __init__(self, read_only=False):
		""" Constructor """
		self.cls()

	def cls(self):
		""" Clear screen """
		self.lines = []
		self.forecolor = DEFAULT_FORECOLOR
		self.backcolor = DEFAULT_BACKCOLOR
		self.reverse   = False
		self.cursor_line   = 0
		self.cursor_column = 0
		self.tab_cursor_column   = 0
		self.tab_size      = TABSIZE
		self.escape = None
		self.line_feed()

	def get_count_lines(self):
		""" Get the total of lines """
		result = len(self.lines)
		if result > 1:
			if self.lines[-1].get() == "":
				result -= 1
		return result

	def get_cursor_line(self):
		""" Get the current line of the cursor """
		return self.cursor_line

	def get_tab_cursor_column(self):
		""" Get the column of cursor in tabuled line """
		# pylint:disable=attribute-defined-outside-init
		line = self.lines[self.cursor_line].get()
		column = 0
		self.tab_cursor_column = 0
		while column < self.cursor_column:
			if line[column] == "\t":
				pos = self.tab_cursor_column%self.tab_size
				self.tab_cursor_column += self.tab_size-pos
				column += 1
			else:
				tab = line.find("\t",column)
				if tab > 0:
					delta = tab - column
					if column + delta > self.cursor_column:
						delta = self.cursor_column - column
						self.tab_cursor_column += delta
						column += delta
					else:
						self.tab_cursor_column += delta
						column += delta
				else:
					delta = self.cursor_column - column
					self.tab_cursor_column += delta
					column += delta

	def set_cursor_column(self):
		""" When the line change compute the cursor position with tabulation in the line """
		# pylint:disable=attribute-defined-outside-init
		line = self.lines[self.cursor_line].get()
		column = 0
		tab_cursor_column = 0
		lenLine = len(line)
		column = 0
		while column < lenLine:
			char = line[column]
			# If the previous position found exactly in the current line
			if tab_cursor_column == self.tab_cursor_column:
				self.cursor_column = column
				break
			# If the previous position not found in the current line
			if tab_cursor_column > self.tab_cursor_column:
				# Keep last existing position
				self.cursor_column = column
				break
			# If tabulation found
			if char == "\t":
				tab_cursor_column += self.tab_size-(tab_cursor_column%self.tab_size)
				column += 1
			else:
				# Optimization to accelerate the cursor position
				tab = line.find("\t", column)

				# Tabulation found
				if tab > 0:
					delta = tab - column
					# If the tabulation position is after the previous tabulation cursor
					if delta + tab_cursor_column > self.tab_cursor_column:
						# Move the cursor to the left
						self.cursor_column = column + (self.tab_cursor_column - tab_cursor_column)
						break
					else:
						# Another tabulation found, move it after
						tab_cursor_column += delta
						column += delta
				# Tabulation not found
				else:
					# Move the cursor to the end of line
					self.cursor_column = column + (self.tab_cursor_column - tab_cursor_column)
					break
		else:
			if len(line) >= 1:
				self.cursor_column = len(line)-1
			else:
				self.cursor_column = 0

	def change_line(self, moveLine):
		""" Move the cursor on another line """
		# pylint:disable=attribute-defined-outside-init
		# If cursor is before the first line
		if moveLine + self.cursor_line < 0:
			# Set the cursor to the first line
			self.cursor_line = 0
			self.cursor_column = 0
			self.change_column(0)
		# If the cursor is after the last line
		elif moveLine + self.cursor_line >= len(self.lines):
			self.cursor_line = len(self.lines) -1
			self.cursor_column = len(self.lines[self.cursor_line].get())
			self.change_column(0)
		# else the cursor is in the lines of text
		else:
			self.cursor_line += moveLine
			if len(self.lines) - 1 == self.cursor_line:
				lenLine = len(self.lines[self.cursor_line].get())
			else:
				lenLine = len(self.lines[self.cursor_line].get())-1

			self.set_cursor_column()
			# If the new cursor position is outside the last line of text
			if self.cursor_column > lenLine:
				self.cursor_column = lenLine

	def change_column(self, move_column):
		""" Move the cursor on another column """
		# pylint:disable=attribute-defined-outside-init
		cursor_line   = self.cursor_line
		cursor_column = self.cursor_column
		# If the cursor go to the previous line
		if move_column + self.cursor_column < 0:
			# If start of line
			if abs(move_column) > 1:
				self.cursor_column = 0
			# If move to the left and must go to previous line
			elif self.cursor_line > 0:
				self.cursor_line -= 1
				self.cursor_column = len(self.lines[self.cursor_line].get())-1
		# If the cursor is at the end of line
		elif move_column + self.cursor_column > len(self.lines[self.cursor_line].get())-1:
			# If the cursor is on the last line of file
			if abs(move_column) > 1 or self.cursor_line+1 == len(self.lines):
				# If the file is empty
				if self.lines[self.cursor_line].get() == "":
					self.cursor_column = 0
					self.tab_cursor_column = 0
				# If the last line of contains return char
				elif self.lines[self.cursor_line].get()[-1] == "\n":
					# Move cursor before return
					self.cursor_column = len(self.lines[self.cursor_line].get())-1
				else:
					# Move cursor after the last char
					self.cursor_column = len(self.lines[self.cursor_line].get())

			# If the cursor is on the end of line and must change of line
			elif self.cursor_line+1 < len(self.lines):
				self.cursor_line += 1
				self.cursor_column = 0
				self.tab_cursor_column = 0
		# Normal move of cursor
		else:
			# Next or previous column
			self.cursor_column += move_column
		if abs(move_column) > 0:
			self.get_tab_cursor_column()

		if self.cursor_column == cursor_column and self.cursor_line == cursor_line:
			return False
		else:
			return True

	def backspace(self):
		""" Manage the backspace key """
		self.replace_char(" ")

	def line_feed(self):
		""" Manage the line feed """
		# pylint:disable=attribute-defined-outside-init
		if self.cursor_line +1 >= len(self.lines):
			self.lines.append(Line())
		self.change_line(1)
		self.change_column(-100000000000)

	def carriage_return(self):
		""" Manage the carriage return """
		self.change_column(-100000000000)

	def replace_char(self, char):
		""" Replace character """
		# pylint:disable=attribute-defined-outside-init
		try:
			self.lines[self.cursor_line].replace_char(char, self.forecolor, self.backcolor, self.reverse, self.cursor_column)
		except:
			self.lines[self.cursor_line] = char

		self.change_column(1)

	def add_char(self, char):
		""" Manage other key, add character """
		# pylint:disable=attribute-defined-outside-init
		result = False
		if ord(char) >= 0x20 and ord(char) != 0x7F or ord(char) == 6:
			self.replace_char(char)
			result = True
		return result

	def move_cursor(self, line, column):
		""" Move the cursor """
		# pylint:disable=attribute-defined-outside-init
		self.cursor_line   = line
		self.cursor_column = column
		self.change_column(0)
		self.get_tab_cursor_column()

	def treat_char(self, char):
		""" Treat character entered """
		# pylint:disable=attribute-defined-outside-init
		if ord(char) >= 0x20 and ord(char) != 0x7F:
			self.add_char(char)
			return True
		return False

	def parse_color(self, escape):
		""" Parse vt100 colors """
		# pylint:disable=attribute-defined-outside-init
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
						color = int(values[3])
						if color < 256:
							foreground = vga_colors[color]
					elif values[0] == '48' and values[1] == '5':
						color = int(values[3])
						if color < 256:
							background = vga_colors[color]
				# Case VT100 RGB colors
				elif len(values) == 5:
					if values[0] == '38' and values[1] == '2':
						foreground = ((int(values[2]) % 256) << 16) | ((int(values[3])%256) << 8) | ((int(values[4])%256))
					elif values[0] == '48' and values[1] == '2':
						background = ((int(values[2]) % 256) << 16) | ((int(values[3])%256) << 8) | ((int(values[4])%256))

				# If color not found
				if foreground is None and background is None and reverse is None:
					# Case VT100 reduced predefined colors and reverse
					for value in values:
						value = int(value)
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

	def parse_erasing(self, escape):
		""" Parse vt100 erasing command """
		# pylint:disable=attribute-defined-outside-init
		if len(escape) >= 3:
			# Erase screen
			if escape[-1] == "J":
				if len(escape) > 3:
					if   escape[2] == "0":
						pass
					elif escape[2] == "1":
						pass
					elif escape[2] == "2":
						self.cls()
			# Erase line
			elif escape[-1] == "K":
				if len(escape) > 3:
					#  erase to end of line
					if   escape[2] == "0":
						self.lines[self.cursor_line].erase_line(self.cursor_column, 1)
					#  Erase to beginning of line
					elif escape[2] == "1":
						self.lines[self.cursor_line].erase_line(self.cursor_column, -1)
						self.cursor_column = 0
					# Erase entire line
					elif escape[2] == "2":
						self.lines[self.cursor_line].clear_line()
						self.cursor_column = 0
					# pass

	def treat_key(self, char):
		""" Treat keys """
		# pylint:disable=attribute-defined-outside-init
		if self.escape is None:
			if self.treat_char(char) is False:
				if   char in BACKSPACE:
					self.backspace()
				elif char in LINE_FEED:
					self.line_feed()
				elif char in CARRIAGE_RETURN:
					self.carriage_return()
				elif char in ESCAPE:
					self.escape = ESCAPE
		else:
			self.escape += char
			if useful.is_key_ended(self.escape):
				escape = self.escape
				self.parse_color(escape)
				self.parse_erasing(escape)
				self.escape = None

	def forget_lines(self, count):
		""" Forget older lines from vt100 console """
		# pylint:disable=attribute-defined-outside-init
		if count > 0:
			if len(self.lines) > count:
				self.lines         = self.lines[count:]
				self.cursor_line -= count
				if self.cursor_line < 0:
					self.cursor_line = 0

	def get_content(self, width):
		""" Get the html content of VT100 """
		result = ""
		for line in self.lines:
			result += line.to_html(width)
		return result
