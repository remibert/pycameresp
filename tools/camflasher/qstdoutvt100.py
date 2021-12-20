""" Stdout VT100 ouptut on qtextbrowser widget """
from vt100 import VT100
import useful

class QStdoutVT100:
	""" Stdout VT100 ouptut on qtextbrowser widget """
	def __init__(self, qtextbrowser):
		""" Constructor with QTextBrowser widget"""
		self.qtextbrowser = qtextbrowser
		self.vt100 = VT100()
		self.buffer = b""
		self.modified = False

	def write(self, string):
		""" Write on stdout """
		if len(string) > 0 or string is None:
			string = useful.decode(string)
			# pylint:disable=consider-using-enumerate
			for char in range(len(string)):
				self.vt100.treat_key(string[char])
			self.modified = True

	def refresh(self):
		""" Refresh the console """
		if self.modified:
			content_width  = self.qtextbrowser.contentsRect().width()
			content_height = self.qtextbrowser.contentsRect().height()
			char_width  = self.qtextbrowser.fontMetrics().boundingRect("W"*100).size().width()
			char_height = self.qtextbrowser.fontMetrics().boundingRectChar("|").size().height()
			width = ((content_width*100)//char_width)-1
			height = content_height//char_height
			self.modified = False

			if self.vt100.get_count_lines() > height:
				self.vt100.forget_lines(self.vt100.get_count_lines()-height)

			content = self.vt100.get_content(width)
			self.qtextbrowser.setHtml(content)

	def flush(self):
		""" Flush stdout """

	def isatty(self):
		""" Test whether a file descriptor refers to a terminal """
		return True
