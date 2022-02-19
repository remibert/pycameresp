# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Logger and exception functions """
import sys
import io
from tools import filesystem, strings

def exception(err, msg=""):
	""" Return the content of exception into a string """
	file = io.StringIO()
	if filesystem.ismicropython():
		# pylint: disable=no-member
		sys.print_exception(err, file)
		text = file.getvalue()
	else:
		try:
			import traceback
			file.write(traceback.format_exc())
		except Exception as err:
			print(err)
		text = file.getvalue()
	return text

def syslog(err, msg="", display=True):
	""" Log the error in syslog.log file """
	filename = "syslog.log"
	if isinstance(err, Exception):
		err = exception(err)
	if filesystem.ismicropython():
		filename = "/" + filename
	if msg != "":
		msg += "\n"
		if display:
			print(strings.tostrings(msg))
	if display:
		print(strings.tostrings(err))

	logFile = open(filename,"a")
	logFile.seek(0,2)

	if logFile.tell() >32*1024:
		logFile.close()
		print("File %s too big"%filename)
		filesystem.rename(filename + ".3",filename + ".4")
		filesystem.rename(filename + ".2",filename + ".3")
		filesystem.rename(filename + ".1",filename + ".2")
		filesystem.rename(filename       ,filename + ".1")
		logFile = open(filename,"a")

	result = "%s%s"%(strings.tostrings(msg),strings.tostrings(err))
	logFile.write(strings.date_ms_to_string() + " %s\n"%(result))
	logFile.close()
	return result

def html_exception(err):
	""" Return the content of exception into an html bytes """
	text = exception(err)
	text = text.replace("\n    ","<br>&nbsp;&nbsp;&nbsp;&nbsp;")
	text = text.replace("\n  ","<br>&nbsp;&nbsp;")
	text = text.replace("\n","<br>")
	return strings.tobytes(text)
