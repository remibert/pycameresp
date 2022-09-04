# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Stdout VT100 ouptut on qtextbrowser widget """
import sys
from threading import Lock
from vt100 import VT100
try:
	from PyQt6.QtCore import Qt,QTimer
	from PyQt6.QtWidgets import QTextBrowser
except:
	from PyQt5.QtCore import Qt,QTimer
	from PyQt5.QtWidgets import QTextBrowser

# Main keys
main_keys = {
	Qt.Key.Key_Escape    : b'\x1b',
	Qt.Key.Key_Tab       : b'\t',
	Qt.Key.Key_Backtab   : b'\x1b[Z',
	Qt.Key.Key_Backspace : b'\x7f',
	Qt.Key.Key_Return    : b'\r',
	Qt.Key.Key_Delete    : b'\x1b[3~',
	Qt.Key.Key_Enter     : b"\x03", # Control C, why it is Key_Enter ????
}

# Function keys
function_keys = {
	Qt.Key.Key_F1        : [b"\x1bOP"  ,b"\x1b[1;2P"],
	Qt.Key.Key_F2        : [b"\x1bOQ"  ,b"\x1b[1;2Q"],
	Qt.Key.Key_F3        : [b"\x1bOR"  ,b"\x1b[1;2R"],
	Qt.Key.Key_F4        : [b"\x1bOS"  ,b"\x1b[1;2S"],
	Qt.Key.Key_F5        : [b"\x1b[15~",b"\x1b[15;2~"],
	Qt.Key.Key_F6        : [b"\x1b[17~",b"\x1b[17;2~"],
	Qt.Key.Key_F7        : [b"\x1b[18~",b"\x1b[18;2~"],
	Qt.Key.Key_F8        : [b"\x1b[19~",b"\x1b[19;2~"],
	Qt.Key.Key_F9        : [b"\x1b[20~",b"\x1b[20;2~"],
	Qt.Key.Key_F10       : [b"\x1b[21~",b"\x1b[21;2~"],
	Qt.Key.Key_F11       : [b"\x1b[23~",b"\x1b[23;2~"],
	Qt.Key.Key_F12       : [b"\x1b[24~",b"\x1b[24;2~"],
}

# Arrow keys, page up and down, home and end
move_keys = {
	#                        Nothing   Shift        Meta         Alt            Control       Shift+Alt    Shift+Meta   Shift+Control
	Qt.Key.Key_Up        : [b"\x1b[A" ,b"\x1b[1;2A",b"\x1b[1;5A",b"\x1b\x1b[A" ,b"\x1b[1;5A" ,b"\x1b[1;2A",b"\x1b[1;6A",b"\x1b[1;6A"],
	Qt.Key.Key_Down      : [b"\x1b[B" ,b"\x1b[1;2B",b"\x1b[1;5B",b"\x1b\x1b[B" ,b"\x1b[1;5B" ,b"\x1b[1;2B",b"\x1b[1;6B",b"\x1b[1;6B"],
	Qt.Key.Key_Right     : [b"\x1b[C" ,b"\x1b[1;2C",b"\x1b[1;5C",b"\x1b\x1b[C" ,b"\x1b[1;5C" ,b"\x1b[1;2C",b"\x1b[1;6C",b"\x1b[1;6C"],
	Qt.Key.Key_Left      : [b"\x1b[D" ,b"\x1b[1;2D",b"\x1b[1;5D",b"\x1b\x1b[D" ,b"\x1b[1;5D" ,b"\x1b[1;2D",b"\x1b[1;6D",b"\x1b[1;6D"],
	Qt.Key.Key_Home      : [b"\x1b[H" ,b"\x1b[1;2H",b"\x1b[1;5H",b"\x1b[1;9H"  ,b"\x1b[1;5H" ,b"\x1b[1;2H",b"\x1b[1;6H",b"\x1b[1;6H"],
	Qt.Key.Key_End       : [b"\x1b[F" ,b"\x1b[1;2F",b"\x1b[1;5F",b"\x1b[1;9F"  ,b"\x1b[1;5F" ,b"\x1b[1;2F",b"\x1b[1;6F",b"\x1b[1;6F"],
	Qt.Key.Key_PageUp    : [b"\x1b[5~",b"\x1b[1;4A",b"\x1b[5~"  ,b"\x1b\x1b[5~",b"\x1b[5~"   ,b"\x1b[5~"  ,b"\x1b[5~"  ,b"\x1b[5~"  ],
	Qt.Key.Key_PageDown  : [b"\x1b[6~",b"\x1b[1;4B",b"\x1b[6~"  ,b"\x1b\x1b[6~",b"\x1b[6~"   ,b"\x1b[6~"  ,b"\x1b[6~"  ,b"\x1b[6~"  ],
}

class QStdoutVT100:
	""" Stdout VT100 ouptut on qtextbrowser widget """
	def __init__(self, qtextbrowser):
		""" Constructor with QTextBrowser widget"""
		self.qtextbrowser = qtextbrowser
		self.qtextbrowser.mouseReleaseEvent = self.on_mouse_release_event
		self.qtextbrowser.mousePressEvent   = self.on_mouse_press_event
		self.qtextbrowser.cursorPositionChanged.connect(self.update_selection)
		self.vt100 = VT100()
		self.lock = Lock()
		self.output = []
		self.can_test = False
		self.stdout = sys.stdout
		self.cursor_timer = QTimer(active=True, interval=500)
		self.cursor_timer.timeout.connect(self.on_refresh_cursor)
		self.cursor_timer.start()
		sys.stdout = self
		self.pressed = False
		self.selection_start = None
		self.selection_end = None
		self.cursor_pos = None

	def on_mouse_release_event(self, evt):
		""" Catch mouse release event """
		QTextBrowser.mouseReleaseEvent(self.qtextbrowser, evt)
		self.pressed = False
		self.get_coordinates()

	def on_mouse_press_event(self, evt):
		""" Catch mouse press event """
		QTextBrowser.mousePressEvent(self.qtextbrowser, evt)
		self.pressed = True

	def reset_pressed(self):
		""" Reset the pressed state """
		self.pressed = False

	def is_select_in_editor(self):
		""" Indicates that selection is in editor """
		if (self.selection_start is not None or self.cursor_pos is not None) and \
			self.vt100.is_in_editor() and \
			self.pressed is False:
			return True
		return False

	def is_in_editor(self):
		""" Indicates if editor is opened """
		return self.vt100.is_in_editor()

	def get_selection(self):
		""" Get selection escape sequence """
		result = ""
		selection = False
		if self.cursor_pos is not None:
			result = "\x1B[%d;%dx"%(self.cursor_pos[0], self.cursor_pos[1])
			self.cursor_pos = None
			selection = False
		elif self.selection_start is not None and self.selection_end is not None:
			start_line, start_column = self.selection_start
			end_line, end_column     = self.selection_end
			if start_line == 0:
				start_line = 1
				start_column = 1
			result = "\x1B[%d;%dx\x1B[%d;%dy"%(start_line, start_column, end_line, end_column)
			self.selection_end = None
			self.selection_start = None
			selection = True
		return result, selection

	def get_coordinates(self):
		""" Convert the mouse position into vt100 cursor coordinates """
		cursor = self.qtextbrowser.textCursor()
		start_col = None
		start_line = None
		end_col = None
		end_line = None
		line = 0
		col = 1
		for i in range(cursor.document().characterCount()):
			if cursor.hasSelection():
				if cursor.selectionStart() <= i <= cursor.selectionEnd():
					if start_col is None and start_line is None:
						start_col = col
						start_line = line
					end_col = col
					end_line = line

				elif i > cursor.selectionEnd():
					break
			elif i >= cursor.position():
				break

			if cursor.document().characterAt(i) == "\u2028":
				col = 1
				line += 1
			else:
				col += 1

		if start_line is not None and start_col is not None:
			self.selection_start = (start_line, start_col)

		if end_line is not None and end_col is not None:
			self.selection_end   = (end_line,   end_col)

		if not cursor.hasSelection():
			self.cursor_pos = (line, col)

	def update_selection(self):
		""" Update selection """
		cursor = self.qtextbrowser.textCursor()
		if cursor.hasSelection():
			self.get_coordinates()
		else:
			self.selection_start = None
			self.selection_end   = None

	def __del__(self):
		""" Destructor """
		self.close()

	def close(self):
		""" Close console redirection """
		sys.stdout = self.stdout

	def test(self):
		""" Unitary test """
		if self.can_test:
			self.vt100.test()

	def on_refresh_cursor(self):
		""" Refresh blinking cursor """
		self.vt100.blink_cursor()

	def write(self, string):
		""" Write on stdout """
		if len(string) > 0 and string is not None and string != "":
			try:
				self.lock.acquire()
				# self.stdout.write(string)
				# pylint:disable=consider-using-enumerate
				for char in range(len(string)):
					output = self.vt100.treat_key(string[char])
					if output is not None:
						self.output.append(output)
				self.vt100.set_modified()
			except Exception as err:
				self.stdout.write(err)
			finally:
				self.lock.release()

	def set_size(self, width, height):
		""" Resize event """
		self.vt100.set_size(width,height)

	def get_size(self):
		""" Return the console size """
		return self.vt100.get_size()

	def refresh(self):
		""" Refresh the console """
		result = ""
		self.can_test = True
		if self.pressed is False:
			if self.vt100.is_modified():
				self.qtextbrowser.setHtml(self.vt100.to_html())
				for output in self.output:
					result += output
				self.output = []
		return result

	def set_colors(self, colors):
		""" Change the default colors """
		self.vt100.set_colors(colors)

	def flush(self):
		""" Flush stdout """
		# NEVER NEVER REFRESH HERE ELSE IT CRASH.... self.refresh()

	def isatty(self):
		""" Test whether a file descriptor refers to a terminal """
		return True

	def convert_key_to_vt100(self, key_event):
		""" Convert the key event qt into vt100 key """
		result = None
		key = key_event.key()
		try:
			# PyQt6
			modifier = key_event.keyCombination().keyboardModifiers() & ~Qt.KeyboardModifier.KeypadModifier
		except:
			# PyQt5
			modifier = key_event.modifiers()& ~Qt.KeyboardModifier.KeypadModifier

		if key >= 0x1000000:
			# Manage main keys
			if key in main_keys:
				result = main_keys[key]
			# Manage function keys
			elif key in function_keys:
				normal, shift = function_keys[key]
				if modifier & Qt.KeyboardModifier.ShiftModifier:
					result = shift
				else:
					result = normal
			# Manage move keys
			elif key in move_keys:
				normal, shift, meta, alt, control, shift_alt, shift_meta, shift_control = move_keys[key]
				if modifier & Qt.KeyboardModifier.ShiftModifier and modifier & Qt.KeyboardModifier.MetaModifier:
					result = shift_meta
				elif modifier & Qt.KeyboardModifier.ShiftModifier and modifier & Qt.KeyboardModifier.AltModifier:
					result = shift_alt
				elif modifier & Qt.KeyboardModifier.ShiftModifier and modifier & Qt.KeyboardModifier.ControlModifier:
					result = shift_control
				elif modifier & Qt.KeyboardModifier.ShiftModifier:
					result = shift
				elif modifier & Qt.KeyboardModifier.MetaModifier:
					result = meta
				elif modifier & Qt.KeyboardModifier.AltModifier:
					result = alt
				elif modifier & Qt.KeyboardModifier.ControlModifier:
					result = control
				else:
					result = normal
		else:
			# If control letter pressed
			if key >= 65 and key <= 90 and (modifier & Qt.KeyboardModifier.ControlModifier or modifier & Qt.KeyboardModifier.MetaModifier):
				key -= 64
				result = key.to_bytes(1,"little")
			else:
				result = key_event.text().encode("utf-8")
		return result
