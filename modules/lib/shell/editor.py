#!/usr/bin/python3
# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# pylint:disable=multiple-statements
# pylint:disable=too-many-lines
""" Class defining a VT100 text editor.
This editor works directly in the board.
This allows you to make quick and easy changes directly on the board, without having to use synchronization tools.
This editor allows script execution, and displays errors and execution time.

Editor shortcuts :
<br> - <b>Exit          </b>: Escape
<br> - <b>Move cursor   </b>: Arrows, Home, End, PageUp, PageDown, Ctrl-Home, Ctrl-End, Ctrl-Left, Ctrl-Right
<br> - <b>Selection     </b>: Shift-Arrows, Shift-Home, Shift-End, Alt-Shift-Arrows, Ctrl-Shift-Left, Ctrl-Shift-Right
<br> - <b>Clipboard     </b>: Selection with Ctrl X(Cut), Ctrl-C(Copy), Ctrl-V(Paste)
<br> - <b>Case change   </b>: Selection with Ctrl-U(Toggle majuscule, minuscule)
<br> - <b>Indent        </b>: Selection with Tab(Indent) or Shift-Tab(Unindent)
<br> - <b>Comment block </b>: Selection with Ctrl-Q
<br> - <b>Save          </b>: Ctrl-S
<br> - <b>Find          </b>: Ctrl-F
<br> - <b>Replace       </b>: Ctrl-H
<br> - <b>Toggle mode   </b>: Ctrl-T (Insertion/Replacement)
<br> - <b>Delete line   </b>: Ctrl-L
<br> - <b>Goto line     </b>: Ctrl-G
<br> - <b>Execute       </b>: F5

This editor also works on linux and osx, and can also be used autonomously,
you need to add the useful.py script to its side.
All the keyboard shortcuts are at the start of the script.

On the boards with low memory, it may work, but on very small files, otherwise it may produce an error due to insufficient memory.
"""
import sys
sys.path.append("lib")
sys.path.append("lib/tools")
try:
	from tools import useful
except:
	import useful

TABSIZE = 4          # Tabulation size
HORIZONTAL_MOVE=8    # Scrolling minimal deplacement

ESCAPE           = "\x1b"

# Move shortcuts
UP               = ["\x1b[A"]
DOWN             = ["\x1b[B"]
RIGHT            = ["\x1b[C"]
LEFT             = ["\x1b[D"]
HOME             = ["\x1b[1;3D", "\x1b[H", "\x1b\x1b[D", "\x1b[1~", "\x1bb"]
END              = ["\x1b[1;3C", "\x1b[F", "\x1b\x1b[C", "\x1b[4~", "\x1bf"]
PAGE_UP          = ["\x1b[1;3A", "\x1b[A", "\x1b\x1b[A", "\x1b[5~"]
PAGE_DOWN        = ["\x1b[1;3B", "\x1b[B", "\x1b\x1b[B", "\x1b[6~"]
TOP              = ["\x1b[1;5H"]
BOTTOM           = ["\x1b[1;5F"]
NEXT_WORD        = ["\x1b[1;5C"]
PREVIOUS_WORD    = ["\x1b[1;5D"]

# Selection shortcuts
SELECT_UP        = ["\x1b[1;2A"]
SELECT_DOWN      = ["\x1b[1;2B"]
SELECT_RIGHT     = ["\x1b[1;2C"]
SELECT_LEFT      = ["\x1b[1;2D"]
SELECT_PAGE_UP   = ["\x1b[1;10A","\x1b[1;4A","\x1b[5;2~"]
SELECT_PAGE_DOWN = ["\x1b[1;10B","\x1b[1;4B","\x1b[6;2~"]
SELECT_HOME      = ["\x1b[1;2H","\x1b[1;10D"]
SELECT_END       = ["\x1b[1;2F","\x1b[1;10C"]
SELECT_TOP       = ["\x1b[1;6H"]
SELECT_BOTTOM    = ["\x1b[1;6F"]
SELECT_ALL       = ["\x01"]
SELECT_NEXT_WORD = ["\x1b[1;6C","\x1b[1;4C"]
SELECT_PREV_WORD = ["\x1b[1;6D","\x1b[1;4D"]

# Clipboard shortcuts
CUT              = ["\x18","\x1bx"]                      # Cut
COPY             = ["\x03","\x1bc"]                      # Copy
PASTE            = ["\x16","\x1bv"]                      # Paste

# Selection modification shortcut
INDENT           = ["\t"]                                # Indent
UNINDENT         = ["\x1b[Z"]                            # Unindent
CHANGE_CASE      = ["\x15"]                              # Change case
COMMENT          = ["\x11"]                              # Comment block

DELETE           = ["\x1b[3~"]                           # Delete pressed
BACKSPACE        = ["\x7F"]                              # Backspace pressed
NEW_LINE         = ["\n", "\r"]                          # New line pressed

TOGGLE_MODE      = ["\x14"]                              # Toggle replace/insert mode
EXIT             = [ESCAPE]                              # Exit
FIND             = ["\x06"]                              # Find
FIND_NEXT        = ["\x1bOR"]                            # Find next
FIND_PREVIOUS    = ["\x1b[1;2R"]                         # Find previous
GOTO             = ["\x07"]                              # Goto line
SAVE             = ["\x13","\x1bs"]                      # Save
DELETE_LINE      = ["\x0C"]                              # Delete line
REPLACE          = ["\x08"]                              # Replace
REPLACE_CURRENT  = ["\x12"]                              # Replace the selection
EXECUTE          = ["\x1b[15~"]                          # Execute script

class View:
	""" Class which manage the view of the edit field """
	def __init__(self, view_height, view_top):
		""" Constructor """
		self.line     = 0
		self.column   = 0
		if view_height is None:
			self.height   = 20
		else:
			self.height          = view_height
		self.width               = 80
		self.top                 = view_top
		self.is_refresh_all        = True
		self.is_refresh_line       = False
		self.is_refresh_line_before = False
		self.is_refresh_line_after  = False
		self.refresh_part         = None
		self.text                = None
		self.tab_cursor_column     = 0
		self.sel_line_start        = None
		self.sel_line_end          = None
		self.screen_height = 1
		self.screen_width = 1

	def write(self, data):
		""" Write data to stdout """
		sys.stdout.write(data)

	def flush(self):
		""" Flush text to stdout """
		try:
			sys.stdout.flush()
		except:
			pass

	def set_text(self, text):
		""" Set the text object """
		self.text = text

	def get_screen_position(self):
		""" Get the screen position of cursor """
		return (self.text.get_cursor_line() - self.line + self.top, self.tab_cursor_column - self.column)

	def reset(self):
		""" Reset VT100 """
		self.write("\x1B""c")
		self.flush()

	def reset_scroll_region(self):
		""" Reset VT100 scroll region """
		if self.screen_height > 0:
			self.set_scrolling_region(0, self.screen_height-1)

	def set_scrolling_region(self, top_line, bottom_line):
		""" Define VT100 scroll region """
		if top_line < bottom_line:
			self.write("\x1B[%d;%dr"%(top_line+1,bottom_line+1))

	def scroll_up(self):
		""" Scroll to up """
		self.set_scrolling_region(self.top, self.height+1)
		self.write("\x1B[1S")

	def scroll_down(self):
		""" Scroll to down """
		self.set_scrolling_region(self.top, self.height+1)
		self.write("\x1B[1T")

	def scroll_part_up(self):
		""" Scroll the upper part """
		line, column = self.get_screen_position()
		if line < self.height:
			self.set_scrolling_region(line, self.height+1)
			self.write("\x1B[1S")

	def scroll_part_down(self):
		""" Scroll the lower part """
		line, column = self.get_screen_position()
		if line < self.height:
			self.set_scrolling_region(line+1, self.height+1)
			self.write("\x1B[1T")
		else:
			self.is_refresh_line_after = True

	def move(self):
		""" Move the view """
		self.tab_cursor_column = self.text.get_tab_cursor(self.text.get_cursor_line())
		# Move view port
		if self.tab_cursor_column < self.column:
			self.is_refresh_all = True
			if self.tab_cursor_column > HORIZONTAL_MOVE:
				self.column = self.tab_cursor_column-HORIZONTAL_MOVE
			else:
				self.column = 0
		elif self.tab_cursor_column >= self.column + self.width:
			self.column = self.tab_cursor_column-self.width+HORIZONTAL_MOVE
			self.is_refresh_all = True
		if self.text.get_cursor_line() < self.line:
			delta = self.line - self.text.get_cursor_line()
			self.line = self.text.get_cursor_line()
			if self.line < 0:
				self.line = 0
			if delta <= 1:
				self.scroll_down()
				self.is_refresh_line = True
			else:
				self.is_refresh_all = True
		elif self.text.get_cursor_line() > self.line + self.height:
			delta =  self.text.get_cursor_line() - self.line - self.height
			self.line = self.text.get_cursor_line()-self.height
			if delta <= 1:
				self.scroll_up()
				self.is_refresh_line = True
			else:
				self.is_refresh_all = True

	def set_refresh_line(self):
		""" Indicates that the line must be refreshed """
		self.is_refresh_line = True

	def set_refresh_after(self):
		""" Indicates that all lines after the current line must be refreshed """
		self.is_refresh_line = True
		self.is_refresh_line_after = True

	def set_refresh_before(self):
		""" Indicates that all lines before the current line must be refreshed """
		self.is_refresh_line = True
		self.is_refresh_line_before = True

	def set_refresh_all(self):
		""" Indicates that all lines must be refreshed """
		self.is_refresh_all = True

	def show_line(self, current_line, screen_line, selection_start, selection_end, quick=False):
		""" Show one line """
		if quick:
			line_to_display = ""
		else:
			line_to_display = "\x1B[%d;1f\x1B[K"%(screen_line+1)
		count_line = self.text.get_count_lines()
		if current_line < count_line and current_line >= 0:
			line = self.text.get_tab_line(current_line)
			partLine = line[self.column:self.column+self.width]
			# If the line selected
			if selection_start is not None:
				# If the line not empty
				if len(partLine) >= 1:
					# If the line have carriage return at the end
					if partLine[-1] == "\n":
						# Remove the carriage return
						partLine = partLine[:-1]
				if len(partLine) > 0:
					dummy, sel_line_start, sel_column_start = selection_start
					dummy, sel_line_end,   sel_column_end   = selection_end
					# If the current line is the end of selection
					if current_line == sel_line_end:
						# If the end of selection is outside the visible part
						if sel_column_end - self.column < 0:
							sel_column_end = 0
						else:
							sel_column_end -= self.column

						# If the start of selection is on the previous lines
						if sel_line_start < sel_line_end:
							# Select the start of line
							partLine = "\x1B[7m" + partLine[:sel_column_end] + "\x1B[m" + partLine[sel_column_end:]
						else:
							# Unselect the end of line
							partLine = partLine[:sel_column_end] + "\x1B[m" + partLine[sel_column_end:]
					# If the current line is the start of selection
					if current_line == sel_line_start:
						# If the start of selection is outside the visible part
						if sel_column_start - self.column < 0:
							sel_column_start = 0
						else:
							sel_column_start -= self.column

						# If the end of selection is on the next lines
						if sel_line_start < sel_line_end:
							# Select the end of line
							partLine = partLine[:sel_column_start] + "\x1B[7m" + partLine[sel_column_start:] + "\x1B[m"
						else:
							# Select the start of line
							partLine = partLine[:sel_column_start] + "\x1B[7m" + partLine[sel_column_start:]
					# If the line is completly selected
					if current_line > sel_line_start and current_line < sel_line_end:
						# Select all the line
						partLine = "\x1B[7m" + partLine + "\x1B[m"
				else:
					partLine = ""
				self.write(line_to_display + partLine)
			else:
				self.write(line_to_display + partLine.rstrip())

	def refresh_line(self, selection_start, selection_end):
		""" Refresh line """
		screen_line,     screen_column = self.get_screen_position()
		refreshed = False

		# If the line must be refreshed before the cursor line
		if self.is_refresh_line_before:
			self.is_refresh_line_before = False
			self.show_line(self.text.get_cursor_line()-1, screen_line-1, selection_start, selection_end)
			refreshed = True
		# If the line must be refreshed after the cursor line
		if self.is_refresh_line_after:
			self.is_refresh_line_after = False
			self.show_line(self.text.get_cursor_line()+1, screen_line+1, selection_start, selection_end)
			offset = self.height - screen_line
			self.show_line(self.text.get_cursor_line()+offset+1, screen_line+offset+1, selection_start, selection_end)
			refreshed = True
		# If only the cursor line must be refresh
		if self.is_refresh_line:
			self.is_refresh_line = False
			self.show_line(self.text.get_cursor_line(), screen_line, selection_start, selection_end)
			refreshed = True

		# If no refresh detected and a selection started
		if selection_start is not None and refreshed is False:
			# Refresh the selection
			self.show_line(self.text.get_cursor_line(), screen_line, selection_start, selection_end)

	def refresh(self):
		""" Refresh view """
		selection_start, selection_end = self.text.get_selection()
		if self.refresh_part is not None:
			self.refresh_content(selection_start, selection_end, self.refresh_part)
			self.refresh_part = None
		# Refresh all required
		if self.is_refresh_all:
			self.refresh_content(selection_start, selection_end, True)
			self.is_refresh_all  = False
			self.is_refresh_line = False
		else:
			# If no selection activated
			if selection_start is None:
				# Refresh the current line
				self.refresh_line(selection_start, selection_end)
			else:
				# Refresh the selection
				self.refresh_content(selection_start, selection_end, False)
		self.move_cursor()
		self.flush()

	def refresh_content(self, selection_start, selection_end, all_):
		""" Refresh content """
		# If selection present
		if selection_start is not None:
			# Get the selection
			dummy, sel_line_start, sel_column_start = selection_start
			dummy, sel_line_end,   sel_column_end   = selection_end
			lineStart = sel_line_start
			lineEnd   = sel_line_end
			# The aim of this part is to limit the refresh area
			# If the precedent display show a selection
			if self.sel_line_end is not None and self.sel_line_start is not None:
				# If the start and end of selection is on the sames lines
				if self.sel_line_end == sel_line_end and self.sel_line_start == sel_line_start:
					lineStart = lineEnd = self.text.get_cursor_line()
				else:
					# If the end of selection is after the precedent display
					if self.sel_line_end > sel_line_end:
						lineEnd = self.sel_line_end
					# If the end of selection is on the same line than the precedent display
					elif self.sel_line_end == sel_line_end:
						# If the start of selection is before the precedent display
						if self.sel_line_start < sel_line_start:
							lineEnd = sel_line_start
						else:
							lineEnd = self.sel_line_start
					# If the start of selection is before the precedent display
					if self.sel_line_start < sel_line_start:
						lineStart = self.sel_line_start
					# If the start of selection is on the same line than the precedent display
					elif self.sel_line_start == sel_line_start:
						# If the end of selection is after the precedent display
						if self.sel_line_end > sel_line_end:
							lineStart = sel_line_end
						else:
							lineStart = self.sel_line_end
		else:
			lineStart = 0
			lineEnd = self.line + self.height
		current_line = self.line
		screen_line = self.top
		if type(all_) == type([]):
			lineStart, lineEnd = all_
			all_ = False
		count_line = self.text.get_count_lines()
		maxLine = self.line + self.height
		if all_:
			# Erase the rest of the screen with empty line (used when the text is shorter than the screen)
			self.move_cursor(screen_line, 0)
			self.write("\x1B[J")
			# Refresh all lines visible
			while current_line < count_line and current_line <= maxLine:
				self.show_line(current_line, screen_line, selection_start, selection_end, True)
				screen_line  += 1
				current_line += 1
				if (current_line < count_line and current_line <= maxLine):
					self.write("\n\r")
		else:
			# Refresh all lines visible
			while current_line < count_line and current_line <= maxLine:
				# If the line is in selection or all must be refreshed
				if lineStart <= current_line <= lineEnd or all_:
					self.show_line(current_line, screen_line, selection_start, selection_end)
				screen_line  += 1
				current_line += 1

		# If selection present
		if selection_start is not None:
			# Save current selection
			dummy, self.sel_line_start, dummy = selection_start
			dummy, self.sel_line_end,   dummy   = selection_end

	def hide_selection(self):
		""" Hide the selection """
		selection_start, selection_end = self.text.get_selection()
		if selection_start is not None:
			self.set_refresh_selection()
			self.sel_line_start = None
			self.sel_line_end   = None

	def set_refresh_selection(self):
		""" Indicates that the selection must be refreshed """
		selection_start, selection_end = self.text.get_selection()
		if selection_start is not None:
			# self.is_refresh_all = True
			lineStart = selection_start[1]
			if self.sel_line_start < lineStart:
				lineStart = self.sel_line_start
			lineEnd = selection_end[1]
			if self.sel_line_end > lineEnd:
				lineEnd = self.sel_line_end
			self.refresh_part = [lineStart, lineEnd]

	def move_cursor(self, screen_line=None, screen_column=None):
		""" Move the cursor in the view """
		self.write(self.get_move_cursor(screen_line, screen_column))

	def get_move_cursor(self, screen_line=None, screen_column=None):
		""" Move the cursor in the view """
		if screen_line is None and screen_column is None:
			screen_line, screen_column = self.get_screen_position()
		return "\x1B[%d;%df"%(screen_line+1,screen_column+1)

	def get_screen_size(self):
		""" Get the screen size """
		height, width = useful.get_screen_size()
		self.screen_height = height
		self.screen_width = width
		self.height = height-self.top-1
		self.width  = width
		self.move_cursor()

	def cls(self):
		""" clear the screen """
		self.write("\x1B[2J")
		self.move_cursor(0,0)

class Text:
	""" Class which manage the text edition """
	def __init__(self, read_only=False):
		""" Constructor """
		self.lines = [""]
		self.cursor_line   = 0
		self.cursor_column = 0
		self.tab_cursor_column   = 0
		self.modified     = False
		self.replace_mode  = False
		self.read_only     = read_only
		self.view         = None
		self.tab_size      = TABSIZE
		self.selection_start = None
		self.selection_end   = None
		self.selection = []
		self.filename = None

	def set_view(self, view):
		""" Define the view attached to the text """
		self.view = view

	def get_count_lines(self):
		""" Get the total of lines """
		return len(self.lines)

	def get_cursor_line(self):
		""" Get the current line of the cursor """
		return self.cursor_line

	def get_tab_cursor(self, current_line, current_column=None):
		""" Get position of cursor with line with tabulation """
		if current_column is None:
			cursor_column = self.cursor_column
		else:
			cursor_column = current_column
		line = self.lines[current_line]
		if "\t" in line:
			tab_cursor_column   = 0
			column = 0
			lenLine = len(line)
			while column < cursor_column:
				if line[column] == "\t":
					pos = tab_cursor_column%self.tab_size
					tab_cursor_column += self.tab_size-pos
					column          += 1
				else:
					tab = line.find("\t",column)
					if tab > 0:
						partSize = tab - column
					else:
						partSize = lenLine - column
					if column + partSize > cursor_column:
						partSize = cursor_column - column
					tab_cursor_column += partSize
					column          += partSize
			return tab_cursor_column
		else:
			return cursor_column

	def get_tab_line(self, current_line = None):
		""" Get the tabuled line """
		line = self.lines[current_line]
		if "\t" in line:
			tabLine = ""
			tab_cursor_column   = 0
			lenLine = len(line)
			column = 0
			while column < lenLine:
				char = line[column]
				if char == "\t":
					pos = tab_cursor_column%self.tab_size
					tab_cursor_column += self.tab_size-pos
					tabLine         += " "*(self.tab_size-pos)
					column          += 1
				else:
					tab = line.find("\t",column)
					if tab > 0:
						part = line[column:tab]
					else:
						part = line[column:]
					tab_cursor_column += len(part)
					tabLine         += part
					column          += len(part)
		else:
			tabLine = line
		return tabLine

	def get_tab_cursor_column(self):
		""" Get the column of cursor in tabuled line """
		line = self.lines[self.cursor_line]
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
		line = self.lines[self.cursor_line]
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

	def load(self, filename_):
		""" Load file in the editor """
		self.filename = None
		try:
			self.lines = []
			self.filename = filename_
			file = open(filename_, "r")
			line = file.readline()
			while line != "":
				self.lines.append(line.replace("\r\n","\n"))
				line = file.readline()
			file.close()
			if len(self.lines) == 0:
				self.lines = [""]
		except MemoryError:
			# pylint: disable=raise-missing-from
			raise MemoryError()
		except OSError:
			self.lines = [""]
			# File not existing
		except Exception as err:
			useful.syslog(err)
			self.lines = [""]

	def save(self):
		""" Save text in the file """
		result = False
		if self.read_only is False:
			if self.filename is not None:
				try:
					file = open(self.filename, "w")
					for line in self.lines:
						file.write(line)
					file.close()
					self.modified = False
					result = True
				except Exception as err:
					useful.syslog(err)
		return result

	def change_line(self, moveLine):
		""" Move the cursor on another line """
		# If cursor is before the first line
		if moveLine + self.cursor_line < 0:
			# Set the cursor to the first line
			self.cursor_line = 0
			self.cursor_column = 0
			self.change_column(0)
		# If the cursor is after the last line
		elif moveLine + self.cursor_line >= len(self.lines):
			self.cursor_line = len(self.lines) -1
			self.cursor_column = len(self.lines[self.cursor_line])
			self.change_column(0)
		# else the cursor is in the lines of text
		else:
			previousLine = self.cursor_line
			self.cursor_line += moveLine
			if len(self.lines) - 1 == self.cursor_line:
				lenLine = len(self.lines[self.cursor_line])
			else:
				lenLine = len(self.lines[self.cursor_line])-1

			self.set_cursor_column()
			# If the new cursor position is outside the last line of text
			if self.cursor_column > lenLine:
				self.cursor_column = lenLine

		if self.selection_start is not None:
			self.selection_end = [self.cursor_column, self.cursor_line,self.get_tab_cursor(self.cursor_line)]
		self.view.move()

	def change_column(self, move_column):
		""" Move the cursor on another column """
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
				self.cursor_column = len(self.lines[self.cursor_line])-1
		# If the cursor is at the end of line
		elif move_column + self.cursor_column > len(self.lines[self.cursor_line])-1:
			# If the cursor is on the last line of file
			if abs(move_column) > 1 or self.cursor_line+1 == len(self.lines):
				# If the file is empty
				if self.lines[self.cursor_line] == "":
					self.cursor_column = 0
					self.tab_cursor_column = 0
				# If the last line of contains return char
				elif self.lines[self.cursor_line][-1] == "\n":
					# Move cursor before return
					self.cursor_column = len(self.lines[self.cursor_line])-1
				else:
					# Move cursor after the last char
					self.cursor_column = len(self.lines[self.cursor_line])

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
		self.close_selection()
		self.view.move()
		if self.cursor_column == cursor_column and self.cursor_line == cursor_line:
			return False
		else:
			return True

	def backspace(self):
		""" Manage the backspace key """
		self.modified = True
		if self.remove_selection() is False:
			# The cursor not in the begining of line
			if self.cursor_column >= 1:
				line = self.lines[self.cursor_line]
				line = line[0:self.cursor_column-1:]+ line[self.cursor_column  : :]
				self.lines[self.cursor_line] = line
				self.change_column(-1)
				self.view.set_refresh_line()
			# The cursor is on the begining of line
			else:
				# If the cursor not on the first line
				if self.cursor_line >= 1:
					# Copy the current line to the end of previous line
					self.cursor_column = len(self.lines[self.cursor_line-1])
					self.lines[self.cursor_line-1] = self.lines[self.cursor_line-1][:-1] + self.lines[self.cursor_line]
					del self.lines[self.cursor_line]
					self.view.scroll_part_up()
					self.cursor_line -= 1
					self.view.set_refresh_after()
					self.change_column(-1)

	def delete(self):
		""" Manage the delete key """
		self.modified = True
		if self.remove_selection() is False:
			line = self.lines[self.cursor_line]
			if self.cursor_column < len(line):
				# If the line is empty
				if line[self.cursor_column] == "\n":
					# If the cursor not at end of files
					if self.cursor_line < len(self.lines)-1:
						# Copy the next line to the current line
						self.lines[self.cursor_line] = line[:self.cursor_column] + self.lines[self.cursor_line+1]
						del self.lines[self.cursor_line+1]
						self.view.scroll_part_up()
						self.view.set_refresh_after()
				# Else the char is deleted in the middle of line
				else:
					line = line[0:self.cursor_column:]+ line[self.cursor_column+1  : :]
					self.lines[self.cursor_line] = line
					self.change_column(0)
					self.view.is_refresh_line = True

	def delete_line(self):
		""" Manage the delete of line key """
		self.hide_selection()
		self.modified = True
		# If file contains one or none line
		if len(self.lines) <= 1:
			# Clean the content of file
			self.lines = [""]
			self.cursor_column = 0
			self.cursor_line = 0
			self.change_column(0)
		# If the current line is not the last of file
		elif self.cursor_line < len(self.lines):
			# Delete the line
			self.cursor_column = 0
			del self.lines[self.cursor_line]
			self.view.scroll_part_up()
			if self.cursor_line >= len(self.lines):
				self.cursor_line = len(self.lines)-1
			self.change_column(0)
		self.view.set_refresh_after()

	def new_line(self):
		""" Manage the newline key """
		self.modified = True
		if self.remove_selection() is False:
			line1 = self.lines[self.cursor_line][:self.cursor_column]+"\n"
			line2 = self.lines[self.cursor_line][self.cursor_column:]
			self.lines[self.cursor_line]=line1
			self.lines.insert(self.cursor_line+1, line2)
			self.view.scroll_part_down()
			self.change_column(1)
			self.view.set_refresh_before()

	def insert_char(self, char):
		""" Insert character """
		self.modified = True
		self.lines[self.cursor_line] = self.lines[self.cursor_line][:self.cursor_column] + char + self.lines[self.cursor_line][self.cursor_column:]
		self.change_column(1)
		self.view.set_refresh_line()

	def replace_char(self, char):
		""" Replace character """
		self.modified = True
		if self.cursor_line == len(self.lines)-1 and self.cursor_column >= len(self.lines[self.cursor_line])-1:
			self.lines[self.cursor_line] = self.lines[self.cursor_line][:self.cursor_column] + char
			self.change_column(1)
			self.view.set_refresh_line()
		# If it is the last char in the line
		elif self.lines[self.cursor_line][self.cursor_column] == "\n":
			# Append char to the line
			self.insert_char(char)
		# Else the char must be replaced in the line
		else:
			self.lines[self.cursor_line] = self.lines[self.cursor_line][:self.cursor_column] + char + self.lines[self.cursor_line][self.cursor_column+1:]
			self.change_column(1)
			self.view.set_refresh_line()

	def open_selection(self):
		""" Start a selection """
		if self.selection_start is None:
			self.selection_start = [self.cursor_column, self.cursor_line, self.get_tab_cursor(self.cursor_line)]

	def close_selection(self):
		""" Terminate selection """
		if self.selection_start is not None:
			self.selection_end = [self.cursor_column, self.cursor_line,self.get_tab_cursor(self.cursor_line)]

	def select_all(self):
		""" Do a select all """
		self.selection_start = [0,0,0]
		lastLine = len(self.lines)-1
		lastColumn = len(self.lines[lastLine])-1
		self.move_cursor(lastLine, lastColumn)
		self.selection_end  = [lastColumn, lastLine, self.get_tab_cursor(lastLine, lastColumn)]
		self.view.set_refresh_all()

	def get_selection(self):
		""" Get information about selection """
		if self.selection_start:
			if self.selection_start[1] > self.selection_end[1]:
				return self.selection_end, self.selection_start
			elif self.selection_start[1] < self.selection_end[1]:
				return self.selection_start, self.selection_end
			elif self.selection_start[0] < self.selection_end[0]:
				return self.selection_start, self.selection_end
			else:
				return self.selection_end, self.selection_start
		else:
			return None, None

	def arrow_up(self, keys):
		""" Manage arrow up key """
		self.hide_selection()
		self.change_line(-1)

	def arrow_down(self, keys):
		""" Manage arrow down key """
		self.hide_selection()
		self.change_line(1)

	def arrow_left(self, keys):
		""" Manage arrow left key """
		self.hide_selection()
		self.change_column(-len(keys))

	def arrow_right(self, keys):
		""" Manage arrow right key """
		self.hide_selection()
		self.change_column(len(keys))

	def select_up(self, keys):
		""" Manage select up key """
		self.open_selection()
		self.change_line(-1)

	def select_down(self, keys):
		""" Manage select down key """
		self.open_selection()
		self.change_line(1)

	def select_left(self, keys):
		""" Manage select left key """
		self.open_selection()
		self.change_column(-len(keys))

	def select_right(self, keys):
		""" Manage select right key """
		self.open_selection()
		self.change_column(len(keys))

	def select_home(self):
		""" Manage home key """
		self.open_selection()
		self.change_column(-100000000000)

	def select_end(self):
		""" Manage end key """
		self.open_selection()
		self.change_column(100000000000)

	def select_page_up(self, keys):
		""" Manage select page up key """
		self.open_selection()
		self.change_line((-self.view.height-1) * len(keys))
		self.change_column(-100000000000)

	def select_page_down(self, keys):
		""" Manage select page down key """
		self.open_selection()
		self.change_line((self.view.height+1) * len(keys))
		self.change_column(100000000000)

	def select_next_word(self):
		""" Manage select next word key """
		self.open_selection()
		self.move_word(1)

	def select_previous_word(self):
		""" Manage select previous word key """
		self.open_selection()
		self.move_word(-1)

	def select_top(self):
		""" Manage select to the first line of text """
		self.open_selection()
		self.change_line(-100000000000)

	def select_bottom(self):
		""" Manage select to the last line of text """
		self.open_selection()
		self.change_line(100000000000)

	def page_up(self, keys):
		""" Manage page up key """
		self.hide_selection()
		self.change_line((-self.view.height-1) * len(keys))

	def page_down(self, keys):
		""" Manage page down key """
		self.hide_selection()
		self.change_line((self.view.height+1) * len(keys))

	def home(self):
		""" Manage home key """
		self.hide_selection()
		self.change_column(-100000000000)

	def end(self):
		""" Manage end key """
		self.hide_selection()
		self.change_column(100000000000)

	def add_char(self, keys):
		""" Manage other key, add character """
		result = False

		if useful.isascii(keys[0]):
			self.remove_selection()
			for char in keys:
				if useful.isascii(char):
					if self.replace_mode:
						self.replace_char(char)
					else:
						self.insert_char(char)
					result = True
		# if result is False:
			# print(useful.dump(keys[0]))
		return result

	def find_next(self, text):
		""" Find next researched text """
		# Get the selection
		selection_start, selection_end = self.get_selection()

		# Hide the selection
		self.hide_selection()

		# Set the start of search at the cursor position
		current_line   = self.cursor_line
		current_column = self.cursor_column

		# If selection activated
		if selection_start is not None and selection_end is not None:
			# If selection is on one line
			if selection_start[1] == selection_end[1] and current_line == selection_start[1]:
				# If selection is exactly the size of text
				if selection_start[0] == current_column:
					# Move the start of search after the text selected
					current_column = selection_end[0]

		# Find the text in next lines
		while current_line < len(self.lines):
			# Search text
			pos = self.lines[current_line].find(text, current_column)

			# If text found
			if pos >= 0:
				# Move the cursor to the text found
				self.cursor_line = current_line
				self.cursor_column = pos + len(text)
				self.change_column(0)
				self.selection_start = [pos, current_line,self.get_tab_cursor(current_line,pos)]
				self.selection_end   = [pos + len(text), current_line, self.get_tab_cursor(current_line, pos + len(text))]
				break
			else:
				# Set the search position at the begin of next line
				current_column = 0
				current_line += 1
		self.view.move()

	def find_previous(self, text):
		""" Find previous researched text """
		# Get the selection
		selection_start, selection_end = self.get_selection()

		# Hide the selection
		self.hide_selection()

		# Set the start of search at the cursor position
		current_line   = self.cursor_line
		current_column = self.cursor_column

		# If selection activated
		if selection_start is not None and selection_end is not None:
			# If selection is on one line
			if selection_start[1] == selection_end[1] and current_line == selection_start[1]:
				# If selection is exactly the size of text
				if selection_end[0] - selection_start[0] == len(text):
					# Move the start of search before the text selected
					current_column = selection_start[0]

		# While the line before the first line not reached
		while current_line >= 0:
			# Get the current line
			line = self.lines[current_line]

			# If the current column is negative
			if current_column < 0:
				# Set the end of line
				current_column = len(line)

			# Search the text in reverse
			pos = line.rfind(text, 0, current_column)

			# If text found
			if pos >= 0:
				self.cursor_line = current_line
				self.cursor_column = pos
				self.change_column(0)
				self.selection_start = [pos, current_line,self.get_tab_cursor(current_line,pos)]
				self.selection_end   = [pos + len(text), current_line, self.get_tab_cursor(current_line, pos + len(text))]
				break
			else:
				# Set the search position at the end of line
				current_column = -1
				current_line -= 1
		self.view.move()

	def hide_selection(self):
		""" Hide selection """
		self.view.hide_selection()
		self.selection_start = self.selection_end = None

	def goto(self, lineNumber):
		""" Goto specified line """
		self.hide_selection()
		if lineNumber < 0:
			self.cursor_line = len(self.lines)-1
		elif lineNumber < 1:
			self.cursor_line = 1
		elif lineNumber < len(self.lines):
			self.cursor_line = lineNumber - 1
		else:
			self.cursor_line = len(self.lines)-1
		self.cursor_column = 0
		self.change_column(0)
		self.view.move()

	def copy_clipboard(self):
		""" Copy selection to clipboard """
		result = []
		if self.selection_start is not None:
			selection_start, selection_end = self.get_selection()
			sel_column_start, sel_line_start, dummy = selection_start
			sel_column_end,   sel_line_end,   dummy = selection_end
			result = []
			if sel_line_start == sel_line_end:
				result.append(self.lines[sel_line_start][sel_column_start:sel_column_end])
			else:
				for line in range(sel_line_start, sel_line_end+1):
					if line == sel_line_start:
						part = self.lines[line][sel_column_start:]
						if part != "":
							result.append(self.lines[line][sel_column_start:])
					elif line == sel_line_end:
						part = self.lines[line][:sel_column_end]
						if part != "":
							result.append(self.lines[line][:sel_column_end])
					else:
						result.append(self.lines[line])
		return result

	def remove_selection(self):
		""" Remove selection """
		if self.selection_start is not None:
			self.modified = True
			selection_start, selection_end = self.get_selection()
			sel_column_start, sel_line_start, dummy = selection_start
			sel_column_end,   sel_line_end,   dummy = selection_end
			start = self.lines[sel_line_start][:sel_column_start]
			end   = self.lines[sel_line_end  ][sel_column_end:]
			self.lines[sel_line_start] = start + end
			if sel_line_start < sel_line_end:
				for line in range(sel_line_end, sel_line_start,-1):
					del self.lines[line]
			self.move_cursor(sel_line_start, sel_column_start)
			self.hide_selection()
			self.view.set_refresh_all()
			return True
		return False

	def paste_clipboard(self, selection):
		""" Paste clipboard at the cursor position """
		if selection != []:
			# Split the line with insertion
			start = self.lines[self.cursor_line][:self.cursor_column]
			end   = self.lines[self.cursor_line][self.cursor_column:]

			# Paste the first line
			self.lines[self.cursor_line] = start + selection[0]

			self.cursor_line += 1

			# Insert all lines from clipboard
			for line in selection[1:-1]:
				self.lines.insert(self.cursor_line, line)
				self.cursor_line += 1

			# If the last line of clipboard is not empty
			if len(selection[-1]) >= 1:
				# If the last line of clipboard contains new line
				if selection[-1][-1] == "\n":
					if len(selection) > 1:
						# Add the new line
						self.lines.insert(self.cursor_line, selection[-1])
						self.cursor_line += 1

					# Add the part after the insertion
					self.lines.insert(self.cursor_line, end)
					self.cursor_column = 0
				else:
					if len(selection) > 1:
						self.lines.insert(self.cursor_line, selection[-1] + end)
						self.cursor_column = len(selection[-1])
					else:
						self.cursor_line -= 1
						self.lines[self.cursor_line] += end
						self.cursor_column = len(start) + len(selection[-1])

			self.move_cursor(self.cursor_line, self.cursor_column)

	def move_cursor(self, line, column):
		""" Move the cursor """
		self.cursor_line   = line
		self.cursor_column = column
		self.change_column(0)
		self.get_tab_cursor_column()

	def copy(self):
		""" Manage copy key """
		self.selection = self.copy_clipboard()

	def cut(self):
		""" Manage cut key """
		self.modified = True
		self.selection = self.copy_clipboard()
		self.remove_selection()

	def paste(self):
		""" Manage paste key """
		self.modified = True
		self.remove_selection()
		self.paste_clipboard(self.selection)
		self.view.set_refresh_all()
		self.hide_selection()

	def change_case(self):
		""" Change the case of selection """
		selection = self.copy_clipboard()
		if selection != []:
			self.modified = True
			selection_start = self.selection_start
			selection_end   = self.selection_end

			self.remove_selection()
			isUpper = None
			for line in selection:
				for char in line:
					if useful.isupper(char):
						isUpper = True
						break
					elif useful.islower(char):
						isUpper = False
						break
				if isUpper is not None:
					break
			# pylint:disable=consider-using-enumerate
			for line in range(len(selection)):
				if isUpper:
					selection[line] = selection[line].lower()
				else:
					selection[line] = selection[line].upper()
			self.paste_clipboard(selection)
			self.view.set_refresh_selection()
			self.selection_start = selection_start
			self.selection_end   = selection_end

	def comment(self):
		""" Comment the selection """
		self.modified = True

		# If selection
		if self.selection_start is not None:
			selection_start, selection_end = self.get_selection()
			_, sel_line_start, _ = selection_start
			_, sel_line_end,   _ = selection_end

			# Add tabulation
			for line in range(sel_line_start, sel_line_end+1):
				if len(self.lines[line]) >= 1:
					if self.lines[line][0] != '#':
						self.lines[line] = "#" + self.lines[line]
					else:
						if len(self.lines[line]) >= 1:
							self.lines[line] = self.lines[line][1:]

			# Move the start selection to the start of first selected line
			self.selection_start = [0,sel_line_start, 0]

			# Get the length of last selected line
			len_line_end =  len(self.lines[sel_line_end])

			# Move the end of selection at the end of line selected
			self.selection_end   = [len_line_end-1, sel_line_end, self.get_tab_cursor(sel_line_end,len_line_end-1)]
			self.view.set_refresh_selection()
		else:
			if len(self.lines[self.cursor_line]) >= 1:
				# If nothing selected
				if self.lines[self.cursor_line][0] == "#":
					self.lines[self.cursor_line] = self.lines[self.cursor_line][1:]
					if self.cursor_column > 0:
						self.change_column(-1)
				else:
					self.lines[self.cursor_line] = "#" + self.lines[self.cursor_line]
					self.change_column(1)
			self.view.set_refresh_line()

	def indent(self, keys):
		""" Manage tabulation key """
		# If nothing selected
		if self.selection_start is None:
			self.add_char(keys)
		else:
			self.modified = True
			# Indent selection
			selection_start, selection_end = self.get_selection()
			sel_column_start, sel_line_start, dummy = selection_start
			sel_column_end,   sel_line_end,   dummy = selection_end

			# If a part of line selected
			if sel_line_start == sel_line_end and not (sel_column_start == 0 and sel_column_end == len(self.lines[sel_line_end])-1):
				self.add_char(INDENT)
			else:
				# If the last line selected is at beginning of line
				if sel_column_end == 0:
					# This line must not be indented
					sel_line_end -= 1

				# Add tabulation
				for line in range(sel_line_start, sel_line_end+1):
					self.lines[line] = "\t" + self.lines[line]

				# Move the start selection to the start of first selected line
				self.selection_start = [0,sel_line_start, 0]

				# If the last line selected is not at beginning of line
				if sel_column_end > 0:
					# Get the length of last selected line
					len_line_end =  len(self.lines[sel_line_end])

					# If the end of selection is not on the last line
					if sel_line_end < len(self.lines)-1:
						len_line_end -= 1

					# Move the end of selection at the end of line selected
					self.selection_end   = [len_line_end, sel_line_end, self.get_tab_cursor(sel_line_end,len_line_end)]
				else:
					# Move the end of selection at the start of the last line selected
					self.selection_end  = [0, sel_line_end+1, 0]
			self.view.set_refresh_selection()

	def unindent(self, keys):
		""" Manage the unindentation key """
		# If nothing selected
		if self.selection_start is None:
			self.backspace()
		else:
			self.modified = True

			# Unindent selection
			selection_start, selection_end = self.get_selection()
			sel_column_start, sel_line_start, dummy = selection_start
			sel_column_end,   sel_line_end,   dummy = selection_end

			# If the selection is only alone line
			if sel_line_start == sel_line_end:
				self.hide_selection()
			else:
				# If the last line selected is at beginning of line
				if sel_column_end == 0:
					# This line must not be indented
					sel_line_end -= 1

				# Remove indentation
				for line in range(sel_line_start, sel_line_end+1):
					if len(self.lines[line]) >= 1:
						if self.lines[line][0] == "\t" or self.lines[line][0] == " ":
							self.lines[line] = self.lines[line][1:]

				# Move the start selection to the start of first selected line
				self.selection_start = [0,sel_line_start, 0]

				# If the last line selected is not at beginning of line
				if sel_column_end > 0:
					# Get the length of last selected line
					len_line_end =  len(self.lines[sel_line_end])

					# If the end of selection is not on the last line
					if sel_line_end < len(self.lines)-1:
						len_line_end -= 1

					# Move the end of selection at the end of line selected
					self.selection_end   = [len_line_end, sel_line_end, self.get_tab_cursor(sel_line_end,len_line_end)]
				else:
					# Move the end of selection at the start of the last line selected
					self.selection_end  = [0, sel_line_end+1, 0]
			self.view.set_refresh_selection()

	def replace(self, old, new):
		""" Replace the selection """
		if self.read_only is False:
			selection = self.copy_clipboard()
			if len(selection) == 1:
				if selection[0] == old:
					self.delete()
					self.insert_char(new)
					return True
		return False

	def get_cursor_char(self):
		""" Get the char on the cursor """
		try:
			return self.lines[self.cursor_line][self.cursor_column]
		except:
			return None

	def move_word(self, direction):
		""" Move the cursor to the word """
		state = 0
		while self.change_column(direction):
			current_char = self.get_cursor_char()
			if current_char is None:
				break
			elif useful.ispunctuation(current_char):
				if state == 0:
					state = 2
				elif state == 1:
					break
			elif useful.isalpha(current_char):
				if state == 0:
					state = 1
				elif state == 2:
					break
			elif useful.isspace(current_char):
				if state == 1:
					break
				if state == 2:
					break

	def next_word(self):
		""" Move the cursor to the next word """
		self.hide_selection()
		self.move_word(1)
		self.view.move()

	def previous_word(self):
		""" Move the cursor to the previous word """
		self.hide_selection()
		self.move_word(-1)
		self.view.move()

	def top(self):
		""" Move the cursor to the first line of text """
		self.goto(1)

	def bottom(self):
		""" Move the cursor to the last line of text """
		self.goto(100000000000)

	def treat_char(self, keys):
		""" Treat character entered """
		char = ord(keys[0][0])
		if self.read_only is False:
			if char >= 0x20 and char != 0x7F:
				self.add_char(keys)
				return True
		return False

	def treat_key(self, keys):
		""" Treat keys """
		if self.treat_char(keys) is False:
			# Move in the edit field
			if   keys[0] in UP  :            self.arrow_up(keys)
			elif keys[0] in DOWN:            self.arrow_down(keys)
			elif keys[0] in LEFT:            self.arrow_left(keys)
			elif keys[0] in RIGHT:           self.arrow_right(keys)
			elif keys[0] in HOME:            self.home()
			elif keys[0] in END:             self.end()
			elif keys[0] in PAGE_UP:         self.page_up(keys)
			elif keys[0] in PAGE_DOWN:       self.page_down(keys)
			elif keys[0] in TOP:             self.top()
			elif keys[0] in BOTTOM:          self.bottom()
			elif keys[0] in NEXT_WORD:       self.next_word()
			elif keys[0] in PREVIOUS_WORD:   self.previous_word()
			# Selection the edit field
			elif keys[0] in SELECT_UP:       self.select_up(keys)
			elif keys[0] in SELECT_DOWN:     self.select_down(keys)
			elif keys[0] in SELECT_RIGHT:    self.select_right(keys)
			elif keys[0] in SELECT_LEFT:     self.select_left(keys)
			elif keys[0] in SELECT_HOME:     self.select_home()
			elif keys[0] in SELECT_END:      self.select_end()
			elif keys[0] in SELECT_TOP:      self.select_top()
			elif keys[0] in SELECT_BOTTOM:   self.select_bottom()
			elif keys[0] in SELECT_PAGE_UP:  self.select_page_up(keys)
			elif keys[0] in SELECT_PAGE_DOWN:self.select_page_down(keys)
			elif keys[0] in SELECT_ALL:      self.select_all()
			elif keys[0] in SELECT_NEXT_WORD:self.select_next_word()
			elif keys[0] in SELECT_PREV_WORD:self.select_previous_word()

			# If the edit is not in read only
			elif self.read_only is False:
				# Modification in the edit field
				if   keys[0] in COPY:            self.copy()
				elif keys[0] in CUT:             self.cut()
				elif keys[0] in PASTE:           self.paste()

				elif keys[0] in INDENT:          self.indent(keys)
				elif keys[0] in UNINDENT:        self.unindent(keys)
				elif keys[0] in CHANGE_CASE:     self.change_case()
				elif keys[0] in COMMENT:         self.comment()

				elif keys[0] in BACKSPACE:       self.backspace()
				elif keys[0] in DELETE:          self.delete()
				elif keys[0] in NEW_LINE:        self.new_line()
				elif keys[0] in DELETE_LINE:     self.delete_line()
			# else: self.add_char(keys)

class Edit:
	""" Class which aggregate the View and Text """
	def __init__(self, view_top=1, view_height=None, read_only=False):
		""" Constructor """
		self.view = View(view_height, view_top)
		self.text = Text(read_only)
		self.text.set_view(self.view)
		self.view.set_text(self.text)

class Editor:
	""" Class which manage a complete editor """
	def __init__(self, filename_, read_only=False):
		""" Constructor """
		self.file = filename_
		self.filename = useful.split(filename_)[1]
		self.edit = Edit(read_only=read_only)
		self.edit.text.load(filename_)
		self.is_refresh_header = True
		self.find_text = None
		self.replace_text = None
		self.keys= []
		self.loop = None

		if (not useful.exists(filename_) and read_only is True) or useful.isdir(filename_):
			print("Cannot open '%s'"%self.filename)
		else:
			self.run()

	def refresh_header(self):
		""" Refresh the header of editor """
		if self.is_refresh_header:
			self.edit.view.move_cursor(0, 0)
			filename_ = "File: %s"%(self.filename)
			if self.edit.text.read_only is False:
				filename_ += " (*)" if self.edit.text.modified else ""
				end = "Mode: %s"%("Replace" if self.edit.text.replace_mode else "Insert")
			else:
				end = "Read only" if self.edit.text.read_only else ""

			header = "\x1B[7m %s%s%s \x1B[m"%(filename_, " "*(self.edit.view.width - len(filename_) - len(end)-2), end)
			self.edit.view.write(header)
			self.edit.view.move_cursor()
			self.is_refresh_header = False

	def refresh(self):
		""" Refresh the editor """
		self.refresh_header()
		self.edit.view.refresh()

	def toggle_mode(self):
		""" Change the replace mode """
		if self.edit.text.replace_mode:
			self.edit.text.replace_mode = False
		else:
			self.edit.text.replace_mode = True
		self.is_refresh_header = True

	def save(self):
		""" Save the file edited """
		self.edit.text.save()
		self.is_refresh_header = True

	def exit(self):
		""" Exit from editor """
		self.edit.view.cls()
		if self.edit.text.modified:
			self.edit.view.write("\nSave file '%s' (\x1b[7mY\x1b[m:Yes, \x1b[7mN\x1b[m:No, \x1b[7mEsc\x1b[m:Cancel) : "%self.filename)
			self.edit.view.flush()
			while 1:
				key = useful.getch()
				if key == "Y" or key == "y":
					if self.edit.text.save():
						self.edit.view.write("Saved\n")
						self.edit.view.flush()
					else:
						self.edit.view.write("Failed to save\n")
						self.edit.view.flush()
					self.loop = False
					break
				elif key == "N" or key == "n":
					self.edit.view.write("Not saved\n")
					self.edit.view.flush()
					self.loop = False
					break
				elif key == ESCAPE:
					self.edit.view.set_refresh_all()
					self.is_refresh_header = True
					break
		else:
			self.loop = False

	def input(self, text, help_=""):
		""" Input value, used to get a line number, or text searched """
		edit_ = Edit(view_top=2, view_height=1, read_only=False)
		edit_.view.cls()
		edit_.view.move_cursor(1,0)
		edit_.view.write(text)
		edit_.view.move_cursor(4,0)
		edit_.view.write(help_)
		result = None
		while 1:
			edit_.view.refresh()
			key = self.get_key()
			if key[0] in NEW_LINE:
				result = edit_.text.lines[0]
				break
			elif key[0] in ESCAPE:
				break
			else:
				edit_.text.treat_key(key)
		return result

	def find(self):
		""" Find a text """
		self.find_text = self.input("Find :","\x1B[7mEsc\x1B[m:Abort  \x1B[7m^Left\x1B[m,\x1B[7m^Up\x1B[m:Previous  \x1B[7m^Down\x1B[m,\x1B[7m^Right\x1B[m:Next")
		self.find_next()
		self.edit.view.set_refresh_all()
		self.is_refresh_header = True

	def replace(self):
		""" Replace a text """
		self.find_text    = self.input("Find to replace :","\x1B[7mEsc\x1B[m:Abort")
		if self.find_text:
			self.replace_text = self.input("Replace with :","\x1B[7mEsc\x1B[m:Abort  \x1B[7m^Left\x1B[m,\x1B[7m^Up\x1B[m:Previous  \x1B[7m^Down\x1B[m,\x1B[7m^Right\x1B[m:Next  \x1B[7m^R\x1B[m:Replace")
			self.find_next()

		self.edit.view.set_refresh_all()
		self.is_refresh_header = True

	def replace_current(self):
		""" Replace current """
		if self.find_text and self.replace_text:
			if self.edit.text.replace(self.find_text, self.replace_text):
				self.find_next()

	def find_next(self):
		""" Find next text """
		if self.find_text:
			self.edit.text.find_next(self.find_text)

	def find_previous(self):
		""" Find previous text """
		if self.find_text:
			self.edit.text.find_previous(self.find_text)

	def goto(self):
		""" Goto line """
		lineNumber = self.input("Goto line :","\x1B[7mEsc\x1B[m:Abort")
		try:
			lineNumber = int(lineNumber)
			self.edit.text.goto(int(lineNumber))
		except:
			pass
		self.edit.view.set_refresh_all()
		self.is_refresh_header = True

	def group_key(self):
		""" Group similar key to optimize move of cursor and edition """
		result = [self.keys.pop(0)]
		while len(self.keys) > 0 and len(result) <= 10:
			if self.keys[0] == result[0]:
				result.append(self.keys.pop(0))
			else:
				if useful.isascii(result[0]) and useful.isascii(self.keys[0]):
					result.append(self.keys.pop(0))
				else:
					break
		return result

	def get_key(self):
		""" Get a key pressed """
		if len(self.keys) == 0:
			while True:
				try:
					key = useful.getch()
				except KeyboardInterrupt:
					key = "\x03"
				self.keys.append(key)
				if useful.kbhit() is False or len(self.keys) > 5:
					break
		return self.group_key()

	def execute(self):
		""" Execute the python script edited """
		self.save()
		loop = True
		while loop:
			self.edit.view.reset_scroll_region()
			self.edit.view.cls()
			self.edit.view.flush()
			startTime = useful.ticks()
			try:
				useful.log(None)
				useful.import_(self.filename)
			except KeyboardInterrupt:
				pass
			endTime = useful.ticks()
			print( "\x1B[7mTime: %d.%03d s Press enter to stop\x1B[m"%((endTime-startTime)/1000, (endTime-startTime)%1000))
			while 1:
				keys = self.get_key()
				if keys[0] in NEW_LINE:
					loop = False
					break
				elif keys[0] in EXECUTE:
					break
				# else:
					# print(useful.dump(keys[0]))
		self.edit.view.cls()
		self.edit.view.set_refresh_all()
		self.is_refresh_header = True

	def run(self):
		""" Core of the editor """
		self.edit.view.cls()
		self.edit.view.get_screen_size()
		self.loop = True
		while(self.loop):
			try:
				self.refresh()
				keys = self.get_key()
				modified = self.edit.text.modified
				if ord(keys[0][0]) < 0x20:
					if   keys[0] in TOGGLE_MODE:    self.toggle_mode()
					elif keys[0] in FIND:           self.find()
					elif keys[0] in REPLACE:        self.replace()
					elif keys[0] in FIND_PREVIOUS:  self.find_previous()
					elif keys[0] in FIND_NEXT:      self.find_next()
					elif keys[0] in REPLACE_CURRENT:self.replace_current()
					elif keys[0] in EXIT:           self.exit()
					elif keys[0] in GOTO:           self.goto()
					elif keys[0] in SAVE:           self.save()
					elif keys[0] in EXECUTE:        self.execute()
				self.edit.text.treat_key(keys)
				if modified != self.edit.text.modified:
					self.is_refresh_header = True
			except KeyboardInterrupt:
				pass
		self.edit.view.reset_scroll_region()
		self.edit.view.reset()

if __name__ == "__main__":
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	else:
		filename = "editor.txt"
	edit = Editor(filename, read_only=False)
