# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Logger and exception functions """
import sys
import io
import tools.filesystem
import tools.strings
import tools.date

def exception(err, msg=""):
	""" Return the content of exception into a string """
	file = io.StringIO()
	if tools.filesystem.ismicropython():
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

def syslog(err, msg="", display=True, write=True):
	""" Log the error in syslog.log file """
	if isinstance(err, Exception):
		err = exception(err)
	if msg != "":
		msg += "\n"
		if display:
			print(tools.strings.tostrings(msg))
	if display:
		print(tools.strings.tostrings(err))

	result = "%s%s"%(tools.strings.tostrings(msg),tools.strings.tostrings(err))

	if write:
		log(result)
	return result

_max_log_size = 32*1024
_max_log_quantity = 4
def set_size(size, quantity):
	""" Change the size of logger
	Parameters :
	- size : max size of syslog file
	- quantity : max quantity of syslog file """
	global _max_log_size
	global _max_log_quantity
	_max_log_size = size
	_max_log_quantity = quantity

def log(msg):
	""" Log message in syslog.log file without printing """
	# pylint:disable=unspecified-encoding
	try:
		filename = "syslog.log"
		if tools.filesystem.ismicropython():
			filename = "/" + filename

		log_file = open(filename,"a")
		log_file.seek(0,2)

		if log_file.tell() > _max_log_size:
			log_file.close()
			for i in range(_max_log_quantity,0,-1):
				old = ".%d"%i
				new = ".%d"%(i-1)
				if i == 1:
					new = ""
				tools.filesystem.rename(filename + new,filename + old)
			log_file = open(filename,"a")

		log_file.write(tools.date.date_ms_to_string() + " %s\n"%(msg))
		log_file.flush()
		log_file.close()
	except:
		print("No space, flash full")

def html_exception(err):
	""" Return the content of exception into an html bytes """
	text = exception(err)
	text = text.replace("\n    ","<br>&nbsp;&nbsp;&nbsp;&nbsp;")
	text = text.replace("\n  ","<br>&nbsp;&nbsp;")
	text = text.replace("\n","<br>")
	return tools.strings.tobytes(text)
