""" Stdout VT100 ouptut on qtextbrowser widget """
import sys
from threading import Lock
from vt100 import VT100
from PyQt6.QtCore import Qt
class QStdoutVT100:
	""" Stdout VT100 ouptut on qtextbrowser widget """
	def __init__(self, qtextbrowser):
		""" Constructor with QTextBrowser widget"""
		self.qtextbrowser = qtextbrowser
		self.vt100 = VT100()
		self.lock = Lock()
		self.output = []
		self.can_test = False
		self.stdout = sys.stdout
		sys.stdout = self

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

	def write(self, string):
		""" Write on stdout """
		if len(string) > 0 and string is not None and string != "":
			try:
				self.lock.acquire()
				# self.stdout.write(string)
				# pylint:disable=consider-using-enumerate
				for char in range(len(string)):
					output = self.vt100.treat_key(string[char])
					if output != "":
						self.output.append(output)
				self.vt100.set_modified()
			except Exception as err:
				self.stdout.write(err)
			finally:
				self.lock.release()

	def get_size(self):
		""" Get the size of VT100 console """
		# Calculate the dimension in pixels of a text of 200 lines with 200 characters
		line = "W"*200 + "\n"
		line = line*200
		line = line[:-1]
		size = self.qtextbrowser.fontMetrics().size(Qt.TextFlag.TextWordWrap,line)

		# Deduce the size of console visible in the window
		width  = (self.qtextbrowser.contentsRect().width()  * 200)// size.width() -  1
		height = (self.qtextbrowser.contentsRect().height() * 200)// size.height()
		return width, height

	def resizeEvent(self):
		""" Resize event """
		width, height = self.get_size()
		self.vt100.set_size(width,height)

	def refresh(self):
		""" Refresh the console """
		result = ""
		self.can_test = True
		if self.vt100.is_modified():
			self.qtextbrowser.setHtml(self.vt100.to_html())
			for output in self.output:
				result += output
			self.output = []
		return result

	def flush(self):
		""" Flush stdout """
		# NEVER NEVER REFRESH HERE ELSE IT CRASH.... self.refresh()

	def isatty(self):
		""" Test whether a file descriptor refers to a terminal """
		return True
