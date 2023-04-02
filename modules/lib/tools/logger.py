# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Logger and exception functions """
import sys
import io
try:
	from tools import filesystem, strings, date
except:
	import filesystem
	import strings

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

def syslog(err, msg="", display=True, write=True):
	""" Log the error in syslog.log file """
	if isinstance(err, Exception):
		err = exception(err)
	if msg != "":
		msg += "\n"
		if display:
			print(strings.tostrings(msg))
	if display:
		print(strings.tostrings(err))

	result = "%s%s"%(strings.tostrings(msg),strings.tostrings(err))

	if write:
		log(result)
	return result

def log(msg):
	""" Log message in syslog.log file without printing """
	# pylint:disable=unspecified-encoding
	try:
		filename = "syslog.log"
		if filesystem.ismicropython():
			filename = "/" + filename

		log_file = open(filename,"a")
		log_file.seek(0,2)

		if log_file.tell() >32*1024:
			log_file.close()
			filesystem.rename(filename + ".3",filename + ".4")
			filesystem.rename(filename + ".2",filename + ".3")
			filesystem.rename(filename + ".1",filename + ".2")
			filesystem.rename(filename       ,filename + ".1")
			log_file = open(filename,"a")

		log_file.write(date.date_ms_to_string() + " %s\n"%(msg))
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
	return strings.tobytes(text)
