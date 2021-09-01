#!/usr/bin/python3
# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
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

ESCAPE           = "\x1B"

# Move shortcuts
UP               = ["\x1B[A"]
DOWN             = ["\x1B[B"]
RIGHT            = ["\x1B[C"]
LEFT             = ["\x1B[D"]
HOME             = ["\x1B[1;3D", "\x1B[H", "\x1B\x1B[D", "\x1B[1~", "\x1Bb"]
END              = ["\x1B[1;3C", "\x1B[F", "\x1B\x1B[C", "\x1B[4~", "\x1Bf"]
PAGE_UP          = ["\x1B[1;3A", "\x1B[A", "\x1B\x1B[A", "\x1B[5~"]
PAGE_DOWN        = ["\x1B[1;3B", "\x1B[B", "\x1B\x1B[B", "\x1B[6~"]
TOP              = ["\x1B[1;5H"]
BOTTOM           = ["\x1B[1;5F"]
NEXT_WORD        = ["\x1B[1;5C"]
PREVIOUS_WORD    = ["\x1B[1;5D"]

# Selection shortcuts
SELECT_UP        = ["\x1B[1;2A"]
SELECT_DOWN      = ["\x1B[1;2B"]
SELECT_RIGHT     = ["\x1B[1;2C"]
SELECT_LEFT      = ["\x1B[1;2D"]
SELECT_PAGE_UP   = ["\x1B[1;10A","\x1B[1;4A","\x1B[5;2~"]
SELECT_PAGE_DOWN = ["\x1B[1;10B","\x1B[1;4B","\x1B[6;2~"]
SELECT_HOME      = ["\x1B[1;2H","\x1B[1;10D"]
SELECT_END       = ["\x1B[1;2F","\x1B[1;10C"]
SELECT_ALL       = ["\x01"]
SELECT_NEXT_WORD = ["\x1B[1;6C","\x1B[1;4C"]
SELECT_PREV_WORD = ["\x1B[1;6D","\x1B[1;4D"]

# Clipboard shortcuts
CUT              = ["\x18","\x1Bx"]                      # Cut
COPY             = ["\x03","\x1Bc"]                      # Copy
PASTE            = ["\x16","\x1Bv"]                      # Paste

# Selection modification shortcut
INDENT           = ["\t"]                                # Indent
UNINDENT         = ["\x1B[Z"]                            # Unindent
CHANGE_CASE      = ["\x15"]                              # Change case
COMMENT          = ["\x11"]                              # Comment block

DELETE           = ["\x1B[3~"]                           # Delete pressed
BACKSPACE        = ["\x7F"]                              # Backspace pressed
NEW_LINE         = ["\n", "\r"]                          # New line pressed

TOGGLE_MODE      = ["\x14"]                              # Toggle replace/insert mode
EXIT             = [ESCAPE]                              # Exit
FIND             = ["\x06"]                              # Find
FIND_NEXT        = ["\x1bOR"]                            # Find next
FIND_PREVIOUS    = ["\x1b[1;2R"]                         # Find previous
GOTO             = ["\x07"]                              # Goto line
SAVE             = ["\x13","\x1Bs"]                      # Save
DELETE_LINE      = ["\x0C"]                              # Delete line
REPLACE          = ["\x08"]                              # Replace
REPLACE_CURRENT  = ["\x12"]                              # Replace the selection
EXECUTE          = ["\x1B[15~"]                          # Execute script

class View:
	""" Class which manage the view of the edit field """
	def __init__(self, viewHeight, viewTop):
		""" Constructor """
		self.line     = 0
		self.column   = 0
		if viewHeight is None:
			self.height   = 20
		else:
			self.height          = viewHeight
		self.width               = 80
		self.top                 = viewTop
		self.isRefreshAll        = True
		self.isRefreshLine       = False
		self.isRefreshLineBefore = False
		self.isRefreshLineAfter  = False
		self.refreshPart         = None
		self.text                = None
		self.tabCursorColumn     = 0
		self.selLineStart        = None
		self.selLineEnd          = None
		self.screenHeight = 1
		self.screenWidth = 1

	def write(self, data):
		""" Write data to stdout """
		sys.stdout.write(data)

	def flush(self):
		""" Flush text to stdout """
		try:
			sys.stdout.flush()
		except:
			pass

	def setText(self, text):
		""" Set the text object """
		self.text = text

	def getScreenPosition(self):
		""" Get the screen position of cursor """
		return (self.text.getCursorLine() - self.line + self.top, self.tabCursorColumn - self.column)

	def reset(self):
		""" Reset VT100 """
		self.write("\x1b""c")
		self.flush()

	def resetScrollRegion(self):
		""" Reset VT100 scroll region """
		if self.screenHeight > 0:
			self.setScrollingRegion(0, self.screenHeight-1)

	def setScrollingRegion(self, topLine, bottomLine):
		""" Define VT100 scroll region """
		if topLine < bottomLine:
			self.write("\x1B[%d;%dr"%(topLine+1,bottomLine+1))

	def scrollUp(self):
		""" Scroll to up """
		self.setScrollingRegion(self.top, self.height+1)
		self.write("\x1B[1S")

	def scrollDown(self):
		""" Scroll to down """
		self.setScrollingRegion(self.top, self.height+1)
		self.write("\x1B[1T")

	def scrollPartUp(self):
		""" Scroll the upper part """
		line, column = self.getScreenPosition()
		if line < self.height:
			self.setScrollingRegion(line, self.height+1)
			self.write("\x1B[1S")

	def scrollPartDown(self):
		""" Scroll the lower part """
		line, column = self.getScreenPosition()
		if line < self.height:
			self.setScrollingRegion(line+1, self.height+1)
			self.write("\x1B[1T")
		else:
			self.isRefreshLineAfter = True

	def move(self):
		""" Move the view """
		self.tabCursorColumn = self.text.getTabCursor(self.text.getCursorLine())
		# Move view port
		if self.tabCursorColumn < self.column:
			self.isRefreshAll = True
			if self.tabCursorColumn > HORIZONTAL_MOVE:
				self.column = self.tabCursorColumn-HORIZONTAL_MOVE
			else:
				self.column = 0
		elif self.tabCursorColumn >= self.column + self.width:
			self.column = self.tabCursorColumn-self.width+HORIZONTAL_MOVE
			self.isRefreshAll = True
		if self.text.getCursorLine() < self.line:
			delta = self.line - self.text.getCursorLine()
			self.line = self.text.getCursorLine()
			if self.line < 0:
				self.line = 0
			if delta <= 1:
				self.scrollDown()
				self.isRefreshLine = True
			else:
				self.isRefreshAll = True
		elif self.text.getCursorLine() > self.line + self.height:
			delta =  self.text.getCursorLine() - self.line - self.height
			self.line = self.text.getCursorLine()-self.height
			if delta <= 1:
				self.scrollUp()
				self.isRefreshLine = True
			else:
				self.isRefreshAll = True

	def setRefreshLine(self):
		""" Indicates that the line must be refreshed """
		self.isRefreshLine = True

	def setRefreshAfter(self):
		""" Indicates that all lines after the current line must be refreshed """
		self.isRefreshLine = True
		self.isRefreshLineAfter = True

	def setRefreshBefore(self):
		""" Indicates that all lines before the current line must be refreshed """
		self.isRefreshLine = True
		self.isRefreshLineBefore = True

	def setRefreshAll(self):
		""" Indicates that all lines must be refreshed """
		self.isRefreshAll = True

	def showLine(self, currentLine, screenLine, selectionStart, selectionEnd, quick=False):
		""" Show one line """
		if quick:
			lineToDisplay = ""
		else:
			lineToDisplay = "\x1B[%d;1f\x1B[K"%(screenLine+1)
		countLine = self.text.getCountLines()
		if currentLine < countLine and currentLine >= 0:
			line = self.text.getTabLine(currentLine)
			partLine = line[self.column:self.column+self.width]
			# If the line selected
			if selectionStart != None:
				# If the line not empty
				if len(partLine) >= 1:
					# If the line have carriage return at the end
					if partLine[-1] == "\n":
						# Remove the carriage return
						partLine = partLine[:-1]
				if len(partLine) > 0:
					dummy, selLineStart, selColumnStart = selectionStart
					dummy, selLineEnd,   selColumnEnd   = selectionEnd
					# If the current line is the end of selection
					if currentLine == selLineEnd:
						# If the end of selection is outside the visible part
						if selColumnEnd - self.column < 0:
							selColumnEnd = 0
						else:
							selColumnEnd -= self.column

						# If the start of selection is on the previous lines
						if selLineStart < selLineEnd:
							# Select the start of line
							partLine = "\x1B[7m" + partLine[:selColumnEnd] + "\x1B[m" + partLine[selColumnEnd:]
						else:
							# Unselect the end of line
							partLine = partLine[:selColumnEnd] + "\x1B[m" + partLine[selColumnEnd:]
					# If the current line is the start of selection
					if currentLine == selLineStart:
						# If the start of selection is outside the visible part
						if selColumnStart - self.column < 0:
							selColumnStart = 0
						else:
							selColumnStart -= self.column

						# If the end of selection is on the next lines
						if selLineStart < selLineEnd:
							# Select the end of line
							partLine = partLine[:selColumnStart] + "\x1B[7m" + partLine[selColumnStart:] + "\x1B[m"
						else:
							# Select the start of line
							partLine = partLine[:selColumnStart] + "\x1B[7m" + partLine[selColumnStart:] 
					# If the line is completly selected
					if currentLine > selLineStart and currentLine < selLineEnd:
						# Select all the line
						partLine = "\x1B[7m" + partLine + "\x1B[m"
				else:
					partLine = ""
				self.write(lineToDisplay + partLine)
			else:
				self.write(lineToDisplay + partLine.rstrip())

	def refreshLine(self, selectionStart, selectionEnd):
		""" Refresh line """
		screenLine,     screenColumn = self.getScreenPosition()
		refreshed = False

		# If the line must be refreshed before the cursor line
		if self.isRefreshLineBefore:
			self.isRefreshLineBefore = False
			self.showLine(self.text.getCursorLine()-1, screenLine-1, selectionStart, selectionEnd)
			refreshed = True
		# If the line must be refreshed after the cursor line
		if self.isRefreshLineAfter:
			self.isRefreshLineAfter = False
			self.showLine(self.text.getCursorLine()+1, screenLine+1, selectionStart, selectionEnd)
			offset = self.height - screenLine
			self.showLine(self.text.getCursorLine()+offset+1, screenLine+offset+1, selectionStart, selectionEnd)
			refreshed = True
		# If only the cursor line must be refresh
		if self.isRefreshLine:
			self.isRefreshLine = False
			self.showLine(self.text.getCursorLine(), screenLine, selectionStart, selectionEnd)
			refreshed = True

		# If no refresh detected and a selection started
		if selectionStart != None and refreshed == False:
			# Refresh the selection
			self.showLine(self.text.getCursorLine(), screenLine, selectionStart, selectionEnd)

	def refresh(self):
		""" Refresh view """
		selectionStart, selectionEnd = self.text.getSelection()
		if self.refreshPart != None:
			self.refreshContent(selectionStart, selectionEnd, self.refreshPart)
			self.refreshPart = None
		# Refresh all required
		if self.isRefreshAll:
			self.refreshContent(selectionStart, selectionEnd, True)
			self.isRefreshAll  = False
			self.isRefreshLine = False
		else:
			# If no selection activated
			if selectionStart == None:
				# Refresh the current line
				self.refreshLine(selectionStart, selectionEnd)
			else:
				# Refresh the selection
				self.refreshContent(selectionStart, selectionEnd, False)
		self.moveCursor()
		self.flush()

	def refreshContent(self, selectionStart, selectionEnd, all_):
		""" Refresh content """
		# If selection present
		if selectionStart != None:
			# Get the selection
			dummy, selLineStart, selColumnStart = selectionStart
			dummy, selLineEnd,   selColumnEnd   = selectionEnd
			lineStart = selLineStart
			lineEnd   = selLineEnd
			# The aim of this part is to limit the refresh area
			# If the precedent display show a selection
			if self.selLineEnd != None and self.selLineStart != None:
				# If the start and end of selection is on the sames lines
				if self.selLineEnd == selLineEnd and self.selLineStart == selLineStart:
					lineStart = lineEnd = self.text.getCursorLine()
				else:
					# If the end of selection is after the precedent display
					if self.selLineEnd > selLineEnd:
						lineEnd = self.selLineEnd
					# If the end of selection is on the same line than the precedent display
					elif self.selLineEnd == selLineEnd:
						# If the start of selection is before the precedent display
						if self.selLineStart < selLineStart:
							lineEnd = selLineStart
						else:
							lineEnd = self.selLineStart
					# If the start of selection is before the precedent display
					if self.selLineStart < selLineStart:
						lineStart = self.selLineStart
					# If the start of selection is on the same line than the precedent display
					elif self.selLineStart == selLineStart:
						# If the end of selection is after the precedent display
						if self.selLineEnd > selLineEnd:
							lineStart = selLineEnd
						else:
							lineStart = self.selLineEnd
		else:
			lineStart = 0
			lineEnd = self.line + self.height
		currentLine = self.line
		screenLine = self.top
		if type(all_) == type([]):
			lineStart, lineEnd = all_
			all_ = False
		countLine = self.text.getCountLines()
		maxLine = self.line + self.height
		if all_:
			# Erase the rest of the screen with empty line (used when the text is shorter than the screen)
			self.moveCursor(screenLine, 0)
			self.write("\x1B[J")
			# Refresh all lines visible
			while currentLine < countLine and currentLine <= maxLine:
				self.showLine(currentLine, screenLine, selectionStart, selectionEnd, True)
				screenLine  += 1
				currentLine += 1
				if (currentLine < countLine and currentLine <= maxLine):
					self.write("\n\r")
		else:
			# Refresh all lines visible
			while currentLine < countLine and currentLine <= maxLine:
				# If the line is in selection or all must be refreshed
				if lineStart <= currentLine <= lineEnd or all_:
					self.showLine(currentLine, screenLine, selectionStart, selectionEnd)
				screenLine  += 1
				currentLine += 1

		# If selection present
		if selectionStart != None:
			# Save current selection
			dummy, self.selLineStart, dummy = selectionStart
			dummy, self.selLineEnd,   dummy   = selectionEnd

	def hideSelection(self):
		""" Hide the selection """
		selectionStart, selectionEnd = self.text.getSelection()
		if selectionStart != None:
			self.setRefreshSelection()
			self.selLineStart = None
			self.selLineEnd   = None

	def setRefreshSelection(self):
		""" Indicates that the selection must be refreshed """
		selectionStart, selectionEnd = self.text.getSelection()
		if selectionStart != None:
			# self.isRefreshAll = True
			lineStart = selectionStart[1]
			if self.selLineStart < lineStart:
				lineStart = self.selLineStart
			lineEnd = selectionEnd[1]
			if self.selLineEnd > lineEnd:
				lineEnd = self.selLineEnd
			self.refreshPart = [lineStart, lineEnd]

	def moveCursor(self, screenLine=None, screenColumn=None):
		""" Move the cursor in the view """
		self.write(self.getMoveCursor(screenLine, screenColumn))

	def getMoveCursor(self, screenLine=None, screenColumn=None):
		""" Move the cursor in the view """
		if screenLine == None and screenColumn == None:
			screenLine, screenColumn = self.getScreenPosition()
		return "\x1B[%d;%df"%(screenLine+1,screenColumn+1)

	def getScreenSize(self):
		""" Get the screen size """
		height, width = useful.getScreenSize()
		self.screenHeight = height
		self.screenWidth = width
		self.height = height-self.top-1
		self.width  = width
		self.moveCursor()

	def cls(self):
		""" Clear the screen """
		self.write("\x1B[2J")
		self.moveCursor(0,0)

class Text:
	""" Class which manage the text edition """
	def __init__(self, readOnly=False):
		""" Constructor """
		self.lines = [""]
		self.cursorLine   = 0
		self.cursorColumn = 0
		self.tabCursorColumn   = 0
		self.modified     = False
		self.replaceMode  = False
		self.readOnly     = readOnly
		self.view         = None
		self.tabSize      = TABSIZE
		self.selectionStart = None
		self.selectionEnd   = None
		self.selection = []
		self.filename = None

	def setView(self, view):
		""" Define the view attached to the text """
		self.view = view

	def getCountLines(self):
		""" Get the total of lines """
		return len(self.lines)

	def getCursorLine(self):
		""" Get the current line of the cursor """
		return self.cursorLine

	def getTabCursor(self, currentLine, currentColumn=None):
		""" Get position of cursor with line with tabulation """
		if currentColumn == None:
			cursorColumn = self.cursorColumn
		else:
			cursorColumn = currentColumn
		line = self.lines[currentLine]
		if "\t" in line:
			tabCursorColumn   = 0
			column = 0
			lenLine = len(line)
			while column < cursorColumn: 
				if line[column] == "\t":
					pos = tabCursorColumn%self.tabSize
					tabCursorColumn += self.tabSize-pos
					column          += 1
				else:
					tab = line.find("\t",column)
					if tab > 0:
						partSize = tab - column
					else:
						partSize = lenLine - column
					if column + partSize > cursorColumn:
						partSize = cursorColumn - column
					tabCursorColumn += partSize
					column          += partSize
			return tabCursorColumn
		else:
			return cursorColumn

	def getTabLine(self, currentLine = None):
		""" Get the tabuled line """
		line = self.lines[currentLine]
		if "\t" in line:
			tabLine = ""
			tabCursorColumn   = 0
			lenLine = len(line)
			column = 0
			while column < lenLine: 
				char = line[column]
				if char == "\t":
					pos = tabCursorColumn%self.tabSize
					tabCursorColumn += self.tabSize-pos
					tabLine         += " "*(self.tabSize-pos)
					column          += 1
				else:
					tab = line.find("\t",column)
					if tab > 0:
						part = line[column:tab]
					else:
						part = line[column:]
					tabCursorColumn += len(part)
					tabLine         += part
					column          += len(part)
		else:
			tabLine = line
		return tabLine

	def getTabCursorColumn(self):
		""" Get the column of cursor in tabuled line """
		line = self.lines[self.cursorLine]
		column = 0
		self.tabCursorColumn = 0
		while column < self.cursorColumn:
			if line[column] == "\t":
				pos = self.tabCursorColumn%self.tabSize
				self.tabCursorColumn += self.tabSize-pos
				column += 1
			else:
				tab = line.find("\t",column)
				if tab > 0:
					delta = tab - column
					if column + delta > self.cursorColumn:
						delta = self.cursorColumn - column
						self.tabCursorColumn += delta
						column += delta
					else:
						self.tabCursorColumn += delta
						column += delta
				else:
					delta = self.cursorColumn - column
					self.tabCursorColumn += delta
					column += delta

	def setCursorColumn(self):
		""" When the line change compute the cursor position with tabulation in the line """
		line = self.lines[self.cursorLine]
		column = 0
		tabCursorColumn = 0
		lenLine = len(line)
		column = 0
		while column < lenLine: 
			char = line[column]
			# If the previous position found exactly in the current line
			if tabCursorColumn == self.tabCursorColumn:
				self.cursorColumn = column
				break
			# If the previous position not found in the current line
			if tabCursorColumn > self.tabCursorColumn:
				# Keep last existing position
				self.cursorColumn = column
				break
			# If tabulation found
			if char == "\t":
				tabCursorColumn += self.tabSize-(tabCursorColumn%self.tabSize)
				column += 1
			else:
				# Optimization to accelerate the cursor position
				tab = line.find("\t", column)

				# Tabulation found
				if tab > 0:
					delta = tab - column
					# If the tabulation position is after the previous tabulation cursor
					if delta + tabCursorColumn > self.tabCursorColumn:
						# Move the cursor to the left
						self.cursorColumn = column + (self.tabCursorColumn - tabCursorColumn)
						break
					else:
						# Another tabulation found, move it after
						tabCursorColumn += delta
						column += delta
				# Tabulation not found
				else:
					# Move the cursor to the end of line
					self.cursorColumn = column + (self.tabCursorColumn - tabCursorColumn)
					break
		else:
			if len(line) >= 1:
				self.cursorColumn = len(line)-1
			else:
				self.cursorColumn = 0

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
		if self.readOnly == False:
			if self.filename != None:
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

	def changeLine(self, moveLine):
		""" Move the cursor on another line """
		# If cursor is before the first line
		if moveLine + self.cursorLine < 0:
			# Set the cursor to the first line
			self.cursorLine = 0
			self.cursorColumn = 0
			self.changeColumn(0)
		# If the cursor is after the last line
		elif moveLine + self.cursorLine >= len(self.lines):
			self.cursorLine = len(self.lines) -1
			self.cursorColumn = len(self.lines[self.cursorLine])
			self.changeColumn(0)
		# else the cursor is in the lines of text
		else:
			previousLine = self.cursorLine
			self.cursorLine += moveLine
			if len(self.lines) - 1 == self.cursorLine:
				lenLine = len(self.lines[self.cursorLine])
			else:
				lenLine = len(self.lines[self.cursorLine])-1

			self.setCursorColumn()
			# If the new cursor position is outside the last line of text
			if self.cursorColumn > lenLine:
				self.cursorColumn = lenLine

		if self.selectionStart != None:
			self.selectionEnd = [self.cursorColumn, self.cursorLine,self.getTabCursor(self.cursorLine)]
		self.view.move()

	def changeColumn(self, moveColumn):
		""" Move the cursor on another column """
		cursorLine   = self.cursorLine
		cursorColumn = self.cursorColumn
		# If the cursor go to the previous line
		if moveColumn + self.cursorColumn < 0:
			# If start of line
			if abs(moveColumn) > 1:
				self.cursorColumn = 0
			# If move to the left and must go to previous line
			elif self.cursorLine > 0:
				self.cursorLine -= 1
				self.cursorColumn = len(self.lines[self.cursorLine])-1
		# If the cursor is at the end of line
		elif moveColumn + self.cursorColumn > len(self.lines[self.cursorLine])-1:
			# If the cursor is on the last line of file
			if abs(moveColumn) > 1 or self.cursorLine+1 == len(self.lines):
				# If the file is empty
				if self.lines[self.cursorLine] == "":
					self.cursorColumn = 0
					self.tabCursorColumn = 0
				# If the last line of contains return char
				elif self.lines[self.cursorLine][-1] == "\n":
					# Move cursor before return
					self.cursorColumn = len(self.lines[self.cursorLine])-1
				else:
					# Move cursor after the last char
					self.cursorColumn = len(self.lines[self.cursorLine])

			# If the cursor is on the end of line and must change of line
			elif self.cursorLine+1 < len(self.lines):
				self.cursorLine += 1
				self.cursorColumn = 0
				self.tabCursorColumn = 0
		# Normal move of cursor
		else:
			# Next or previous column
			self.cursorColumn += moveColumn
		if abs(moveColumn) > 0:
			self.getTabCursorColumn()
		self.closeSelection()
		self.view.move()
		if self.cursorColumn == cursorColumn and self.cursorLine == cursorLine:
			return False
		else:
			return True

	def backspace(self):
		""" Manage the backspace key """
		self.modified = True
		if self.removeSelection() == False:
			# The cursor not in the begining of line
			if self.cursorColumn >= 1:
				line = self.lines[self.cursorLine]
				line = line[0:self.cursorColumn-1:]+ line[self.cursorColumn  : :]
				self.lines[self.cursorLine] = line
				self.changeColumn(-1)
				self.view.setRefreshLine()
			# The cursor is on the begining of line
			else:
				# If the cursor not on the first line
				if self.cursorLine >= 1:
					# Copy the current line to the end of previous line
					self.cursorColumn = len(self.lines[self.cursorLine-1])
					self.lines[self.cursorLine-1] = self.lines[self.cursorLine-1][:-1] + self.lines[self.cursorLine]
					del self.lines[self.cursorLine]
					self.view.scrollPartUp()
					self.cursorLine -= 1
					self.view.setRefreshAfter()
					self.changeColumn(-1)

	def delete(self):
		""" Manage the delete key """
		self.modified = True
		if self.removeSelection() == False:
			line = self.lines[self.cursorLine]
			if self.cursorColumn < len(line):
				# If the line is empty
				if line[self.cursorColumn] == "\n":
					# If the cursor not at end of files
					if self.cursorLine < len(self.lines)-1:
						# Copy the next line to the current line
						self.lines[self.cursorLine] = line[:self.cursorColumn] + self.lines[self.cursorLine+1]
						del self.lines[self.cursorLine+1]
						self.view.scrollPartUp()
						self.view.setRefreshAfter()
				# Else the char is deleted in the middle of line
				else:
					line = line[0:self.cursorColumn:]+ line[self.cursorColumn+1  : :]
					self.lines[self.cursorLine] = line
					self.changeColumn(0)
					self.view.isRefreshLine = True

	def deleteLine(self):
		""" Manage the delete of line key """
		self.hideSelection()
		self.modified = True
		# If file contains one or none line
		if len(self.lines) <= 1:
			# Clean the content of file
			self.lines = [""]
			self.cursorColumn = 0
			self.cursorLine = 0
			self.changeColumn(0)
		# If the current line is not the last of file
		elif self.cursorLine < len(self.lines):
			# Delete the line
			self.cursorColumn = 0
			del self.lines[self.cursorLine]
			self.view.scrollPartUp()
			if self.cursorLine >= len(self.lines):
				self.cursorLine = len(self.lines)-1
			self.changeColumn(0)
		self.view.setRefreshAfter()

	def newLine(self):
		""" Manage the newline key """
		self.modified = True
		if self.removeSelection() == False:
			line1 = self.lines[self.cursorLine][:self.cursorColumn]+"\n"
			line2 = self.lines[self.cursorLine][self.cursorColumn:]
			self.lines[self.cursorLine]=line1
			self.lines.insert(self.cursorLine+1, line2)
			self.view.scrollPartDown()
			self.changeColumn(1)
			self.view.setRefreshBefore()

	def insertChar(self, char):
		""" Insert character """
		self.modified = True
		self.lines[self.cursorLine] = self.lines[self.cursorLine][:self.cursorColumn] + char + self.lines[self.cursorLine][self.cursorColumn:]
		self.changeColumn(1)
		self.view.setRefreshLine()

	def replaceChar(self, char):
		""" Replace character """
		self.modified = True
		if self.cursorLine == len(self.lines)-1 and self.cursorColumn >= len(self.lines[self.cursorLine])-1:
			self.lines[self.cursorLine] = self.lines[self.cursorLine][:self.cursorColumn] + char 
			self.changeColumn(1)
			self.view.setRefreshLine()
		# If it is the last char in the line
		elif self.lines[self.cursorLine][self.cursorColumn] == "\n":
			# Append char to the line
			self.insertChar(char)
		# Else the char must be replaced in the line
		else:
			self.lines[self.cursorLine] = self.lines[self.cursorLine][:self.cursorColumn] + char + self.lines[self.cursorLine][self.cursorColumn+1:]
			self.changeColumn(1)
			self.view.setRefreshLine()

	def openSelection(self):
		""" Start a selection """
		if self.selectionStart == None:
			self.selectionStart = [self.cursorColumn, self.cursorLine, self.getTabCursor(self.cursorLine)]

	def closeSelection(self):
		""" Terminate selection """
		if self.selectionStart != None:
			self.selectionEnd = [self.cursorColumn, self.cursorLine,self.getTabCursor(self.cursorLine)]

	def selectAll(self):
		""" Do a select all """
		self.selectionStart = [0,0,0]
		lastLine = len(self.lines)-1
		lastColumn = len(self.lines[lastLine])-1
		self.moveCursor(lastLine, lastColumn)
		self.selectionEnd  = [lastColumn, lastLine, self.getTabCursor(lastLine, lastColumn)]
		self.view.setRefreshAll()

	def getSelection(self):
		""" Get information about selection """
		if self.selectionStart:
			if self.selectionStart[1] > self.selectionEnd[1]:
				return self.selectionEnd, self.selectionStart
			elif self.selectionStart[1] < self.selectionEnd[1]:
				return self.selectionStart, self.selectionEnd
			elif self.selectionStart[0] < self.selectionEnd[0]:
				return self.selectionStart, self.selectionEnd
			else:
				return self.selectionEnd, self.selectionStart
		else:
			return None, None

	def arrowUp(self, keys):
		""" Manage arrow up key """
		self.hideSelection()
		self.changeLine(-1)
	
	def arrowDown(self, keys):
		""" Manage arrow down key """
		self.hideSelection()
		self.changeLine(1)

	def arrowLeft(self, keys):
		""" Manage arrow left key """
		self.hideSelection()
		self.changeColumn(-len(keys))

	def arrowRight(self, keys):
		""" Manage arrow right key """
		self.hideSelection()
		self.changeColumn(len(keys))

	def selectUp(self, keys):
		""" Manage select up key """
		self.openSelection()
		self.changeLine(-1)
	
	def selectDown(self, keys):
		""" Manage select down key """
		self.openSelection()
		self.changeLine(1)

	def selectLeft(self, keys):
		""" Manage select left key """
		self.openSelection()
		self.changeColumn(-len(keys))

	def selectRight(self, keys):
		""" Manage select right key """
		self.openSelection()
		self.changeColumn(len(keys))

	def selectHome(self):
		""" Manage home key """
		self.openSelection()
		self.changeColumn(-100000000000)

	def selectEnd(self):
		""" Manage end key """
		self.openSelection()
		self.changeColumn(100000000000)

	def selectPageUp(self, keys):
		""" Manage select page up key """
		self.openSelection()
		self.changeLine((-self.view.height-1) * len(keys))
		self.changeColumn(-100000000000)

	def selectPageDown(self, keys):
		""" Manage select page down key """
		self.openSelection()
		self.changeLine((self.view.height+1) * len(keys))
		self.changeColumn(100000000000)

	def selectNextWord(self):
		""" Manage select next word key """
		self.openSelection()
		self.moveWord(1)

	def selectPreviousWord(self):
		""" Manage select previous word key """
		self.openSelection()
		self.moveWord(-1)

	def pageUp(self, keys):
		""" Manage page up key """
		self.hideSelection()
		self.changeLine((-self.view.height-1) * len(keys))

	def pageDown(self, keys):
		""" Manage page down key """
		self.hideSelection()
		self.changeLine((self.view.height+1) * len(keys))

	def home(self):
		""" Manage home key """
		self.hideSelection()
		self.changeColumn(-100000000000)

	def end(self):
		""" Manage end key """
		self.hideSelection()
		self.changeColumn(100000000000)

	def addChar(self, keys):
		""" Manage other key, add character """
		result = False

		if useful.isascii(keys[0]):
			self.removeSelection()
			for char in keys:
				if useful.isascii(char):
					if self.replaceMode:
						self.replaceChar(char)
					else:
						self.insertChar(char)
					result = True
		# if result == False:
			# print(useful.dump(keys[0]))
		return result

	def findNext(self, text):
		""" Find next researched text """
		# Get the selection
		selectionStart, selectionEnd = self.getSelection()

		# Hide the selection
		self.hideSelection()

		# Set the start of search at the cursor position
		currentLine   = self.cursorLine
		currentColumn = self.cursorColumn

		# If selection activated
		if selectionStart != None and selectionEnd != None:
			# If selection is on one line
			if selectionStart[1] == selectionEnd[1] and currentLine == selectionStart[1]:
				# If selection is exactly the size of text
				if selectionStart[0] == currentColumn:
					# Move the start of search after the text selected
					currentColumn = selectionEnd[0]

		# Find the text in next lines
		while currentLine < len(self.lines):
			# Search text
			pos = self.lines[currentLine].find(text, currentColumn)

			# If text found
			if pos >= 0:
				# Move the cursor to the text found
				self.cursorLine = currentLine
				self.cursorColumn = pos + len(text)
				self.changeColumn(0)
				self.selectionStart = [pos, currentLine,self.getTabCursor(currentLine,pos)]
				self.selectionEnd   = [pos + len(text), currentLine, self.getTabCursor(currentLine, pos + len(text))]
				break
			else:
				# Set the search position at the begin of next line
				currentColumn = 0
				currentLine += 1
		self.view.move()

	def findPrevious(self, text):
		""" Find previous researched text """
		# Get the selection
		selectionStart, selectionEnd = self.getSelection()

		# Hide the selection
		self.hideSelection()

		# Set the start of search at the cursor position
		currentLine   = self.cursorLine
		currentColumn = self.cursorColumn

		# If selection activated
		if selectionStart != None and selectionEnd != None:
			# If selection is on one line
			if selectionStart[1] == selectionEnd[1] and currentLine == selectionStart[1]:
				# If selection is exactly the size of text
				if selectionEnd[0] - selectionStart[0] == len(text):
					# Move the start of search before the text selected
					currentColumn = selectionStart[0]

		# While the line before the first line not reached
		while currentLine >= 0:
			# Get the current line
			line = self.lines[currentLine]

			# If the current column is negative
			if currentColumn < 0:
				# Set the end of line
				currentColumn = len(line)

			# Search the text in reverse
			pos = line.rfind(text, 0, currentColumn)

			# If text found
			if pos >= 0:
				self.cursorLine = currentLine
				self.cursorColumn = pos
				self.changeColumn(0)
				self.selectionStart = [pos, currentLine,self.getTabCursor(currentLine,pos)]
				self.selectionEnd   = [pos + len(text), currentLine, self.getTabCursor(currentLine, pos + len(text))]
				break
			else:
				# Set the search position at the end of line
				currentColumn = -1
				currentLine -= 1
		self.view.move()

	def hideSelection(self):
		""" Hide selection """
		self.view.hideSelection()
		self.selectionStart = self.selectionEnd = None

	def goto(self, lineNumber):
		""" Goto specified line """
		self.hideSelection()
		if lineNumber < 0:
			self.cursorLine = len(self.lines)-1
		elif lineNumber < 1:
			self.cursorLine = 1
		elif lineNumber < len(self.lines):
			self.cursorLine = lineNumber - 1
		else:
			self.cursorLine = len(self.lines)-1
		self.cursorColumn = 0
		self.changeColumn(0)
		self.view.move()

	def copyClipboard(self):
		""" Copy selection to clipboard """
		result = []
		if self.selectionStart != None:
			selectionStart, selectionEnd = self.getSelection()
			selColumnStart, selLineStart, dummy = selectionStart
			selColumnEnd,   selLineEnd,   dummy = selectionEnd
			result = []
			if selLineStart == selLineEnd:
				result.append(self.lines[selLineStart][selColumnStart:selColumnEnd])
			else:
				for line in range(selLineStart, selLineEnd+1):
					if line == selLineStart:
						part = self.lines[line][selColumnStart:]
						if part != "":
							result.append(self.lines[line][selColumnStart:])
					elif line == selLineEnd:
						part = self.lines[line][:selColumnEnd]
						if part != "":
							result.append(self.lines[line][:selColumnEnd])
					else:
						result.append(self.lines[line])
		return result

	def removeSelection(self):
		""" Remove selection """
		if self.selectionStart != None:
			self.modified = True
			selectionStart, selectionEnd = self.getSelection()
			selColumnStart, selLineStart, dummy = selectionStart
			selColumnEnd,   selLineEnd,   dummy = selectionEnd
			start = self.lines[selLineStart][:selColumnStart]
			end   = self.lines[selLineEnd  ][selColumnEnd:]
			self.lines[selLineStart] = start + end
			if selLineStart < selLineEnd:
				for line in range(selLineEnd, selLineStart,-1):
					del self.lines[line]
			self.moveCursor(selLineStart, selColumnStart)
			self.hideSelection()
			self.view.setRefreshAll()
			return True
		return False

	def pasteClipboard(self, selection):
		""" Paste clipboard at the cursor position """
		if selection != []:
			# Split the line with insertion
			start = self.lines[self.cursorLine][:self.cursorColumn]
			end   = self.lines[self.cursorLine][self.cursorColumn:]

			# Paste the first line
			self.lines[self.cursorLine] = start + selection[0]

			self.cursorLine += 1

			# Insert all lines from clipboard
			for line in selection[1:-1]:
				self.lines.insert(self.cursorLine, line)
				self.cursorLine += 1

			# If the last line of clipboard is not empty
			if len(selection[-1]) >= 1:
				# If the last line of clipboard contains new line
				if selection[-1][-1] == "\n":
					if len(selection) > 1:
						# Add the new line
						self.lines.insert(self.cursorLine, selection[-1])
						self.cursorLine += 1

					# Add the part after the insertion
					self.lines.insert(self.cursorLine, end)
					self.cursorColumn = 0
				else:
					if len(selection) > 1:
						self.lines.insert(self.cursorLine, selection[-1] + end)
						self.cursorColumn = len(selection[-1])
					else:
						self.cursorLine -= 1
						self.lines[self.cursorLine] += end
						self.cursorColumn = len(start) + len(selection[-1])
					
			self.moveCursor(self.cursorLine, self.cursorColumn)

	def moveCursor(self, line, column):
		""" Move the cursor """
		self.cursorLine   = line
		self.cursorColumn = column
		self.changeColumn(0)
		self.getTabCursorColumn()

	def copy(self):
		""" Manage copy key """
		self.selection = self.copyClipboard()

	def cut(self):
		""" Manage cut key """
		self.modified = True
		self.selection = self.copyClipboard()
		self.removeSelection()

	def paste(self):
		""" Manage paste key """
		self.modified = True
		self.removeSelection()
		self.pasteClipboard(self.selection)
		self.view.setRefreshAll()
		self.hideSelection()

	def changeCase(self):
		""" Change the case of selection """
		selection = self.copyClipboard()
		if selection != []:
			self.modified = True
			selectionStart = self.selectionStart
			selectionEnd   = self.selectionEnd

			self.removeSelection()
			isUpper = None
			for line in selection:
				for char in line:
					if useful.isupper(char):
						isUpper = True
						break
					elif useful.islower(char):
						isUpper = False
						break
				if isUpper != None:
					break
			for line in range(len(selection)):
				if isUpper:
					selection[line] = selection[line].lower()
				else:
					selection[line] = selection[line].upper()
			self.pasteClipboard(selection)
			self.view.setRefreshSelection()
			self.selectionStart = selectionStart
			self.selectionEnd   = selectionEnd

	def comment(self):
		""" Comment the selection """
		self.modified = True

		# If selection
		if self.selectionStart != None:
			selectionStart, selectionEnd = self.getSelection()
			selColumnStart, selLineStart, dummy = selectionStart
			selColumnEnd,   selLineEnd,   dummy = selectionEnd

			# Add tabulation
			for line in range(selLineStart, selLineEnd+1):
				if len(self.lines[line]) >= 1:
					if self.lines[line][0] != '#':
						self.lines[line] = "#" + self.lines[line]
					else:
						if len(self.lines[line]) >= 1:
							self.lines[line] = self.lines[line][1:]

			# Move the start selection to the start of first selected line
			self.selectionStart = [0,selLineStart, 0]

			# Get the length of last selected line
			lenLineEnd =  len(self.lines[selLineEnd])

			# Move the end of selection at the end of line selected
			self.selectionEnd   = [lenLineEnd-1, selLineEnd, self.getTabCursor(selLineEnd,lenLineEnd-1)]
			self.view.setRefreshSelection()
		else:
			if len(self.lines[self.cursorLine]) >= 1:
				# If nothing selected
				if self.lines[self.cursorLine][0] == "#":
					self.lines[self.cursorLine] = self.lines[self.cursorLine][1:]
					if self.cursorColumn > 0:
						self.changeColumn(-1)
				else:
					self.lines[self.cursorLine] = "#" + self.lines[self.cursorLine]
					self.changeColumn(1)
			self.view.setRefreshLine()

	def indent(self, keys):
		""" Manage tabulation key """
		# If nothing selected
		if self.selectionStart == None:
			self.addChar(keys)
		else:
			self.modified = True
			# Indent selection
			selectionStart, selectionEnd = self.getSelection()
			selColumnStart, selLineStart, dummy = selectionStart
			selColumnEnd,   selLineEnd,   dummy = selectionEnd

			# If a part of line selected
			if selLineStart == selLineEnd and not (selColumnStart == 0 and selColumnEnd == len(self.lines[selLineEnd])-1):
				self.addChar(INDENT)
			else:
				# If the last line selected is at beginning of line
				if selColumnEnd == 0:
					# This line must not be indented
					selLineEnd -= 1

				# Add tabulation
				for line in range(selLineStart, selLineEnd+1):
					self.lines[line] = "\t" + self.lines[line]

				# Move the start selection to the start of first selected line
				self.selectionStart = [0,selLineStart, 0]

				# If the last line selected is not at beginning of line
				if selColumnEnd > 0:
					# Get the length of last selected line
					lenLineEnd =  len(self.lines[selLineEnd])

					# If the end of selection is not on the last line
					if selLineEnd < len(self.lines)-1:
						lenLineEnd -= 1

					# Move the end of selection at the end of line selected
					self.selectionEnd   = [lenLineEnd, selLineEnd, self.getTabCursor(selLineEnd,lenLineEnd)]
				else:
					# Move the end of selection at the start of the last line selected
					self.selectionEnd  = [0, selLineEnd+1, 0]
			self.view.setRefreshSelection()

	def unindent(self, keys):
		""" Manage the unindentation key """
		# If nothing selected
		if self.selectionStart == None:
			self.backspace()
		else:
			self.modified = True

			# Unindent selection
			selectionStart, selectionEnd = self.getSelection()
			selColumnStart, selLineStart, dummy = selectionStart
			selColumnEnd,   selLineEnd,   dummy = selectionEnd

			# If the selection is only alone line
			if selLineStart == selLineEnd:
				self.hideSelection()
			else:
				# If the last line selected is at beginning of line
				if selColumnEnd == 0:
					# This line must not be indented
					selLineEnd -= 1

				# Remove indentation
				for line in range(selLineStart, selLineEnd+1):
					if len(self.lines[line]) >= 1:
						if self.lines[line][0] == "\t" or self.lines[line][0] == " ":
							self.lines[line] = self.lines[line][1:]

				# Move the start selection to the start of first selected line
				self.selectionStart = [0,selLineStart, 0]

				# If the last line selected is not at beginning of line
				if selColumnEnd > 0:
					# Get the length of last selected line
					lenLineEnd =  len(self.lines[selLineEnd])

					# If the end of selection is not on the last line
					if selLineEnd < len(self.lines)-1:
						lenLineEnd -= 1

					# Move the end of selection at the end of line selected
					self.selectionEnd   = [lenLineEnd, selLineEnd, self.getTabCursor(selLineEnd,lenLineEnd)]
				else:
					# Move the end of selection at the start of the last line selected
					self.selectionEnd  = [0, selLineEnd+1, 0]
			self.view.setRefreshSelection()

	def replace(self, old, new):
		""" Replace the selection """
		if self.readOnly == False:
			selection = self.copyClipboard()
			if len(selection) == 1:
				if selection[0] == old:
					self.delete()
					self.insertChar(new)
					return True
		return False

	def getCursorChar(self):
		""" Get the char on the cursor """
		try:
			return self.lines[self.cursorLine][self.cursorColumn]
		except:
			return None

	def moveWord(self, direction):
		""" Move the cursor to the word """
		state = 0
		while self.changeColumn(direction):
			currentChar = self.getCursorChar()
			if currentChar == None:
				break
			elif useful.ispunctuation(currentChar):
				if state == 0:
					state = 2
				elif state == 1:
					break
			elif useful.isalpha(currentChar):
				if state == 0:
					state = 1
				elif state == 2:
					break
			elif useful.isspace(currentChar):
				if state == 1:
					break
				if state == 2:
					break

	def nextWord(self):
		""" Move the cursor to the next word """
		self.hideSelection()
		self.moveWord(1)
		self.view.move()

	def previousWord(self):
		""" Move the cursor to the previous word """
		self.hideSelection()
		self.moveWord(-1)
		self.view.move()

	def top(self):
		""" Move the cursor to the first line of text """
		self.goto(1)

	def bottom(self):
		""" Move the cursor to the last line of text """
		self.goto(100000000000)

	def treatChar(self, keys):
		""" Treat character entered """
		char = ord(keys[0][0])
		if self.readOnly is False:
			if char >= 0x20 and char != 0x7F:
				self.addChar(keys)
				return True
		return False

	def treatKey(self, keys):
		""" Treat keys """
		if self.treatChar(keys) == False:
			# Move in the edit field
			if   keys[0] in UP  :            self.arrowUp(keys)
			elif keys[0] in DOWN:            self.arrowDown(keys)
			elif keys[0] in LEFT:            self.arrowLeft(keys)
			elif keys[0] in RIGHT:           self.arrowRight(keys)
			elif keys[0] in HOME:            self.home()
			elif keys[0] in END:             self.end()
			elif keys[0] in PAGE_UP:         self.pageUp(keys)
			elif keys[0] in PAGE_DOWN:       self.pageDown(keys)
			elif keys[0] in TOP:             self.top()
			elif keys[0] in BOTTOM:          self.bottom()
			elif keys[0] in NEXT_WORD:       self.nextWord()
			elif keys[0] in PREVIOUS_WORD:   self.previousWord()
			# Selection the edit field
			elif keys[0] in SELECT_UP:       self.selectUp(keys)
			elif keys[0] in SELECT_DOWN:     self.selectDown(keys)
			elif keys[0] in SELECT_RIGHT:    self.selectRight(keys)
			elif keys[0] in SELECT_LEFT:     self.selectLeft(keys)
			elif keys[0] in SELECT_HOME:     self.selectHome()
			elif keys[0] in SELECT_END:      self.selectEnd()
			elif keys[0] in SELECT_PAGE_UP:  self.selectPageUp(keys)
			elif keys[0] in SELECT_PAGE_DOWN:self.selectPageDown(keys)
			elif keys[0] in SELECT_ALL:      self.selectAll()
			elif keys[0] in SELECT_NEXT_WORD:self.selectNextWord()
			elif keys[0] in SELECT_PREV_WORD:self.selectPreviousWord()

			# If the edit is not in read only
			elif self.readOnly is False:
				# Modification in the edit field
				if   keys[0] in COPY:            self.copy()
				elif keys[0] in CUT:             self.cut()
				elif keys[0] in PASTE:           self.paste()

				elif keys[0] in INDENT:          self.indent(keys)
				elif keys[0] in UNINDENT:        self.unindent(keys)
				elif keys[0] in CHANGE_CASE:     self.changeCase()
				elif keys[0] in COMMENT:         self.comment()

				elif keys[0] in BACKSPACE:       self.backspace()
				elif keys[0] in DELETE:          self.delete()
				elif keys[0] in NEW_LINE:        self.newLine()
				elif keys[0] in DELETE_LINE:     self.deleteLine()
			# else: self.addChar(keys)

class Edit:
	""" Class which aggregate the View and Text """
	def __init__(self, viewTop=1, viewHeight=None, readOnly=False):
		""" Constructor """
		self.view = View(viewHeight, viewTop)
		self.text = Text(readOnly)
		self.text.setView(self.view)
		self.view.setText(self.text)

class Editor:
	""" Class which manage a complete editor """
	def __init__(self, filename_, readOnly=False):
		""" Constructor """
		self.file = filename_
		self.filename = useful.split(filename_)[1]
		self.edit = Edit(readOnly=readOnly)
		self.edit.text.load(filename_)
		self.isRefreshHeader = True
		self.findText = None
		self.replaceText = None
		self.keys= []
		self.loop = None

		if (not useful.exists(filename_) and readOnly == True) or useful.isdir(filename_):
			print("Cannot open '%s'"%self.filename)
		else:
			self.run()

	def refreshHeader(self):
		""" Refresh the header of editor """
		if self.isRefreshHeader:
			self.edit.view.moveCursor(0, 0)
			filename_ = "File: %s"%(self.filename)
			if self.edit.text.readOnly == False:
				filename_ += " (*)" if self.edit.text.modified else ""
				end = "Mode: %s"%("Replace" if self.edit.text.replaceMode else "Insert")
			else:
				end = "Read only" if self.edit.text.readOnly else ""

			header = "\x1B[7m %s%s%s \x1B[m"%(filename_, " "*(self.edit.view.width - len(filename_) - len(end)-2), end)
			self.edit.view.write(header)
			self.edit.view.moveCursor()
			self.isRefreshHeader = False

	def refresh(self):
		""" Refresh the editor """
		self.refreshHeader()
		self.edit.view.refresh()

	def toggleMode(self):
		""" Change the replace mode """
		if self.edit.text.replaceMode:
			self.edit.text.replaceMode = False
		else:
			self.edit.text.replaceMode = True
		self.isRefreshHeader = True

	def save(self):
		""" Save the file edited """
		self.edit.text.save()
		self.isRefreshHeader = True

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
					self.edit.view.setRefreshAll()
					self.isRefreshHeader = True
					break
		else:
			self.loop = False

	def input(self, text, help_=""):
		""" Input value, used to get a line number, or text searched """
		edit_ = Edit(viewTop=2, viewHeight=1, readOnly=False)
		edit_.view.cls()
		edit_.view.moveCursor(1,0)
		edit_.view.write(text)
		edit_.view.moveCursor(4,0)
		edit_.view.write(help_)
		result = None
		while 1:
			edit_.view.refresh()
			key = self.getKey()
			if key[0] in NEW_LINE:
				result = edit_.text.lines[0]
				break
			elif key[0] in ESCAPE:
				break
			else:
				edit_.text.treatKey(key)
		return result

	def find(self):
		""" Find a text """
		self.findText = self.input("Find :","\x1B[7mEsc\x1B[m:Abort  \x1B[7m^Left\x1B[m,\x1B[7m^Up\x1B[m:Previous  \x1B[7m^Down\x1B[m,\x1B[7m^Right\x1B[m:Next")
		self.findNext()
		self.edit.view.setRefreshAll()
		self.isRefreshHeader = True

	def replace(self):
		""" Replace a text """
		self.findText    = self.input("Find to replace :","\x1B[7mEsc\x1B[m:Abort")
		if self.findText:
			self.replaceText = self.input("Replace with :","\x1B[7mEsc\x1B[m:Abort  \x1B[7m^Left\x1B[m,\x1B[7m^Up\x1B[m:Previous  \x1B[7m^Down\x1B[m,\x1B[7m^Right\x1B[m:Next  \x1B[7m^R\x1B[m:Replace")
			self.findNext()

		self.edit.view.setRefreshAll()
		self.isRefreshHeader = True

	def replaceCurrent(self):
		""" Replace current """
		if self.findText and self.replaceText:
			if self.edit.text.replace(self.findText, self.replaceText):
				self.findNext()

	def findNext(self):
		""" Find next text """
		if self.findText:
			self.edit.text.findNext(self.findText)

	def findPrevious(self):
		""" Find previous text """
		if self.findText:
			self.edit.text.findPrevious(self.findText)

	def goto(self):
		""" Goto line """
		lineNumber = self.input("Goto line :","\x1B[7mEsc\x1B[m:Abort")
		try:
			lineNumber = int(lineNumber)
			self.edit.text.goto(int(lineNumber))
		except:
			pass
		self.edit.view.setRefreshAll()
		self.isRefreshHeader = True

	def groupKey(self):
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

	def getKey(self):
		""" Get a key pressed """
		if len(self.keys) == 0:
			while True:
				try:
					key = useful.getch()
				except KeyboardInterrupt:
					key = "\x03"
				self.keys.append(key)
				if useful.kbhit() == False or len(self.keys) > 5:
					break
		return self.groupKey()

	def execute(self):
		""" Execute the python script edited """
		self.save()
		loop = True
		while loop:
			self.edit.view.resetScrollRegion()
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
				keys = self.getKey()
				if keys[0] in NEW_LINE:
					loop = False
					break
				elif keys[0] in EXECUTE:
					break
				# else:
					# print(useful.dump(keys[0]))
		self.edit.view.cls()
		self.edit.view.setRefreshAll()
		self.isRefreshHeader = True

	def run(self):
		""" Core of the editor """
		self.edit.view.cls()
		self.edit.view.getScreenSize()
		self.loop = True
		while(self.loop):
			try:
				self.refresh()
				keys = self.getKey()
				modified = self.edit.text.modified
				if ord(keys[0][0]) < 0x20:
					if   keys[0] in TOGGLE_MODE:    self.toggleMode()
					elif keys[0] in FIND:           self.find()
					elif keys[0] in REPLACE:        self.replace()
					elif keys[0] in FIND_PREVIOUS:  self.findPrevious()
					elif keys[0] in FIND_NEXT:      self.findNext()
					elif keys[0] in REPLACE_CURRENT:self.replaceCurrent()
					elif keys[0] in EXIT:           self.exit()
					elif keys[0] in GOTO:           self.goto()
					elif keys[0] in SAVE:           self.save()
					elif keys[0] in EXECUTE:        self.execute()
				self.edit.text.treatKey(keys)
				if modified != self.edit.text.modified:
					self.isRefreshHeader = True
			except KeyboardInterrupt:
				pass
		self.edit.view.resetScrollRegion()
		self.edit.view.reset()

if __name__ == "__main__":
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	else:
		filename = "editor.txt"
	edit = Editor(filename, readOnly=False)
