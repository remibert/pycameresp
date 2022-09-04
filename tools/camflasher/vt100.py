# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLETS
""" Class used to manage VT100 """
# pylint:disable=too-many-lines
# pylint:disable=consider-using-f-string
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


COLOR_OK    ="\x1B[42;93m"
COLOR_FAILED="\x1B[93;101m"
COLOR_NONE  ="\x1B[m"

TEXT_BACKCOLOR    = 0xFFFFFFFF
TEXT_FORECOLOR    = 0xFF000000
REVERSE_BACKCOLOR = 0xFFAAAAAA
REVERSE_FORECOLOR = 0xFF000000
CURSOR_BACKCOLOR  = 0xFFAAAAAA
CURSOR_FORECOLOR  = 0xFF000000


DEFAULT_COLORS = {
	"text_colors":{
		"text_backcolor"   : 0xFFFFFAE6,
		"text_forecolor"   : 0xFF4D4700,
		"cursor_backcolor" : 0xFF645D00,
		"cursor_forecolor" : 0xFFFFFCD9,
		"reverse_backcolor": 0xFFDFD9A8,
		"reverse_forecolor": 0xFF322D00,
	},
	"ansi_colors":[
		0xFF000000, 0xFFAA0000, 0xFF009800, 0xFFAA5500, 0xFF0000AA, 0xFFAA00AA, 0xFF009898, 0xFFAAAAAA,
		0xFF555555, 0xFFFF5555, 0xFF55FF55, 0xFFFFFF55, 0xFF5555FF, 0xFFFF55FF, 0xFF55FFFF, 0xFFFFFFFF]
}


FLAG_REVERSE   = 0x01
FLAG_BOLD      = 0x02
FLAG_ITALIC    = 0x04
FLAG_UNDERLINE = 0x08
FLAG_FAINT     = 0x10

VGA_COLORS = [
	#       30,         31,         32,         33,         34,         35,         36,         37,
	#       40,         41,         42,         43,         44,         45,         46,         47,
	0xFF000000, 0xFFAA0000, 0xFF00AA00, 0xFFAA5500, 0xFF0000AA, 0xFFAA00AA, 0xFF00AAAA, 0xFFAAAAAA,

	#       90,         91,         92,         93,         94,         95,         96,         97,
	#      100,        101,        102,        103,        104,        105,        106,        107,
	0xFF555555, 0xFFFF5555, 0xFF55FF55, 0xFFFFFF55, 0xFF5555FF, 0xFFFF55FF, 0xFF55FFFF, 0xFFFFFFFF,

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
	0xFF000000,0xFF000033,0xFF000066,0xFF000099,0xFF0000CC,0xFF0000FF,
	0xFF003300,0xFF003333,0xFF003366,0xFF003399,0xFF0033CC,0xFF0033FF,
	0xFF006600,0xFF006633,0xFF006666,0xFF006699,0xFF0066CC,0xFF0066FF,
	0xFF009900,0xFF009933,0xFF009966,0xFF009999,0xFF0099CC,0xFF0099FF,
	0xFF00CC00,0xFF00CC33,0xFF00CC66,0xFF00CC99,0xFF00CCCC,0xFF00CCFF,
	0xFF00FF00,0xFF00FF33,0xFF00FF66,0xFF00FF99,0xFF00FFCC,0xFF00FFFF,
	0xFF330000,0xFF330033,0xFF330066,0xFF330099,0xFF3300CC,0xFF3300FF,
	0xFF333300,0xFF333333,0xFF333366,0xFF333399,0xFF3333CC,0xFF3333FF,
	0xFF336600,0xFF336633,0xFF336666,0xFF336699,0xFF3366CC,0xFF3366FF,
	0xFF339900,0xFF339933,0xFF339966,0xFF339999,0xFF3399CC,0xFF3399FF,
	0xFF33CC00,0xFF33CC33,0xFF33CC66,0xFF33CC99,0xFF33CCCC,0xFF33CCFF,
	0xFF33FF00,0xFF33FF33,0xFF33FF66,0xFF33FF99,0xFF33FFCC,0xFF33FFFF,
	0xFF660000,0xFF660033,0xFF660066,0xFF660099,0xFF6600CC,0xFF6600FF,
	0xFF663300,0xFF663333,0xFF663366,0xFF663399,0xFF6633CC,0xFF6633FF,
	0xFF666600,0xFF666633,0xFF666666,0xFF666699,0xFF6666CC,0xFF6666FF,
	0xFF669900,0xFF669933,0xFF669966,0xFF669999,0xFF6699CC,0xFF6699FF,
	0xFF66CC00,0xFF66CC33,0xFF66CC66,0xFF66CC99,0xFF66CCCC,0xFF66CCFF,
	0xFF66FF00,0xFF66FF33,0xFF66FF66,0xFF66FF99,0xFF66FFCC,0xFF66FFFF,
	0xFF990000,0xFF990033,0xFF990066,0xFF990099,0xFF9900CC,0xFF9900FF,
	0xFF993300,0xFF993333,0xFF993366,0xFF993399,0xFF9933CC,0xFF9933FF,
	0xFF996600,0xFF996633,0xFF996666,0xFF996699,0xFF9966CC,0xFF9966FF,
	0xFF999900,0xFF999933,0xFF999966,0xFF999999,0xFF9999CC,0xFF9999FF,
	0xFF99CC00,0xFF99CC33,0xFF99CC66,0xFF99CC99,0xFF99CCCC,0xFF99CCFF,
	0xFF99FF00,0xFF99FF33,0xFF99FF66,0xFF99FF99,0xFF99FFCC,0xFF99FFFF,
	0xFFCC0000,0xFFCC0033,0xFFCC0066,0xFFCC0099,0xFFCC00CC,0xFFCC00FF,
	0xFFCC3300,0xFFCC3333,0xFFCC3366,0xFFCC3399,0xFFCC33CC,0xFFCC33FF,
	0xFFCC6600,0xFFCC6633,0xFFCC6666,0xFFCC6699,0xFFCC66CC,0xFFCC66FF,
	0xFFCC9900,0xFFCC9933,0xFFCC9966,0xFFCC9999,0xFFCC99CC,0xFFCC99FF,
	0xFFCCCC00,0xFFCCCC33,0xFFCCCC66,0xFFCCCC99,0xFFCCCCCC,0xFFCCCCFF,
	0xFFCCFF00,0xFFCCFF33,0xFFCCFF66,0xFFCCFF99,0xFFCCFFCC,0xFFCCFFFF,
	0xFFFF0000,0xFFFF0033,0xFFFF0066,0xFFFF0099,0xFFFF00CC,0xFFFF00FF,
	0xFFFF3300,0xFFFF3333,0xFFFF3366,0xFFFF3399,0xFFFF33CC,0xFFFF33FF,
	0xFFFF6600,0xFFFF6633,0xFFFF6666,0xFFFF6699,0xFFFF66CC,0xFFFF66FF,
	0xFFFF9900,0xFFFF9933,0xFFFF9966,0xFFFF9999,0xFFFF99CC,0xFFFF99FF,
	0xFFFFCC00,0xFFFFCC33,0xFFFFCC66,0xFFFFCC99,0xFFFFCCCC,0xFFFFCCFF,
	0xFFFFFF00,0xFFFFFF33,0xFFFFFF66,0xFFFFFF99,0xFFFFFFCC,0xFFFFFFFF,

	# for i in range(24):
	# 	color = 8 + i*10
	# 	print("0x%02X%02X%02X,"%(color,color,color))
	# grayscale from black to white in 24 steps
	0xFF080808, 0xFF121212, 0xFF1C1C1C, 0xFF262626, 0xFF303030, 0xFF3A3A3A, 0xFF444444, 0xFF4E4E4E,
	0xFF585858, 0xFF626262, 0xFF6C6C6C, 0xFF767676, 0xFF808080, 0xFF8A8A8A, 0xFF949494, 0xFF9E9E9E,
	0xFFA8A8A8, 0xFFB2B2B2, 0xFFBCBCBC, 0xFFC6C6C6, 0xFFD0D0D0, 0xFFDADADA, 0xFFE4E4E4, 0xFFEEEEEE,
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

def to_html_color(color):
	""" Convert color into html color """
	return "#%06X"%(color & 0xFFFFFF)

class Line:
	""" VT 100 line """
	def __init__(self, width):
		""" VT100 line constructor """
		self.width      = width
		self.line       = ""
		self.forecolors = []
		self.backcolors = []
		self.flags      = []
		self.htmline    = None
		self.cursor     = None
		self.cursor_on  = False
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
			self.forecolors += [TEXT_FORECOLOR]*delta
			self.backcolors += [TEXT_BACKCOLOR]*delta
			self.flags      += [0]*delta
			self.htmline    = None

	def truncate(self, length):
		""" Truncate the line """
		if len(self.line) > length:
			self.line       = self.line      [:length]
			self.forecolors = self.forecolors[:length]
			self.backcolors = self.backcolors[:length]
			self.flags      = self.flags     [:length]
			self.htmline    = None

	def clear_line(self):
		""" Clear the content of line """
		self.line       = ""
		self.forecolors = []
		self.backcolors = []
		self.flags      = []
		self.fill(self.width)

	def replace_char(self, char, forecolor, backcolor, flags, cursor_column):
		""" Replace character """
		self.htmline = None
		if cursor_column > len(self.line):
			delta = (cursor_column-len(self.line))
			self.line += " "*delta + char
			self.forecolors += [TEXT_FORECOLOR]*delta + [forecolor]*len(char)
			self.backcolors += [TEXT_BACKCOLOR]*delta + [backcolor]*len(char)
			self.flags      += [0]*delta              + [flags]*len(char)
		else:
			self.line       = self.line      [:cursor_column] + char                  + self.line      [cursor_column+1:]
			self.forecolors = self.forecolors[:cursor_column] + [forecolor]*len(char) + self.forecolors[cursor_column+1:]
			self.backcolors = self.backcolors[:cursor_column] + [backcolor]*len(char) + self.backcolors[cursor_column+1:]
			self.flags      = self.flags     [:cursor_column] + [flags    ]*len(char) + self.flags     [cursor_column+1:]

	def erase_line(self, cursor_column, direction = None):
		""" Erase the line """
		if cursor_column <= self.width and cursor_column >= 0:
			delta = self.width-cursor_column
			# Erase to end of line
			if direction == "0" or direction == "":
				self.line       = self.line      [:cursor_column] + " "*delta
				self.forecolors = self.forecolors[:cursor_column] + [TEXT_FORECOLOR]*delta
				self.backcolors = self.backcolors[:cursor_column] + [TEXT_BACKCOLOR]*delta
				self.flags      = self.flags     [:cursor_column] + [0]*delta
				self.htmline    = None
			# Erase to beginning of line
			elif direction == "1":
				self.line       =  " "*cursor_column                 + self.line      [cursor_column:]
				self.forecolors =  [TEXT_FORECOLOR]*cursor_column + self.forecolors[cursor_column:]
				self.backcolors =  [TEXT_BACKCOLOR]*cursor_column + self.backcolors[cursor_column:]
				self.flags      =  [0]*cursor_column                 + self.flags     [cursor_column:]
				self.htmline    = None
			# Erase entire line
			elif direction == "2":
				self.line       = " "*self.width
				self.forecolors += [TEXT_FORECOLOR]*self.width
				self.backcolors += [TEXT_BACKCOLOR]*self.width
				self.flags      += [0]*self.width
				self.htmline    = None

	def get(self):
		""" Get the content of line"""
		return self.line

	def to_html(self, cursor=None, cursor_on=False):
		""" Export line to html with color and reverse video """
		if self.htmline is None or cursor != self.cursor or cursor_on != self.cursor_on:
			self.cursor = cursor
			self.cursor_on = cursor_on
			previous_forecolor = None
			previous_backcolor = None
			previous_reverse   = None
			previous_underline = None
			previous_bold      = None
			previous_italic    = None
			previous_faint     = None
			htmlline = ""

			# If the line not content cursor
			if cursor is None:
				# The line can be simplified
				stripped_length = len(self.line.rstrip())
				length = len(self.line)
				can_cut = True

				# Search in the end of line if the can be simplified
				for i in range(stripped_length, length):
					# If the end of line content faint
					if self.flags[i] & FLAG_FAINT:
						can_cut = False
						break
					# If the end of line content underline
					if self.flags[i] & FLAG_UNDERLINE:
						can_cut = False
						break
					# If the end of line content reversion
					if self.flags[i] & FLAG_REVERSE:
						can_cut = False
						break
					# If the end of line content italic
					if self.flags[i] & FLAG_ITALIC:
						can_cut = False
						break
					# If the end of line content bold
					if self.flags[i] & FLAG_BOLD:
						can_cut = False
						break
					# Or if the end of line content backcolor
					if self.backcolors[i] != TEXT_BACKCOLOR:
						can_cut = False
						break
					# Or if the end of line content forecolor
					if self.forecolors[i] != TEXT_FORECOLOR:
						can_cut = False
						break
				# The line can be simplified to boost performance
				if can_cut:
					length = stripped_length
			else:
				length = len(self.line)

			cursor_set = False
			# For all character in the line
			for i in range(length):
				part = ""
				changed = False

				# Treat the forecolor case
				forecolor = self.forecolors[i]
				if forecolor != previous_forecolor:
					changed = True
					previous_forecolor = forecolor

				# Treat the backcolor case
				backcolor = self.backcolors[i]
				if backcolor != previous_backcolor:
					changed = True
					previous_backcolor = backcolor

				# Treat the reverse case
				reverse = self.flags[i] & FLAG_REVERSE
				if reverse != previous_reverse:
					changed = True
					previous_reverse = reverse

				# Treat the underline case
				underline = self.flags[i] & FLAG_UNDERLINE
				if underline != previous_underline:
					changed = True
					previous_underline = underline

				# Treat the faint case
				faint = self.flags[i] & FLAG_FAINT
				if faint != previous_faint:
					changed = True
					previous_faint = faint

				# Treat the italic case
				italic = self.flags[i] & FLAG_ITALIC
				if italic != previous_italic:
					changed = True
					previous_italic = italic

				# Treat the faint case
				bold = self.flags[i] & FLAG_BOLD
				if bold != previous_bold:
					changed = True
					previous_bold = bold

				# In case of reverse
				if reverse != 0:
					if backcolor == TEXT_BACKCOLOR:
						back = REVERSE_BACKCOLOR
					else:
						back = forecolor

					if forecolor == TEXT_FORECOLOR:
						fore = REVERSE_FORECOLOR
					else:
						fore = backcolor
				else:
					fore = forecolor
					back = backcolor

				# If the previous character is with cursor
				if cursor_set is True:
					# Force the change of color
					changed = True
					cursor_set = False

				flags_html = ""
				if underline:
					flags_html += "text-decoration: underline;"

				if faint and bold:
					flags_html += "font-weight: bold;"
				elif faint:
					flags_html += "font-weight: lighter;"
				elif bold:
					flags_html += "font-weight: bold;"
				else:
					flags_html += "font-weight: normal;"

				if italic:
					flags_html += "font-style: italic;"
				else:
					flags_html += "font-style: normal;"

				if 0 <= fore <= 255:
					fore = VGA_COLORS[fore]

				if 0 <= back <= 255:
					back = VGA_COLORS[back]

				back = to_html_color(back)
				fore = to_html_color(fore)
				# If cursor on this character
				if cursor == i:
					if cursor_on:
						part = '<span style="color:%s;background-color:%s;%s">'%(to_html_color(CURSOR_FORECOLOR), to_html_color(CURSOR_BACKCOLOR),flags_html)
					else:
						part = '<span style="color:%s;background-color:%s;%s">'%(fore,back,flags_html)
					if i > 0:
						part = '</span>' + part
					cursor_set = True
				else:
					# The color must be changed
					if changed:
						part = '<span style="color:%s;background-color:%s;%s">'%(fore,back,flags_html)
						if i > 0:
							part = '</span>' + part
					else:
						part = ""

				# Treat specials characters
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

	def replace_color(self, backcolor, forecolor):
		""" Replace the default background color and text color """
		# pylint:disable=consider-using-enumerate
		# pylint:disable=global-variable-not-assigned
		global TEXT_BACKCOLOR, TEXT_FORECOLOR
		for i in range(len(self.forecolors)):
			if self.forecolors[i] == TEXT_FORECOLOR:
				self.forecolors[i] = forecolor
		for i in range(len(self.backcolors)):
			if self.backcolors[i] == TEXT_BACKCOLOR:
				self.backcolors[i] = backcolor
		self.htmline = None


class VT100:
	""" Class which manage the VT100 console """
	def __init__(self, width = 80, height = 20):
		""" Constructor """
		self.width               = width
		self.height              = height
		self.lines               = []

		self.forecolor           = TEXT_FORECOLOR
		self.backcolor           = TEXT_BACKCOLOR
		self.flags               = 0
		self.region_start        = 0
		self.region_end          = self.height

		self.cursor_line         = 0
		self.cursor_column       = 0
		self.previous_line       = -1
		self.previous_column     = -1
		self.cursor_column_saved = None
		self.cursor_line_saved   = None

		self.escape              = None
		self.modified            = True

		self.set_size(width,height)
		self.cls()
		self.test_number = 0
		self.output              = None
		self.cursor_on           = False
		self.edit_detected = 1000

	def reset(self):
		""" Reset to initial state """
		self.forecolor           = TEXT_FORECOLOR
		self.backcolor           = TEXT_BACKCOLOR
		self.flags               = 0
		self.region_start        = 0
		self.region_end          = self.height

		self.cursor_line         = 0
		self.cursor_column       = 0
		self.cursor_column_saved = None
		self.cursor_line_saved   = None
		self.cls()

	def set_colors(self, colors):
		""" Change the default colors """
		# pylint:disable=global-variable-not-assigned
		global TEXT_BACKCOLOR, TEXT_FORECOLOR, CURSOR_BACKCOLOR, CURSOR_FORECOLOR, REVERSE_FORECOLOR, REVERSE_BACKCOLOR, VGA_COLORS
		for line in self.lines:
			line.replace_color(colors["text_colors"]["text_backcolor"], colors["text_colors"]["text_forecolor"])
		TEXT_BACKCOLOR    = colors["text_colors"]["text_backcolor"]
		TEXT_FORECOLOR    = colors["text_colors"]["text_forecolor"]
		CURSOR_BACKCOLOR  = colors["text_colors"]["cursor_backcolor"]
		CURSOR_FORECOLOR  = colors["text_colors"]["cursor_forecolor"]
		REVERSE_BACKCOLOR = colors["text_colors"]["reverse_backcolor"]
		REVERSE_FORECOLOR = colors["text_colors"]["reverse_forecolor"]
		self.forecolor    = colors["text_colors"]["text_forecolor"]
		self.backcolor    = colors["text_colors"]["text_backcolor"]

		for i in range(16):
			VGA_COLORS[i] = colors["ansi_colors"][i]
		self.modified = True

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

	def blink_cursor(self):
		""" Reverse the color of cursor """
		self.modified = True
		if self.previous_line != self.cursor_line or self.previous_column != self.cursor_column:
			self.cursor_on = True
			self.previous_column = self.cursor_column
			self.previous_line   = self.cursor_line
		else:
			self.cursor_on = not self.cursor_on

	def is_in_editor(self):
		""" Indicates that the editor is running or not """
		if self.edit_detected >= 4:
			return False
		return True

	def treat_char(self, char):
		""" Treat character entered """
		try:
			if ord(char) >= 0x20 and ord(char) != 0x7F:
				if char == "\u25B7":
					self.edit_detected = 0
				else:
					self.edit_detected += 1
				if self.cursor_column >= self.width:
					self.cursor_column = 0
					self.auto_scroll(1)
				if self.cursor_line >= self.height:
					self.cursor_line = self.height-1
				self.lines[self.cursor_line].replace_char(char, self.forecolor, self.backcolor, self.flags, self.cursor_column)
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

	def split(self, value):
		""" Return the value splited according to the right separator """
		if ";" in value:
			return value.split(";")
		else:
			return value.split(":")

	def parse_color(self, escape):
		""" Parse vt100 colors """
		result = False
		if len(escape) >= 3:
			# If color modification detected
			if escape[-1] == "m" and escape[1]=="[":
				foreground = None
				background = None
				flags    = None

				data = escape[2:-1]
				values = self.split(data)
				# Case clear
				if len(values) <= 1:
					if len(values[0]) == 0:
						flags = 0
						foreground = TEXT_FORECOLOR
						background = TEXT_BACKCOLOR
				# Case VT100 large predefined colors
				if len(values) == 3:
					if values[0] == '38' and values[1] == '5':
						color = self.to_int(values[2])
						if color < 256:
							foreground = color
					elif values[0] == '48' and values[1] == '5':
						color = self.to_int(values[2])
						if color < 256:
							background = color
				# Case VT100 RGB colors
				elif len(values) == 5:
					if values[0] == '38' and values[1] == '2':
						foreground = ((self.to_int(values[2]) % 256) << 16) | ((self.to_int(values[3])%256) << 8) | ((self.to_int(values[4])%256))
					elif values[0] == '48' and values[1] == '2':
						background = ((self.to_int(values[2]) % 256) << 16) | ((self.to_int(values[3])%256) << 8) | ((self.to_int(values[4])%256))

				# If color not found
				if foreground is None and background is None and flags is None:
					# Case VT100 reduced predefined colors and reverse
					for value in values:
						value = self.to_int(value)
						if value == 0:
							foreground = TEXT_FORECOLOR
							background = TEXT_BACKCOLOR
							flags   = 0
						elif value == 1:
							if flags is None:
								flags = 0
							flags |= FLAG_BOLD
						elif value == 21:
							if flags is None:
								flags = 0
							flags &= ~FLAG_BOLD
						elif value == 2:
							if flags is None:
								flags = 0
							flags |= FLAG_FAINT
						elif value == 22:
							if flags is None:
								flags = 0
							flags &= ~FLAG_FAINT
						elif value == 3:
							if flags is None:
								flags = 0
							flags |= FLAG_ITALIC
						elif value == 23:
							if flags is None:
								flags = 0
							flags &= ~FLAG_ITALIC
						elif value == 4:
							if flags is None:
								flags = 0
							flags |= FLAG_UNDERLINE
						elif value == 24:
							if flags is None:
								flags = 0
							flags &= ~FLAG_UNDERLINE
						elif value == 7:
							if flags is None:
								flags = 0
							flags |= FLAG_REVERSE
						elif value == 27:
							if flags is None:
								flags = 0
							flags &= ~FLAG_REVERSE
						elif 30 <= value <= 37:
							foreground = value-30
						elif value == 39:
							foreground = TEXT_FORECOLOR
						elif 40 <= value <= 47:
							background = value-40
						elif value == 49:
							background = TEXT_BACKCOLOR
						elif 90 <= value <= 97:
							foreground = value-90+8
						elif 100 <= value <= 107:
							background = value-100+8

				# If color modification detected
				if foreground is not None:
					self.forecolor = foreground
				if background is not None:
					self.backcolor = background
				# if flags changed
				if flags is not None:
					self.flags = flags
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
						line, column = self.split(escape[2:-1])
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
				values = self.split(data)
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
		result = '<body style="background-color:%s">'%to_html_color(TEXT_BACKCOLOR)
		pos = 0
		for line in self.lines:
			if pos == self.cursor_line:
				cursor = self.cursor_column
				cursor_on = self.cursor_on
			else:
				cursor = None
				cursor_on = None
			pos += 1
			text_line = line.to_html(cursor, cursor_on)
			if pos == self.height:
				result += text_line + "\n"
			else:
				result += text_line + "<br>\n"
		result += '</body>'
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
